import type { AgentMeta, AgentId } from "../types";

export const AGENT_META: Record<AgentId, AgentMeta> = {
  master: {
    id: "master",
    name: "ICE QAgent",
    title: "Intelligent Routing",
    eyebrow: "Auto-Routed",
    accent: "#71c5e8",
    description:
      "Ask anything — the intent agent automatically routes your query to the right specialist: HR, QA, or Security.",
    starterPrompts: [
      "What benefits am I enrolled in?",
      "How do I run the regression suite?",
      "How does the security guardrail work?",
    ],
  },
  hr: {
    id: "hr",
    name: "Nova",
    title: "HR & Onboarding",
    eyebrow: "Human Resources",
    accent: "#71c5e8",
    description:
      "A warm, knowledgeable HR colleague helping new hires settle in at ICE. Grounded in the internal handbook.",
    starterPrompts: [
      "How many PTO days do I get?",
      "What's our parental leave policy?",
      "Can I wear jeans to the office?",
      "Walk me through the 401(k) match.",
    ],
  },
  qa: {
    id: "qa",
    name: "QA Expert",
    title: "Quality Assurance",
    eyebrow: "Engineering",
    accent: "#71c5e8",
    description:
      "A senior QA engineer with years at ICE. Knows the Playwright suites, CI pipelines, and FIX testing inside out.",
    starterPrompts: [
      "How do I run the test suite?",
      "Walk me through our CI pipeline.",
      "How do we test FIX order entry?",
      "What's the conftest fixture pattern?",
    ],
  },
  security: {
    id: "security",
    name: "Security Guardrail",
    title: "Security & Compliance",
    eyebrow: "Always-On",
    accent: "#71c5e8",
    description:
      "Layered defense: prompt-injection detection, PII redaction, and policy enforcement on every response.",
    starterPrompts: [
      "How does the guardrail detect prompt injection?",
      "What PII fields are redacted?",
      "Show the security policy stack.",
    ],
  },
};

export const AGENT_ORDER: AgentId[] = ["master", "hr", "qa", "security"];
