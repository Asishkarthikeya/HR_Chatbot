import { useCallback, useState } from "react";
import type { AgentId, ChatMessage, ChatSource, ReasoningStep } from "../types";

interface ApiChatResponse {
  response: string;
  agent: string;
  intent: string;
  confidence: number;
  sources: ChatSource[];
  reasoning_trace: ReasoningStep[];
  used_web_search: boolean;
  guardrail_blocked: boolean;
  threat_level: string;
}

function mapAgentBack(agent: string): AgentId | undefined {
  const a = agent.toLowerCase();
  if (a.includes("hr")) return "hr";
  if (a.includes("qa")) return "qa";
  if (a.includes("security") || a.includes("guardrail")) return "security";
  return undefined;
}

async function callAgent(
  agent: AgentId,
  query: string,
  history: ChatMessage[],
): Promise<ApiChatResponse> {
  const chatHistory = history.slice(-6).map((m) => ({
    role: m.role,
    content: m.text,
  }));

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, agent, chat_history: chatHistory }),
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = String(body.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }

  return (await res.json()) as ApiChatResponse;
}

export function useChatSession(agent: AgentId) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [pending, setPending] = useState(false);

  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed) return;

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        text: trimmed,
        createdAt: new Date().toISOString(),
      };
      const historyForCall: ChatMessage[] = [];
      setMessages((prev) => {
        historyForCall.push(...prev);
        return [...prev, userMsg];
      });
      setPending(true);

      try {
        const data = await callAgent(agent, trimmed, historyForCall);
        const reply: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          agent: mapAgentBack(data.agent) ?? agent,
          text: data.response || "(no response)",
          createdAt: new Date().toISOString(),
          intent: data.intent,
          confidence: data.confidence,
          sources: data.sources,
          reasoningTrace: data.reasoning_trace,
          usedWebSearch: data.used_web_search,
          guardrailBlocked: data.guardrail_blocked,
          threatLevel: data.threat_level,
        };
        setMessages((prev) => [...prev, reply]);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        const errReply: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          agent,
          text: `Couldn't reach the agent pipeline — ${msg}. Check that the FastAPI backend is running on port 8000 (\`uvicorn api:app --reload\`).`,
          createdAt: new Date().toISOString(),
          error: true,
        };
        setMessages((prev) => [...prev, errReply]);
      } finally {
        setPending(false);
      }
    },
    [agent],
  );

  const reset = useCallback(() => setMessages([]), []);

  return { messages, pending, send, reset };
}
