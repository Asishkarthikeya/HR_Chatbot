"""
Security & Scope Guardrails — Multi-layer threat detection and response.

Implements a defense-in-depth approach:
1. Pattern-based detection for known sensitive data request patterns
2. Threat classification with severity levels
3. Context-aware response generation
4. Audit logging for security monitoring
5. Jailbreak/prompt injection detection
"""

import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# ── Threat Pattern Definitions ────────────────────────────────────────

CREDENTIAL_PATTERNS = [
    r"\b(password|passwd|pwd)\b",
    r"\b(api[_\s-]?key|secret[_\s-]?key|access[_\s-]?key)\b",
    r"\b(token|bearer|jwt|oauth)\b.*\b(give|share|provide|show|tell|what)\b",
    r"\b(give|share|provide|show|tell|what)\b.*\b(token|bearer|jwt|oauth)\b",
    r"\b(connection[_\s-]?string|conn[_\s-]?str)\b",
    r"\b(credentials?|creds?)\b",
    r"\b(private[_\s-]?key|ssh[_\s-]?key|pem[_\s-]?file)\b",
    r"\b(aws|azure|gcp)\b.*\b(key|secret|token)\b",
]

DATABASE_PATTERNS = [
    r"\b(database|db)\b.*\b(password|access|login|credentials?)\b",
    r"\b(prod|production)\b.*\b(database|db|server|access)\b",
    r"\b(admin)\b.*\b(password|access|login|credentials?)\b",
    r"\b(root)\b.*\b(password|access|login)\b",
    r"\b(staging|prod)\b.*\b(db|database)\b.*\b(password|cred)\b",
]

MNPI_PATTERNS = [
    r"\b(trade|trading)\b.*\b(volume|data|information)\b.*\b(unreleased|confidential|internal)\b",
    r"\b(merger|acquisition|takeover)\b.*\b(pending|upcoming|planned)\b",
    r"\b(earnings|revenue|profit)\b.*\b(unreleased|upcoming|next quarter)\b",
    r"\b(insider|mnpi|material non-public)\b",
    r"\b(clearing)\b.*\b(volume|real|actual)\b.*\b(data|numbers)\b",
]

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+(instructions?|prompts?|rules?)",
    r"you\s+are\s+now\s+(a|an|my)",
    r"(system\s+prompt|initial\s+prompt|original\s+instructions?)",
    r"pretend\s+(you|to\s+be)",
    r"(jailbreak|bypass|override)\s+(the|your|safety|security|filter)",
    r"act\s+as\s+(if|though)\s+you\s+(have\s+no|don.t\s+have)",
    r"(forget|disregard|ignore)\s+(everything|all|your)\s+(above|previous|rules)",
]

# Out-of-scope detection is now handled by the LLM intent classifier,
# which gives more natural, conversational responses instead of rigid blocks.
OUT_OF_SCOPE_PATTERNS = []


# ── Threat Classifications ────────────────────────────────────────────

class ThreatLevel:
    CRITICAL = "CRITICAL"   # Credential/MNPI requests — hard block
    HIGH = "HIGH"           # Prompt injection attempts — hard block
    MEDIUM = "MEDIUM"       # Out-of-scope queries — soft block
    LOW = "LOW"             # Edge cases — warn and redirect
    NONE = "NONE"           # Clean query


class GuardrailResult:
    """Structured result from guardrail evaluation."""

    def __init__(self, is_blocked: bool, threat_level: str, threat_type: str,
                 detected_patterns: list, response: str, audit_log: dict):
        self.is_blocked = is_blocked
        self.threat_level = threat_level
        self.threat_type = threat_type
        self.detected_patterns = detected_patterns
        self.response = response
        self.audit_log = audit_log

    def to_dict(self) -> dict:
        return {
            "response": self.response,
            "agent": f"{'Security' if self.threat_level in (ThreatLevel.CRITICAL, ThreatLevel.HIGH) else 'Scope'} Guardrail",
            "sources": [],
            "used_web_search": False,
            "confidence": 1.0,
            "threat_level": self.threat_level,
            "threat_type": self.threat_type,
            "tool_calls": [{"tool": "guardrail_scan", "input": "query_screening"}],
            "reasoning_trace": [
                {"step": "SCAN", "detail": f"Detected threat: {self.threat_type} ({self.threat_level})"},
                {"step": "BLOCK", "detail": f"Matched patterns: {self.detected_patterns}"},
                {"step": "RESPOND", "detail": "Returning guardrail response"},
            ],
        }


# ── Pattern Matching Engine ───────────────────────────────────────────

def _match_patterns(query: str, patterns: list[str]) -> list[str]:
    """Match query against a list of regex patterns. Returns matched pattern strings."""
    query_lower = query.lower()
    matches = []
    for pattern in patterns:
        if re.search(pattern, query_lower):
            matches.append(pattern)
    return matches


def _create_audit_log(query: str, threat_level: str, threat_type: str,
                      patterns: list[str]) -> dict:
    """Create an audit log entry for security monitoring."""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "threat_level": threat_level,
        "threat_type": threat_type,
        "query_hash": hash(query),  # Don't log the actual query for privacy
        "query_length": len(query),
        "patterns_matched": len(patterns),
    }
    logger.warning(
        f"[GUARDRAIL] {threat_level} | Type: {threat_type} | "
        f"Patterns matched: {len(patterns)} | Query length: {len(query)}"
    )
    return log_entry


# ── Response Templates ────────────────────────────────────────────────

