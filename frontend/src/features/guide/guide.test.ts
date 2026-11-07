import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";
import { canOpen, navFor, parseHash } from "../../shared/routes";
import { GuidePage } from "./Guide";
import { ROLE_GUIDES, ROLE_ORDER, WORKFLOW } from "./guide-content";

afterEach(() => vi.unstubAllGlobals());

describe("static product guides", () => {
  it.each(["how-it-works", "role-guide"] as const)(
    "renders %s without session context or data requests",
    (page) => {
      const fetcher = vi.fn();
      vi.stubGlobal("fetch", fetcher);
      const html = renderToStaticMarkup(createElement(GuidePage, { page }));
      expect(html).toContain('id="guide-main"');
      expect(html).toContain('href="#/"');
      expect(html).toContain("Sign in");
      expect(fetcher).not.toHaveBeenCalled();
      expect(html.match(/class="handoff-illustration"/g)).toHaveLength(1);
    },
  );

  it("can be embedded without nesting another main or replacing the account shell", () => {
    const html = renderToStaticMarkup(
      createElement(GuidePage, { page: "role-guide", embedded: true }),
    );
    expect(html).not.toContain("<main");
    expect(html).not.toContain("public-header");
    expect(html).toContain("This is a guide—not a change to your account.");
  });

  it.each(ROLE_ORDER)(
    "links both guides for %s without widening existing restricted screens",
    (role) => {
      const links = navFor(role)
        .flatMap((group) => group.items)
        .map((item) => item.href);
      for (const page of ["how-it-works", "role-guide"] as const) {
        expect(parseHash("#/" + page)).toEqual({ name: page });
        expect(canOpen(role, { name: page })).toBe(true);
        expect(links).toContain("#/" + page);
      }
      expect(canOpen(role, { name: "settings" })).toBe(role === "HR");
      expect(canOpen(role, { name: "documents" })).toBe(role === "HR");
      expect(canOpen(role, { name: "review" })).toBe(
        role === "HR" || role === "IT",
      );
      expect(ROLE_GUIDES[role].actions.length).toBeGreaterThan(0);
      expect(ROLE_GUIDES[role].boundary).not.toBe("");
      expect(ROLE_GUIDES[role].handoff).not.toBe("");
    },
  );

  it("explains exact outcomes instead of promising autonomous approval or delivery", () => {
    const html = renderToStaticMarkup(
      createElement(GuidePage, { page: "how-it-works" }),
    );
    expect(WORKFLOW).toHaveLength(5);
    expect(html).toContain("Reserved. Collection still pending.");
    expect(html).toContain("Illustrative demo. No live employee record.");
    expect(html).toContain("It does not own permissions or approvals.");
    expect(html).toContain(
      "Manual tasks, document review, department records and human approvals continue.",
    );
  });
});
