

# ICE QAgent — Agentic RAG Onboarding Assistant

An intelligent, multi-agent onboarding assistant for the Intercontinental Exchange (ICE) QA Automation team. Built with **Agentic RAG** over a **LangGraph** multi-agent state machine, exposed through a **FastAPI** backend and a **React + Vite + TypeScript** frontend, with enterprise security guardrails, contextual retrieval, and multi-provider LLM failover.

A legacy **Streamlit** UI (`app.py`) is still included for the Hugging Face Space deployment.

## What's new

- ⚛️ **React + TypeScript frontend** (`frontend/`) — login, dashboard, per-agent chat, history, dark/light theme, voice input via Web Speech API, and a full 8-section pipeline diagram.
- 🚀 **FastAPI backend** (`api.py`) — a thin async wrapper around the LangGraph pipeline with CORS, Pydantic validation, and threadpool offload so the sync graph call doesn't block the event loop.
- 🧭 **Auto-routing entry point** — the `master` agent lets the intent classifier decide which specialist handles each query; `hr`, `qa`, and `security` remain as forced-intent shortcuts.
- 🔐 **Modular auth + chat history + voice** (`src/auth.py`, `src/chat_history.py`, `src/voice_agent.py`) reusable across the Streamlit and FastAPI entry points.

## Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. USER INTERFACE                                                  │
│     React + Vite (frontend/)  ─┐                                    │
│     Legacy Streamlit (app.py)  ├─▶  FastAPI (api.py) /api/chat      │
│                                 │                                   │
│     Dashboard • Chat • History • Voice (Web Speech) • Theme toggle │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. MULTI-AGENT ORCHESTRATION (LangGraph — src/graph.py)            │
│                                                                     │
│  User Query → Pre-Routing Guardrail → Intent Agent (LLM Classifier) │
│                (Regex • Injection      (Routes to specialist)       │
│                 • MNPI • Credentials)                               │
│                      │                                              │
│           ┌──────────┼──────────────┐                               │
│           ▼          ▼              ▼                               │
│     HR & Onboarding  QA Expert   Security                           │
│       Agent          Agent       Guardrail                          │
│                                                                     │
│     + Greeting Node  + Out-of-Scope Node  (no RAG, direct LLM)      │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  3. SPECIALIST AGENTS (ReAct Reasoning)                             │
│                                                                     │
│  QA Expert Agent          HR & Onboarding Agent   Security Guardrail│
│  • search_internal_docs() • check_sensitivity()   • credential     │
│  • evaluate_relevance()   • search_hr_docs()        regex patterns │
│  • search_web() (Tavily)  • assess_confidence()   • MNPI patterns  │
│  • validate_answer()      • extract_citations()   • injection      │
│  Web fallback: YES        • validate_answer()       patterns       │
│                           Web fallback: NO                          │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  4. ADVANCED RAG PIPELINE (src/retriever.py)                        │
│                                                                     │
│  Conversation    LLM Query    Semantic    Keyword    Cross-Encoder  │
│  Reformulation → Expansion →  Search   →  Boost   →  Re-Rank        │
│  (Follow-up      (Colloquial  (ChromaDB   (Hybrid    (FlashRank     │
│   → standalone)   → formal)    + MiniLM)   Scoring)   ms-marco)     │
│                                                          ↓          │
│                                                    ReAct Synthesis  │
│                                                    + Self-Validate  │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  5. DATA & KNOWLEDGE SOURCES                                        │
│                                                                     │
│  HR Docs (6 files)     QA Docs (7 files)      Tavily Web Search    │
│  • Employee Handbook   • Automation Standards  • QA Agent fallback  │
│  • Benefits Guide      • Test Environment      • 3 results max     │
│  • Code of Conduct     • API & FIX Testing     • AI summary        │
│  • New Hire FAQ        • Deployment Pipeline   • Only when local   │
│  • Office Info         • Team Structure          confidence < 0.7  │
│  • Onboarding Checklist• Clearing Standards                        │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  6. LLM INFRASTRUCTURE (Waterfall Fallback — src/config.py)         │
│                                                                     │
│  Groq (Llama)                   Google Gemini                       │
│  llama-3.3-70b-versatile        gemini-2.0-flash                    │
│  llama-3.1-8b-instant           gemini-2.0-flash-lite               │
│  llama-4-scout-17b                                                  │
│  qwen3-32b                                                          │
│                                                                     │
│  Auto-fallback on: 429 • quota exhausted • 404 • timeouts           │
│  60-second cooldown before retrying a failed model                  │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  7. EMBEDDING & VECTOR STORE (src/ingest.py)                        │
│                                                                     │
│  Markdown → Recursive Chunker → Contextual Summary → Embed → Chroma │
│  (.md)      (600 chars/100       (LLM-generated       (all-MiniLM   │
│              overlap)              per-chunk context)   L6-v2)       │
│                                                                     │
│  Reranker: FlashRank (ms-marco-MiniLM-L-12-v2 cross-encoder)        │
│  Context cache: .context_cache/ (skips unchanged chunks)            │
└──────────────────────┬──────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  8. RESPONSE RENDERING                                              │
│  Agent Badge • Intent • Confidence % • Markdown Response • Sources │
│  • Collapsible Reasoning Trace • Web Search Flag • Guardrail State │
└─────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Tool |
|-------|------|
| Frontend | React 18 + Vite 5 + TypeScript + React Router 7 (vanilla CSS, token-based theming) |
| Voice | Web Speech API (STT) — Groq Whisper (legacy Streamlit) |
| API | FastAPI + Pydantic + Uvicorn |
| Orchestration | LangGraph (multi-agent state machine) |
| LLM | Groq Llama / Google Gemini (waterfall fallback) |
| Embeddings | all-MiniLM-L6-v2 (384-dim, local HuggingFace) |
| Reranker | FlashRank ms-marco-MiniLM-L-12-v2 cross-encoder |
| Vector DB | ChromaDB (persistent, `hr_docs` + `qa_docs` collections) |
| Web Search | Tavily (QA agent fallback only) |
| Legacy UI | Streamlit 1.35 (for the Hugging Face Space) |

