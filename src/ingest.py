"""Document ingestion pipeline — loads, chunks, embeds, and contextualizes documents into ChromaDB.

Enhanced with Anthropic-style contextual chunking: each chunk gets a brief LLM-generated
summary prepended that situates it within the broader document, significantly improving
retrieval accuracy for ambiguous or colloquial queries.
"""

import os
import sys
import hashlib
import json
import logging
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
    CHROMA_PERSIST_DIR,
    HR_COLLECTION_NAME,
    QA_COLLECTION_NAME,
    HR_DATA_DIR,
    QA_DATA_DIR,
    EMBEDDING_MODEL,
    get_llm_with_fallback,
)

logger = logging.getLogger(__name__)

# Cache directory for contextualized chunks (avoids re-processing unchanged docs)
CONTEXT_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".context_cache")


def load_documents(directory: str):
    loader = DirectoryLoader(
        directory,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    return loader.load()


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=CHUNK_SEPARATORS,
    )
    return splitter.split_documents(documents)


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def _get_doc_title(source_path: str) -> str:
    """Extract a human-readable document title from the file path."""
    basename = os.path.basename(source_path)
    return basename.replace(".md", "").replace("_", " ")


def _generate_chunk_context(chunk_content: str, full_doc_content: str, doc_title: str, llm) -> str:
    """Generate a contextual summary for a chunk using the LLM.
    
    This implements Anthropic's Contextual Retrieval technique: each chunk gets a
    brief (2-3 sentence) explanation that situates it within the broader document.
    This dramatically improves retrieval accuracy for ambiguous queries.
    """
    prompt = (
        f"You are helping improve search retrieval by adding context to document chunks.\n\n"
        f"Document title: {doc_title}\n\n"
        f"Full document (first 3000 chars for context):\n{full_doc_content[:3000]}\n\n"
        f"Chunk to contextualize:\n{chunk_content}\n\n"
        f"Write a brief 2-3 sentence context that explains:\n"
        f"1. Which document this chunk is from\n"
        f"2. What section or topic this chunk covers\n"
        f"3. How it fits within the broader document\n\n"
        f"Be concise and factual. Start with 'This chunk is from...'"
    )
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        logger.warning(f"[Ingest] Contextual summary failed for chunk: {e}")
        # Fallback: use document title as minimal context
        return f"This chunk is from the document '{doc_title}'."


def _get_cache_key(chunk_content: str, doc_title: str) -> str:
    """Generate a stable cache key for a chunk."""
    content = f"{doc_title}::{chunk_content}"
    return hashlib.sha256(content.encode()).hexdigest()


def _load_context_cache() -> dict:
    """Load the context cache from disk."""
    cache_path = os.path.join(CONTEXT_CACHE_DIR, "context_cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_context_cache(cache: dict):
    """Save the context cache to disk."""
    os.makedirs(CONTEXT_CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CONTEXT_CACHE_DIR, "context_cache.json")
    with open(cache_path, "w") as f:
        json.dump(cache, f)


def contextualize_chunks(chunks, documents, llm) -> list:
    """Add contextual summaries to each chunk using the LLM.
    
    For each chunk, generates a brief summary that explains what document it comes from
    and what topic it covers. This context is prepended to the chunk content before
    embedding, which significantly improves retrieval accuracy.
    
    Uses a local file cache to avoid re-processing unchanged chunks.
    """
    # Build a doc content lookup by source path
    doc_content_map = {}
    for doc in documents:
        source = doc.metadata.get("source", "")
        doc_content_map[source] = doc.page_content

    cache = _load_context_cache()
    contextualized = []
    new_contexts = 0
    cached_contexts = 0

    for i, chunk in enumerate(chunks):
        source = chunk.metadata.get("source", "")
        doc_title = _get_doc_title(source)
        full_doc_content = doc_content_map.get(source, "")

        cache_key = _get_cache_key(chunk.page_content, doc_title)

        if cache_key in cache:
            context = cache[cache_key]
            cached_contexts += 1
        else:
            context = _generate_chunk_context(chunk.page_content, full_doc_content, doc_title, llm)
            cache[cache_key] = context
            new_contexts += 1

        # Prepend context to chunk content
        chunk.page_content = f"[Context: {context}]\n\n{chunk.page_content}"
        contextualized.append(chunk)

        if (i + 1) % 10 == 0:
            print(f"    Contextualized {i + 1}/{len(chunks)} chunks...")

    _save_context_cache(cache)
    print(f"    Context generation: {new_contexts} new, {cached_contexts} cached")
    return contextualized


def ingest_collection(data_dir: str, collection_name: str, embeddings, llm):
    print(f"Loading documents from {data_dir}...")
    docs = load_documents(data_dir)
    print(f"  Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"  Split into {len(chunks)} chunks")

    print(f"  Generating contextual summaries for each chunk...")
    contextualized_chunks = contextualize_chunks(chunks, docs, llm)

    print(f"  Embedding and storing in collection '{collection_name}'...")
    vectorstore = Chroma.from_documents(
        contextualized_chunks,
        embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print(f"  Done! Collection '{collection_name}' has {vectorstore._collection.count()} vectors")
    return vectorstore


def run_ingestion():
    print("=" * 60)
    print("ICE QAgent — Document Ingestion Pipeline (with Contextual Chunking)")
    print("=" * 60)

    embeddings = get_embeddings()
    llm = get_llm_with_fallback()

    print("\n[1/2] Ingesting HR documents...")
    ingest_collection(HR_DATA_DIR, HR_COLLECTION_NAME, embeddings, llm)

    print("\n[2/2] Ingesting QA documents...")
    ingest_collection(QA_DATA_DIR, QA_COLLECTION_NAME, embeddings, llm)

    print("\n" + "=" * 60)
    print("Ingestion complete! (with contextual chunk summaries)")
    print(f"ChromaDB persisted at: {CHROMA_PERSIST_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    run_ingestion()
