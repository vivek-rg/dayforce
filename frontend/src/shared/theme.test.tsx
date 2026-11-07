import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";
import { getInitialTheme } from "./theme-context";
import { ThemeProvider, ThemeToggle } from "./theme";

afterEach(() => vi.unstubAllGlobals());

describe("Initial theme", () => {
  it.each([null, "invalid"])(
    "defaults to light despite a dark system preference when saved value is %s",
    (saved) => {
      vi.stubGlobal("window", { matchMedia: () => ({ matches: true }) });
      vi.stubGlobal("localStorage", { getItem: () => saved });
      expect(getInitialTheme()).toBe("light");
    },
  );

  it.each(["light", "dark"] as const)("keeps a saved %s choice", (saved) => {
    vi.stubGlobal("window", {});
    vi.stubGlobal("localStorage", { getItem: () => saved });
    expect(getInitialTheme()).toBe(saved);
  });

  it("falls back to light when browser storage is blocked", () => {
    vi.stubGlobal("window", {});
    vi.stubGlobal("localStorage", {
      getItem: () => {
        throw new Error("Storage blocked");
      },
    });
    expect(getInitialTheme()).toBe("light");
  });
});

describe("Theme system", () => {
  it("renders ThemeToggle button with accessible aria-label", () => {
    const html = renderToStaticMarkup(
      createElement(ThemeProvider, null, createElement(ThemeToggle, null)),
    );
    expect(html).toContain("theme-toggle");
    expect(html).toMatch(/aria-label="Switch to (dark|light) mode"/);
    expect(html).toContain("<svg");
  });

  it("renders ThemeToggle with custom className and label visibility", () => {
    const html = renderToStaticMarkup(
      createElement(
        ThemeProvider,
        null,
        createElement(ThemeToggle, {
          className: "custom-toggle",
          showLabel: false,
        }),
      ),
    );
    expect(html).toContain('class="custom-toggle"');
    expect(html).not.toContain("theme-toggle-label");
  });
});
