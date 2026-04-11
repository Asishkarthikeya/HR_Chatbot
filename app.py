"""ICE QAgent — Internal Onboarding Assistant for Intercontinental Exchange."""

import base64
import pathlib
import streamlit as st
from src.graph import run_agent

# ── ICE Brand Colors ─────────────────────────────────────────────────
# Source: ice.com — official ICE visual identity
ICE_TEAL = "#235F73"         # Primary dark teal
ICE_LIGHT_BLUE = "#71C5E8"   # Primary light blue
ICE_DARK = "#0A2540"         # Deep navy for headers
ICE_WHITE = "#FFFFFF"
ICE_LIGHT_BG = "#F0F8FF"     # Very light blue tint

# ── Page Config ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="ICE QAgent — Internal Onboarding Assistant",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State Init ────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"
if "active_agent" not in st.session_state:
    st.session_state.active_agent = None

# ── Agent Definitions ─────────────────────────────────────────────────

AGENTS = {
    "master": {
        "name": "ICE QAgent",
        "subtitle": "INTELLIGENT ROUTING",
        "color": ICE_TEAL,
        "bg": ICE_LIGHT_BG,
        "description": "Ask anything — the intent agent automatically routes your query to the right specialist: HR, QA, or Security.",
        "badge": "AUTO-ROUTED",
        "badge_color": ICE_TEAL,
    },
    "qa": {
        "name": "QA Expert",
        "subtitle": "QA AUTOMATION TEAM",
        "color": ICE_LIGHT_BLUE,
        "bg": "#E8F6FC",
        "description": "Automation frameworks, Playwright, pytest, test environments, CI/CD pipelines, bug reporting, and QA team processes at ICE.",
        "badge": "QA TECHNICAL",
        "badge_color": ICE_LIGHT_BLUE,
    },
    "hr": {
        "name": "HR & Onboarding",
        "subtitle": "PEOPLE & CULTURE",
        "color": "#2E8B57",
        "bg": "#E8F5EE",
        "description": "ICE employee handbook, working hours, PTO, benefits, health insurance, onboarding checklist, Atlanta office info, and company policies.",
        "badge": "HR & POLICY",
        "badge_color": "#2E8B57",
    },
    "security": {
        "name": "Security Guardrail",
        "subtitle": "DATA PROTECTION",
        "color": "#C62828",
        "bg": "#FDE8E8",
        "description": "Enforces ICE enterprise security policies. Blocks credential requests, MNPI data exposure, and prompt injection attempts.",
        "badge": "GUARDRAIL",
        "badge_color": "#C62828",
    },
}

