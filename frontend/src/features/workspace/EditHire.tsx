import { useState } from "react";
import { api } from "../../shared/api";
import type { Hire } from "../../shared/api-types";
import { useAction, useResource } from "../../shared/hooks";
import { ActionError, Field } from "../../shared/ui";

const STATUSES: Hire["employment_status"][] = [
  "PRE_JOINING",
  "ACTIVE",
  "WITHDRAWN",
];
const STATUS_LABELS: Record<Hire["employment_status"], string> = {
  PRE_JOINING: "Pre joining",
  ACTIVE: "Active",
  WITHDRAWN: "Withdrawn",
};

export function EditHire({
  hire,
  onSaved,
}: {
  hire: Hire;
  onSaved: () => void;
}) {
  const reference = useResource("reference", (signal) => api.reference(signal));
  const [designation, setDesignation] = useState(hire.designation);
  const [workEmail, setWorkEmail] = useState(hire.work_email);
  const [personalEmail, setPersonalEmail] = useState(hire.personal_email ?? "");
  const [phone, setPhone] = useState(hire.phone ?? "");
  const [department, setDepartment] = useState(hire.department_id);
  const [status, setStatus] = useState(hire.employment_status);
  const action = useAction();
  const valid = designation.trim() !== "" && workEmail.trim() !== "";

  async function save() {
    const result = await action.run(() =>
      api.patchHire(hire.id, {
        expected_profile_version: hire.profile_version,
        designation: designation.trim(),
        work_email: workEmail.trim(),
        personal_email: personalEmail.trim() || null,
        phone: phone.trim() || null,
        department_id: department,
        employment_status: status,
      }),
    );
    if (result.ok) onSaved();
  }

  return (
    <section className="form-panel" aria-label="Edit employee details">
      <h2 className="panel-title">Edit details</h2>
      <p className="muted small">
        Location changes need a reviewed proposal, so they are not edited here.
      </p>
      <div className="form-grid">
        <Field label="Designation">
          <input
            className="input"
            value={designation}
            maxLength={200}
            onChange={(event) => setDesignation(event.target.value)}
          />
        </Field>
        <Field label="Department">
          <select
            className="input"
            value={department}
            onChange={(event) => setDepartment(event.target.value)}
          >
            {(reference.data?.departments ?? []).map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
            {!reference.data && <option value={department}>Loading</option>}
          </select>
        </Field>
        <Field label="Work email">
          <input
            className="input"
            type="email"
            value={workEmail}
            maxLength={200}
            onChange={(event) => setWorkEmail(event.target.value)}
          />
        </Field>
        <Field label="Personal email (optional)">
          <input
            className="input"
            type="email"
            value={personalEmail}
            maxLength={200}
            onChange={(event) => setPersonalEmail(event.target.value)}
          />
        </Field>
        <Field label="Phone (optional)">
          <input
            className="input"
            type="tel"
            value={phone}
            maxLength={200}
            onChange={(event) => setPhone(event.target.value)}
          />
        </Field>
        <Field label="Employment status">
          <select
            className="input"
            value={status}
            onChange={(event) =>
              setStatus(event.target.value as Hire["employment_status"])
            }
          >
            {STATUSES.map((item) => (
              <option key={item} value={item}>
                {STATUS_LABELS[item]}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <ActionError error={action.error} onReload={onSaved} />
      <div className="form-actions">
        <button
          type="button"
          className="btn btn-primary"
          disabled={!valid || action.pending}
          onClick={() => void save()}
        >
          {action.pending ? "Saving" : "Save details"}
        </button>
      </div>
    </section>
  );
}
