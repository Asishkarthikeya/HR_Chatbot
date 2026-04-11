"""
LangGraph Orchestrator — Multi-agent state machine with intent routing.

Architecture:
1. Pre-routing guardrail scan (pattern-based, runs BEFORE LLM)
2. LLM-based intent classification
3. Conditional routing to specialized agent nodes
4. Each agent runs its own ReAct-style reasoning loop
5. Post-processing: confidence check, response formatting

State flows through the graph carrying query, intent, response, sources,
confidence scores, reasoning traces, and conversation history.
"""

import re
import logging
from typing import TypedDict, Literal, Annotated

from langgraph.graph import StateGraph, END

from src.config import get_llm_with_fallback
from src.prompts.router_prompt import ROUTER_PROMPT
from src.agents.qa_agent import QAExpertAgent
from src.agents.hr_agent import HROnboardingAgent
from src.agents.guardrails import scan_query, handle_sensitive_info, handle_out_of_scope

logger = logging.getLogger(__name__)


# ── State Definition ──────────────────────────────────────────────────

class AgentState(TypedDict):
    # Input
    query: str
    chat_history: list          # Previous messages for context
    forced_intent: str          # If set, skip LLM classifier and route directly

    # Routing
    intent: str                 # qa_technical | hr_general | sensitive_info | out_of_scope | greeting
    guardrail_blocked: bool     # True if pre-routing guardrail caught it

    # Output
    response: str
    agent: str
    sources: list
    used_web_search: bool

    # Metadata
    confidence: float           # 0.0 – 1.0 confidence in the answer
    tool_calls: list            # Tools invoked during processing
    reasoning_trace: list       # Step-by-step reasoning log
    threat_level: str           # From guardrail scan


# ── LLM Factory ───────────────────────────────────────────────────────

def get_llm():
    """Get an LLM with waterfall fallback across providers.

    Tries Gemini models first (if configured), then falls back to Groq Llama
    models on rate limit errors. See config.py for the full fallback chain.
    """
    return get_llm_with_fallback()


# ── Graph Nodes ───────────────────────────────────────────────────────

def pre_routing_guardrail(state: AgentState) -> AgentState:
    """First line of defense: pattern-based guardrail scan.

    Runs BEFORE the LLM intent classifier to catch obvious threats
    without wasting an LLM call. Checks for:
    - Prompt injection / jailbreak attempts
    - Credential / secret requests
    - MNPI (Material Non-Public Information) requests
    - Out-of-scope topics
    """
    logger.info(f"[Graph] Pre-routing guardrail scan for: '{state['query'][:50]}...'")

    result = scan_query(state["query"])

    if result.is_blocked:
        logger.warning(f"[Graph] Query BLOCKED by guardrail: {result.threat_type} ({result.threat_level})")
        return {
            **state,
            "guardrail_blocked": True,
            "intent": result.threat_type,
            "response": result.response,
            "agent": f"{'Security' if result.threat_level in ('CRITICAL', 'HIGH') else 'Scope'} Guardrail",
            "confidence": 1.0,
            "threat_level": result.threat_level,
            "tool_calls": [{"tool": "guardrail_scan", "input": "pre_routing"}],
            "reasoning_trace": result.to_dict()["reasoning_trace"],
        }

    logger.info("[Graph] Pre-routing guardrail: CLEAR")
    return {**state, "guardrail_blocked": False, "threat_level": "NONE"}