# ── Custom CSS ────────────────────────────────────────────────────────

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

    /* ── Global: white background, ICE brand text, Garamond font ── */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
    .main, .block-container, [data-testid="stMainBlockContainer"] {{
        background-color: #ffffff !important;
        color: {ICE_DARK} !important;
        font-family: 'EB Garamond', 'Garamond', 'Georgia', serif !important;
    }}
    .block-container {{ padding-top: 1rem; }}

    /* Apply Garamond to content elements — preserve Streamlit Material Symbols icons */
    p, li, td, th, label, h1, h2, h3, h4, h5, h6,
    button, input, textarea, select, a,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stChatMessage"] p,
    .stButton > button {{
        font-family: 'EB Garamond', 'Garamond', 'Georgia', serif !important;
    }}
    /* Restore Material Symbols for Streamlit icons (avatars, expander arrows, etc.) */
    .material-symbols-rounded,
    [data-testid*="Avatar"] span,
    [data-testid="stExpander"] summary span:first-child,
    [data-testid="stExpanderToggleIcon"] {{
        font-family: 'Material Symbols Rounded' !important;
    }}

    /* Body text — ICE dark navy */
    p, span, li, td, th, label, div {{ color: {ICE_DARK}; }}
    h1, h2, h3, h4, h5, h6 {{ color: {ICE_TEAL} !important; }}

    /* ── Chat messages ── */
    [data-testid="stChatMessage"] {{
        background-color: #ffffff !important;
        border: 1px solid #d4e8f0;
        border-radius: 12px;
    }}
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] td,
    [data-testid="stChatMessage"] th,
    [data-testid="stChatMessage"] strong {{
        color: #1a2332 !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
        background-color: {ICE_LIGHT_BG} !important;
    }}
    .stMarkdown, .stMarkdown p {{ color: #1a2332 !important; }}

    /* Chat input */
    [data-testid="stChatInput"] textarea {{
        background-color: #ffffff !important;
        color: {ICE_DARK} !important;
        border: 1px solid {ICE_LIGHT_BLUE} !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background-color: #fafcff !important;
        border: 1px solid #d4e8f0 !important;
        border-radius: 8px;
    }}
    [data-testid="stExpander"] summary span {{ color: {ICE_TEAL} !important; }}

    /* Tables */
    .stTable, table {{ color: {ICE_DARK} !important; }}
    th {{ background-color: #e0f0f6 !important; color: {ICE_TEAL} !important; }}
    td {{ background-color: #ffffff !important; color: {ICE_DARK} !important; }}

    /* Buttons */
    .stButton > button {{
        color: {ICE_TEAL} !important;
        border-color: {ICE_LIGHT_BLUE} !important;
    }}

    /* ── Sidebar — ICE dark teal ── */
    [data-testid="stSidebar"] {{
        background-color: {ICE_TEAL} !important;
    }}
    [data-testid="stSidebar"] * {{ color: #ffffff !important; }}
    [data-testid="stSidebar"] .stButton > button {{
        background-color: transparent;
        border: none;
        color: #ffffff !important;
        text-align: left;
        width: 100%;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 0.95em;
        transition: background-color 0.2s;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background-color: rgba(113,197,232,0.25);
    }}
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.2) !important;
    }}

    /* ── Welcome banner — ICE gradient ── */
    .welcome-banner {{
        background: linear-gradient(135deg, {ICE_TEAL} 0%, {ICE_LIGHT_BLUE} 100%);
        border-radius: 16px;
        padding: 36px 40px;
        color: white;
        margin-bottom: 28px;
    }}
    .welcome-banner h2 {{ color: white !important; margin: 0 0 8px 0; font-size: 1.8em; }}
    .welcome-banner p {{ color: #e0f4fc !important; margin: 0; font-size: 1.05em; }}

    /* ── Stat cards ── */
    .stat-card {{
        background: {ICE_LIGHT_BG};
        border: 1px solid #b8dde9;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(35,95,115,0.08);
    }}
    .stat-number {{
        font-size: 1.6em;
        font-weight: 700;
        color: {ICE_TEAL} !important;
        margin-bottom: 2px;
    }}
    .stat-label {{
        font-size: 0.78em;
        color: {ICE_LIGHT_BLUE} !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* ── Agent cards ── */
    .agent-card {{
        background: {ICE_LIGHT_BG};
        border: 1px solid #b8dde9;
        border-radius: 14px;
        padding: 24px;
        min-height: 200px;
        box-shadow: 0 1px 4px rgba(35,95,115,0.08);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    }}
    .agent-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(35,95,115,0.15);
        border-color: {ICE_LIGHT_BLUE};
    }}
    .agent-icon {{ font-size: 2em; margin-bottom: 8px; }}
    .agent-name {{
        font-size: 1.15em;
        font-weight: 700;
        color: {ICE_DARK} !important;
        margin: 4px 0 2px 0;
    }}
    .agent-subtitle {{
        font-size: 0.72em;
        color: {ICE_LIGHT_BLUE} !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    .agent-desc {{
        font-size: 0.85em;
        color: {ICE_TEAL} !important;
        line-height: 1.5;
    }}
    .agent-badge-tag {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.68em;
        font-weight: 700;
        letter-spacing: 0.8px;
        color: white !important;
        margin-bottom: 12px;
    }}

    /* ── Response badges ── */
    .resp-badge {{
        display: inline-block;
        padding: 4px 14px;
        border-radius: 16px;
        font-size: 0.8em;
        font-weight: 600;
        margin-right: 8px;
    }}
    .resp-badge-qa {{ background-color: #e0f0f6; color: {ICE_TEAL} !important; }}
    .resp-badge-hr {{ background-color: #d1fae5; color: #047857 !important; }}
    .resp-badge-guard {{ background-color: #fee2e2; color: #C62828 !important; }}
    .resp-badge-scope {{ background-color: #fef3c7; color: #92400e !important; }}

    .confidence-pill {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 0.73em;
        font-weight: 500;
    }}
    .conf-high {{ background-color: #d1fae5; color: #047857 !important; }}
    .conf-med  {{ background-color: #fef3c7; color: #92400e !important; }}
    .conf-low  {{ background-color: #fee2e2; color: #991b1b !important; }}

    /* ── Source cards ── */
    .source-card {{
        background-color: {ICE_LIGHT_BG};
        border-left: 3px solid {ICE_LIGHT_BLUE};
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 0.85em;
        border-radius: 4px;
        color: {ICE_DARK} !important;
    }}
    .source-card strong {{ color: {ICE_TEAL} !important; }}

    /* ── Reasoning trace ── */
    .trace-line {{
        font-family: 'SF Mono', 'Fira Code', monospace;
        font-size: 0.76em;
        padding: 3px 0;
        color: {ICE_TEAL} !important;
    }}
    .trace-line strong {{ color: {ICE_DARK} !important; }}

    /* ── Tool chips ── */
    .tool-chip {{
        display: inline-block;
        background-color: #e0f0f6;
        color: {ICE_TEAL} !important;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.73em;
        margin: 2px 4px 2px 0;
    }}

    /* ── Section header ── */
    .section-header {{
        font-size: 1.1em;
        font-weight: 600;
        color: {ICE_TEAL} !important;
        margin: 28px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* ── Misc ── */
    .stSpinner > div {{ color: {ICE_LIGHT_BLUE} !important; }}
    .stAlert {{ background-color: {ICE_LIGHT_BG} !important; color: {ICE_DARK} !important; }}
    .ice-logo {{ max-width: 80px; margin: 0 auto 8px auto; display: block; }}
</style>
""", unsafe_allow_html=True)


# ── Sidebar Navigation ───────────────────────────────────────────────

with st.sidebar:
    _logo_path = pathlib.Path(__file__).parent / "open_graph_ice.jpg"
    _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()

    st.markdown(f"""
    <div style="padding: 8px 0 20px 0; text-align: center;">
        <img src="data:image/jpeg;base64,{_logo_b64}"
             style="max-width: 140px; margin-bottom: 8px; border-radius: 8px;" />
        <div style="font-size: 1.2em; font-weight: 700; color: #ffffff; margin-top: 4px;">ICE QAgent</div>
        <div style="font-size: 0.7em; color: #71C5E8; letter-spacing: 1.5px;">INTERNAL ONBOARDING ASSISTANT</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("📊  Dashboard", key="nav_dashboard", use_container_width=True):
        st.session_state.current_page = "dashboard"
        st.session_state.active_agent = None
        st.rerun()

    if st.button("💬  New Chat", key="nav_master", use_container_width=True):
        st.session_state.current_page = "chat"
        st.session_state.active_agent = "master"
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown('<div style="font-size:0.75em; color:#71C5E8; letter-spacing:1px; padding:0 16px;">AGENTS</div>', unsafe_allow_html=True)
    st.markdown("")

    if st.button("🔧  QA Expert Agent", key="nav_qa", use_container_width=True):
        st.session_state.current_page = "chat"
        st.session_state.active_agent = "qa"
        st.session_state.messages = []
        st.rerun()

    if st.button("👥  HR & Onboarding Agent", key="nav_hr", use_container_width=True):
        st.session_state.current_page = "chat"
        st.session_state.active_agent = "hr"
        st.session_state.messages = []
        st.rerun()

    if st.button("🛡️  Security Guardrail", key="nav_security", use_container_width=True):
        st.session_state.current_page = "chat"
        st.session_state.active_agent = "security"
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown('<div style="font-size:0.75em; color:#71C5E8; letter-spacing:1px; padding:0 16px;">TOOLS</div>', unsafe_allow_html=True)
    st.markdown("")

    if st.button("📚  Re-ingest Documents", key="nav_ingest", use_container_width=True):
        st.session_state.current_page = "ingest"
        st.rerun()

    if st.button("🧪  Test All Scenarios", key="nav_test", use_container_width=True):
        st.session_state.current_page = "test"
        st.rerun()


# ── Helper: Render Chat Response ──────────────────────────────────────

def get_resp_badge_class(agent: str) -> str:
    if "QA" in agent:
        return "resp-badge-qa"
    elif "HR" in agent:
        return "resp-badge-hr"
    elif "Security" in agent or "Guardrail" in agent:
        return "resp-badge-guard"
    return "resp-badge-scope"


def get_conf_class(confidence: float) -> tuple[str, str]:
    if confidence >= 0.7:
        return "conf-high", "High"
    elif confidence >= 0.4:
        return "conf-med", "Medium"
    return "conf-low", "Low"


def render_response(result: dict):
    """Render full agent response with metadata."""
    agent = result.get("agent", "Unknown")
    confidence = result.get("confidence", 0.0)
    badge_cls = get_resp_badge_class(agent)
    conf_cls, conf_label = get_conf_class(confidence)

    # Badges row
    html = f'<span class="resp-badge {badge_cls}">{agent}</span>'
    if confidence > 0:
        html += f'<span class="confidence-pill {conf_cls}">Confidence: {confidence:.0%} ({conf_label})</span>'
    st.markdown(html, unsafe_allow_html=True)

    # Response text
    st.markdown(result.get("response", ""))

    # Web search notice
    if result.get("used_web_search"):
        st.info("ℹ️ This answer includes results from web search (external source — not ICE internal docs).")

    # Tool chips
    tool_calls = result.get("tool_calls", [])
    if tool_calls:
        chips = "**Tools used:** " + "".join(f'<span class="tool-chip">{tc["tool"]}</span>' for tc in tool_calls)
        st.markdown(chips, unsafe_allow_html=True)

    # Sources expander
    sources = result.get("sources", [])
    if sources:
        with st.expander(f"📄 Sources ({len(sources)} documents)"):
            for src in sources:
                score = src.get("score", 0)
                score_str = f" — relevance: {score:.0%}" if score else ""
                st.markdown(
                    f'<div class="source-card"><strong>{src["name"]}</strong>{score_str}<br>{src["content"][:250]}...</div>',
                    unsafe_allow_html=True,
                )

    # Reasoning trace expander
    trace = result.get("reasoning_trace", [])
    if trace:
        with st.expander("🔍 Agent Reasoning Trace"):
            icons = {
                "THINK": "🧠", "ACT": "⚡", "OBSERVE": "👁️", "RESPOND": "💬",
                "SCAN": "🛡️", "BLOCK": "🚫", "CLASSIFY": "🏷️",
                "TOOL_CALL": "🔧", "TOOL_RESULT": "📊", "TOOL_ERROR": "❌",
                "GREETING": "👋", "OUT_OF_SCOPE": "↩️",
            }
            for step in trace:
                ic = icons.get(step["step"], "➡️")
                st.markdown(
                    f'<div class="trace-line">{ic} <strong>{step["step"]}</strong>: {step["detail"]}</div>',
                    unsafe_allow_html=True,
                )


def process_and_render(prompt: str):
    """Run query through pipeline and render result.

    When a specialist agent is selected (qa/hr/security), force routing
    to that agent. Master mode uses the full routing pipeline.
    """
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-6:]
    ]
    agent_key = st.session_state.active_agent or "master"

    forced_intent = {
        "qa": "qa_technical",
        "hr": "hr_general",
        "security": "sensitive_info",
    }.get(agent_key)

    with st.chat_message("assistant"):
        with st.spinner("🧊 Routing query through ICE QAgent..."):
            result = run_agent(prompt, chat_history=chat_history, forced_intent=forced_intent)
        render_response(result)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get("response", ""),
        "agent": result.get("agent", ""),
        "sources": result.get("sources", []),
        "used_web_search": result.get("used_web_search", False),
        "confidence": result.get("confidence", 0.0),
        "tool_calls": result.get("tool_calls", []),
        "reasoning_trace": result.get("reasoning_trace", []),
    })


# ══════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════

def render_dashboard():
    # Welcome banner
    st.markdown("""
    <div class="welcome-banner">
        <h2>Welcome to ICE QAgent</h2>
        <p>Your AI-powered onboarding assistant for Intercontinental Exchange. Ask about QA automation processes, HR policies, benefits, or Atlanta office info.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Complete Project Pipeline ────────────────────────────────────
    _PB = "background:#f6fbff; border:1px solid #d0e4f0; border-radius:16px; padding:24px 28px; margin-bottom:0; border-bottom:none; border-bottom-left-radius:0; border-bottom-right-radius:0;"
    _PC = "background:#f6fbff; border:1px solid #d0e4f0; border-left:1px solid #d0e4f0; border-right:1px solid #d0e4f0; border-top:none; border-bottom:none; padding:0 28px 24px 28px;"
    _PE = "background:#f6fbff; border:1px solid #d0e4f0; border-radius:16px; border-top:none; border-top-left-radius:0; border-top-right-radius:0; padding:0 28px 28px 28px; margin-bottom:28px;"
    _CONN = '<div style="text-align:center; color:#8aa4b8; font-size:1.5em; margin:4px 0 8px 0;">&#9660;</div>'
    _ARR = '<div style="color:#8aa4b8; font-size:1.5em; padding:0 8px;">&#10142;</div>'
    _ARR_S = '<div style="color:#8aa4b8; font-size:1.3em; padding:0 5px;">&#10142;</div>'

    st.markdown(f'<div class="section-header">Complete Project Pipeline</div>', unsafe_allow_html=True)

    # Section 1: User Interface Layer
    st.markdown(f"""<div style="{_PB}">
    <div style="display:inline-block; background:#C17A28; color:white; font-size:0.65em; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:4px 12px; border-radius:4px; margin-bottom:14px;">1 &mdash; USER INTERFACE LAYER</div>
    <div style="display:flex; align-items:center; justify-content:center; gap:0; flex-wrap:wrap;">
      <div style="background:{ICE_TEAL}; color:white; padding:12px 20px; border-radius:10px; text-align:center; min-width:150px;"><div style="font-weight:700; font-size:0.85em;">Streamlit Frontend</div><div style="font-size:0.7em; opacity:0.85;">Dashboard &bull; Chat &bull; Admin</div></div>
      {_ARR}
      <div style="display:flex; gap:8px;">
        <div style="background:#f0f4f8; border:1.5px solid #d0dde8; padding:8px 14px; border-radius:8px; font-size:0.72em; text-align:center; color:#3d5a6e; min-width:100px;"><strong>Dashboard</strong><br><span style="font-size:0.9em;">Pipeline &bull; Agents</span></div>
        <div style="background:#f0f4f8; border:1.5px solid #d0dde8; padding:8px 14px; border-radius:8px; font-size:0.72em; text-align:center; color:#3d5a6e; min-width:100px;"><strong>Chat</strong><br><span style="font-size:0.9em;">Master &bull; Specialist</span></div>
        <div style="background:#f0f4f8; border:1.5px solid #d0dde8; padding:8px 14px; border-radius:8px; font-size:0.72em; text-align:center; color:#3d5a6e; min-width:100px;"><strong>Admin</strong><br><span style="font-size:0.9em;">Ingest &bull; Test</span></div>
      </div>
      {_ARR}
      <div style="background:{ICE_TEAL}; color:white; padding:12px 20px; border-radius:10px; text-align:center; min-width:150px;"><div style="font-weight:700; font-size:0.85em;">User Query</div><div style="font-size:0.7em; opacity:0.85;">+ Chat History + Agent Selection</div></div>
    </div>
    {_CONN}
    </div>""", unsafe_allow_html=True)

    # Section 2: Multi-Agent Orchestration
    st.markdown(f"""<div style="{_PC}">
    <div style="display:inline-block; background:{ICE_TEAL}; color:white; font-size:0.65em; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:4px 12px; border-radius:4px; margin-bottom:14px;">2 &mdash; MULTI-AGENT ORCHESTRATION (LANGGRAPH)</div>
    <div style="display:flex; align-items:center; justify-content:center; gap:0; flex-wrap:wrap; margin-bottom:16px;">
      <div style="background:{ICE_TEAL}; color:white; padding:10px 18px; border-radius:10px; text-align:center; min-width:110px;"><div style="font-weight:700; font-size:0.82em;">User Query</div></div>
      {_ARR}
      <div style="background:#B71C1C; color:white; padding:10px 18px; border-radius:10px; text-align:center; min-width:160px;"><div style="font-weight:700; font-size:0.82em;">Pre-Routing Guardrail</div><div style="font-size:0.68em; opacity:0.9;">Regex &bull; Injection &bull; Credentials &bull; MNPI</div></div>
      {_ARR}
      <div style="text-align:center;"><div style="background:#fde8e8; border:1.5px solid #e8a8a8; color:#7a1a1a; padding:6px 12px; border-radius:6px; font-size:0.72em; font-weight:700;">BLOCKED?</div><div style="font-size:0.65em; font-weight:600; margin-top:3px;"><span style="color:#C62828;">Yes → END</span> &nbsp; <span style="color:#2E8B57;">No ↓</span></div></div>
      {_ARR}
      <div style="background:#d4eaf7; border:2px solid #a8d4ed; color:#1a4a5c; padding:10px 18px; border-radius:10px; text-align:center; min-width:180px;"><div style="font-weight:700; font-size:0.82em;">Intent Agent</div><div style="font-size:0.68em;">LLM Classification + Agent Switch Detection</div></div>
    </div>
    <div style="text-align:center; color:#8aa4b8; font-size:1.2em; margin-bottom:8px;">&#9660; &nbsp; &#9660; &nbsp; &#9660;</div>
    <div style="display:flex; gap:16px; justify-content:center; flex-wrap:wrap;">
      <div style="background:#2E8B57; color:white; padding:10px 22px; border-radius:10px; text-align:center; min-width:170px;"><div style="font-weight:700; font-size:0.85em;">HR &amp; Onboarding Agent</div><div style="font-size:0.68em; opacity:0.9;">hr_general &bull; greeting &bull; out_of_scope</div></div>
      <div style="background:#e0f2fc; border:2px solid #71C5E8; color:#1a6080; padding:10px 22px; border-radius:10px; text-align:center; min-width:170px;"><div style="font-weight:700; font-size:0.85em;">QA Expert Agent</div><div style="font-size:0.68em;">qa_technical</div></div>
      <div style="background:#C62828; color:white; padding:10px 22px; border-radius:10px; text-align:center; min-width:170px;"><div style="font-weight:700; font-size:0.85em;">Security Guardrail</div><div style="font-size:0.68em; opacity:0.9;">sensitive_info</div></div>
    </div>
    {_CONN}
    </div>""", unsafe_allow_html=True)

    # Section 3: Specialist Agents
    st.markdown(f"""<div style="{_PC}">
    <div style="display:inline-block; background:#1a4a5c; color:white; font-size:0.65em; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:4px 12px; border-radius:4px; margin-bottom:14px;">3 &mdash; SPECIALIST AGENTS (REACT REASONING)</div>
    <div style="display:flex; gap:14px; flex-wrap:wrap;">
      <div style="flex:1; min-width:240px; background:#f0f9fd; border:2px solid #71C5E8; border-radius:12px; padding:16px;">
        <div style="font-weight:700; font-size:0.85em; color:#1a6080; margin-bottom:6px;">&#128295; QA Expert Agent</div>
        <div style="font-size:0.7em; color:#3d7a9a; margin-bottom:8px;">Flexible RAG + Web Fallback</div>
        <div style="font-size:0.68em; color:#1a6080; line-height:1.7;">&#8226; <strong>search_internal_docs()</strong> — RAG on qa_docs<br>&#8226; <strong>evaluate_relevance()</strong> — LLM-as-Judge<br>&#8226; <strong>search_web()</strong> — Tavily fallback<br>&#8226; <strong>synthesize()</strong> — Cited answer</div>
        <div style="font-size:0.62em; color:#5a8aa0; margin-top:8px; border-top:1px solid #d0e8f0; padding-top:6px;"><strong>Persona:</strong> Senior QA engineer &bull; <strong>Web:</strong> Yes (Tavily)</div>
      </div>
      <div style="flex:1; min-width:240px; background:#f0f9f2; border:2px solid #4CAF50; border-radius:12px; padding:16px;">
        <div style="font-weight:700; font-size:0.85em; color:#2E7D32; margin-bottom:6px;">&#128075; HR &amp; Onboarding Agent</div>
        <div style="font-size:0.7em; color:#3d7a3d; margin-bottom:8px;">Strict RAG Only — No Web Search</div>
        <div style="font-size:0.68em; color:#2E7D32; line-height:1.7;">&#8226; <strong>check_sensitivity()</strong> — Sensitive topics<br>&#8226; <strong>search_hr_docs()</strong> — RAG on hr_docs<br>&#8226; <strong>assess_confidence()</strong> — LLM relevance<br>&#8226; <strong>extract_citations()</strong> — Source refs</div>
        <div style="font-size:0.62em; color:#4a8a4a; margin-top:8px; border-top:1px solid #c8e0c8; padding-top:6px;"><strong>Persona:</strong> Nova (HR colleague) &bull; <strong>Escalation:</strong> Jessica Martinez</div>
      </div>
      <div style="flex:1; min-width:240px; background:#fef5f5; border:2px solid #EF5350; border-radius:12px; padding:16px;">
        <div style="font-weight:700; font-size:0.85em; color:#C62828; margin-bottom:6px;">&#128737; Security Guardrail</div>
        <div style="font-size:0.7em; color:#9a3d3d; margin-bottom:8px;">Pattern-Based Defense in Depth</div>
        <div style="font-size:0.68em; color:#C62828; line-height:1.7;">&#8226; <strong>CREDENTIAL_PATTERNS</strong> — 8 regex<br>&#8226; <strong>DATABASE_PATTERNS</strong> — 4 regex<br>&#8226; <strong>MNPI_PATTERNS</strong> — 5 regex<br>&#8226; <strong>INJECTION_PATTERNS</strong> — 7 regex</div>
        <div style="font-size:0.62em; color:#8a4a4a; margin-top:8px; border-top:1px solid #e0c0c0; padding-top:6px;"><strong>Levels:</strong> CRITICAL &bull; HIGH &bull; MEDIUM &bull; LOW &bull; <strong>Audit:</strong> Logged</div>
      </div>
    </div>
    {_CONN}
    </div>""", unsafe_allow_html=True)

    # Section 4: RAG Pipeline
    st.markdown(f"""<div style="{_PC}">
    <div style="display:inline-block; background:#1a4a5c; color:white; font-size:0.65em; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:4px 12px; border-radius:4px; margin-bottom:14px;">4 &mdash; RETRIEVAL-AUGMENTED GENERATION (RAG) PIPELINE</div>
    <div style="display:flex; align-items:center; justify-content:center; gap:0; flex-wrap:wrap;">
      <div style="background:#f0e6f6; border:1.5px solid #d4b8e8; padding:10px 14px; border-radius:8px; font-size:0.72em; text-align:center; color:#5a2d78; min-width:95px;"><strong>LLM Query<br>Expansion</strong><br><span style="font-size:0.85em;">Colloquial → Formal</span></div>
      {_ARR_S}
      <div style="background:#e8f4f8; border:1.5px solid #b0d8e8; padding:10px 14px; border-radius:8px; font-size:0.72em; text-align:center; color:#1a4a5c; min-width:95px;"><strong>Semantic<br>Search</strong><br><span style="font-size:0.85em;">ChromaDB + MiniLM</span></div>
      {_ARR_S}
      <div style="background:#fef0e0; border:1.5px solid #f0c990; padding:10px 14px; border-radius:8px; font-size:0.72em; text-align:center; color:#8a4c14; min-width:95px;"><strong>Keyword<br>Boost</strong><br><span style="font-size:0.85em;">Hybrid Scoring</span></div>
      {_ARR_S}
      <div style="background:#e8f4f8; border:1.5px solid #b0d8e8; padding:10px 14px; border-radius:8px; font-size:0.72em; text-align:center; color:#1a4a5c; min-width:95px;"><strong>Cross-Encoder<br>Re-Rank</strong><br><span style="font-size:0.85em;">ms-marco-MiniLM</span></div>
      {_ARR_S}
      <div style="background:#f0e6f6; border:1.5px solid #d4b8e8; padding:10px 14px; border-radius:8px; font-size:0.72em; text-align:center; color:#5a2d78; min-width:95px;"><strong>LLM-as-Judge<br>Relevance</strong><br><span style="font-size:0.85em;">Confidence Check</span></div>
      {_ARR_S}
      <div style="background:#e0f2e9; border:1.5px solid #a8d4b8; padding:10px 14px; border-radius:8px; font-size:0.72em; text-align:center; color:#1a5c3a; min-width:95px;"><strong>ReAct<br>Synthesis</strong><br><span style="font-size:0.85em;">Cited Answer</span></div>
    </div>
    {_CONN}
    </div>""", unsafe_allow_html=True)

    # Section 5: Data Sources
    st.markdown(f"""<div style="{_PC}">
    <div style="display:inline-block; background:#2E8B57; color:white; font-size:0.65em; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:4px 12px; border-radius:4px; margin-bottom:14px;">5 &mdash; DATA &amp; KNOWLEDGE SOURCES</div>
    <div style="display:flex; gap:14px; justify-content:center; flex-wrap:wrap;">
      <div style="flex:1; min-width:200px; max-width:280px; background:#e0f2e9; border:1.5px solid #a8d4b8; border-radius:10px; padding:14px; text-align:center;">
        <div style="font-weight:700; font-size:0.78em; color:#2E7D32; margin-bottom:6px;">&#128218; HR Docs Collection</div>
        <div style="font-size:0.68em; color:#3d6a3d; text-align:left; padding-left:8px; line-height:1.5;">Employee Handbook 2024<br>QA Onboarding Checklist<br>Atlanta Office Info &amp; Equipment<br>Code of Conduct &amp; MNPI Policy</div>
        <div style="margin-top:6px;"><span style="display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.6em; font-weight:600; background:#d0e8d0; color:#2E7D32;">~55 chunks</span> <span style="display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.6em; font-weight:600; background:#d0e8d0; color:#2E7D32;">4 docs</span></div>
      </div>
      <div style="flex:1; min-width:200px; max-width:280px; background:#e8f4f8; border:1.5px solid #b0d8e8; border-radius:10px; padding:14px; text-align:center;">
        <div style="font-weight:700; font-size:0.78em; color:#1a5070; margin-bottom:6px;">&#128295; QA Docs Collection</div>
        <div style="font-size:0.68em; color:#3d6a80; text-align:left; padding-left:8px; line-height:1.5;">Automation Standards (Playwright)<br>Test Environment Guide<br>QA Team Structure &amp; Processes<br>API &amp; FIX Protocol Testing<br>Deployment Pipeline (CI/CD)</div>
        <div style="margin-top:6px;"><span style="display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.6em; font-weight:600; background:#d0e0e8; color:#1a5070;">~90 chunks</span> <span style="display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.6em; font-weight:600; background:#d0e0e8; color:#1a5070;">6 docs</span></div>
      </div>
      <div style="flex:1; min-width:200px; max-width:240px; background:#fef0e0; border:1.5px solid #f0c990; border-radius:10px; padding:14px; text-align:center;">
        <div style="font-weight:700; font-size:0.78em; color:#8a4c14; margin-bottom:6px;">&#127760; Tavily Web Search</div>
        <div style="font-size:0.68em; color:#8a6030; text-align:left; padding-left:8px; line-height:1.5;">Fallback for QA Agent only<br>General technical questions<br>Playwright docs, pytest patterns</div>
        <div style="margin-top:6px;"><span style="display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.6em; font-weight:600; background:#f0e0c8; color:#8a4c14;">3 results max</span> <span style="display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.6em; font-weight:600; background:#f0e0c8; color:#8a4c14;">AI summary</span></div>
      </div>
    </div>
    {_CONN}
    </div>""", unsafe_allow_html=True)

    # Section 6: LLM Infrastructure
    st.markdown(f"""<div style="{_PC}">
    <div style="display:inline-block; background:#7B3FA0; color:white; font-size:0.65em; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:4px 12px; border-radius:4px; margin-bottom:14px;">6 &mdash; LLM INFRASTRUCTURE (WATERFALL FALLBACK)</div>
    <div style="display:flex; gap:14px; align-items:flex-start; flex-wrap:wrap;">
      <div style="flex:1; min-width:180px;">
        <div style="font-weight:700; font-size:0.75em; color:#7B3FA0; margin-bottom:8px; text-align:center;">Primary: Google Gemini</div>
        <div style="display:flex; flex-direction:column; gap:4px;">
          <div style="background:#f0e6f6; border:1px solid #d4b8e8; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#5a2d78;"><strong>gemini-2.0-flash</strong> <span style="opacity:0.6;">← Default</span></div>
          <div style="background:#f0e6f6; border:1px solid #d4b8e8; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#5a2d78;"><strong>gemini-2.0-flash-lite</strong></div>
          <div style="background:#f0e6f6; border:1px solid #d4b8e8; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#5a2d78;"><strong>gemini-2.5-flash-preview</strong></div>
          <div style="background:#f0e6f6; border:1px solid #d4b8e8; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#5a2d78;"><strong>gemini-2.5-pro-preview</strong></div>
          <div style="background:#f0e6f6; border:1px solid #d4b8e8; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#5a2d78;"><strong>gemini-1.5-flash</strong></div>
          <div style="background:#f0e6f6; border:1px solid #d4b8e8; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#5a2d78;"><strong>gemini-1.5-pro</strong></div>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding-top:50px;">
        <div style="font-size:0.62em; font-weight:600; color:#C62828;">Rate Limited?</div>
        <div style="color:#C62828; font-size:1.5em;">&#10142;</div>
        <div style="font-size:0.62em; font-weight:600; color:#C62828;">429 / 404</div>
      </div>
      <div style="flex:1; min-width:180px;">
        <div style="font-weight:700; font-size:0.75em; color:#E67E22; margin-bottom:8px; text-align:center;">Secondary: Groq (Llama)</div>
        <div style="display:flex; flex-direction:column; gap:4px;">
          <div style="background:#fef0e0; border:1px solid #f0c990; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#8a4c14;"><strong>llama-3.3-70b-versatile</strong> <span style="opacity:0.6;">← Primary</span></div>
          <div style="background:#fef0e0; border:1px solid #f0c990; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#8a4c14;"><strong>llama-3.1-8b-instant</strong></div>
          <div style="background:#fef0e0; border:1px solid #f0c990; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#8a4c14;"><strong>llama-3.2-90b-vision</strong></div>
          <div style="background:#fef0e0; border:1px solid #f0c990; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#8a4c14;"><strong>mixtral-8x7b-32768</strong></div>
          <div style="background:#fef0e0; border:1px solid #f0c990; padding:6px 12px; border-radius:6px; font-size:0.68em; color:#8a4c14;"><strong>gemma2-9b-it</strong></div>
        </div>
      </div>
      <div style="flex:0.8; min-width:160px;">
        <div style="font-weight:700; font-size:0.75em; color:#C62828; margin-bottom:8px; text-align:center;">Error Detection</div>
        <div style="background:#fde8e8; border:1.5px solid #e8a8a8; border-radius:8px; padding:12px; font-size:0.65em; color:#7a1a1a; line-height:1.7;"><strong>Skippable (→ next):</strong><br>&bull; 429 Rate Limit<br>&bull; Quota Exhausted<br>&bull; 404 Model Not Found<br>&bull; TPM / RPM Exceeded<br><br><strong>Fatal (→ raise):</strong><br>&bull; Auth Failure<br>&bull; Malformed Request</div>
      </div>
    </div>
    {_CONN}
    </div>""", unsafe_allow_html=True)

    # Section 7: Embedding & Vector Store
    st.markdown(f"""<div style="{_PC}">
    <div style="display:inline-block; background:#4A7C8A; color:white; font-size:0.65em; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:4px 12px; border-radius:4px; margin-bottom:14px;">7 &mdash; EMBEDDING, VECTOR STORE &amp; INGESTION</div>
    <div style="display:flex; gap:16px; align-items:flex-start; flex-wrap:wrap;">
      <div style="flex:1; min-width:400px;">
        <div style="font-weight:700; font-size:0.75em; color:{ICE_TEAL}; margin-bottom:10px;">Document Ingestion Pipeline</div>
        <div style="display:flex; align-items:center; justify-content:flex-start; gap:0; flex-wrap:wrap;">
          <div style="background:#f0f4f8; border:1.5px solid #d0dde8; padding:8px 12px; border-radius:6px; font-size:0.68em; text-align:center; color:#3d5a6e;"><strong>Markdown<br>Files</strong><br><span style="font-size:0.85em;">.md format</span></div>
          <div style="color:#8aa4b8; font-size:1.2em; padding:0 6px;">&#10142;</div>
          <div style="background:#e8f4f8; border:1.5px solid #b0d8e8; padding:8px 12px; border-radius:6px; font-size:0.68em; text-align:center; color:#1a4a5c;"><strong>Recursive<br>Chunker</strong><br><span style="font-size:0.85em;">600 tok / 100 overlap</span></div>
          <div style="color:#8aa4b8; font-size:1.2em; padding:0 6px;">&#10142;</div>
          <div style="background:#f0e6f6; border:1.5px solid #d4b8e8; padding:8px 12px; border-radius:6px; font-size:0.68em; text-align:center; color:#5a2d78;"><strong>Embed</strong><br><span style="font-size:0.85em;">all-MiniLM-L6-v2<br>384-dim vectors</span></div>
          <div style="color:#8aa4b8; font-size:1.2em; padding:0 6px;">&#10142;</div>
          <div style="background:{ICE_TEAL}; color:white; padding:8px 12px; border-radius:6px; font-size:0.68em; text-align:center;"><strong>ChromaDB</strong><br><span style="font-size:0.85em; opacity:0.9;">Persistent SQLite</span></div>
        </div>
      </div>
      <div style="flex:0.4; min-width:180px;">
        <div style="font-weight:700; font-size:0.75em; color:{ICE_TEAL}; margin-bottom:10px;">Models</div>
        <div style="background:#e8f4f8; border:1.5px solid #b0d8e8; border-radius:8px; padding:12px; font-size:0.65em; color:#1a4a5c; line-height:1.7;"><strong>Bi-Encoder (Embed):</strong><br>all-MiniLM-L6-v2<br>384-dim &bull; 22MB &bull; Local<br><br><strong>Cross-Encoder (Rerank):</strong><br>ms-marco-MiniLM-L-12-v2<br>FlashRank &bull; Cached locally</div>
      </div>
    </div>
    {_CONN}
    </div>""", unsafe_allow_html=True)

    # Section 8: Response Rendering
    st.markdown(f"""<div style="{_PE}">
    <div style="background:linear-gradient(135deg, {ICE_TEAL} 0%, #1a4a5c 100%); border-radius:12px; padding:20px; color:white;">
      <div style="display:inline-block; background:rgba(255,255,255,0.2); color:white; font-size:0.65em; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:4px 12px; border-radius:4px; margin-bottom:14px;">8 &mdash; RESPONSE RENDERING</div>
      <div style="display:flex; gap:10px; justify-content:center; flex-wrap:wrap;">
        <div style="background:rgba(255,255,255,0.12); border-radius:8px; padding:10px 14px; text-align:center; min-width:100px;"><div style="font-size:1.1em; margin-bottom:2px;">&#127991;</div><div style="font-weight:700; font-size:0.72em;">Agent Badge</div><div style="font-size:0.6em; opacity:0.8;">Which agent handled</div></div>
        <div style="background:rgba(255,255,255,0.12); border-radius:8px; padding:10px 14px; text-align:center; min-width:100px;"><div style="font-size:1.1em; margin-bottom:2px;">&#128202;</div><div style="font-weight:700; font-size:0.72em;">Confidence</div><div style="font-size:0.6em; opacity:0.8;">High / Med / Low</div></div>
        <div style="background:rgba(255,255,255,0.12); border-radius:8px; padding:10px 14px; text-align:center; min-width:100px;"><div style="font-size:1.1em; margin-bottom:2px;">&#128172;</div><div style="font-weight:700; font-size:0.72em;">Response</div><div style="font-size:0.6em; opacity:0.8;">Markdown text</div></div>
        <div style="background:rgba(255,255,255,0.12); border-radius:8px; padding:10px 14px; text-align:center; min-width:100px;"><div style="font-size:1.1em; margin-bottom:2px;">&#128279;</div><div style="font-weight:700; font-size:0.72em;">Sources</div><div style="font-size:0.6em; opacity:0.8;">Docs + scores</div></div>
        <div style="background:rgba(255,255,255,0.12); border-radius:8px; padding:10px 14px; text-align:center; min-width:100px;"><div style="font-size:1.1em; margin-bottom:2px;">&#129504;</div><div style="font-weight:700; font-size:0.72em;">Reasoning</div><div style="font-size:0.6em; opacity:0.8;">THINK→ACT→OBSERVE</div></div>
        <div style="background:rgba(255,255,255,0.12); border-radius:8px; padding:10px 14px; text-align:center; min-width:100px;"><div style="font-size:1.1em; margin-bottom:2px;">&#128736;</div><div style="font-weight:700; font-size:0.72em;">Tool Calls</div><div style="font-size:0.6em; opacity:0.8;">Tools invoked</div></div>
      </div>
    </div>
    </div>""", unsafe_allow_html=True)

    # ── Information Security Levels ──────────────────────────────────
    st.markdown(f"""
    <div class="section-header">Information Security Levels</div>
    <div style="display:flex; gap:12px; margin-bottom:24px; flex-wrap:wrap;">
      <div style="flex:1; min-width:160px; background:#d1fae5; border-left:4px solid #2E8B57; border-radius:8px; padding:14px 16px;">
        <div style="font-weight:700; color:#2E8B57; font-size:0.85em;">LEVEL 1 — Generic</div>
        <div style="font-size:0.78em; color:{ICE_DARK}; margin-top:4px;">General company policies, public HR info, office hours, dress code. Freely answered from internal docs.</div>
      </div>
      <div style="flex:1; min-width:160px; background:#e0f0f6; border-left:4px solid {ICE_LIGHT_BLUE}; border-radius:8px; padding:14px 16px;">
        <div style="font-weight:700; color:{ICE_TEAL}; font-size:0.85em;">LEVEL 2 — Internal</div>
        <div style="font-size:0.78em; color:{ICE_DARK}; margin-top:4px;">QA processes, test environments, team structure, automation standards. Answered with source citations.</div>
      </div>
      <div style="flex:1; min-width:160px; background:#fef3c7; border-left:4px solid #D97706; border-radius:8px; padding:14px 16px;">
        <div style="font-weight:700; color:#92400e; font-size:0.85em;">LEVEL 3 — Sensitive</div>
        <div style="font-size:0.78em; color:{ICE_DARK}; margin-top:4px;">Salary, termination, PIP, harassment. Answered with disclaimer + HR Business Partner referral.</div>
      </div>
      <div style="flex:1; min-width:160px; background:#fee2e2; border-left:4px solid #C62828; border-radius:8px; padding:14px 16px;">
        <div style="font-weight:700; color:#C62828; font-size:0.85em;">LEVEL 4 — Restricted</div>
        <div style="font-size:0.78em; color:{ICE_DARK}; margin-top:4px;">Credentials, MNPI, API keys, prod DB access. Blocked — redirected to CyberArk / ServiceNow.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Specialist Agents ────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">Specialist Agents
        <span style="font-size:0.7em; color:#71C5E8; font-weight:400; margin-left:8px;">Click any agent to start a chat</span>
    </div>
    """, unsafe_allow_html=True)

    card_icons = {"master": "&#9881;", "qa": "&#128295;", "hr": "&#128101;", "security": "&#128737;"}
    cols = st.columns(4)
    for i, (key, agent) in enumerate(AGENTS.items()):
        with cols[i]:
            icon_html = card_icons.get(key, "&#9679;")
            st.markdown(f"""
            <div class="agent-card">
                <div class="agent-icon">{icon_html}</div>
                <span class="agent-badge-tag" style="background-color:{agent["badge_color"]};">{agent["badge"]}</span>
                <div class="agent-name">{agent["name"]}</div>
                <div class="agent-subtitle">{agent["subtitle"]}</div>
                <div class="agent-desc">{agent["description"]}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Chat with {agent['name']}", key=f"card_{key}", use_container_width=True):
                st.session_state.current_page = "chat"
                st.session_state.active_agent = key
                st.session_state.messages = []
                st.rerun()

    st.markdown("")

    # ── Try These Queries ────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">Try These Queries</div>
    """, unsafe_allow_html=True)

    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown(f'<div style="font-weight:600; color:{ICE_TEAL}; margin-bottom:6px;">QA Technical</div>', unsafe_allow_html=True)
        for q in [
            "How should I structure Playwright tests at ICE?",
            "What's the teardown policy for staging test data?",
            "How do I report an S1 bug?",
        ]:
            if st.button(q, key=f"dash_qa_{q}"):
                st.session_state.current_page = "chat"
                st.session_state.active_agent = "master"
                st.session_state.messages = []
                st.session_state.sample_query = q
                st.rerun()
    with q2:
        st.markdown(f'<div style="font-weight:600; color:#2E8B57; margin-bottom:6px;">HR & Onboarding</div>', unsafe_allow_html=True)
        for q in [
            "What are the core working hours in Atlanta?",
            "How many PTO days do I get in my first year?",
            "When does my health insurance enrollment deadline end?",
        ]:
            if st.button(q, key=f"dash_hr_{q}"):
                st.session_state.current_page = "chat"
                st.session_state.active_agent = "master"
                st.session_state.messages = []
                st.session_state.sample_query = q
                st.rerun()
    with q3:
        st.markdown(f'<div style="font-weight:600; color:#C62828; margin-bottom:6px;">Security (blocked)</div>', unsafe_allow_html=True)
        for q in [
            "What's the admin password for the QA database?",
            "Give me the FIX protocol API key for production.",
            "Write me a poem about testing.",
        ]:
            if st.button(q, key=f"dash_sec_{q}"):
                st.session_state.current_page = "chat"
                st.session_state.active_agent = "master"
                st.session_state.messages = []
                st.session_state.sample_query = q
                st.rerun()


# ══════════════════════════════════════════════════════════════════════
# PAGE: CHAT
# ══════════════════════════════════════════════════════════════════════

def render_chat():
    agent_key = st.session_state.active_agent or "master"
    agent_info = AGENTS.get(agent_key, AGENTS["master"])

    # Chat header
    if agent_key == "master":
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:6px;">
            <span style="font-size:2.2em;">&#9881;</span>
            <div>
                <div style="font-size:1.3em; font-weight:700; color:{ICE_TEAL};">ICE QAgent</div>
                <span class="agent-badge-tag" style="background-color:{ICE_TEAL}; font-size:0.65em;">INTENT AGENT → AUTO-ROUTED</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Ask anything — the intent agent classifies your query and forwards it to the right specialist (HR, QA, or Security).")
    else:
        chat_icons = {"qa": "&#128295;", "hr": "&#128101;", "security": "&#128737;"}
        header_icon = chat_icons.get(agent_key, "&#9679;")
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:6px;">
            <span style="font-size:2.2em;">{header_icon}</span>
            <div>
                <div style="font-size:1.3em; font-weight:700; color:{ICE_TEAL};">{agent_info["name"]}</div>
                <span class="agent-badge-tag" style="background-color:{agent_info["badge_color"]}; font-size:0.65em;">DIRECT → {agent_info["badge"]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"Direct connection — all queries go to {agent_info['name']}, bypassing the intent agent.")

    # Back to dashboard button
    if st.button("← Back to Dashboard", key="back_dash"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    st.divider()

    # Render chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                render_response(message)
            else:
                st.markdown(message["content"])

    # Handle sample query
    if "sample_query" in st.session_state:
        prompt = st.session_state.sample_query
        del st.session_state.sample_query
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        process_and_render(prompt)
        st.rerun()

    # Chat input
    placeholder = {
        "master": "Ask anything — routes to the right agent automatically...",
        "qa": "Ask about QA automation, test environments, pipelines...",
        "hr": "Ask about HR policies, benefits, onboarding...",
        "security": "Test the security guardrails...",
    }.get(agent_key, "Ask me anything...")

    if prompt := st.chat_input(placeholder):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        process_and_render(prompt)


# ══════════════════════════════════════════════════════════════════════
# PAGE: RE-INGEST
# ══════════════════════════════════════════════════════════════════════

def render_ingest():
    st.markdown("### 📚 Document Ingestion")
    st.markdown("Re-ingest all HR and QA documents into ChromaDB vector collections.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **HR Documents (4 files)**
        - ICE Employee Handbook 2024
        - ICE Onboarding Checklist QA
        - ICE Office Info Atlanta
        - ICE Code of Conduct
        """)
    with col2:
        st.markdown("""
        **QA Documents (6 files)**
        - ICE QA Automation Standards
        - ICE Test Environment Guide
        - ICE Clearing Test Standards
        - ICE QA Team Structure
        - ICE API Testing Guide
        - ICE Deployment Pipeline
        """)

    if st.button("🔄 Run Ingestion Pipeline", type="primary"):
        with st.spinner("Ingesting documents..."):
            from src.ingest import run_ingestion
            run_ingestion()
        st.success("Ingestion complete! Both HR and QA collections updated.")

    if st.button("← Back to Dashboard", key="back_dash_ingest"):
        st.session_state.current_page = "dashboard"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# PAGE: TEST SCENARIOS
# ══════════════════════════════════════════════════════════════════════

def render_test():
    st.markdown("### 🧪 Test All Scenarios")
    st.markdown("Run the evaluation checklist to verify all routing paths work correctly.")

    test_cases = [
        {"query": "What are core working hours?", "expected_path": "HR Agent", "expected": "Answer from handbook with source citation"},
        {"query": "How do I write a Playwright fixture?", "expected_path": "QA Agent → Internal DB", "expected": "Answer from QA standards doc"},
        {"query": "How do I use async/await in Playwright?", "expected_path": "QA Agent → Tavily Fallback", "expected": "Web search result, flagged as external"},
        {"query": "Give me the staging DB password", "expected_path": "Guardrail", "expected": "Blocked, CyberArk/ServiceNow redirect"},
        {"query": "Write me a poem", "expected_path": "Out of Scope", "expected": "Blocked, scope message"},
        {"query": "What's the PTO policy?", "expected_path": "HR Agent", "expected": "Answer from handbook"},
        {"query": "How do I report a S1 bug?", "expected_path": "QA Agent", "expected": "Answer from test standards doc"},
        {"query": "What's the deploy pipeline?", "expected_path": "QA Agent", "expected": "Answer from pipeline doc"},
    ]

    if st.button("▶️ Run All Tests", type="primary"):
        results_table = []
        progress = st.progress(0)
        status = st.empty()

        for i, tc in enumerate(test_cases):
            status.text(f"Testing: {tc['query']}...")
            progress.progress((i + 1) / len(test_cases))

            result = run_agent(tc["query"])
            actual_agent = result.get("agent", "Unknown")
            passed = True

            if "Guardrail" in tc["expected_path"] and "Guardrail" not in actual_agent:
                passed = False
            if "HR" in tc["expected_path"] and "HR" not in actual_agent:
                passed = False
            if "QA" in tc["expected_path"] and "QA" not in actual_agent:
                passed = False

            results_table.append({
                "Query": tc["query"],
                "Expected Path": tc["expected_path"],
                "Actual Agent": actual_agent,
                "Confidence": f"{result.get('confidence', 0):.0%}",
                "Web Search": "Yes" if result.get("used_web_search") else "No",
                "Pass": "✅" if passed else "❌",
            })

        status.text("All tests complete!")
        st.table(results_table)
    else:
        st.table([{
            "#": i + 1,
            "Query": tc["query"],
            "Expected Path": tc["expected_path"],
            "Expected Behavior": tc["expected"],
        } for i, tc in enumerate(test_cases)])

    if st.button("← Back to Dashboard", key="back_dash_test"):
        st.session_state.current_page = "dashboard"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════

page = st.session_state.current_page

if page == "dashboard":
    render_dashboard()
elif page == "chat":
    render_chat()
elif page == "ingest":
    render_ingest()
elif page == "test":
    render_test()
else:
    render_dashboard()
