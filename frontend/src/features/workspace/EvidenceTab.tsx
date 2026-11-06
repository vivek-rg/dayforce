import { api } from "../../shared/api";
import type { Plan } from "../../shared/api-types";
import { type Resource, useAction } from "../../shared/hooks";
import { useUser } from "../../shared/session-context";
import { ActionError, DataState, EvidenceCard } from "../../shared/ui";

export function EvidenceTab({
  hireId,
  plan,
}: {
  hireId: string;
  plan: Resource<Plan>;
}) {
  const user = useUser();
  const action = useAction();

  async function runChecks() {
    const result = await action.run(() => api.runChecks(hireId));
    if (result.ok) plan.reload();
  }

  return (
    <DataState
      resource={plan}
      isEmpty={(data) => data.checks.length === 0}
      empty="No evidence is recorded yet for the checks your role can see."
    >
      {(data) => (
        <>
          <p className="muted small">
            These are independent checks against recorded facts. Task completion
            does not change them. Missing evidence is Unknown, and a real
            mismatch is Blocked.
          </p>
          {user.role !== "EMPLOYEE" && (
            <div className="form-actions">
              <button
                type="button"
                className="btn"
                disabled={action.pending}
                onClick={() => void runChecks()}
              >
                {action.pending ? "Checking" : "Run checks now"}
              </button>
            </div>
          )}
          <ActionError error={action.error} onReload={plan.reload} />
          <div className="evidence-list">
            {data.checks.map((evidence) => (
              <EvidenceCard key={evidence.id} evidence={evidence} />
            ))}
          </div>
        </>
      )}
    </DataState>
  );
}
