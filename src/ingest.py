"""Document ingestion pipeline — loads, chunks, and embeds documents into ChromaDB."""

import os
import sys
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
)


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


def ingest_collection(data_dir: str, collection_name: str, embeddings):
    print(f"Loading documents from {data_dir}...")
    docs = load_documents(data_dir)
    print(f"  Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"  Split into {len(chunks)} chunks")

    print(f"  Embedding and storing in collection '{collection_name}'...")
    vectorstore = Chroma.from_documents(
        chunks,
        embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print(f"  Done! Collection '{collection_name}' has {vectorstore._collection.count()} vectors")
    return vectorstore


def run_ingestion():
    print("=" * 60)
    print("ICE QAgent — Document Ingestion Pipeline")
    print("=" * 60)

    embeddings = get_embeddings()

    print("\n[1/2] Ingesting HR documents...")
    ingest_collection(HR_DATA_DIR, HR_COLLECTION_NAME, embeddings)

    print("\n[2/2] Ingesting QA documents...")
    ingest_collection(QA_DATA_DIR, QA_COLLECTION_NAME, embeddings)

    print("\n" + "=" * 60)
    print("Ingestion complete!")
    print(f"ChromaDB persisted at: {CHROMA_PERSIST_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    run_ingestion()
