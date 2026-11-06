import { useState } from "react";
import { api } from "../../shared/api";
import type { Hire, Plan, Proposal } from "../../shared/api-types";
import { locationLabel } from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import { ActionError, Field, Notice } from "../../shared/ui";
import { PlanDiffView } from "../review/PlanDiffView";

export function LocationChange({
  hire,
  plan,
  onChanged,
}: {
  hire: Hire;
  plan?: Plan;
  onChanged: () => void;
}) {
  const reference = useResource("reference", (signal) => api.reference(signal));
  const [location, setLocation] = useState<Hire["location_id"] | "">("");
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const action = useAction();
  const options = (reference.data?.locations ?? []).filter(
    (item) => item !== hire.location_id,
  );

  async function submit() {
    if (!location) return;
    const result = await action.run(() =>
      api.changePreview(hire.id, {
        location_id: location,
        expected_profile_version: hire.profile_version,
      }),
    );
    if (result.ok) {
      setProposal(result.value);
      onChanged();
    }
  }

  return (
    <section className="form-panel" aria-label="Propose location change">
      <h2 className="panel-title">Propose location change</h2>
      <p className="muted small">
        This creates a reviewable proposal. The profile does not change until a
        reviewer approves it. Current location:{" "}
        {locationLabel(hire.location_id)} ({hire.location_id}).
      </p>
      {proposal ? (
        <>
          <Notice
            tone="info"
            title="Proposal created. Nothing has changed yet."
          >
            It is waiting for review in the <a href="#/review">Review inbox</a>.
          </Notice>
          {proposal.plan_diff && (
            <PlanDiffView
              diff={proposal.plan_diff}
              tasks={plan?.tasks}
              checks={plan?.checks}
            />
          )}
        </>
      ) : (
        <div className="inline-form">
          <Field label="New location">
            <select
              className="input"
              value={location}
              onChange={(event) =>
                setLocation(event.target.value as Hire["location_id"] | "")
              }
            >
              <option value="">Choose a location</option>
              {options.map((item) => (
                <option key={item} value={item}>
                  {locationLabel(item)} ({item})
                </option>
              ))}
            </select>
          </Field>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!location || action.pending}
            onClick={() => void submit()}
          >
            {action.pending ? "Creating proposal" : "Preview plan impact"}
          </button>
        </div>
      )}
      <ActionError
        error={action.error ?? reference.error ?? null}
        onReload={onChanged}
      />
    </section>
  );
}
