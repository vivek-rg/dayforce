import type { Plan } from "../../shared/api-types";
import type { Resource } from "../../shared/hooks";
import { DataState, EvidenceCard } from "../../shared/ui";

export function EvidenceTab({ plan }: { plan: Resource<Plan> }) {
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
