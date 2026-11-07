import { renderToStaticMarkup } from "react-dom/server";
import { expect, it, vi } from "vitest";
import { InvestigationTab } from "./InvestigationTab";

const view = vi.hoisted(() => ({ state: "ESCALATED" }));

vi.mock("../../shared/session-context", () => ({
  useUser: () => ({ id: "U_HR", role: "HR" }),
  useShell: () => ({ aiHealth: null }),
}));

vi.mock("../../shared/hooks", () => ({
  useInterval: vi.fn(),
  useAction: () => ({ pending: false, error: null }),
  useResource: (key: string) => ({
    loading: false,
    refreshing: false,
    error: null,
    reload: vi.fn(),
    data: key.startsWith("cases:")
      ? { items: [{ id: "CASE_1" }] }
      : {
          id: "CASE_1",
          hire_id: "HIRE_1",
          state: view.state,
          kind: "INVESTIGATION",
          message: "Check the location.",
          model_calls: 1,
          tool_calls: 0,
          questions: [],
          proposals: [],
          evidence: [],
          timeline: [],
        },
  }),
}));

it.each(["ESCALATED", "RESOLVED"])(
  "offers a manual handoff for an escalated case, not a resolved one (%s)",
  (state) => {
    view.state = state;
    const html = renderToStaticMarkup(
      <InvestigationTab hireId="HIRE_1" onChanged={() => {}} />,
    );
    if (state === "ESCALATED") {
      expect(html).toContain("Continue without AI");
      expect(html).toContain("Your saved work is kept.");
      expect(html).toContain('href="#/hires/HIRE_1/plan"');
      expect(html).toContain("usual review and");
    } else {
      expect(html).not.toContain("Continue without AI");
    }
  },
);
