import { describe, expect, it } from "vitest";
import type { Document, Task } from "./api-types";
import {
  buildTimeline,
  canComplete,
  canStart,
  claimProof,
  currentDocument,
  dayOffset,
  dependencyNote,
  filterTasks,
  nextStep,
  offsetLabel,
  planLedger,
  proposalStage,
  uploadProblem,
} from "./logic";
import {
  checkLabel,
  factValue,
  formatDate,
  humanize,
  reasonText,
} from "./format";
import { canOpen, homeHref, navFor, parseHash } from "./routes";

function task(overrides: Partial<Task> = {}): Task {
  return {
    id: "T1",
    hire_id: "H1",
    hire_name: "Priya",
    category: "equipment",
    title: "Hand over laptop",
    description: "",
    owner_user_id: "U1",
    owner_name: "Imran",
    due_date: "2026-11-10",
    priority: "HIGH",
    critical: true,
    work_state: "PENDING",
    display_status: "NOT_STARTED",
    check_type: "device_handover_recorded",
    evidence_result: "UNKNOWN",
    version: 1,
    depends_on: [],
    ...overrides,
  };
}

const complete = {
  work_state: "COMPLETED",
  display_status: "COMPLETED",
} as const;

function doc(overrides: Partial<Document> = {}): Document {
  return {
    id: "D1",
    hire_id: "H1",
    hire_name: "Priya",
    category: "tax",
    state: "SUBMITTED",
    original_name: "tax.txt",
    mime_type: "text/plain",
    size_bytes: 10,
    text_available: true,
    version: 1,
    created_at: "2026-11-01T00:00:00Z",
    reviews: [],
    ...overrides,
  };
}

describe("claimProof", () => {
  it("never treats a completed task with unknown evidence as proven", () => {
    const view = claimProof(task(complete));
    expect(view.claim).toBe("Completed");
    expect(view.proof).toBe("Unknown");
    expect(view.verdict).toBe("GAP");
    expect(view.flag).toBe("Claim without proof");
  });

  it("marks completed plus verified as proven", () => {
    expect(
      claimProof(task({ ...complete, evidence_result: "VERIFIED" })).verdict,
    ).toBe("PROVEN");
  });

  it("flags evidence that contradicts a claim", () => {
    expect(
      claimProof(task({ ...complete, evidence_result: "BLOCKED" })).verdict,
    ).toBe("CONTRADICTED");
  });

  it("separates a task with no check from a missing receipt", () => {
    const noCheck = claimProof(
      task({ ...complete, check_type: null, evidence_result: null }),
    );
    expect(noCheck.verdict).toBe("NO_CHECK");
    expect(noCheck.proof).toBe("No check");
    const unchecked = claimProof(task({ ...complete, evidence_result: null }));
    expect(unchecked.verdict).toBe("GAP");
    expect(unchecked.proof).toBe("Not checked");
  });

  it("shows proof that arrived before the claim", () => {
    expect(claimProof(task({ evidence_result: "VERIFIED" })).verdict).toBe(
      "PROOF_FIRST",
    );
  });

  it("does not flag open or cancelled work", () => {
    expect(claimProof(task()).flag).toBeNull();
    expect(claimProof(task({ work_state: "CANCELLED" })).verdict).toBe(
      "CANCELLED",
    );
  });
});

describe("planLedger", () => {
  it("counts claims, proof and gaps, ignoring cancelled tasks", () => {
    expect(
      planLedger([
        task(),
        task({ ...complete, evidence_result: "VERIFIED" }),
        task(complete),
        task({ ...complete, evidence_result: "BLOCKED" }),
        task({ ...complete, check_type: null, evidence_result: null }),
        task({ work_state: "CANCELLED" }),
      ]),
    ).toEqual({ total: 5, claimed: 4, proven: 1, gaps: 2, noCheck: 1 });
  });
});

