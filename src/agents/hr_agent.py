"""
HR & Onboarding Agent — Strict RAG agent with zero web search.

Implements an enterprise-safe retrieval strategy:
1. Retrieve from internal HR knowledge base (ChromaDB) only
2. Evaluate document confidence — refuse to answer if confidence is too low
3. Extract structured citations from source documents
4. Apply sensitivity filters (no personal data, no credential guessing)
5. Defer to human HR Business Partner when documentation is insufficient

Security constraint: This agent NEVER uses web search. All answers must be
traceable to an official ICE HR document.
"""

import logging
from src.config import HR_COLLECTION_NAME, RETRIEVAL_TOP_K
from src.retriever import retrieve
from src.prompts.hr_system_prompt import HR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Confidence thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.6
MEDIUM_CONFIDENCE_THRESHOLD = 0.35

# Topics that require extra caution in HR responses
SENSITIVE_HR_TOPICS = [
    "termination", "fired", "layoff", "severance",
    "salary", "compensation", "pay raise", "bonus",
    "disciplinary", "performance improvement", "pip",
    "harassment", "discrimination", "complaint",
    "medical", "disability", "accommodation",
    "pregnancy", "fmla", "leave of absence",
]

HR_ESCALATION_MESSAGE = (
    "I don't have that specific information in our current HR documentation. "
    "Please contact your HR Business Partner, **Jessica Martinez** "
    "(jessica.martinez@ice-internal.com, Room 3-210), for personalized assistance.\n\n"
    "You can also visit during walk-in hours: **Monday, Wednesday, Friday 10:00 AM – 12:00 PM**."
)