def intent_detector(state: AgentState) -> AgentState:
    """LLM-based intent classification (skipped when forced_intent is set).

    Classifies the query into one of these categories:
    - qa_technical: QA automation, frameworks, testing processes
    - hr_general: HR policies, benefits, onboarding, office info
    - greeting: Greetings and simple small talk
    - sensitive_info: Credential/MNPI requests (backup for guardrail)
    - out_of_scope: Non-work topics
    """
    # ── Greeting detection (runs even with forced_intent) ──
    # Simple greetings like "hi", "hello", "hey" should always get a
    # natural response instead of triggering the full RAG pipeline.
    query_stripped = state["query"].strip().lower()
    greeting_patterns = re.compile(
        r"^(hi|hello|hey|howdy|hola|good\s*(morning|afternoon|evening|day)|"
        r"what'?s\s*up|sup|yo|greetings|namaste|hii+|heyy+|helloo+)[\s!?.,:;)*]*$",
        re.IGNORECASE,
    )
    if greeting_patterns.match(query_stripped):
        logger.info(f"[Graph] Greeting detected: '{state['query']}' → routing to greeting node")
        return {
            **state,
            "intent": "greeting",
            "reasoning_trace": state.get("reasoning_trace", []) + [
                {"step": "CLASSIFY", "detail": "Greeting detected (pattern match, pre-forced-intent)"}
            ],
        }

    # If a specialist agent was selected in the UI, skip LLM classification
    forced = state.get("forced_intent", "")
    if forced:
        logger.info(f"[Graph] Forced intent from UI: {forced} (skipping LLM classifier)")
        return {
            **state,
            "intent": forced,
            "reasoning_trace": state.get("reasoning_trace", []) + [
                {"step": "CLASSIFY", "detail": f"Forced intent: {forced} (specialist agent selected)"}
            ],
        }

    # Check if the user is asking to be connected to a specific agent
    query_lower = state["query"].lower()
    agent_switch = None
    if re.search(r"(connect|talk|switch|transfer|take)\s+(me\s+)?(to\s+)?(the\s+)?(qa|quality)", query_lower):
        agent_switch = ("qa_technical", "QA Expert")
    elif re.search(r"(connect|talk|switch|transfer|take)\s+(me\s+)?(to\s+)?(the\s+)?(hr|human\s+resource|onboarding)", query_lower):
        agent_switch = ("hr_general", "HR & Onboarding")

    if agent_switch:
        intent, agent_name = agent_switch
        logger.info(f"[Graph] Agent switch request detected → {agent_name}")
        return {
            **state,
            "intent": intent,
            "reasoning_trace": state.get("reasoning_trace", []) + [
                {"step": "CLASSIFY", "detail": f"Agent switch request → {agent_name}"}
            ],
        }

    logger.info("[Graph] Running LLM intent classifier...")

    llm = get_llm()

    # Include chat history context for better classification
    history_context = ""
    if state.get("chat_history"):
        recent = state["chat_history"][-4:]  # Last 2 exchanges
        history_lines = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{role}: {msg['content'][:100]}")
        history_context = "\nRecent conversation:\n" + "\n".join(history_lines) + "\n"

    prompt = ROUTER_PROMPT.format(query=state["query"]) + history_context
    response = llm.invoke(prompt)
    intent = response.content.strip().lower().replace('"', "").replace("'", "")

    # Validate intent
    valid_intents = {"qa_technical", "hr_general", "sensitive_info", "out_of_scope", "greeting"}
    if intent not in valid_intents:
        logger.warning(f"[Graph] Invalid intent '{intent}', defaulting to out_of_scope")
        intent = "out_of_scope"

    logger.info(f"[Graph] Intent classified as: {intent}")
    return {
        **state,
        "intent": intent,
        "reasoning_trace": state.get("reasoning_trace", []) + [
            {"step": "CLASSIFY", "detail": f"Intent: {intent}"}
        ],
    }


def qa_agent_node(state: AgentState) -> AgentState:
    """QA Expert Agent node — runs the full ReAct reasoning loop."""
    logger.info("[Graph] Routing to QA Expert Agent...")

    llm = get_llm()
    agent = QAExpertAgent(llm)
    result = agent.run(state["query"])

    return {
        **state,
        "response": result["response"],
        "agent": result["agent"],
        "sources": result["sources"],
        "used_web_search": result["used_web_search"],
        "confidence": result["confidence"],
        "tool_calls": result["tool_calls"],
        "reasoning_trace": state.get("reasoning_trace", []) + result["reasoning_trace"],
    }


def hr_agent_node(state: AgentState) -> AgentState:
    """HR & Onboarding Agent node — runs the strict RAG reasoning loop."""
    logger.info("[Graph] Routing to HR & Onboarding Agent...")

    llm = get_llm()
    agent = HROnboardingAgent(llm)
    result = agent.run(state["query"])

    return {
        **state,
        "response": result["response"],
        "agent": result["agent"],
        "sources": result["sources"],
        "used_web_search": result["used_web_search"],
        "confidence": result["confidence"],
        "tool_calls": result["tool_calls"],
        "reasoning_trace": state.get("reasoning_trace", []) + result["reasoning_trace"],
    }


def sensitive_info_node(state: AgentState) -> AgentState:
    """Sensitive info guardrail node — LLM-classified (backup path)."""
    logger.info("[Graph] Routing to Sensitive Info guardrail...")

    result = handle_sensitive_info(state["query"])
    return {
        **state,
        "response": result["response"],
        "agent": result["agent"],
        "sources": [],
        "used_web_search": False,
        "confidence": 1.0,
        "tool_calls": result.get("tool_calls", []),
        "reasoning_trace": state.get("reasoning_trace", []) + result.get("reasoning_trace", []),
    }


def greeting_node(state: AgentState) -> AgentState:
    """Greeting handler — routed to the HR agent for a natural welcome."""
    logger.info("[Graph] Routing greeting to HR & Onboarding Agent...")

    llm = get_llm()
    prompt = (
        "You are Nova, a friendly HR onboarding colleague at Intercontinental Exchange (ICE). "
        "A new hire on the QA team just greeted you or said something casual. "
        "Respond naturally and warmly like a real colleague — keep it short (2-3 sentences). "
        "Don't list out everything you can do. Just be conversational and welcoming.\n\n"
        f"User: {state['query']}"
    )
    response = llm.invoke(prompt)

    return {
        **state,
        "response": response.content,
        "agent": "HR & Onboarding Agent",
        "sources": [],
        "used_web_search": False,
        "confidence": 1.0,
        "tool_calls": [],
        "reasoning_trace": state.get("reasoning_trace", []) + [
            {"step": "GREETING", "detail": "Routed to HR agent for conversational response"}
        ],
    }