describe("timeline", () => {
  it("computes calendar offsets across a month boundary", () => {
    expect(dayOffset("2026-11-01", "2026-10-25")).toBe(-7);
    expect(dayOffset("2026-11-01", "2026-11-01")).toBe(0);
    expect(offsetLabel(-7)).toBe("D−7");
    expect(offsetLabel(0)).toBe("Day 0");
    expect(offsetLabel(5)).toBe("D+5");
  });

  it("orders by offset and puts a milestone before same-day tasks", () => {
    const entries = buildTimeline(
      [
        task({ id: "late", due_date: "2026-11-11" }),
        task({ id: "joining-day", due_date: "2026-11-10" }),
        task({ id: "early", due_date: "2026-11-03" }),
      ],
      "2026-11-10",
      "2026-11-05",
    );
    expect(entries.map((entry) => entry.id)).toEqual([
      "early",
      "today",
      "joining",
      "joining-day",
      "late",
      "first-week",
    ]);
  });
});

describe("task permissions and notes", () => {
  it("offers start and complete only to the owner in the right state", () => {
    expect(canStart(task(), "U1")).toBe(true);
    expect(canStart(task(), "U2")).toBe(false);
    expect(canStart(task({ work_state: "IN_PROGRESS" }), "U1")).toBe(false);
    expect(canComplete(task({ work_state: "IN_PROGRESS" }), "U1")).toBe(true);
    expect(canComplete(task({ work_state: "WAITING_DEPENDENCY" }), "U1")).toBe(
      false,
    );
    expect(canComplete(task(complete), "U1")).toBe(false);
  });

  it("names open prerequisites and hides those out of scope", () => {
    const first = task({ id: "A", title: "Reserve device" });
    const waiting = task({
      id: "B",
      work_state: "WAITING_DEPENDENCY",
      depends_on: ["A"],
    });
    expect(dependencyNote(waiting, [first, waiting])).toBe(
      "Waiting for: Reserve device",
    );
    expect(dependencyNote(waiting, [waiting])).toBe(
      "Waiting for an earlier task",
    );
    expect(dependencyNote(task(), [])).toBeNull();
  });

  it("filters tasks by status, category and text", () => {
    const tasks = [
      task({ id: "A", display_status: "OVERDUE" }),
      task({ id: "B", category: "payroll", title: "Payroll setup" }),
    ];
    const ids = (filter: Parameters<typeof filterTasks>[1]) =>
      filterTasks(tasks, filter).map((item) => item.id);
    expect(ids({ search: "", status: "OVERDUE", category: "" })).toEqual(["A"]);
    expect(ids({ search: "", status: "", category: "payroll" })).toEqual(["B"]);
    expect(ids({ search: "PAYROLL", status: "", category: "" })).toEqual(["B"]);
  });
});

describe("proposalStage", () => {
  const future = "2030-01-01T00:00:00Z";
  const now = new Date("2026-11-06T00:00:00Z").getTime();

  it("never treats approval as success", () => {
    const stage = (
      action_state:
        | "PENDING"
        | "RUNNING"
        | "SUCCEEDED"
        | "FAILED"
        | "UNKNOWN"
        | null,
    ) =>
      proposalStage(
        { decision: "APPROVE", action_state, expires_at: future },
        now,
      );
    expect(stage(null)).toBe("EXECUTING");
    expect(stage("PENDING")).toBe("EXECUTING");
    expect(stage("RUNNING")).toBe("EXECUTING");
    expect(stage("SUCCEEDED")).toBe("SUCCEEDED");
    expect(stage("FAILED")).toBe("FAILED");
    expect(stage("UNKNOWN")).toBe("UNKNOWN");
  });

  it("recognises rejected, waiting and expired proposals", () => {
    expect(proposalStage({ decision: "REJECT", expires_at: future }, now)).toBe(
      "REJECTED",
    );
    expect(proposalStage({ expires_at: future }, now)).toBe(
      "AWAITING_DECISION",
    );
    expect(proposalStage({ expires_at: "2020-01-01T00:00:00Z" }, now)).toBe(
      "EXPIRED",
    );
  });
});

