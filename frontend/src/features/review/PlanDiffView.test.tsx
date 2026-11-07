import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import type { PlanDiff } from "../../shared/api-types";
import { PlanDiffView } from "./PlanDiffView";

const original: PlanDiff = {
  create: [],
  cancel: [],
  preserve: [],
  invalidate_checks: [],
};

it("shows restored tasks separately and still renders older saved previews", () => {
  const html = renderToStaticMarkup(
    <PlanDiffView diff={{ ...original, restore: ["TASK_TO_RESTORE"] }} />,
  );
  expect(html).toContain("Tasks to restore");
  expect(html).toContain("TASK_TO_RESTORE");
  expect(() =>
    renderToStaticMarkup(<PlanDiffView diff={original} />),
  ).not.toThrow();
});
