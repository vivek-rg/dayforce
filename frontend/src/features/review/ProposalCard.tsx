import { useState } from "react";
import { ApiError, api } from "../../shared/api";
import type { Proposal } from "../../shared/api-types";
import {
  type Tone,
  formatDateTime,
  humanize,
  locationLabel,
} from "../../shared/format";
import { useAction, useInterval, useResource } from "../../shared/hooks";
import { type ProposalStage, proposalStage } from "../../shared/logic";
import { hireHref } from "../../shared/routes";
import { useUser } from "../../shared/session-context";
import { ActionError, Badge, Facts, Field, Notice } from "../../shared/ui";
import { PlanDiffView } from "./PlanDiffView";

const STAGE_TONE: Record<ProposalStage, Tone> = {
  AWAITING_DECISION: "info",
  EXPIRED: "muted",
  REJECTED: "muted",
  EXECUTING: "warn",
  SUCCEEDED: "ok",
  FAILED: "bad",
  UNKNOWN: "warn",
};
const POLL_MS = 2000;
const MAX_POLLS = 60;

function describe(proposal: Proposal): string {
  const { payload } = proposal;
  return payload.action_type === "CHANGE_WORK_LOCATION"
    ? `Change work location to ${locationLabel(payload.location_id)}`
    : `Reserve equipment ${payload.equipment_record_id}`;
}

function Outcome({
  proposal,
  stage,
  stalled,
}: {
  proposal: Proposal;
  stage: ProposalStage;
  stalled: boolean;
}) {
  switch (stage) {
    case "REJECTED":
      return (
        <Notice tone="muted" title="Rejected">
          No action ran.
        </Notice>
      );
    case "EXECUTING":
      return (
        <Notice tone="warn" title="Approved. Pending execution.">
          Approval queues the work. It is not a result. The stored outcome
          appears here once it has been read back.
          {stalled &&
            " This is taking longer than usual, so check that the worker is running."}
        </Notice>
      );
    case "SUCCEEDED":
      return (
        <Notice tone="ok" title="Action finished">
          <p className="outcome">
            {proposal.outcome ?? "No outcome text was returned."}
          </p>
        </Notice>
      );
    case "FAILED":
      return (
        <Notice tone="bad" title="Action failed. Nothing is reported as done.">
          {proposal.outcome && <p className="outcome">{proposal.outcome}</p>}
          <p>Ask for a fresh proposal if this is still needed.</p>
        </Notice>
      );
    case "UNKNOWN":
      return (
        <Notice tone="warn" title="Outcome unknown">
          {proposal.outcome && <p className="outcome">{proposal.outcome}</p>}
          <p>
            Do not retry. Check the record first, because the action may have
            taken effect.
          </p>
        </Notice>
      );
    default:
      return null;
  }
}