SENSITIVE_INFO_RESPONSE = (
    "I totally understand you need access, but I'm not able to share credentials, "
    "API keys, or passwords directly — that's handled through our secure channels "
    "to keep everything safe.\n\n"
    "Here's where to go:\n\n"
    "| What you need | Where to go |\n"
    "|------|--------|\n"
    "| Database credentials | **CyberArk** (cyberark.ice-internal.com) |\n"
    "| IT access requests | **ServiceNow** (servicenow.ice-internal.com) |\n"
    "| Something urgent | **IT Help Desk** — just dial ext. 2-HELP |\n"
    "| VPN/Network access | **Cisco AnyConnect** via IT Help Desk |\n\n"
    "Just submit a ServiceNow request with your manager's approval and "
    "you should be all set! Let me know if you need help with anything else."
)

MNPI_RESPONSE = (
    "Good question, but that touches on Material Non-Public Information (MNPI), "
    "and I need to be careful here.\n\n"
    "As part of ICE, we all have a responsibility to protect this kind of data. "
    "That includes things like unreleased financial figures, trade volumes, "
    "or pending deals.\n\n"
    "If you need this for a legitimate business reason, reach out to the "
    "**Compliance team** at compliance@ice-internal.com — they'll point you "
    "in the right direction.\n\n"
    "You can also review the **ICE Code of Conduct** section on MNPI handling "
    "for more details. Want me to help with anything else?"
)

INJECTION_RESPONSE = (
    "Hmm, that doesn't quite look like an onboarding question! 😅\n\n"
    "I'm here specifically to help you settle in at ICE — things like your "
    "benefits, office info, QA tools, team processes, and all that good stuff.\n\n"
    "What would you like to know about your onboarding?"
)

OUT_OF_SCOPE_RESPONSE = (
    "Ha, I wish I could help with that! But I'm really only set up for "
    "ICE onboarding stuff — HR policies, benefits, office logistics, QA tools, "
    "team processes, that kind of thing.\n\n"
    "Is there anything about your onboarding I can help with?"
)


# ── Main Guardrail Functions ──────────────────────────────────────────

def scan_query(query: str) -> GuardrailResult:
    """Run the full guardrail scan against a query.

    Checks (in priority order):
    1. Prompt injection / jailbreak attempts (CRITICAL)
    2. Credential / secret requests (CRITICAL)
    3. MNPI requests (CRITICAL)
    4. Out-of-scope topics (MEDIUM)
    """
    # Check 1: Prompt injection (highest priority)
    injection_matches = _match_patterns(query, PROMPT_INJECTION_PATTERNS)
    if injection_matches:
        audit = _create_audit_log(query, ThreatLevel.HIGH, "prompt_injection", injection_matches)
        return GuardrailResult(
            is_blocked=True,
            threat_level=ThreatLevel.HIGH,
            threat_type="prompt_injection",
            detected_patterns=injection_matches,
            response=INJECTION_RESPONSE,
            audit_log=audit,
        )

    # Check 2: Credential requests
    cred_matches = _match_patterns(query, CREDENTIAL_PATTERNS)
    db_matches = _match_patterns(query, DATABASE_PATTERNS)
    if cred_matches or db_matches:
        all_matches = cred_matches + db_matches
        audit = _create_audit_log(query, ThreatLevel.CRITICAL, "credential_request", all_matches)
        return GuardrailResult(
            is_blocked=True,
            threat_level=ThreatLevel.CRITICAL,
            threat_type="credential_request",
            detected_patterns=all_matches,
            response=SENSITIVE_INFO_RESPONSE,
            audit_log=audit,
        )

    # Check 3: MNPI requests
    mnpi_matches = _match_patterns(query, MNPI_PATTERNS)
    if mnpi_matches:
        audit = _create_audit_log(query, ThreatLevel.CRITICAL, "mnpi_request", mnpi_matches)
        return GuardrailResult(
            is_blocked=True,
            threat_level=ThreatLevel.CRITICAL,
            threat_type="mnpi_request",
            detected_patterns=mnpi_matches,
            response=MNPI_RESPONSE,
            audit_log=audit,
        )

    # Check 4: Out-of-scope
    oos_matches = _match_patterns(query, OUT_OF_SCOPE_PATTERNS)
    if oos_matches:
        audit = _create_audit_log(query, ThreatLevel.MEDIUM, "out_of_scope", oos_matches)
        return GuardrailResult(
            is_blocked=True,
            threat_level=ThreatLevel.MEDIUM,
            threat_type="out_of_scope",
            detected_patterns=oos_matches,
            response=OUT_OF_SCOPE_RESPONSE,
            audit_log=audit,
        )

    # Clean — no threats detected
    return GuardrailResult(
        is_blocked=False,
        threat_level=ThreatLevel.NONE,
        threat_type="none",
        detected_patterns=[],
        response="",
        audit_log={},
    )


def handle_sensitive_info(query: str) -> dict:
    """Legacy interface — routes through the full scan."""
    result = scan_query(query)
    if result.is_blocked and result.threat_type in ("credential_request", "mnpi_request"):
        return result.to_dict()
    # Fallback to default sensitive info response
    return GuardrailResult(
        is_blocked=True,
        threat_level=ThreatLevel.CRITICAL,
        threat_type="credential_request",
        detected_patterns=[],
        response=SENSITIVE_INFO_RESPONSE,
        audit_log=_create_audit_log(query, ThreatLevel.CRITICAL, "credential_request", []),
    ).to_dict()


def handle_out_of_scope(query: str) -> dict:
    """Legacy interface — routes through the full scan."""
    return GuardrailResult(
        is_blocked=True,
        threat_level=ThreatLevel.MEDIUM,
        threat_type="out_of_scope",
        detected_patterns=[],
        response=OUT_OF_SCOPE_RESPONSE,
        audit_log=_create_audit_log(query, ThreatLevel.MEDIUM, "out_of_scope", []),
    ).to_dict()
