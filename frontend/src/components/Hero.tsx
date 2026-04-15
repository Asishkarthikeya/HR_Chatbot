import { CTAButton } from "./CTAButton";

export function Hero() {
  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero__bg" aria-hidden="true" />
      <div className="hero__overlay" aria-hidden="true" />

      <div className="l-container hero__inner l-center">
        <span className="u-eyebrow">Intercontinental Exchange · Atlanta</span>
        <div className="hero__accent-bar" aria-hidden="true" />
        <h1 id="hero-title" className="u-display hero__title">
          ICE QAgent
        </h1>
        <p className="u-lead hero__subtitle">
          An internal onboarding assistant for the Quality Assurance team.
          Private, grounded, and routed through specialist agents for HR, QA,
          and Security.
        </p>

        <div className="hero__meta" aria-hidden="true">
          <span>Private by design</span>
          <span>Multi-agent routing</span>
          <span>Voice enabled</span>
        </div>

        <div className="hero__cta">
          <CTAButton label="Sign In" href="/login" />
        </div>
      </div>
    </section>
  );
}
