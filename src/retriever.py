"""Advanced retrieval pipeline with conversation-aware query reformulation,
LLM-powered query expansion, hybrid search, and cross-encoder re-ranking."""

import re
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from flashrank import Ranker, RerankRequest

from src.config import (
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    RETRIEVAL_TOP_K,
)

logger = logging.getLogger(__name__)

# Initialize re-ranker once (loads model on first use)
_reranker = None


def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="./flashrank_cache")
    return _reranker


def _get_llm():
    """Get an LLM instance for query expansion with waterfall fallback.

    Uses the centralized waterfall factory from config.py — automatically
    falls back across Gemini → Groq models on rate limit errors.
    """
    from src.config import get_llm_with_fallback
    return get_llm_with_fallback()


def get_vectorstore(collection_name: str):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma(
        collection_name=collection_name,
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
    )


# ── Conversation-Aware Query Reformulation ─────────────────────────────

def _looks_like_followup(query: str) -> bool:
    """Detect if a query looks like a follow-up that needs context from prior messages.
    
    Follow-up indicators:
    - Very short query (under 8 words)
    - Contains pronouns/references: "it", "that", "those", "they", "this"
    - Starts with "what about", "how about", "and", "but", "also"
    - Contains comparative words: "same", "similar", "different", "instead"
    """
    query_lower = query.lower().strip()
    words = query_lower.split()
    
    # Short queries are more likely follow-ups
    is_short = len(words) <= 8
    
    # Follow-up signal words
    followup_starters = [
        "what about", "how about", "and ", "but ", "also ", "or ",
        "what if", "same for", "how does that", "is that", "does that",
        "can i also", "what else", "anything else", "tell me more",
    ]
    starts_with_followup = any(query_lower.startswith(s) for s in followup_starters)
    
    # Pronouns that reference prior context
    context_pronouns = {"it", "that", "those", "they", "this", "them", "its", "their"}
    has_pronouns = bool(context_pronouns.intersection(set(words)))
    
    # Comparative/continuation words
    continuation_words = {"same", "similar", "different", "instead", "other", "another", "else", "too"}
    has_continuation = bool(continuation_words.intersection(set(words)))
    
    return starts_with_followup or (is_short and (has_pronouns or has_continuation))


def reformulate_query(query: str, chat_history: list) -> str:
    """Reformulate a follow-up query into a self-contained search query using chat history.
    
    This is the KEY feature for conversation-aware retrieval. Without it, a follow-up
    like "what about for remote workers?" would search for those exact words instead
    of "PTO policy for remote workers at ICE".
    
    Only triggers when the query looks like a follow-up (short, contains pronouns, etc.).
    For standalone queries, returns the original query unchanged.
    
    Args:
        query: The user's current message
        chat_history: List of previous messages [{"role": "user"/"assistant", "content": "..."}]
    
    Returns:
        Reformulated self-contained query string
    """
    # If no chat history or query doesn't look like a follow-up, skip reformulation
    if not chat_history or not _looks_like_followup(query):
        return query
    
    try:
        llm = _get_llm()
        
        # Build recent conversation context (last 3-4 messages)
        recent = chat_history[-4:]
        history_text = "\n".join(
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content'][:300]}"
            for msg in recent
        )
        
        reformulation_prompt = (
            "You are a search query reformulator. Given a conversation and a follow-up question, "
            "rewrite the follow-up as a SELF-CONTAINED search query that can be understood without "
            "the conversation context.\n\n"
            "Rules:\n"
            "- Include the key topic/subject from the conversation in the reformulated query\n"
            "- Keep it concise (under 15 words)\n"
            "- Do NOT answer the question — just reformulate it\n"
            "- Output ONLY the reformulated query, nothing else\n\n"
            f"Conversation:\n{history_text}\n\n"
            f"Follow-up question: {query}\n\n"
            f"Reformulated search query:"
        )
        
        response = llm.invoke(reformulation_prompt)
        reformulated = response.content.strip().strip('"').strip("'")
        
        # Sanity check: don't use reformulation if it's too long or empty
        if reformulated and len(reformulated) < 200 and len(reformulated) > 3:
            logger.info(f"[Retriever] Query reformulated: '{query}' → '{reformulated}'")
            return reformulated
        
        logger.warning(f"[Retriever] Reformulation produced invalid result, using original query")
        return query
        
    except Exception as e:
        logger.warning(f"[Retriever] Query reformulation failed: {e}, using original query")
        return query


# ── Query Expansion ────────────────────────────────────────────────────

