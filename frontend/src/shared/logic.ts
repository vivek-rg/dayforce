import type { CheckResult, Document, Hire, Proposal, Task } from "./api-types";
import { type Tone, displayStatusTone, humanize } from "./format";

export type Verdict =
  | "PROVEN"
  | "GAP"
  | "CONTRADICTED"
  | "NO_CHECK"
  | "PROOF_FIRST"
  | "OPEN"
  | "CANCELLED";

export type ClaimProofView = {
  claim: string;
  claimTone: Tone;
  proof: string;
  result: CheckResult | "NOT_CHECKED" | "NO_CHECK";
  verdict: Verdict;
  flag: string | null;
};

type ClaimInput = Pick<
  Task,
  "work_state" | "display_status" | "evidence_result" | "check_type"
>;

/** The product's central idea as data: what was claimed, what is proven, and how they relate. */
export function claimProof(task: ClaimInput): ClaimProofView {
  const result: ClaimProofView["result"] =
    task.evidence_result ?? (task.check_type ? "NOT_CHECKED" : "NO_CHECK");
  const proof = {
    VERIFIED: "Verified",
    BLOCKED: "Blocked",
    UNKNOWN: "Unknown",
    NOT_APPLICABLE: "Not applicable",
    NOT_CHECKED: "Not checked",
    NO_CHECK: "No check",
  }[result];
  const claimed = task.work_state === "COMPLETED";
  let verdict: Verdict = "OPEN";
  let flag: string | null = null;
  if (task.work_state === "CANCELLED") {
    verdict = "CANCELLED";
  } else if (claimed && result === "VERIFIED") {
    verdict = "PROVEN";
    flag = "Claim proven";
  } else if (claimed && result === "BLOCKED") {
    verdict = "CONTRADICTED";
    flag = "Evidence contradicts the claim";
  } else if (claimed && (result === "UNKNOWN" || result === "NOT_CHECKED")) {
    verdict = "GAP";
    flag = "Claim without proof";
  } else if (claimed) {
    verdict = "NO_CHECK";
    flag = "Claim only, no independent check";
  } else if (result === "VERIFIED") {
    verdict = "PROOF_FIRST";
    flag = "Proof exists, task still open";
  }
  return {
    claim: humanize(task.display_status),
    claimTone: displayStatusTone(task.display_status),
    proof,
    result,
    verdict,
    flag,
  };
}

export type PlanLedger = {
  total: number;
  claimed: number;
  proven: number;
  gaps: number;
  noCheck: number;
};

export function planLedger(tasks: Task[]): PlanLedger {
  const ledger: PlanLedger = {
    total: 0,
    claimed: 0,
    proven: 0,
    gaps: 0,
    noCheck: 0,
  };
  for (const task of tasks) {
    if (task.work_state === "CANCELLED") continue;
    ledger.total += 1;
    if (task.work_state !== "COMPLETED") continue;
    ledger.claimed += 1;
    const { verdict } = claimProof(task);
    if (verdict === "PROVEN") ledger.proven += 1;
    else if (verdict === "GAP" || verdict === "CONTRADICTED") ledger.gaps += 1;
    else ledger.noCheck += 1;
  }
  return ledger;
}

export function groupByCategory(tasks: Task[]): [string, Task[]][] {
  const groups = new Map<string, Task[]>();
  for (const task of tasks) {
    const group = groups.get(task.category);
    if (group) group.push(task);
    else groups.set(task.category, [task]);
  }
  return [...groups.entries()];
}

function dayNumber(iso: string): number {
  const [year, month, day] = iso.slice(0, 10).split("-").map(Number);
  return Date.UTC(year, month - 1, day) / 86_400_000;
}

/** Whole calendar days from the start date. Negative means before joining. */
export function dayOffset(start: string, date: string): number {
  return dayNumber(date) - dayNumber(start);
}

export function offsetLabel(offset: number): string {
  if (offset === 0) return "Day 0";
  return offset < 0 ? `D−${-offset}` : `D+${offset}`;
}

export function addDays(iso: string, days: number): string {
  return new Date((dayNumber(iso) + days) * 86_400_000)
    .toISOString()
    .slice(0, 10);
}

