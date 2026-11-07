import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const css = readFileSync(new URL("./src/styles.css", import.meta.url), "utf8");
const fonts = readFileSync(new URL("./src/fonts.css", import.meta.url), "utf8");
const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");

function luminance(hex: string) {
  const rgb = hex.match(/[a-f0-9]{2}/gi)!.map((part) => {
    const value = parseInt(part, 16) / 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });
  return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
}

function contrast(a: string, b: string) {
  const values = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (values[0] + 0.05) / (values[1] + 0.05);
}

describe("Open Handoffs visual guardrails", () => {
  it("keeps readable text and primary controls on the approved surfaces", () => {
    for (const background of ["#ffffff", "#f7f7f7", "#f1f1f1"]) {
      for (const foreground of ["#141414", "#454545", "#626262", "#b4232c"]) {
        expect(contrast(foreground, background)).toBeGreaterThanOrEqual(4.5);
      }
    }
    for (const background of ["#b4232c", "#941c24"]) {
      expect(contrast("#ffffff", background)).toBeGreaterThanOrEqual(4.5);
    }
    expect(contrast("#b4232c", "#fff1f2")).toBeGreaterThanOrEqual(4.5);
    expect(contrast("#b4232c", "#ffffff")).toBeGreaterThanOrEqual(3);
    expect(css).toContain("--accent: #b4232c;");
    expect(css).toContain("--accent-hover: #941c24;");
    expect(css).toContain("--accent-soft: #fff1f2;");
    expect(css).toContain("--side: #ffffff;");
    expect(css).toContain("outline-color: var(--focus)");
  });

  it("keeps optional motion finite and behind the user motion preference", () => {
    const motion = css.slice(css.indexOf("/* Motion connects claim to proof"));
    expect(motion).toContain("prefers-reduced-motion: no-preference");
    expect(motion).toContain("handoff-link 560ms");
    expect(motion).toContain("account-open 160ms");
    expect(motion).toContain("paper-handoff 1800ms");
    expect(motion).toContain("helper-greeting 1800ms");
    expect(motion).not.toMatch(
      /infinite|animation-delay|will-change|height:\s*100vh/,
    );
    expect(css).toMatch(
      /prefers-reduced-motion: reduce[^]*?animation: none !important/,
    );
  });

  it("bundles the licensed font without contacting a font service", () => {
    expect(css).toContain('@import "./fonts.css"');
    expect(fonts).toContain('font-family: "Source Sans 3"');
    expect(fonts).toContain("data:font/woff2;base64,d09GMg");
    expect(html).not.toMatch(/fonts\.(googleapis|gstatic)\.com/);
  });

  it("does not restore gradients, decorative side borders or pulsing states", () => {
    expect(css).not.toMatch(/(?:linear|radial|conic)-gradient\(/);
    expect(css).not.toMatch(/border-(?:left|right)(?:-width)?:\s*[2-9]px/);
    expect(css).not.toMatch(/animation:.*infinite/);
    expect(css).toContain("prefers-reduced-motion: reduce");
    expect(css).toContain(":focus-visible");
  });
});
