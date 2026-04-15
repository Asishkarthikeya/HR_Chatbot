import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../state/auth";
import { ThemeToggle } from "./ThemeToggle";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", kbd: "01" },
  { to: "/chat/master", label: "Auto-Routed", kbd: "02" },
  { to: "/chat/hr", label: "HR & Onboarding", kbd: "03" },
  { to: "/chat/qa", label: "QA Expert", kbd: "04" },
  { to: "/chat/security", label: "Security", kbd: "05" },
  { to: "/history", label: "History", kbd: "06" },
];

export function Sidebar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const initials = (user?.name ?? "ICE")
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const handleSignOut = () => {
    signOut();
    navigate("/login", { replace: true });
  };

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <img
          src="/open_graph_ice.jpg"
          alt="ICE"
          className="sidebar__brand-logo"
        />
        <span className="sidebar__brand-word">QAgent</span>
      </div>

      <nav className="sidebar__nav" aria-label="Primary">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `sidebar__link ${isActive ? "is-active" : ""}`.trim()
            }
          >
            <span className="sidebar__kbd">{item.kbd}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__spacer" />

      <div className="sidebar__user">
        <div className="sidebar__avatar" aria-hidden="true">
          {initials}
        </div>
        <div className="sidebar__user-meta">
          <div className="sidebar__user-name">{user?.name ?? "Guest"}</div>
          <div className="sidebar__user-role">
            {user?.role ?? "Not signed in"}
          </div>
        </div>
      </div>

      <ThemeToggle />

      <button
        type="button"
        className="sidebar__signout"
        onClick={handleSignOut}
      >
        Sign out
      </button>
    </aside>
  );
}
