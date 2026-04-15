import { AGENTS } from "../config";
import { AgentCard } from "./AgentCard";

export function AgentsSection() {
  return (
    <section className="section section--agents" id="agents">
      <div className="l-container">
        <div className="section__head">
          <span className="u-eyebrow">The Platform</span>
          <h2 className="u-headline">Three specialists, one conversation.</h2>
          <p className="u-lead">
            Every question is routed to the right expert, grounded in internal
            ICE documentation, and checked by a dedicated security layer
            before it reaches you.
          </p>
        </div>

        <div className="l-grid-3">
          {AGENTS.map((agent) => (
            <AgentCard
              key={agent.id}
              label={agent.label}
              title={agent.title}
              body={agent.body}
              footer={agent.footer}
            />
          ))}
        </div>

        <div className="section__footnote">
          Intercontinental Exchange · Internal tool · Not for external use
        </div>
      </div>
    </section>
  );
}
