import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { MOCK_HISTORY } from "../data/history";
import { AGENT_META } from "../data/agents";
import type { AgentId } from "../types";

const FILTERS: { id: "all" | AgentId; label: string }[] = [
  { id: "all", label: "All conversations" },
  { id: "hr", label: "HR & Onboarding" },
  { id: "qa", label: "QA Expert" },
  { id: "security", label: "Security" },
];

export function HistoryPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<"all" | AgentId>("all");

  const items = MOCK_HISTORY.filter(
    (h) => filter === "all" || h.agent === filter,
  );

  return (
    <div className="page">
      <header className="page__header">
        <span className="u-eyebrow">Conversation Archive</span>
        <h1 className="page__title">Your past chats.</h1>
        <p className="page__lead">
          Every conversation is privately stored and searchable. Click any
          entry to reopen it with the original agent.
        </p>
      </header>

      <div className="history__filters">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            type="button"
            className={`chip ${filter === f.id ? "is-active" : ""}`.trim()}
            onClick={() => setFilter(f.id)}
          >
            {f.label}
          </button>
        ))}
      </div>

      <ul className="history__list" role="list">
        {items.map((h) => {
          const meta = AGENT_META[h.agent];
          const when = new Date(h.updatedAt).toLocaleString([], {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          });
          return (
            <li key={h.id}>
              <button
                type="button"
                className="history__row"
                onClick={() => navigate(`/chat/${h.agent}`)}
              >
                <div className="history__row-left">
                  <span className="history__agent">{meta.title}</span>
                  <h3 className="history__row-title">{h.title}</h3>
                  <p className="history__row-preview">{h.preview}</p>
                </div>
                <div className="history__row-right">
                  <span className="history__count">{h.messageCount} msgs</span>
                  <span className="history__when">{when}</span>
                  <span className="history__arrow" aria-hidden="true">
                    →
                  </span>
                </div>
              </button>
            </li>
          );
        })}
      </ul>

      {items.length === 0 && (
        <div className="history__empty">
          No conversations yet for this filter. Start a new chat from the
          sidebar.
        </div>
      )}
    </div>
  );
}
