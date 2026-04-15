import { useState, type FormEvent } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../state/auth";

export function LoginPage() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const from =
    (location.state as { from?: { pathname: string } } | null)?.from
      ?.pathname ?? "/dashboard";

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email || !password) {
      setError("Enter an email and password to continue.");
      return;
    }
    setBusy(true);
    try {
      await signIn(email, password);
      navigate(from, { replace: true });
    } catch {
      setError("Sign-in failed. Try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="login">
      <div className="login__bg" aria-hidden="true" />
      <div className="login__overlay" aria-hidden="true" />

      <div className="login__panel">
        <div className="login__brand">
          <img
            src="/open_graph_ice.jpg"
            alt="ICE"
            className="login__brand-logo"
          />
          <span className="login__brand-word">QAgent</span>
        </div>

        <span className="u-eyebrow">Secure Internal Sign-In</span>
        <h1 className="login__title">Welcome back.</h1>
        <p className="login__lead">
          Your onboarding assistant for the Intercontinental Exchange Quality
          Assurance team.
        </p>

        <form className="login__form" onSubmit={onSubmit} noValidate>
          <label className="field">
            <span className="field__label">Corporate Email</span>
            <input
              className="field__input"
              type="email"
              placeholder="firstname.lastname@ice.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
              autoFocus
            />
          </label>

          <label className="field">
            <span className="field__label">Password</span>
            <input
              className="field__input"
              type="password"
              placeholder="••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </label>

          {error && <div className="login__error">{error}</div>}

          <button
            type="submit"
            className="btn btn--primary login__submit"
            disabled={busy}
          >
            <span>{busy ? "Signing in…" : "Sign In"}</span>
            <span className="btn__arrow" aria-hidden="true">
              →
            </span>
          </button>
        </form>

        <div className="login__footer">
          Need help? Contact the IT Help Desk at{" "}
          <span className="login__footer-em">ext. 2-HELP</span> or open a
          ServiceNow ticket.
        </div>
      </div>

      <div className="login__meta">
        <span>Intercontinental Exchange</span>
        <span>Atlanta · Internal Tool</span>
        <span>v1.0.0</span>
      </div>
    </div>
  );
}
