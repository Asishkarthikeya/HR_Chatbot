import { useTheme } from "../state/theme";

interface Props {
  variant?: "inline" | "compact";
}

export function ThemeToggle({ variant = "inline" }: Props) {
  const { theme, toggle } = useTheme();
  const isDark = theme === "dark";
  return (
    <button
      type="button"
      className={`theme-toggle theme-toggle--${variant}`}
      onClick={toggle}
      aria-pressed={isDark}
      aria-label={`Switch to ${isDark ? "light" : "dark"} mode`}
      title={`Switch to ${isDark ? "light" : "dark"} mode`}
    >
      <span className="theme-toggle__icon" aria-hidden="true">
        {isDark ? "☀" : "☾"}
      </span>
      <span className="theme-toggle__label">
        {isDark ? "Light" : "Dark"} mode
      </span>
    </button>
  );
}