def out_of_scope_node(state: AgentState) -> AgentState:
    """Out-of-scope handler — HR agent politely redirects."""
    logger.info("[Graph] Routing out-of-scope to HR & Onboarding Agent...")

    llm = get_llm()
    prompt = (
        "You are Nova, a friendly HR onboarding colleague at Intercontinental Exchange (ICE). "
        "Someone just asked you something outside your scope — you only help with "
        "ICE onboarding, HR policies, benefits, office info, and QA automation tools.\n\n"
        "Respond naturally and warmly. Acknowledge what they asked, let them know it's "
        "not your area, and gently steer them back. Keep it short (2-3 sentences). "
        "Don't list everything you can do.\n\n"
        f"User: {state['query']}"
    )
    response = llm.invoke(prompt)

    return {
        **state,
        "response": response.content,
        "agent": "HR & Onboarding Agent",
        "sources": [],
        "used_web_search": False,
        "confidence": 1.0,
        "tool_calls": [],
        "reasoning_trace": state.get("reasoning_trace", []) + [
            {"step": "OUT_OF_SCOPE", "detail": "HR agent redirected out-of-scope query"}
        ],
    }


# ── Routing Logic ─────────────────────────────────────────────────────

def check_guardrail_result(state: AgentState) -> Literal["blocked", "continue_to_classifier"]:
    """After pre-routing guardrail: either short-circuit (blocked) or continue to LLM classifier."""
    if state.get("guardrail_blocked"):
        return "blocked"
    return "continue_to_classifier"


def route_by_intent(state: AgentState) -> Literal["qa_agent", "hr_agent", "sensitive_info", "out_of_scope", "greeting"]:
    """Route to the appropriate agent based on LLM-classified intent."""
    intent = state["intent"]
    routing = {
        "qa_technical": "qa_agent",
        "hr_general": "hr_agent",
        "sensitive_info": "sensitive_info",
        "out_of_scope": "out_of_scope",
        "greeting": "greeting",
    }
    return routing.get(intent, "out_of_scope")


# ── Graph Construction ────────────────────────────────────────────────

def build_graph():
    """Build the LangGraph state machine.

    Flow:
    pre_routing_guardrail
        ├── [BLOCKED] → END (guardrail response)
        └── [CLEAR]  → intent_detector
                            ├── qa_agent → END
                            ├── hr_agent → END
                            ├── greeting → END
                            ├── sensitive_info → END
                            └── out_of_scope → END
    """
    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("pre_routing_guardrail", pre_routing_guardrail)
    workflow.add_node("intent_detector", intent_detector)
    workflow.add_node("qa_agent", qa_agent_node)
    workflow.add_node("hr_agent", hr_agent_node)
    workflow.add_node("sensitive_info", sensitive_info_node)
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("out_of_scope", out_of_scope_node)

    # Entry point: always start with guardrail scan
    workflow.set_entry_point("pre_routing_guardrail")

    # Guardrail → either blocked (END) or continue to classifier
    workflow.add_conditional_edges(
        "pre_routing_guardrail",
        check_guardrail_result,
        {
            "blocked": END,
            "continue_to_classifier": "intent_detector",
        },
    )

    # Intent detector → route to appropriate agent
    workflow.add_conditional_edges(
        "intent_detector",
        route_by_intent,
        {
            "qa_agent": "qa_agent",
            "hr_agent": "hr_agent",
            "sensitive_info": "sensitive_info",
            "out_of_scope": "out_of_scope",
            "greeting": "greeting",
        },
    )

    # All agent nodes → END
    workflow.add_edge("qa_agent", END)
    workflow.add_edge("hr_agent", END)
    workflow.add_edge("sensitive_info", END)
    workflow.add_edge("greeting", END)
    workflow.add_edge("out_of_scope", END)

    return workflow.compile()


# ── Public API ────────────────────────────────────────────────────────

# Compile graph once at module level for reuse
_compiled_graph = None


def get_graph():
    """Get or create the compiled graph (singleton)."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_agent(query: str, chat_history: list = None, forced_intent: str = None) -> dict:
    """Run a query through the ICE QAgent pipeline.

    Args:
        query: The user's question
        chat_history: Optional list of previous messages for context
        forced_intent: If set, skip LLM classifier and route directly to this agent
                       (used when user selects a specialist agent in the sidebar)

    Returns:
        Dict with response, agent, sources, confidence, reasoning trace, etc.
    """
    graph = get_graph()

    initial_state: AgentState = {
        "query": query,
        "chat_history": chat_history or [],
        "forced_intent": forced_intent or "",
        "intent": "",
        "guardrail_blocked": False,
        "response": "",
        "agent": "",
        "sources": [],
        "used_web_search": False,
        "confidence": 0.0,
        "tool_calls": [],
        "reasoning_trace": [],
        "threat_level": "NONE",
    }

    result = graph.invoke(initial_state)
    return result