describe("portal logic", () => {
  it("checks uploads against the documented limits", () => {
    expect(uploadProblem({ name: "a.PDF", size: 100 })).toBeNull();
    expect(uploadProblem({ name: "a.exe", size: 100 })).toMatch(
      /Allowed types/,
    );
    expect(uploadProblem({ name: "a.txt", size: 0 })).toMatch(/empty/);
    expect(uploadProblem({ name: "a.txt", size: 5 * 1024 * 1024 + 1 })).toMatch(
      /5 MB/,
    );
  });

  it("ignores superseded documents", () => {
    const items = [
      doc({ id: "old", state: "SUPERSEDED" }),
      doc({ id: "new", state: "REJECTED" }),
    ];
    expect(currentDocument(items, "tax")?.id).toBe("new");
    expect(currentDocument(items, "education")).toBeUndefined();
  });

  it("puts a returned document first, then active work, then waiting", () => {
    const pending = task({ id: "P", due_date: "2026-11-02" });
    const active = task({
      id: "A",
      due_date: "2026-11-09",
      work_state: "IN_PROGRESS",
    });
    const waiting = task({ id: "W", work_state: "WAITING_DEPENDENCY" });
    const sentBack = doc({ state: "RESUBMISSION_REQUESTED" });
    expect(nextStep([pending], [sentBack], "U1").kind).toBe("resubmit");
    expect(nextStep([pending, active], [], "U1")).toMatchObject({
      task: { id: "A" },
    });
    expect(nextStep([waiting], [], "U1").kind).toBe("waiting");
    expect(nextStep([task(complete)], [], "U1").kind).toBe("done");
    expect(nextStep([pending], [], "someone-else").kind).toBe("done");
  });
});

describe("formatting", () => {
  it("makes codes readable, with a fallback for unknown ones", () => {
    expect(reasonText("RESERVED_COLLECTION_PENDING")).toMatch(/not a delivery/);
    expect(reasonText("SOME_NEW_REASON")).toBe("Some new reason");
    expect(checkLabel("payroll_setup_confirmed")).toBe(
      "Payroll setup confirmed",
    );
    expect(humanize("WAITING_HUMAN")).toBe("Waiting human");
  });

  it("does not shift a date-only value across time zones", () => {
    expect(formatDate("2026-11-06")).toBe("06 Nov 2026");
  });

  it("renders observed facts as text", () => {
    expect(factValue(null)).toBe("None");
    expect(factValue(true)).toBe("Yes");
    expect(factValue(3)).toBe("3");
  });
});

describe("routes", () => {
  it("parses hash routes", () => {
    expect(parseHash("")).toEqual({ name: "home" });
    expect(parseHash("#/")).toEqual({ name: "home" });
    expect(parseHash("#/hires")).toEqual({ name: "directory" });
    expect(parseHash("#/hires/new")).toEqual({ name: "new-hire" });
    expect(parseHash("#/hires/H%201")).toEqual({
      name: "hire",
      hireId: "H 1",
      tab: "plan",
    });
    expect(parseHash("#/hires/H1/evidence")).toEqual({
      name: "hire",
      hireId: "H1",
      tab: "evidence",
    });
    expect(parseHash("#/hires/H1/nope")).toEqual({ name: "not-found" });
    expect(parseHash("#/constructor")).toEqual({ name: "not-found" });
  });

  it("keeps screens to the right roles", () => {
    expect(canOpen("HR", { name: "dashboard" })).toBe(true);
    expect(canOpen("EMPLOYEE", { name: "dashboard" })).toBe(false);
    expect(canOpen("IT", { name: "review" })).toBe(true);
    expect(canOpen("MANAGER", { name: "review" })).toBe(false);
    expect(canOpen("EMPLOYEE", { name: "assistant" })).toBe(true);
  });

  it("lands every role on a page it may open, and only links to those", () => {
    const roles = [
      "HR",
      "IT",
      "PAYROLL",
      "BENEFITS",
      "TRAINING",
      "MANAGER",
      "EMPLOYEE",
    ] as const;
    expect(homeHref("EMPLOYEE")).toBe("#/portal");
    for (const role of roles) {
      expect(canOpen(role, parseHash(homeHref(role)))).toBe(true);
      for (const group of navFor(role)) {
        for (const item of group.items) {
          expect(canOpen(role, parseHash(item.href))).toBe(true);
        }
      }
    }
  });
});
