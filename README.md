

# ICE QAgent — Agentic RAG Onboarding Assistant

An intelligent, multi-agent onboarding assistant for the Intercontinental Exchange (ICE) QA Automation team. Built with **Agentic RAG** and **LangGraph** multi-agent orchestration with enterprise security guardrails.

## Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. USER INTERFACE (Streamlit)                                      │
│     Dashboard → Chat (Master/Specialist) → Admin (Ingest/Test)      │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. MULTI-AGENT ORCHESTRATION (LangGraph)                           │
│                                                                     │
│  User Query → Pre-Routing Guardrail → Intent Agent (LLM Classifier) │
│                (Regex • Injection      (Routes to specialist)       │
│                 • MNPI • Credentials)                               │
│                      │                                              │
│           ┌──────────┼──────────────┐                               │
│           ▼          ▼              ▼                               │
│     HR & Onboarding  QA Expert   Security                          │
│       Agent          Agent       Guardrail                         │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  3. SPECIALIST AGENTS (ReAct Reasoning)                             │
│                                                                     │
│  QA Expert Agent          HR & Onboarding Agent   Security Guardrail│
│  • search_internal_docs() • check_sensitivity()   • 8 credential   │
│  • evaluate_relevance()   • search_hr_docs()        regex patterns │
│  • search_web() (Tavily)  • assess_confidence()   • 5 MNPI patterns│
│  • synthesize()           • extract_citations()   • 7 injection    │
│  Web fallback: YES        Web fallback: NO          patterns       │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  4. RAG PIPELINE (6-stage retrieval)                                │
│                                                                     │
│  LLM Query    Semantic    Keyword    Cross-Encoder   LLM-as-Judge  │
│  Expansion → Search    → Boost    → Re-Rank       → Relevance     │
│  (Colloquial  (ChromaDB   (Hybrid    (ms-marco-      (Confidence   │
│   → Formal)    + MiniLM)   Scoring)   MiniLM-L12)     Check)       │
│                                                          ↓         │
│                                                     ReAct Synthesis │
│                                                     (Cited Answer)  │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  5. DATA & KNOWLEDGE SOURCES                                        │
│                                                                     │
│  HR Docs (4 files)     QA Docs (6 files)      Tavily Web Search    │
│  • Employee Handbook   • Automation Standards  • QA Agent fallback  │
│  • Onboarding Guide    • Test Environment      • 3 results max     │
│  • Office Info         • API & FIX Testing     • AI summary        │
│  • Code of Conduct     • Deployment Pipeline                       │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  6. LLM INFRASTRUCTURE (Waterfall Fallback)                         │
│                                                                     │
│  Primary: Google Gemini          Secondary: Groq (Llama)           │
│  gemini-2.0-flash (default)      llama-3.3-70b-versatile           │
│  gemini-2.0-flash-lite           llama-3.1-8b-instant              │
│  gemini-2.5-flash-preview        llama-3.2-90b-vision              │
│  gemini-2.5-pro-preview          mixtral-8x7b-32768               │
│  gemini-1.5-flash/pro            gemma2-9b-it                     │
│                                                                     │
│  Auto-fallback on: 429 Rate Limit • 404 Not Found • Quota Exceeded │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  7. EMBEDDING & VECTOR STORE                                        │
│                                                                     │
│  Markdown → Recursive Chunker → Embed → ChromaDB (Persistent)     │
│  (.md)      (600 tok/100 overlap) (all-MiniLM-L6-v2, 384-dim)     │
│                                                                     │
│  Reranker: FlashRank (ms-marco-MiniLM-L-12-v2 cross-encoder)      │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  8. RESPONSE RENDERING                                              │
│  Agent Badge • Confidence % • Markdown Response • Sources •        │
│  Reasoning Trace (THINK→ACT→OBSERVE) • Tool Calls                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Tool |
|-----------|------|
| Orchestration | LangGraph (multi-agent state machine) |
| LLM | Google Gemini / Groq Llama (waterfall fallback) |
| Embeddings | all-MiniLM-L6-v2 (384-dim, local) |
| Reranker | FlashRank ms-marco-MiniLM-L-12-v2 |
| Vector DB | ChromaDB (2 persistent collections) |
| Web Search | Tavily (QA agent fallback only) |
| Frontend | Streamlit |

## Security Classification

| Level | Type | Action |
|-------|------|--------|
| Level 1 — Generic | Company policies, office hours | Fully answered |
| Level 2 — Internal | QA processes, test environments | Answered with citations |
| Level 3 — Sensitive | Salary, termination, harassment | Answered + HR escalation |
| Level 4 — Restricted | Credentials, MNPI, API keys | Blocked |

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Ingest documents into ChromaDB:**
   ```bash
   python -m src.ingest
   ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
├── data/
│   ├── hr/              # HR & onboarding documents (4 files)
│   └── qa/              # QA technical documents (6 files)
├── src/
│   ├── config.py        # LLM waterfall fallback + settings
│   ├── ingest.py        # Document ingestion pipeline
│   ├── retriever.py     # 6-stage RAG retrieval pipeline
│   ├── graph.py         # LangGraph multi-agent orchestration
│   ├── agents/
│   │   ├── qa_agent.py      # QA Expert Agent (ReAct + web fallback)
│   │   ├── hr_agent.py      # HR Agent (strict RAG + escalation)
│   │   └── guardrails.py    # Security guardrail (regex patterns)
│   └── prompts/
│       ├── router_prompt.py      # Intent classification
│       ├── qa_system_prompt.py   # QA engineer persona
│       └── hr_system_prompt.py   # Nova HR colleague persona
├── .streamlit/
│   └── config.toml      # ICE brand theming
├── app.py               # Streamlit UI (dashboard + chat)
├── requirements.txt
└── .env.example
```
