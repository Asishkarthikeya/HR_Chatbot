import { useEffect, useMemo, useRef } from "react";
import { Navigate, useParams } from "react-router-dom";
import { AGENT_META } from "../data/agents";
import { useChatSession } from "../state/chat";
import { ChatMessage } from "../components/ChatMessage";
import { ChatComposer } from "../components/ChatComposer";
import type { AgentId } from "../types";

const VALID: AgentId[] = ["master", "hr", "qa", "security"];

function isAgent(id: string | undefined): id is AgentId {
  return !!id && (VALID as string[]).includes(id);
}

export function ChatPage() {
  const { agent } = useParams<{ agent: string }>();

  if (!isAgent(agent)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <ChatView agent={agent} />;
}

function ChatView({ agent }: { agent: AgentId }) {
  const meta = useMemo(() => AGENT_META[agent], [agent]);
  const { messages, pending, send, reset } = useChatSession(agent);
  const scrollerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    reset();
  }, [agent, reset]);

  useEffect(() => {
    const el = scrollerRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, pending]);

  const empty = messages.length === 0;

  return (
    <div className="chat">
      <header className="chat__header">
        <div className="chat__header-meta">
          <span className="u-eyebrow">{meta.eyebrow}</span>
          <h1 className="chat__title">{meta.title}</h1>
          <p className="chat__lead">{meta.description}</p>
        </div>
        <div className="chat__header-badge" aria-hidden="true">
          <span>{meta.name.slice(0, 2).toUpperCase()}</span>
        </div>
      </header>

      <div className="chat__scroller" ref={scrollerRef}>
        {empty ? (
          <div className="chat__empty">
            <span className="u-eyebrow">Suggested starters</span>
            <div className="chat__starters">
              {meta.starterPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  className="chat__starter"
                  onClick={() => send(prompt)}
                >
                  <span>{prompt}</span>
                  <span aria-hidden="true">→</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat__messages">
            {messages.map((m) => (
              <ChatMessage key={m.id} message={m} />
            ))}
            {pending && (
              <div className="chat__typing" aria-live="polite">
                <span />
                <span />
                <span />
              </div>
            )}
          </div>
        )}
      </div>

      <div className="chat__composer-wrap">
        <ChatComposer onSend={send} disabled={pending} />
        <div className="chat__footnote">
          Grounded in internal ICE documentation · Security guardrail active
        </div>
      </div>
    </div>
  );
}