export function ProposalCard({
  proposal: initial,
  onChanged,
}: {
  proposal: Proposal;
  onChanged: () => void;
}) {
  const user = useUser();
  const [note, setNote] = useState("");
  const [polls, setPolls] = useState(0);
  const action = useAction();
  const fresh = useResource(`proposal:${initial.id}`, (signal) =>
    api.proposal(initial.id, signal),
  );
  // Plan titles make a diff readable. If the plan cannot be read, the raw IDs still show.
  const plan = useResource(
    initial.plan_diff ? `plan:${initial.hire_id}` : null,
    (signal) => api.plan(initial.hire_id, signal),
  );
  const proposal = fresh.data ?? initial;
  // eslint-disable-next-line react-hooks/purity -- expiry is compared to the time of this render.
  const stage = proposalStage(proposal, Date.now());
  const isReviewer = user.role === proposal.reviewer_role;
  const polling = stage === "EXECUTING" && polls < MAX_POLLS;

  useInterval(
    () => {
      setPolls((value) => value + 1);
      fresh.reload();
    },
    polling ? POLL_MS : null,
  );

  async function decide(decision: "APPROVE" | "REJECT") {
    const result = await action.run(() =>
      api.decide(proposal.id, { decision, note: note.trim() }),
    );
    if (result.ok) {
      setPolls(0);
      fresh.reload();
      onChanged();
    }
  }

  const conflict =
    action.error instanceof ApiError && action.error.status === 409;

  return (
    <article className="proposal">
      <header className="proposal-head">
        <div>
          <h3>{describe(proposal)}</h3>
          <p className="muted small">
            <a href={hireHref(proposal.hire_id)}>{proposal.hire_name}</a> ·{" "}
            <span className="mono">{proposal.id}</span>
          </p>
        </div>
        <Badge tone={STAGE_TONE[stage]}>{humanize(stage)}</Badge>
      </header>
      <Facts
        items={[
          ["Reviewer role", proposal.reviewer_role],
          [
            "Expires",
            <time className="num" dateTime={proposal.expires_at}>
              {formatDateTime(proposal.expires_at)}
            </time>,
          ],
          ["Case", <span className="mono">{proposal.case_id}</span>],
        ]}
      />
      <div className="proposal-grid">
        <div>
          <h4 className="eyebrow">Exact payload</h4>
          <pre className="code">
            {JSON.stringify(proposal.payload, null, 2)}
          </pre>
        </div>
        <div>
          <h4 className="eyebrow">Expected versions</h4>
          <pre className="code">
            {JSON.stringify(proposal.expected_versions, null, 2)}
          </pre>
        </div>
        <div>
          <h4 className="eyebrow">Evidence IDs</h4>
          {proposal.evidence_ids.length ? (
            <ul className="plain-list mono">
              {proposal.evidence_ids.map((id) => (
                <li key={id}>{id}</li>
              ))}
            </ul>
          ) : (
            <p className="muted small">
              None cited. This came from a manual request.
            </p>
          )}
        </div>
      </div>
      {proposal.plan_diff && (
        <div>
          <h4 className="eyebrow">Plan impact</h4>
          <PlanDiffView
            diff={proposal.plan_diff}
            tasks={plan.data?.tasks}
            checks={plan.data?.checks}
          />
        </div>
      )}
      <Outcome
        proposal={proposal}
        stage={stage}
        stalled={!polling && stage === "EXECUTING"}
      />
      {stage === "EXPIRED" && (
        <Notice tone="muted" title="This proposal has expired">
          It can no longer be approved. Ask for a new one if this is still
          needed.
        </Notice>
      )}
      {conflict ? (
        <Notice
          tone="bad"
          title="A fresh review is needed"
          action={
            <button
              type="button"
              className="btn btn-sm"
              onClick={() => {
                action.clear();
                fresh.reload();
                onChanged();
              }}
            >
              Reload
            </button>
          }
        >
          <p>{action.error?.message}</p>
          <p>
            No decision was applied, and nothing is retried automatically. If
            this proposal is out of date, reject it and ask for a new one.
          </p>
        </Notice>
      ) : (
        <ActionError error={action.error} />
      )}
      {isReviewer && stage === "AWAITING_DECISION" && !conflict && (
        <div className="decision">
          <Field label="Note (optional)">
            <input
              className="input"
              value={note}
              onChange={(event) => setNote(event.target.value)}
            />
          </Field>
          <div className="decision-buttons">
            <button
              type="button"
              className="btn btn-primary"
              disabled={action.pending}
              onClick={() => void decide("APPROVE")}
            >
              Approve
            </button>
            <button
              type="button"
              className="btn"
              disabled={action.pending}
              onClick={() => void decide("REJECT")}
            >
              Reject
            </button>
          </div>
        </div>
      )}
      {!isReviewer && stage === "AWAITING_DECISION" && (
        <p className="muted small">
          Waiting for {proposal.reviewer_role} to review.
        </p>
      )}
    </article>
  );
}