def expand_query_with_llm(query: str) -> list[str]:
    """Use the LLM to generate better search queries from colloquial user input.

    This is critical for queries like "can I wear track pants to work" which need
    to be translated to formal terms like "dress code policy" for retrieval to work.
    """
    queries = [query]

    try:
        llm = _get_llm()
        expansion_prompt = (
            "You are a search query optimizer for an enterprise knowledge base containing "
            "HR policies and QA engineering documentation.\n\n"
            "Given the user's question, generate 2-3 alternative search queries that would "
            "match relevant documents. Focus on:\n"
            "- Formal/policy terminology (e.g., 'track pants' → 'dress code policy')\n"
            "- Specific document section names that might exist\n"
            "- Key concepts the user is really asking about\n\n"
            f"User question: {query}\n\n"
            "Return ONLY the alternative queries, one per line. No numbering, no explanations."
        )
        response = llm.invoke(expansion_prompt)
        expanded = [
            line.strip().strip("-•*").strip()
            for line in response.content.strip().split("\n")
            if line.strip() and len(line.strip()) > 5
        ]
        queries.extend(expanded[:3])
        logger.info(f"[Retriever] LLM expanded '{query}' → {queries}")

    except Exception as e:
        logger.warning(f"[Retriever] LLM expansion failed: {e}, falling back to heuristic")
        # Fallback to heuristic expansion
        keywords = re.sub(
            r"^(what|how|where|when|who|why|can|do|does|is|are|tell me about|explain)\s+",
            "", query.lower(), flags=re.IGNORECASE,
        ).rstrip("?").strip()
        if keywords != query.lower().rstrip("?").strip():
            queries.append(keywords)
        if "ice" not in query.lower():
            queries.append(f"ICE {keywords}")

    return queries


def keyword_filter(query: str, documents: list) -> list:
    """Boost documents that contain exact keyword matches from the query.

    Returns documents sorted by keyword overlap count (descending), breaking ties
    by original order (which preserves semantic similarity ranking).
    """
    query_terms = set(re.findall(r"\b\w{3,}\b", query.lower()))
    stop_words = {"the", "what", "how", "does", "are", "for", "and", "that", "this", "with", "from", "have", "can", "wear", "going"}
    query_terms -= stop_words

    scored = []
    for i, (doc, sem_score) in enumerate(documents):
        doc_text = doc.page_content.lower()
        keyword_hits = sum(1 for term in query_terms if term in doc_text)
        scored.append((doc, sem_score, keyword_hits, i))

    scored.sort(key=lambda x: (-x[2], -x[1], x[3]))
    return [(doc, sem_score) for doc, sem_score, _, _ in scored]


def rerank_documents(query: str, documents: list, top_k: int = None) -> list:
    """Re-rank documents using FlashRank cross-encoder for more accurate relevance scoring."""
    if not documents:
        return documents

    if top_k is None:
        top_k = RETRIEVAL_TOP_K

    ranker = get_reranker()

    passages = []
    for doc, _ in documents:
        passages.append({
            "id": id(doc),
            "text": doc.page_content,
            "meta": doc.metadata,
        })

    rerank_request = RerankRequest(query=query, passages=passages)
    reranked = ranker.rerank(rerank_request)

    doc_map = {id(doc): doc for doc, _ in documents}
    result = []
    for item in reranked[:top_k]:
        doc_id = item["id"]
        if doc_id in doc_map:
            result.append((doc_map[doc_id], item["score"]))

    return result


def retrieve(query: str, collection_name: str, top_k: int = None, chat_history: list = None) -> list:
    """Full retrieval pipeline:
    1. Conversation-aware query reformulation (for follow-up questions)
    2. LLM-powered query expansion (translates colloquial → formal terms)
    3. Semantic search across all query variations (deduplicated)
    4. Keyword overlap boost (hybrid scoring)
    5. Cross-encoder re-ranking (ms-marco for final precision)

    Returns list of (Document, score) tuples, ranked by relevance.
    """
    if top_k is None:
        top_k = RETRIEVAL_TOP_K

    # Step 0: Conversation-aware reformulation (KEY FEATURE)
    search_query = reformulate_query(query, chat_history or [])
    
    vectorstore = get_vectorstore(collection_name)

    # Step 1: LLM-powered query expansion (on the reformulated query)
    queries = expand_query_with_llm(search_query)

    # Step 2: Semantic search across all query variations (deduplicate by content)
    seen_content = set()
    all_results = []
    fetch_k = top_k * 2

    for q in queries:
        results = vectorstore.similarity_search_with_relevance_scores(q, k=fetch_k)
        for doc, score in results:
            content_hash = hash(doc.page_content)
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                all_results.append((doc, score))

    if not all_results:
        return []

    # Step 3: Hybrid boost — keyword overlap scoring
    hybrid_results = keyword_filter(search_query, all_results)

    # Step 4: Cross-encoder re-ranking using the BEST expanded query
    # Use the expanded formal query for re-ranking (better match than colloquial)
    rerank_query = queries[1] if len(queries) > 1 else search_query
    reranked = rerank_documents(rerank_query, hybrid_results, top_k=top_k)

    return reranked