export function todayIso(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

export type TimelineEntry =
  | {
      kind: "milestone";
      id: string;
      date: string;
      offset: number;
      label: string;
    }
  | { kind: "task"; id: string; date: string; offset: number; task: Task };

/** Tasks by due date with calendar milestones. On the same day a milestone comes first. */
export function buildTimeline(
  tasks: Task[],
  startDate: string,
  today: string,
): TimelineEntry[] {
  const milestones: [string, string, string][] = [
    ["joining", startDate, "Joining date"],
    ["first-week", addDays(startDate, 7), "End of first week"],
    ["today", today, "Today"],
  ];
  const entries: TimelineEntry[] = [
    ...milestones.map(
      ([id, date, label]): TimelineEntry => ({
        kind: "milestone",
        id,
        date,
        offset: dayOffset(startDate, date),
        label,
      }),
    ),
    ...tasks.map(
      (task): TimelineEntry => ({
        kind: "task",
        id: task.id,
        date: task.due_date,
        offset: dayOffset(startDate, task.due_date),
        task,
      }),
    ),
  ];
  return entries.sort(
    (a, b) =>
      a.offset - b.offset ||
      Number(a.kind === "task") - Number(b.kind === "task"),
  );
}

export function canStart(task: Task, userId: string): boolean {
  return task.owner_user_id === userId && task.work_state === "PENDING";
}

export function canComplete(task: Task, userId: string): boolean {
  return (
    task.owner_user_id === userId &&
    (task.work_state === "PENDING" || task.work_state === "IN_PROGRESS")
  );
}

export function canReassign(task: Task): boolean {
  return task.work_state !== "COMPLETED" && task.work_state !== "CANCELLED";
}

/** Names what a task waits for. Prerequisites outside the viewer's scope stay unnamed. */
export function dependencyNote(task: Task, tasks: Task[]): string | null {
  if (task.depends_on.length === 0) return null;
  const known = task.depends_on
    .map((dep) => tasks.find((item) => item.id === dep))
    .filter((item): item is Task => item !== undefined);
  const open = known.filter(
    (item) =>
      item.work_state !== "COMPLETED" && item.work_state !== "CANCELLED",
  );
  if (task.work_state === "WAITING_DEPENDENCY") {
    const names = open.map((item) => item.title).join(", ");
    return names ? `Waiting for: ${names}` : "Waiting for an earlier task";
  }
  const names = known.map((item) => item.title).join(", ");
  return names ? `Follows: ${names}` : "Follows an earlier task";
}

export type HireFilter = { search: string; status: string; location: string };

export function filterHires(hires: Hire[], filter: HireFilter): Hire[] {
  const query = filter.search.trim().toLowerCase();
  return hires.filter(
    (hire) =>
      (!filter.status || hire.onboarding_status === filter.status) &&
      (!filter.location || hire.location_id === filter.location) &&
      (!query ||
        [
          hire.display_name,
          hire.employee_code,
          hire.designation,
          hire.work_email,
        ]
          .join(" ")
          .toLowerCase()
          .includes(query)),
  );
}

export type TaskFilter = { search: string; status: string; category: string };

export function filterTasks(tasks: Task[], filter: TaskFilter): Task[] {
  const query = filter.search.trim().toLowerCase();
  return tasks.filter(
    (task) =>
      (!filter.status || task.display_status === filter.status) &&
      (!filter.category || task.category === filter.category) &&
      (!query ||
        `${task.title} ${task.hire_name}`.toLowerCase().includes(query)),
  );
}

export const MAX_UPLOAD_BYTES = 5 * 1024 * 1024;
const ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".txt"];
export const UPLOAD_ACCEPT = ALLOWED_EXTENSIONS.join(",");

/** A friendly early check. The server still validates type, contents and size. */
export function uploadProblem(file: {
  name: string;
  size: number;
}): string | null {
  const name = file.name.toLowerCase();
  if (!ALLOWED_EXTENSIONS.some((extension) => name.endsWith(extension))) {
    return "Allowed types are PDF, PNG, JPEG and TXT.";
  }
  if (file.size === 0) return "The file is empty.";
  if (file.size > MAX_UPLOAD_BYTES) return "Files must be 5 MB or smaller.";
  return null;
}

export function currentDocument(
  documents: Document[],
  category: Document["category"],
): Document | undefined {
  return documents.find(
    (item) => item.category === category && item.state !== "SUPERSEDED",
  );
}

export function latestReviewReason(document: Document): string | null {
  const reason = document.reviews.at(-1)?.reason.trim();
  return reason ? reason : null;
}

export type NextStep =
  | { kind: "resubmit"; document: Document }
  | { kind: "task"; task: Task }
  | { kind: "waiting"; task: Task }
  | { kind: "done" };

export function nextStep(
  tasks: Task[],
  documents: Document[],
  userId: string,
): NextStep {
  const sentBack = documents.find(
    (item) =>
      item.state === "REJECTED" || item.state === "RESUBMISSION_REQUESTED",
  );
  if (sentBack) return { kind: "resubmit", document: sentBack };
  const mine = tasks
    .filter((task) => task.owner_user_id === userId)
    .sort((a, b) => a.due_date.localeCompare(b.due_date));
  const active =
    mine.find((task) => task.work_state === "IN_PROGRESS") ??
    mine.find((task) => task.work_state === "PENDING");
  if (active) return { kind: "task", task: active };
  const waiting = mine.find((task) => task.work_state === "WAITING_DEPENDENCY");
  return waiting ? { kind: "waiting", task: waiting } : { kind: "done" };
}

export type ProposalStage =
  | "AWAITING_DECISION"
  | "EXPIRED"
  | "REJECTED"
  | "EXECUTING"
  | "SUCCEEDED"
  | "FAILED"
  | "UNKNOWN";

/** Approval queues work; it is not success. Only a final action state ends the wait. */
export function proposalStage(
  proposal: Pick<Proposal, "decision" | "action_state" | "expires_at">,
  now: number,
): ProposalStage {
  if (proposal.decision === "REJECT") return "REJECTED";
  if (proposal.decision === "APPROVE") {
    const state = proposal.action_state;
    if (state === "SUCCEEDED" || state === "FAILED" || state === "UNKNOWN") {
      return state;
    }
    return "EXECUTING";
  }
  return new Date(proposal.expires_at).getTime() <= now
    ? "EXPIRED"
    : "AWAITING_DECISION";
}
