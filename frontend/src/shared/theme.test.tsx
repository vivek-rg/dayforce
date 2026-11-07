import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { ThemeProvider, ThemeToggle } from "./theme";

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
