export const DASHBOARD_URL =
  import.meta.env.VITE_DASHBOARD_URL ?? "http://localhost:8501";

export const AGENTS = [
  {
    id: "hr",
    label: "Module 01",
    title: "HR & Onboarding",
    body: "Benefits, PTO, policies, and first-week logistics — grounded in the internal ICE handbook and answered by Nova, your HR colleague.",
    footer: "Nova · Grounded retrieval",
  },
  {
    id: "qa",
    label: "Module 02",
    title: "QA Expert",
    body: "Playwright suites, CI pipelines, FIX simulators, and the internal QA standards — onboarding guidance from a senior QA engineer's perspective.",
    footer: "Senior QA · Technical depth",
  },
  {
    id: "security",
    label: "Module 03",
    title: "Security Guardrail",
    body: "Prompt-injection defense, PII redaction, and policy enforcement on every response. Runs silently behind every agent conversation.",
    footer: "Always-on · Layered defense",
  },
] as const;
