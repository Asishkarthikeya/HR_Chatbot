import { useNavigate } from "react-router-dom";
import { AGENT_META, AGENT_ORDER } from "../data/agents";
import { useAuth } from "../state/auth";
import { Pipeline } from "../components/Pipeline";

export function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="page">
      <header className="page__header">
        <span className="u-eyebrow">Welcome back</span>
        <h1 className="page__title">
          Good to see you,{" "}
          <em className="page__title-em">{user?.name?.split(" ")[0] ?? "there"}</em>
          .
        </h1>
        <p className="page__lead">
          Pick a specialist below to start a conversation, or scroll to see how
          the platform routes and grounds every question you ask.
        </p>
      </header>

      <section className="quick-agents" aria-label="Jump to an agent">
        {AGENT_ORDER.map((id) => {
          const a = AGENT_META[id];
          return (
            <button
              key={id}
              type="button"
              className="quick-agents__card"
              onClick={() => navigate(`/chat/${id}`)}
            >
              <span className="u-label">{a.eyebrow}</span>
              <h3 className="quick-agents__title">{a.title}</h3>
              <p className="quick-agents__body">{a.description}</p>
              <span className="quick-agents__cta">
                Open agent <span aria-hidden="true">→</span>
              </span>
            </button>
          );
        })}
      </section>

      <Pipeline />
    </div>
  );
}
