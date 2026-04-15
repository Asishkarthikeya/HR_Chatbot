const ARR = <span className="arrow" aria-hidden="true">→</span>;
const ARR_S = <span className="arrow arrow--sm" aria-hidden="true">→</span>;

export function Pipeline() {
  return (
    <section className="pipeline" aria-label="How the platform works">
      <div className="pipeline__head">
        <span className="u-eyebrow">The Pipeline</span>
        <h2 className="pipeline__title">
          From a question to a grounded, guarded answer.
        </h2>
      </div>

      <div className="pipeline__stack">
        {/* 1 — User Interface Layer */}
        <article className="pline pline--ui">
          <span className="pline__badge">1 — User Interface Layer</span>
          <div className="flow">
            <div className="pill pill--primary">
              <div className="pill__title">React Frontend</div>
              <div className="pill__sub">Dashboard · Chat · History</div>
            </div>
            {ARR}
            <div className="flow__row" style={{ flex: "0 1 auto", width: "auto" }}>
              <div className="tile tile--slate">
                <strong>Dashboard</strong>
                <div className="tile__sub">Pipeline · Agents</div>
              </div>
              <div className="tile tile--slate">
                <strong>Chat</strong>
                <div className="tile__sub">Specialist · Voice</div>
              </div>
              <div className="tile tile--slate">
                <strong>History</strong>
                <div className="tile__sub">Sessions · Threads</div>
              </div>
            </div>
            {ARR}
            <div className="pill pill--primary">
              <div className="pill__title">User Query</div>
              <div className="pill__sub">+ Chat history + Agent selection</div>
            </div>
          </div>
        </article>

        {/* 2 — Multi-Agent Orchestration */}
        <article className="pline pline--orch">
          <span className="pline__badge">2 — Multi-Agent Orchestration (LangGraph)</span>
          <div className="flow" style={{ marginBottom: "var(--space-4)" }}>
            <div className="pill pill--teal">
              <div className="pill__title">User Query</div>
            </div>
            {ARR}
            <div className="pill pill--red">
              <div className="pill__title">Pre-Routing Guardrail</div>
              <div className="pill__sub">Regex · Injection · Credentials · MNPI</div>
            </div>
            {ARR}
            <div style={{ textAlign: "center" }}>
              <div
                style={{
                  background: "#fde8e8",
                  border: "1.5px solid #e8a8a8",
                  color: "#7a1a1a",
                  padding: "0.4rem 0.8rem",
                  borderRadius: "6px",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  fontFamily: "var(--font-sans)",
                }}
              >
                BLOCKED?
              </div>
              <div style={{ fontSize: "0.62rem", fontWeight: 600, marginTop: "3px" }}>
                <span style={{ color: "#c62828" }}>Yes → END</span>
                {"  "}
                <span style={{ color: "#2e8b57" }}>No ↓</span>
              </div>
            </div>
            {ARR}
            <div className="pill pill--teal">
              <div className="pill__title">Intent Agent</div>
              <div className="pill__sub">LLM classification + switch detection</div>
            </div>
          </div>
          <div
            style={{
              textAlign: "center",
              color: "var(--text-muted-dark)",
              fontSize: "1.2em",
              margin: "var(--space-3) 0",
            }}
          >
            ▼ &nbsp; ▼ &nbsp; ▼
          </div>
          <div className="flow" style={{ gap: "var(--space-4)" }}>
            <div className="pill pill--green">
              <div className="pill__title">HR &amp; Onboarding Agent</div>
              <div className="pill__sub">hr_general · greeting · out_of_scope</div>
            </div>
            <div className="pill pill--cyan">
              <div className="pill__title">QA Expert Agent</div>
              <div className="pill__sub">qa_technical</div>
            </div>
            <div className="pill pill--red">
              <div className="pill__title">Security Guardrail</div>
              <div className="pill__sub">sensitive_info</div>
            </div>
          </div>
        </article>

        {/* 3 — Specialist Agents */}
        <article className="pline pline--agents">
          <span className="pline__badge">3 — Specialist Agents (ReAct Reasoning)</span>
          <div className="flow__row">
            <div className="acard acard--qa">
              <div className="acard__title">QA Expert Agent</div>
              <div className="acard__sub">Flexible RAG + Web Fallback</div>
              <ul className="acard__list">
                <li>
                  <strong>search_internal_docs()</strong> — RAG on qa_docs
                </li>
                <li>
                  <strong>evaluate_relevance()</strong> — LLM-as-Judge
                </li>
                <li>
                  <strong>search_web()</strong> — Tavily fallback
                </li>
                <li>
                  <strong>synthesize()</strong> — Cited answer
                </li>
              </ul>
              <div className="acard__foot">
                <strong>Persona:</strong> Senior QA engineer · <strong>Web:</strong> Yes
                (Tavily)
              </div>
            </div>
            <div className="acard acard--hr">
              <div className="acard__title">HR &amp; Onboarding Agent</div>
              <div className="acard__sub">Strict RAG Only — No Web Search</div>
              <ul className="acard__list">
                <li>
                  <strong>check_sensitivity()</strong> — Sensitive topics
                </li>
                <li>
                  <strong>search_hr_docs()</strong> — RAG on hr_docs
                </li>
                <li>
                  <strong>assess_confidence()</strong> — LLM relevance
                </li>
                <li>
                  <strong>extract_citations()</strong> — Source refs
                </li>
              </ul>
              <div className="acard__foot">
                <strong>Persona:</strong> Nova · <strong>Escalation:</strong> Jessica
                Martinez
              </div>
            </div>
            <div className="acard acard--security">
              <div className="acard__title">Security Guardrail</div>
              <div className="acard__sub">Pattern-Based Defense in Depth</div>
              <ul className="acard__list">
                <li>
                  <strong>CREDENTIAL_PATTERNS</strong> — 8 regex
                </li>
                <li>
                  <strong>DATABASE_PATTERNS</strong> — 4 regex
                </li>
                <li>
                  <strong>MNPI_PATTERNS</strong> — 5 regex
                </li>
                <li>
                  <strong>INJECTION_PATTERNS</strong> — 7 regex
                </li>
              </ul>
              <div className="acard__foot">
                <strong>Levels:</strong> CRITICAL · HIGH · MEDIUM · LOW · audited
              </div>
            </div>
          </div>
        </article>

        {/* 4 — RAG Pipeline */}
        <article className="pline pline--rag">
          <span className="pline__badge">
            4 — Retrieval-Augmented Generation (RAG) Pipeline
          </span>
          <div className="flow">
            <div className="tile tile--purple">
              <strong>LLM Query Expansion</strong>
              <div className="tile__sub">Colloquial → Formal</div>
            </div>
            {ARR_S}
            <div className="tile tile--blue">
              <strong>Semantic Search</strong>
              <div className="tile__sub">ChromaDB + MiniLM</div>
            </div>
            {ARR_S}
            <div className="tile tile--amber">
              <strong>Keyword Boost</strong>
              <div className="tile__sub">Hybrid scoring</div>
            </div>
            {ARR_S}
            <div className="tile tile--blue">
              <strong>Cross-Encoder Re-Rank</strong>
              <div className="tile__sub">ms-marco-MiniLM</div>
            </div>
            {ARR_S}
            <div className="tile tile--purple">
              <strong>LLM-as-Judge</strong>
              <div className="tile__sub">Confidence check</div>
            </div>
            {ARR_S}
            <div className="tile tile--green">
              <strong>ReAct Synthesis</strong>
              <div className="tile__sub">Cited answer</div>
            </div>
          </div>
        </article>

        {/* 5 — Data & Knowledge Sources */}
        <article className="pline pline--data">
          <span className="pline__badge">5 — Data &amp; Knowledge Sources</span>
          <div className="flow__row">
            <div className="dcard dcard--green">
              <div className="dcard__title">HR Docs Collection</div>
              <ul className="dcard__list">
                <li>Employee Handbook 2024</li>
                <li>QA Onboarding Checklist</li>
                <li>Atlanta Office Info &amp; Equipment</li>
                <li>Code of Conduct &amp; MNPI Policy</li>
              </ul>
              <div className="dcard__badges">
                <span className="dcard__badge">~55 chunks</span>
                <span className="dcard__badge">4 docs</span>
              </div>
            </div>
            <div className="dcard dcard--blue">
              <div className="dcard__title">QA Docs Collection</div>
              <ul className="dcard__list">
                <li>Automation Standards (Playwright)</li>
                <li>Test Environment Guide</li>
                <li>QA Team Structure &amp; Processes</li>
                <li>API &amp; FIX Protocol Testing</li>
                <li>Deployment Pipeline (CI/CD)</li>
              </ul>
              <div className="dcard__badges">
                <span className="dcard__badge">~90 chunks</span>
                <span className="dcard__badge">6 docs</span>
              </div>
            </div>
            <div className="dcard dcard--amber">
              <div className="dcard__title">Tavily Web Search</div>
              <ul className="dcard__list">
                <li>Fallback for QA Agent only</li>
                <li>General technical questions</li>
                <li>Playwright docs, pytest patterns</li>
              </ul>
              <div className="dcard__badges">
                <span className="dcard__badge">3 results max</span>
                <span className="dcard__badge">AI summary</span>
              </div>
            </div>
          </div>
        </article>

        {/* 6 — LLM Infrastructure */}
        <article className="pline pline--llm">
          <span className="pline__badge">6 — LLM Infrastructure (Waterfall Fallback)</span>
          <div className="flow__row" style={{ alignItems: "flex-start" }}>
            <div className="model-col model-col--primary">
              <div className="model-col__head">Primary: Google Gemini</div>
              <div className="model-list">
                <div className="model-chip model-chip--primary">
                  <strong>gemini-2.0-flash</strong>
                  <span className="model-chip__default">← Default</span>
                </div>
                <div className="model-chip model-chip--primary">
                  <strong>gemini-2.0-flash-lite</strong>
                </div>
                <div className="model-chip model-chip--primary">
                  <strong>gemini-2.5-flash-preview</strong>
                </div>
                <div className="model-chip model-chip--primary">
                  <strong>gemini-2.5-pro-preview</strong>
                </div>
                <div className="model-chip model-chip--primary">
                  <strong>gemini-1.5-flash</strong>
                </div>
                <div className="model-chip model-chip--primary">
                  <strong>gemini-1.5-pro</strong>
                </div>
              </div>
            </div>

            <div className="waterfall-arrow">
              <div>Rate limited?</div>
              <div className="waterfall-arrow__big">→</div>
              <div>429 / 404</div>
            </div>

            <div className="model-col model-col--secondary">
              <div className="model-col__head">Secondary: Groq (Llama)</div>
              <div className="model-list">
                <div className="model-chip model-chip--secondary">
                  <strong>llama-3.3-70b-versatile</strong>
                  <span className="model-chip__default">← Primary</span>
                </div>
                <div className="model-chip model-chip--secondary">
                  <strong>llama-3.1-8b-instant</strong>
                </div>
                <div className="model-chip model-chip--secondary">
                  <strong>llama-3.2-90b-vision</strong>
                </div>
                <div className="model-chip model-chip--secondary">
                  <strong>gemma2-9b-it</strong>
                </div>
              </div>
            </div>

            <div className="model-col model-col--error">
              <div className="model-col__head">Error Detection</div>
              <div className="err-panel">
                <strong>Skippable (→ next):</strong>
                <br />• 429 Rate Limit
                <br />• Quota exhausted
                <br />• 404 Model not found
                <br />• Model decommissioned
                <br />• TPM / RPM exceeded
                <br />
                <br />
                <strong>Fatal (→ raise):</strong>
                <br />• Auth failure
                <br />• Malformed request
              </div>
            </div>
          </div>
        </article>

        {/* 7 — Embedding & Vector Store */}
        <article className="pline pline--embed">
          <span className="pline__badge">7 — Embedding, Vector Store &amp; Ingestion</span>
          <div className="flow__row" style={{ alignItems: "flex-start" }}>
            <div style={{ flex: 1.6, minWidth: 400 }}>
              <div
                style={{
                  fontFamily: "var(--font-sans)",
                  fontWeight: 700,
                  fontSize: "0.75rem",
                  color: "#235f73",
                  marginBottom: "var(--space-3)",
                }}
              >
                Document Ingestion Pipeline
              </div>
              <div className="flow flow--start">
                <div className="tile tile--slate">
                  <strong>Markdown Files</strong>
                  <div className="tile__sub">.md format</div>
                </div>
                {ARR_S}
                <div className="tile tile--blue">
                  <strong>Recursive Chunker</strong>
                  <div className="tile__sub">600 tok / 100 overlap</div>
                </div>
                {ARR_S}
                <div className="tile tile--purple">
                  <strong>Embed</strong>
                  <div className="tile__sub">all-MiniLM-L6-v2 · 384-dim</div>
                </div>
                {ARR_S}
                <div className="pill pill--teal">
                  <div className="pill__title">ChromaDB</div>
                  <div className="pill__sub">Persistent SQLite</div>
                </div>
              </div>
            </div>
            <div style={{ flex: 0.6, minWidth: 200 }}>
              <div
                style={{
                  fontFamily: "var(--font-sans)",
                  fontWeight: 700,
                  fontSize: "0.75rem",
                  color: "#235f73",
                  marginBottom: "var(--space-3)",
                }}
              >
                Models
              </div>
              <div
                style={{
                  background: "#e8f4f8",
                  border: "1.5px solid #b0d8e8",
                  borderRadius: "8px",
                  padding: "var(--space-4)",
                  fontFamily: "var(--font-sans)",
                  fontSize: "0.72rem",
                  lineHeight: 1.7,
                  color: "#1a4a5c",
                }}
              >
                <strong>Bi-Encoder (Embed):</strong>
                <br />
                all-MiniLM-L6-v2
                <br />
                384-dim · 22MB · Local
                <br />
                <br />
                <strong>Cross-Encoder (Rerank):</strong>
                <br />
                ms-marco-MiniLM-L-12-v2
                <br />
                FlashRank · Cached locally
              </div>
            </div>
          </div>
        </article>

        {/* 8 — Response Rendering */}
        <article className="pline pline--resp">
          <span className="pline__badge">8 — Response Rendering</span>
          <div className="flow__row">
            <div className="rtile">
              <div className="rtile__title">Agent Badge</div>
              <div className="rtile__sub">Which agent handled</div>
            </div>
            <div className="rtile">
              <div className="rtile__title">Confidence</div>
              <div className="rtile__sub">High / Med / Low</div>
            </div>
            <div className="rtile">
              <div className="rtile__title">Response</div>
              <div className="rtile__sub">Markdown text</div>
            </div>
            <div className="rtile">
              <div className="rtile__title">Sources</div>
              <div className="rtile__sub">Docs + scores</div>
            </div>
            <div className="rtile">
              <div className="rtile__title">Reasoning</div>
              <div className="rtile__sub">THINK → ACT → OBSERVE</div>
            </div>
            <div className="rtile">
              <div className="rtile__title">Tool Calls</div>
              <div className="rtile__sub">Tools invoked</div>
            </div>
          </div>
        </article>
      </div>

      {/* Information Security Levels */}
      <div className="pipeline__head" style={{ marginTop: "var(--space-8)" }}>
        <span className="u-eyebrow">Governance</span>
        <h2 className="pipeline__title">Information security levels.</h2>
      </div>
      <div className="seclevels">
        <div className="seclevel seclevel--1">
          <div className="seclevel__title">LEVEL 1 — Generic</div>
          <div className="seclevel__body">
            General company policies, public HR info, office hours, dress code. Freely
            answered from internal docs.
          </div>
        </div>
        <div className="seclevel seclevel--2">
          <div className="seclevel__title">LEVEL 2 — Internal</div>
          <div className="seclevel__body">
            QA processes, test environments, team structure, automation standards.
            Answered with source citations.
          </div>
        </div>
        <div className="seclevel seclevel--3">
          <div className="seclevel__title">LEVEL 3 — Sensitive</div>
          <div className="seclevel__body">
            Salary, termination, PIP, harassment. Answered with disclaimer + HR
            Business Partner referral.
          </div>
        </div>
        <div className="seclevel seclevel--4">
          <div className="seclevel__title">LEVEL 4 — Restricted</div>
          <div className="seclevel__body">
            Credentials, MNPI, API keys, prod DB access. Blocked — redirected to
            CyberArk / ServiceNow.
          </div>
        </div>
      </div>
    </section>
  );
}
