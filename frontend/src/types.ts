export type AgentId = "hr" | "qa" | "security" | "master";

export interface AgentMeta {
  id: AgentId;
  name: string;
  title: string;
  eyebrow: string;
  accent: string;
  description: string;
  starterPrompts: string[];
}

export interface ChatSource {
  name: string;
  score: number;
  content: string;
}

export interface ReasoningStep {
  step: string;
  detail: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  agent?: AgentId;
  text: string;
  createdAt: string;
  intent?: string;
  confidence?: number;
  sources?: ChatSource[];
  reasoningTrace?: ReasoningStep[];
  usedWebSearch?: boolean;
  guardrailBlocked?: boolean;
  threatLevel?: string;
  error?: boolean;
}

export interface ChatSession {
  id: string;
  agent: AgentId;
  title: string;
  preview: string;
  messageCount: number;
  updatedAt: string;
}

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
  startedAt: string;
}
