import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { HandoffIllustration } from "./HandoffIllustration";

it("keeps the original handoff drawing decorative and self-contained", () => {
  const html = renderToStaticMarkup(createElement(HandoffIllustration));
  expect(html).toContain('aria-hidden="true"');
  expect(html).toContain('focusable="false"');
  expect(html).toContain('class="handoff-paper"');
  expect(html).toContain('class="handoff-helper"');
  expect(html).not.toMatch(
    /<text|<image|<script|<animate|<title|id=|href=|tabindex=/i,
  );
});