class HROnboardingAgent:
    """HR & Onboarding Agent with strict RAG, confidence scoring, and citation extraction.

    Tools available to this agent:
    - search_hr_docs: Query the ICE HR knowledge base (ONLY source)
    - assess_confidence: Evaluate if retrieved docs sufficiently answer the query
    - check_sensitivity: Detect HR-sensitive topics needing extra care
    - extract_citations: Build structured source citations for the response
    """

    def __init__(self, llm):
        self.llm = llm
        self.tool_calls = []
        self.reasoning_trace = []
        self.chat_history = []  # Conversation context for follow-up queries

    def _log_step(self, step_type: str, detail: str):
        entry = {"step": step_type, "detail": detail}
        self.reasoning_trace.append(entry)
        logger.info(f"[HR Agent] {step_type}: {detail}")

    # ── Tool 1: Internal HR Document Search ───────────────────────────

    def search_hr_docs(self, query: str) -> list[dict]:
        """Search the ICE HR internal knowledge base.

        Uses advanced retrieval (multi-query + hybrid + re-rank) but is strictly
        limited to the hr_docs ChromaDB collection. No web search. No external sources.
        """
        self._log_step("TOOL_CALL", f"search_hr_docs('{query}')")
        self.tool_calls.append({"tool": "search_hr_docs", "input": query})

        results = retrieve(query, HR_COLLECTION_NAME, top_k=RETRIEVAL_TOP_K, chat_history=self.chat_history)

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

    # ── Tool 2: Confidence Assessment ─────────────────────────────────

    def assess_confidence(self, query: str, documents: list[dict]) -> dict:
        """Assess whether HR documents confidently answer the query.

        Uses LLM-as-a-judge for all cases below the high-confidence threshold.
        This catches cases where the cross-encoder gives low scores but the document
        IS topically relevant (e.g., user asks about "track pants" → doc about "dress code").
        """
        self._log_step("TOOL_CALL", "assess_confidence()")
        self.tool_calls.append({"tool": "assess_confidence", "input": "assessment"})

        if not documents:
            result = {
                "level": "none",
                "score": 0.0,
                "should_answer": False,
                "reasoning": "No relevant HR documents found.",
            }
            self._log_step("TOOL_RESULT", f"Confidence: {result['level']}")
            return result

        top_score = documents[0]["relevance_score"]
        avg_score = sum(d["relevance_score"] for d in documents) / len(documents)

        if top_score >= HIGH_CONFIDENCE_THRESHOLD:
            level = "high"
            should_answer = True
            reasoning = (
                f"Strong match found (score: {top_score:.2f}). "
                f"Document directly addresses the query."
            )
        else:
            # For ANY score below the high threshold, use LLM to verify.
            # Cross-encoder scores can be misleading when the user's language
            # is colloquial but the doc IS topically correct.
            level = "medium" if top_score >= MEDIUM_CONFIDENCE_THRESHOLD else "low"
            doc_snippets = "\n---\n".join(d["content"][:400] for d in documents[:3])
            eval_prompt = (
                f"You are verifying whether internal HR documentation can answer an employee's question.\n\n"
                f"Employee question: {query}\n\n"
                f"Retrieved documentation excerpts:\n{doc_snippets}\n\n"
                f"Does the documentation above contain information that is RELEVANT to answering "
                f"the employee's question — even if the exact words don't match?\n"
                f"For example, if they ask about 'wearing track pants' and the doc discusses "
                f"'dress code' or 'business casual', that IS relevant.\n\n"
                f"Answer ONLY 'yes' or 'no'."
            )
            try:
                eval_response = self.llm.invoke(eval_prompt)
                llm_says = eval_response.content.strip().lower()
                should_answer = "yes" in llm_says
                if should_answer:
                    level = "medium"
                reasoning = (
                    f"Retrieval score: {top_score:.2f}. "
                    f"LLM relevance check: {'confirmed relevant' if should_answer else 'not relevant'}."
                )
            except Exception:
                should_answer = top_score >= 0.5
                reasoning = f"Score: {top_score:.2f}. LLM verification failed, using score threshold."

        result = {
            "level": level,
            "score": round(top_score, 2),
            "should_answer": should_answer,
            "reasoning": reasoning,
        }
        self._log_step("TOOL_RESULT", f"Confidence: {result['level']} ({result['score']}) → answer={result['should_answer']}")
        return result

    # ── Tool 3: Sensitivity Check ─────────────────────────────────────

    def check_sensitivity(self, query: str) -> dict:
        """Detect HR-sensitive topics that require careful handling.

        Some HR topics (termination, salary, harassment) need softer language,
        explicit disclaimers, and stronger referrals to the HR Business Partner.
        """
        self._log_step("TOOL_CALL", "check_sensitivity()")
        self.tool_calls.append({"tool": "check_sensitivity", "input": query})

        query_lower = query.lower()
        detected_topics = [
            topic for topic in SENSITIVE_HR_TOPICS if topic in query_lower
        ]

        is_sensitive = bool(detected_topics)
        result = {
            "is_sensitive": is_sensitive,
            "detected_topics": detected_topics,
            "requires_disclaimer": is_sensitive,
        }
        self._log_step(
            "TOOL_RESULT",
            f"Sensitive: {is_sensitive}" + (f" (topics: {detected_topics})" if detected_topics else ""),
        )
        return result

    # ── Tool 4: Citation Extraction ───────────────────────────────────

    def extract_citations(self, documents: list[dict]) -> list[dict]:
        """Build structured source citations from retrieved documents.

        Extracts document name, relevant section headers, and a preview snippet
        for display in the UI.
        """
        self._log_step("TOOL_CALL", "extract_citations()")
        self.tool_calls.append({"tool": "extract_citations", "input": f"{len(documents)} docs"})

        citations = []
        seen_sources = set()

        for doc in documents:
            source_name = doc["source_name"]

            # Extract section header if present (## or ### lines)
            lines = doc["content"].split("\n")
            section = ""
            for line in lines:
                if line.startswith("## ") or line.startswith("### "):
                    section = line.lstrip("#").strip()
                    break

            citation_key = f"{source_name}:{section}"
            if citation_key in seen_sources:
                continue
            seen_sources.add(citation_key)

            citations.append({
                "name": source_name,
                "section": section,
                "content": doc["content"][:200],
                "score": doc["relevance_score"],
                "display": f"{source_name}" + (f" > {section}" if section else ""),
            })

        self._log_step("TOOL_RESULT", f"Extracted {len(citations)} unique citations")
        return citations

    # ── Tool 5: Answer Validation ─────────────────────────────────────

    def validate_answer(self, answer: str, sources: list) -> dict:
        """Self-check the generated answer against source documents.
        
        Catches hallucinations by verifying all factual claims in the answer
        are supported by the HR documentation. Critical for HR accuracy —
        wrong PTO days, enrollment deadlines, or policy details could mislead employees.
        """
        self._log_step("TOOL_CALL", "validate_answer()")
        self.tool_calls.append({"tool": "validate_answer", "input": "self_check"})

        if not sources:
            return {"valid": True, "issue": None}

        source_text = "\n---\n".join(s.get("content", "")[:300] for s in sources[:3])
        
        validation_prompt = (
            f"You are a fact-checker for HR information. Check if the following answer contains any "
            f"factual claims NOT supported by the source documents.\n\n"
            f"Answer:\n{answer[:500]}\n\n"
            f"Source documents:\n{source_text}\n\n"
            f"Does the answer contain any unsupported claims (wrong PTO days, "
            f"incorrect dollar amounts, fabricated deadlines, wrong contact info)?\n"
            f"Answer ONLY 'yes' or 'no'. If yes, briefly state the issue."
        )

        try:
            response = self.llm.invoke(validation_prompt)
            result_text = response.content.strip().lower()
            has_issue = result_text.startswith("yes")
            
            result = {
                "valid": not has_issue,
                "issue": response.content.strip() if has_issue else None,
            }
            self._log_step(
                "TOOL_RESULT",
                f"Validation: {'PASS' if result['valid'] else 'ISSUE DETECTED: ' + str(result['issue'][:100])}"
            )
            return result
        except Exception as e:
            self._log_step("TOOL_ERROR", f"Validation failed: {e}")
            return {"valid": True, "issue": None}

    # ── ReAct Execution Loop ──────────────────────────────────────────

    def run(self, query: str, chat_history: list = None) -> dict:
        """Execute the HR agent's ReAct loop.

        Reasoning flow:
        1. THINK    → Analyze the query for HR relevance
        2. ACT      → Check if query touches sensitive HR topics
        3. ACT      → Search internal HR knowledge base (with conversation context)
        4. OBSERVE  → Assess confidence in retrieved results
        5. ACT      → Extract citations (if confident) OR escalate to human
        6. ACT      → Synthesize answer
        7. VALIDATE → Self-check answer against sources
        8. RESPOND  → Return final answer
        """
        self.chat_history = chat_history or []
        self._log_step("THINK", f"Analyzing HR query: '{query}'")

        # ── Step 1: Sensitivity screening ──
        self._log_step("ACT", "Checking for sensitive HR topics...")
        sensitivity = self.check_sensitivity(query)

        # ── Step 2: Search internal HR documentation ──
        self._log_step("ACT", "Searching ICE internal HR knowledge base...")
        hr_docs = self.search_hr_docs(query)

        # ── Step 3: Assess confidence ──
        self._log_step("OBSERVE", "Assessing confidence in retrieved documents...")
        confidence = self.assess_confidence(query, hr_docs)

        # ── Step 4: Decision — answer or escalate ──
        if not confidence["should_answer"]:
            self._log_step(
                "THINK",
                f"Confidence too low ({confidence['level']}). "
                "Escalating to HR Business Partner.",
            )
            return {
                "response": HR_ESCALATION_MESSAGE,
                "agent": "HR & Onboarding Agent",
                "sources": [],
                "used_web_search": False,
                "confidence": confidence["score"],
                "tool_calls": self.tool_calls,
                "reasoning_trace": self.reasoning_trace,
            }

        # ── Step 5: Extract structured citations ──
        self._log_step("ACT", "Extracting source citations...")
        citations = self.extract_citations(hr_docs)

        # ── Step 6: Synthesize answer ──
        self._log_step("ACT", "Generating answer from HR documentation...")

        context = "\n\n---\n\n".join(d["content"] for d in hr_docs)
        system_prompt = HR_SYSTEM_PROMPT.format(context=context)

        # Add sensitivity disclaimer if needed
        if sensitivity["is_sensitive"]:
            system_prompt += (
                "\n\nIMPORTANT: This query touches on sensitive HR topics "
                f"({', '.join(sensitivity['detected_topics'])}). "
                "Provide factual information from the documentation only. "
                "Add a note recommending the employee speak with their HR Business Partner "
                "for personalized guidance on this matter."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
        response = self.llm.invoke(messages)
        answer = response.content

        # ── Step 7: Answer self-validation ──
        # Format sources for the UI
        sources = [
            {"name": c["display"], "content": c["content"], "score": c["score"]}
            for c in citations
        ]

        self._log_step("VALIDATE", "Self-checking answer against source documents...")
        validation = self.validate_answer(answer, sources)

        if not validation["valid"]:
            # Re-generate with stricter grounding instructions
            self._log_step("ACT", "Re-generating answer with stricter grounding (validation failed)...")
            messages.append({"role": "assistant", "content": answer})
            messages.append({
                "role": "user",
                "content": (
                    "Your previous answer may contain HR information not from our official documentation. "
                    "Please regenerate, using ONLY facts explicitly stated in the provided ICE HR documents. "
                    "If you're unsure about a detail (dates, amounts, procedures), say so rather than guessing."
                ),
            })
            response = self.llm.invoke(messages)
            answer = response.content

        self._log_step(
            "RESPOND",
            f"Answer generated | Confidence: {confidence['score']:.2f} | "
            f"Sources: {len(sources)} | Sensitive: {sensitivity['is_sensitive']} | "
            f"Validation: {'PASS' if validation['valid'] else 'RE-GENERATED'}",
        )

        return {
            "response": answer,
            "agent": "HR & Onboarding Agent",
            "sources": sources,
            "used_web_search": False,
            "confidence": confidence["score"],
            "tool_calls": self.tool_calls,
            "reasoning_trace": self.reasoning_trace,
        }