## Security Classification

| Level | Type | Action |
|-------|------|--------|
| Level 1 — Generic | Company policies, office hours | Fully answered |
| Level 2 — Internal | QA processes, test environments | Answered with citations |
| Level 3 — Sensitive | Salary, termination, harassment | Answered + HR escalation |
| Level 4 — Restricted | Credentials, MNPI, API keys | Blocked pre-LLM by guardrail |

## Setup

### Option A — React + FastAPI (modern stack)

**Terminal 1 — FastAPI backend:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit with your API keys
python -m src.ingest   # one-time: build ChromaDB
uvicorn api:app --reload --port 8000
```

**Terminal 2 — React frontend:**
```bash
cd frontend
npm install
npm run dev            # opens http://localhost:5173
```

The Vite dev server proxies `/api` → `http://127.0.0.1:8000`, so you hit a single URL in the browser.

### Option B — Streamlit (legacy)

```bash
pip install -r requirements.txt
cp .env.example .env
python -m src.ingest
streamlit run app.py
```

## Environment Variables

```
GROQ_API_KEY=gsk_...          # required (Llama models)
GOOGLE_API_KEY=...            # optional (Gemini fallback)
TAVILY_API_KEY=tvly-...       # optional (QA agent web search)
LLM_PROVIDER=groq             # "groq" or "google"
```

## Project Structure

```
├── api.py                    # FastAPI /api/chat wrapper around run_agent
├── app.py                    # Legacy Streamlit UI (Hugging Face Space)
├── requirements.txt
├── .env.example
│
├── data/
│   ├── hr/                   # HR & onboarding docs (6 markdown files)
│   └── qa/                   # QA technical docs (7 markdown files)
│
├── src/
│   ├── config.py             # LLM waterfall + provider settings
│   ├── ingest.py             # Contextual chunking + embedding pipeline
│   ├── retriever.py          # 5-stage advanced RAG retrieval
│   ├── graph.py              # LangGraph multi-agent state machine
│   ├── auth.py               # ChromaDB-backed user auth (salted SHA-256)
│   ├── chat_history.py       # Per-user JSON session persistence
│   ├── voice_agent.py        # Groq Whisper STT + nav command parsing
│   ├── agents/
│   │   ├── qa_agent.py       # QA Expert (ReAct + Tavily fallback)
│   │   ├── hr_agent.py       # Nova HR Agent (strict RAG + escalation)
│   │   └── guardrails.py     # Pre-routing pattern-based guardrail
│   └── prompts/
│       ├── router_prompt.py        # Intent classifier
│       ├── qa_system_prompt.py     # Senior QA engineer persona
│       └── hr_system_prompt.py     # Nova HR colleague persona
│
├── frontend/                 # React + Vite + TypeScript app
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts        # /api proxy → 127.0.0.1:8000
│   ├── tsconfig.json
│   ├── public/               # ICE brand assets (logo, backdrops)
│   └── src/
│       ├── main.tsx
│       ├── App.tsx           # Routes + ThemeProvider + AuthProvider
│       ├── layouts/AppShell.tsx
│       ├── pages/            # Home, Login, Dashboard, Chat, History
│       ├── components/       # Sidebar, TopBar, ChatMessage, ChatComposer,
│       │                     # Pipeline, ThemeToggle, AgentCard, ...
│       ├── state/            # auth, chat, theme (React Context hooks)
│       ├── data/             # agents, history, pipeline metadata
│       ├── styles/           # tokens, reset, layout, per-component CSS
│       └── types.ts
│
└── .streamlit/
    └── config.toml           # ICE brand theming (legacy Streamlit only)
```

## How a query flows through the system

1. **Frontend** (`frontend/src/state/chat.ts`) posts to `/api/chat` with `{query, agent, chat_history}`.
2. **FastAPI** (`api.py`) validates, maps the UI agent to a forced intent (or auto-route), and offloads to `asyncio.to_thread(run_agent, …)`.
3. **Pre-routing guardrail** scans for prompt injection, credential, database, and MNPI patterns — blocked queries short-circuit to END with a canned redirect.
4. **Intent detector** runs greeting regex → forced intent check → agent-switch regex → LLM classifier, outputting one of `hr_general`, `qa_technical`, `sensitive_info`, `greeting`, `out_of_scope`.
5. **Specialist agent** executes its ReAct loop: search → confidence check → (answer or escalate/fallback) → generate → validate against sources.
6. **Retriever** reformulates the query with chat context, expands it, runs ChromaDB semantic search, boosts keyword overlap, then re-ranks with FlashRank.
7. **Response** flows back as `ChatResponse` JSON with intent, confidence, sources, reasoning trace, and guardrail metadata — rendered with collapsible panels in the React `ChatMessage` component.

## License

MIT
