"""
QA Expert Agent — ReAct-style agent with multi-step reasoning.

Implements a flexible RAG strategy:
1. Retrieve from internal QA knowledge base (ChromaDB)
2. Evaluate relevance of retrieved documents
3. If internal docs are insufficient, autonomously fall back to Tavily web search
4. Synthesize answer with source citations and confidence scoring
"""

import json
import logging
from tavily import TavilyClient

from src.config import QA_COLLECTION_NAME, TAVILY_API_KEY, RETRIEVAL_TOP_K
from src.retriever import retrieve
from src.prompts.qa_system_prompt import QA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Relevance thresholds for retrieval quality evaluation
HIGH_CONFIDENCE_THRESHOLD = 0.7
LOW_CONFIDENCE_THRESHOLD = 0.3


class QAExpertAgent:
    """QA Expert Agent with ReAct-style tool use and multi-step reasoning.

    Tools available to this agent:
    - search_internal_docs: Query the ICE QA knowledge base
    - search_web: Fall back to Tavily for general technical questions
    - evaluate_relevance: Score whether retrieved docs answer the query
    """

    def __init__(self, llm):
        self.llm = llm
        self.tool_calls = []  # Track tool usage for transparency
        self.reasoning_trace = []  # Track reasoning steps

    def _log_step(self, step_type: str, detail: str):
        """Record a reasoning step for the agent trace."""
        entry = {"step": step_type, "detail": detail}
        self.reasoning_trace.append(entry)
        logger.info(f"[QA Agent] {step_type}: {detail}")

    # ── Tool 1: Internal Document Search ──────────────────────────────

    def search_internal_docs(self, query: str) -> list[dict]:
        """Search the ICE QA internal knowledge base using advanced retrieval.

        Pipeline: multi-query expansion → semantic search → keyword boost → cross-encoder re-rank.
        Returns scored document chunks with metadata.
        """
        self._log_step("TOOL_CALL", f"search_internal_docs('{query}')")
        self.tool_calls.append({"tool": "search_internal_docs", "input": query})

        results = retrieve(query, QA_COLLECTION_NAME, top_k=RETRIEVAL_TOP_K)

        documents = []
        for doc, score in results:
            source_file = doc.metadata.get("source", "Unknown")
            source_name = source_file.split("/")[-1].replace(".md", "").replace("_", " ")
            documents.append({
                "content": doc.page_content,
                "source_file": source_file,
                "source_name": source_name,
                "relevance_score": round(score, 4),
            })

        self._log_step(
            "TOOL_RESULT",
            f"Found {len(documents)} chunks | "
            f"Top score: {documents[0]['relevance_score'] if documents else 'N/A'}",
        )
        return documents

    # ── Tool 2: Web Search (Tavily) ───────────────────────────────────

    def search_web(self, query: str) -> list[dict]:
        """Search the web using Tavily for general technical questions.

        Only used when internal docs don't have the answer (e.g., generic Playwright syntax).
        Tavily returns LLM-optimized structured results.
        """
        self._log_step("TOOL_CALL", f"search_web('{query}')")
        self.tool_calls.append({"tool": "search_web", "input": query})

        if not TAVILY_API_KEY:
            self._log_step("TOOL_RESULT", "Tavily API key not configured — skipping web search")
            return []

        try:
            client = TavilyClient(api_key=TAVILY_API_KEY)
            response = client.search(
                query,
                max_results=3,
                search_depth="advanced",
                include_answer=True,
            )

            results = []
            # Include Tavily's generated answer if available
            if response.get("answer"):
                results.append({
                    "content": response["answer"],
                    "source_name": "Tavily AI Summary",
                    "url": "",
                    "relevance_score": 0.95,
                })

            for item in response.get("results", []):
                results.append({
                    "content": item.get("content", "")[:500],
                    "source_name": item.get("title", "Web Result"),
                    "url": item.get("url", ""),
                    "relevance_score": item.get("score", 0.5),
                })

            self._log_step("TOOL_RESULT", f"Found {len(results)} web results")
            return results

        except Exception as e:
            self._log_step("TOOL_ERROR", f"Web search failed: {str(e)}")
            return []

    # ── Tool 3: Relevance Evaluation ──────────────────────────────────

    def evaluate_relevance(self, query: str, documents: list[dict]) -> dict:
        """Evaluate whether retrieved documents sufficiently answer the query.

        Uses the LLM to assess relevance rather than relying solely on embedding scores.
        Returns a verdict with confidence level.
        """
        self._log_step("TOOL_CALL", "evaluate_relevance()")
        self.tool_calls.append({"tool": "evaluate_relevance", "input": "assessment"})

        if not documents:
            return {"verdict": "no_results", "confidence": 0.0, "reasoning": "No documents retrieved."}

        top_score = documents[0]["relevance_score"]

        # Fast path: very high scores are clearly sufficient
        if top_score >= HIGH_CONFIDENCE_THRESHOLD:
            result = {
                "verdict": "sufficient",
                "confidence": min(top_score, 1.0),
                "reasoning": f"Top document scored {top_score:.2f} (above {HIGH_CONFIDENCE_THRESHOLD} threshold).",
            }
            self._log_step("TOOL_RESULT", f"Verdict: {result['verdict']} ({result['confidence']:.2f})")
            return result

        # For anything below high confidence, use LLM-as-a-judge.
        # Cross-encoder scores can be misleading when user language is colloquial
        # but the document IS topically relevant.
        doc_snippets = "\n---\n".join(d["content"][:400] for d in documents[:3])
        eval_prompt = (
            f"You are evaluating whether internal documentation can answer a user's question.\n\n"
            f"Question: {query}\n\n"
            f"Document excerpts:\n{doc_snippets}\n\n"
            f"Does the documentation contain information RELEVANT to answering this question, "
            f"even if the exact words differ? For example, if they ask about 'track pants' and "
            f"the doc discusses 'dress code', that IS relevant.\n\n"
            f"Answer ONLY 'yes' or 'no'."
        )

        try:
            eval_response = self.llm.invoke(eval_prompt)
            llm_says = eval_response.content.strip().lower()
            is_sufficient = "yes" in llm_says

            result = {
                "verdict": "sufficient" if is_sufficient else "insufficient",
                "confidence": max(top_score, 0.6) if is_sufficient else top_score * 0.5,
                "reasoning": f"LLM relevance check: {'confirmed relevant' if is_sufficient else 'not relevant'} "
                f"(retrieval score: {top_score:.2f}).",
            }
        except Exception:
            result = {
                "verdict": "sufficient" if top_score >= 0.5 else "insufficient",
                "confidence": top_score,
                "reasoning": f"Score-based fallback: {top_score:.2f}.",
            }

        self._log_step("TOOL_RESULT", f"Verdict: {result['verdict']} ({result['confidence']:.2f})")
        return result

    # ── ReAct Execution Loop ──────────────────────────────────────────

    def run(self, query: str) -> dict:
        """Execute the QA agent's ReAct loop.

        Reasoning flow:
        1. THINK  → Analyze the query
        2. ACT    → Search internal knowledge base
        3. OBSERVE → Evaluate retrieval quality
        4. ACT    → (If needed) Fall back to web search
        5. RESPOND → Synthesize final answer with citations
        """
        self._log_step("THINK", f"Analyzing query: '{query}'")

        # ── Step 1: Search internal QA documentation ──
        self._log_step("ACT", "Searching ICE internal QA knowledge base...")
        internal_docs = self.search_internal_docs(query)

        # ── Step 2: Evaluate relevance of internal results ──
        self._log_step("OBSERVE", "Evaluating relevance of retrieved documents...")
        relevance = self.evaluate_relevance(query, internal_docs)

        sources = []
        context_parts = []
        web_context = ""
        used_web_search = False

        if relevance["verdict"] == "sufficient":
            # Internal docs are good enough — use them
            self._log_step("THINK", "Internal documentation is sufficient. Synthesizing answer.")
            for doc in internal_docs:
                context_parts.append(doc["content"])
                sources.append({
                    "name": doc["source_name"],
                    "content": doc["content"][:200],
                    "score": doc["relevance_score"],
                })
        else:
            # Internal docs insufficient — try web search fallback
            self._log_step(
                "THINK",
                f"Internal docs scored {relevance['confidence']:.2f}. "
                "Falling back to Tavily web search for general technical info.",
            )

            # Still include internal docs if they have some relevance
            for doc in internal_docs:
                if doc["relevance_score"] >= LOW_CONFIDENCE_THRESHOLD:
                    context_parts.append(doc["content"])
                    sources.append({
                        "name": doc["source_name"],
                        "content": doc["content"][:200],
                        "score": doc["relevance_score"],
                    })

            # ── Step 3: Web search fallback ──
            self._log_step("ACT", "Searching the web via Tavily...")
            web_results = self.search_web(query)
            used_web_search = True

            if web_results:
                web_parts = []
                for result in web_results:
                    web_parts.append(f"**{result['source_name']}**: {result['content']}")
                    sources.append({
                        "name": f"Web: {result['source_name']}",
                        "content": result["content"][:200],
                        "score": result["relevance_score"],
                        "url": result.get("url", ""),
                    })
                web_context = (
                    "\nWeb Search Results (external source — not from ICE internal docs):\n"
                    + "\n\n".join(web_parts)
                )

        # ── Step 4: Synthesize answer via LLM ──
        self._log_step("ACT", "Generating final answer with LLM...")

        context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant internal documents found."
        system_prompt = QA_SYSTEM_PROMPT.format(context=context, web_context=web_context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        response = self.llm.invoke(messages)

        # Calculate overall confidence
        if sources:
            confidence = max(s.get("score", 0) for s in sources)
        else:
            confidence = 0.0

        self._log_step(
            "RESPOND",
            f"Answer generated | Confidence: {confidence:.2f} | "
            f"Sources: {len(sources)} | Web search: {used_web_search}",
        )

        return {
            "response": response.content,
            "agent": "QA Expert Agent",
            "sources": sources,
            "used_web_search": used_web_search,
            "confidence": round(confidence, 2),
            "tool_calls": self.tool_calls,
            "reasoning_trace": self.reasoning_trace,
        }
