import { ThemeToggle } from "./ThemeToggle";

export function TopBar() {
  return (
    <header className="topbar">
      <div className="l-container topbar__inner">
        <a href="/" className="topbar__mark">
          <img
            src="/open_graph_ice.jpg"
            alt="ICE"
            className="topbar__logo"
          />
          <em>QAgent</em>
        </a>
        <nav className="topbar__nav" aria-label="Primary">
          <a href="#agents">Agents</a>
          <a href="#about">About</a>
          <a href="#contact">Contact</a>
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}
