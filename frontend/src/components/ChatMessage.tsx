import { useState } from "react";
import type { ChatMessage as ChatMessageT } from "../types";
import { AGENT_META } from "../data/agents";

export function ChatMessage({ message }: { message: ChatMessageT }) {
  const isUser = message.role === "user";
  const agent = message.agent ? AGENT_META[message.agent] : undefined;
  const time = new Date(message.createdAt).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <article
      className={`msg ${isUser ? "msg--user" : "msg--agent"} ${
        message.error ? "msg--error" : ""
      }`.trim()}
    >
      <div className="msg__avatar" aria-hidden="true">
        {isUser ? "YOU" : agent?.name.slice(0, 2).toUpperCase() ?? "AI"}
      </div>
      <div className="msg__body">
        <header className="msg__meta">
          <span className="msg__who">
            {isUser ? "You" : agent?.name ?? "Agent"}
          </span>
          <span className="msg__time">{time}</span>
        </header>
        <div className="msg__text">
          {message.text.split("\n\n").map((para, i) => (
            <p key={i}>{renderInline(para)}</p>
          ))}
        </div>
        {!isUser && !message.error && <AgentMeta message={message} />}
      </div>
    </article>
  );
}

function AgentMeta({ message }: { message: ChatMessageT }) {
  const [showTrace, setShowTrace] = useState(false);
  const [showSources, setShowSources] = useState(false);

  const conf =
    typeof message.confidence === "number"
      ? Math.round(message.confidence * 100)
      : null;
  const confLabel =
    conf === null ? null : conf >= 75 ? "High" : conf >= 45 ? "Medium" : "Low";
  const confClass =
    conf === null ? "" : conf >= 75 ? "high" : conf >= 45 ? "med" : "low";

  const hasSources = (message.sources?.length ?? 0) > 0;
  const hasTrace = (message.reasoningTrace?.length ?? 0) > 0;
  const showBadges =
    conf !== null ||
    hasSources ||
    hasTrace ||
    message.usedWebSearch ||
    message.guardrailBlocked ||
    !!message.intent;

  if (!showBadges) return null;

  return (
    <div className="msg__agent-meta">
      <div className="msg__badges">
        {message.intent && (
          <span className="msg__badge msg__badge--intent">
            {message.intent.replace(/_/g, " ")}
          </span>
        )}
        {conf !== null && confLabel && (
          <span className={`msg__badge msg__badge--conf msg__badge--${confClass}`}>
            Confidence · {confLabel} ({conf}%)
          </span>
        )}
        {message.usedWebSearch && (
          <span className="msg__badge msg__badge--web">Web search</span>
        )}
        {message.guardrailBlocked && (
          <span className="msg__badge msg__badge--block">
            Blocked · {message.threatLevel ?? "HIGH"}
          </span>
        )}
        {hasSources && (
          <button
            type="button"
            className="msg__badge msg__badge--link"
            onClick={() => setShowSources((v) => !v)}
          >
            {showSources ? "Hide" : "Show"} sources ({message.sources!.length})
          </button>
        )}
        {hasTrace && (
          <button
            type="button"
            className="msg__badge msg__badge--link"
            onClick={() => setShowTrace((v) => !v)}
          >
            {showTrace ? "Hide" : "Show"} reasoning
          </button>
        )}
      </div>

      {showSources && hasSources && (
        <ul className="msg__sources">
          {message.sources!.map((s, i) => (
            <li key={i} className="msg__source">
              <div className="msg__source-head">
                <span className="msg__source-name">{s.name || `Source ${i + 1}`}</span>
                {s.score > 0 && (
                  <span className="msg__source-score">
                    {(s.score * 100).toFixed(0)}%
                  </span>
                )}
              </div>
              {s.content && <p className="msg__source-snippet">{s.content}</p>}
            </li>
          ))}
        </ul>
      )}

      {showTrace && hasTrace && (
        <ol className="msg__trace">
          {message.reasoningTrace!.map((t, i) => (
            <li key={i} className="msg__trace-item">
              <span className="msg__trace-step">{t.step}</span>
              <span className="msg__trace-detail">{t.detail}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function renderInline(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
}
