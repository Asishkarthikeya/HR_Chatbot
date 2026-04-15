import type { ChatSession, ChatMessage } from "../types";

export const MOCK_HISTORY: ChatSession[] = [
  {
    id: "hist-1",
    agent: "hr",
    title: "PTO balance & rollover rules",
    preview:
      "You get 15 PTO days per year in your first two years, accruing bi-weekly. Only 5 days roll over…",
    messageCount: 6,
    updatedAt: "2026-04-12T16:22:00Z",
  },
  {
    id: "hist-2",
    agent: "qa",
    title: "How to run the regression suite",
    preview:
      "Make sure your VPN is connected first, then run pytest tests/ -v. If anything fails on first run, check the .env…",
    messageCount: 4,
    updatedAt: "2026-04-12T14:03:00Z",
  },
  {
    id: "hist-3",
    agent: "qa",
    title: "CI pipeline walkthrough",
    preview:
      "The CI pipeline runs on GitHub Actions every time you push to a PR. Lint → unit → integration → Snyk → build → Allure…",
    messageCount: 9,
    updatedAt: "2026-04-11T19:47:00Z",
  },
  {
    id: "hist-4",
    agent: "hr",
    title: "Parental leave policy",
    preview:
      "At the Atlanta HQ, primary caregivers get 16 weeks fully paid and secondary caregivers get 4 weeks. The London office…",
    messageCount: 3,
    updatedAt: "2026-04-10T11:15:00Z",
  },
  {
    id: "hist-5",
    agent: "security",
    title: "Prompt injection test coverage",
    preview:
      "The guardrail catches jailbreak attempts, role confusion, and indirect injection via retrieved documents…",
    messageCount: 5,
    updatedAt: "2026-04-09T09:33:00Z",
  },
  {
    id: "hist-6",
    agent: "hr",
    title: "Dress code clarification",
    preview:
      "Dark jeans are fine on non-client days — pair them with a collared shirt. Sneakers, athletic wear, and ripped jeans…",
    messageCount: 2,
    updatedAt: "2026-04-08T15:02:00Z",
  },
];

export const SAMPLE_THREADS: Record<string, ChatMessage[]> = {
  "hist-1": [
    {
      id: "m1",
      role: "user",
      text: "How many PTO days do I get?",
      createdAt: "2026-04-12T16:20:12Z",
    },
    {
      id: "m2",
      role: "assistant",
      agent: "hr",
      text:
        "In your first two years, you get **15 PTO days per year**. That goes up to 20 days at year 3 and 25 days at year 6+. PTO accrues bi-weekly, so you can check your current balance anytime in Workday.\n\nJust a heads up — only 5 unused days roll over to the next year, so make sure to use them!",
      createdAt: "2026-04-12T16:20:14Z",
    },
  ],
};
