import { createContext, useContext } from "react";

export type Theme = "light" | "dark";

export interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

export const ThemeContext = createContext<ThemeContextValue | null>(null);

export function getInitialTheme(): Theme {
  if (typeof window === "undefined") return "light";
  try {
    const saved = localStorage.getItem("onboardiq_theme");
    if (saved === "light" || saved === "dark") return saved;
  } catch {
    // Storage can be blocked; the site must still open.
  }
  return "light";
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    return {
      theme: "light",
      toggleTheme: () => {},
      setTheme: () => {},
    };
  }
  return ctx;
}
