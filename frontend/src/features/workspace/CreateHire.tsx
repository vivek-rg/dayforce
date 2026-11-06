import { type FormEvent, useState } from "react";
import { ApiError, api } from "../../shared/api";
import type { HireCreate, Reference } from "../../shared/api-types";
import { humanize, locationLabel } from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import { hireHref } from "../../shared/routes";
import {
  ActionError,
  DataState,
  Facts,
  Field,
  Notice,
  PageHeader,
} from "../../shared/ui";

type Draft = {
  display_name: string;
  worker_type: HireCreate["worker_type"];
  role: HireCreate["role"];
  location_id: HireCreate["location_id"] | "";
  work_mode: HireCreate["work_mode"];
  start_date: string;
  manager_user_id: string;
  employee_user_id: string;
  department_id: string;
  designation: string;
  work_email: string;
  personal_email: string;
  phone: string;
};

const EMPTY: Draft = {
  display_name: "",
  worker_type: "employee",
  role: "engineer",
  location_id: "",
  work_mode: "office",
  start_date: "",
  manager_user_id: "",
  employee_user_id: "",
  department_id: "",
  designation: "",
  work_email: "",
  personal_email: "",
  phone: "",
};

const STEPS = ["Identity", "Role and location", "Manager and login", "Review"];

function stepErrors(
  step: number,
  draft: Draft,
): Partial<Record<keyof Draft, string>> {
  const errors: Partial<Record<keyof Draft, string>> = {};
  if (step === 0) {
    if (!draft.display_name.trim()) errors.display_name = "Enter a name.";
    if (!draft.work_email.trim()) errors.work_email = "Enter a work email.";
  }
  if (step === 1) {
    if (!draft.designation.trim()) errors.designation = "Enter a designation.";
    if (!draft.department_id) errors.department_id = "Choose a department.";
    if (!draft.location_id) errors.location_id = "Choose a location.";
    if (!draft.start_date) errors.start_date = "Choose a start date.";
  }
  if (step === 2 && !draft.manager_user_id) {
    errors.manager_user_id = "Choose a manager.";
  }
  return errors;
}

function toBody(draft: Draft): HireCreate {
  return {
    display_name: draft.display_name.trim(),
    worker_type: draft.worker_type,
    role: draft.role,
    location_id: draft.location_id as HireCreate["location_id"],
    work_mode: draft.work_mode,
    start_date: draft.start_date,
    manager_user_id: draft.manager_user_id,
    employee_user_id: draft.employee_user_id || null,
    department_id: draft.department_id,
    designation: draft.designation.trim(),
    work_email: draft.work_email.trim(),
    personal_email: draft.personal_email.trim() || null,
    phone: draft.phone.trim() || null,
  };
}

function Wizard({ reference }: { reference: Reference }) {
  const [step, setStep] = useState(0);
  const [draft, setDraft] = useState<Draft>(EMPTY);
  const [showErrors, setShowErrors] = useState(false);
  const action = useAction();
  const errors = stepErrors(step, draft);

  function set<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  function next(event: FormEvent) {
    event.preventDefault();
    if (Object.keys(errors).length > 0) {
      setShowErrors(true);
      return;
    }
    setShowErrors(false);
    setStep((value) => value + 1);
  }

  async function submit() {
    const result = await action.run(() => api.createHire(toBody(draft)));
    if (result.ok) window.location.hash = hireHref(result.value.id);
  }

  const err = (key: keyof Draft) => (showErrors ? errors[key] : undefined);
  const nameOf = (userId: string) =>
    reference.users.find((user) => user.id === userId)?.display_name ?? userId;
  const managers = reference.users.filter((user) => user.role === "MANAGER");
  const department = reference.departments.find(
    (item) => item.id === draft.department_id,
  );
  const policyBlocked =
    action.error instanceof ApiError &&
    action.error.code === "POLICY_REVIEW_REQUIRED";

  return (
    <div className="wizard">
      <ol className="wizard-steps">
        {STEPS.map((label, index) => (
          <li
            key={label}
            className="wizard-step"
            data-state={
              index === step ? "current" : index < step ? "done" : "todo"
            }
            aria-current={index === step ? "step" : undefined}
          >
            <span className="num">{index + 1}</span> {label}
          </li>
        ))}
      </ol>
      <form className="form-panel" onSubmit={next} noValidate>
        {step === 0 && (
          <div className="form-grid">
            <Field label="Full name" error={err("display_name")}>
              <input
                className="input"
                value={draft.display_name}
                onChange={(event) => set("display_name", event.target.value)}
                autoComplete="off"
              />
            </Field>
            <Field label="Worker type">
              <select
                className="input"
                value={draft.worker_type}
                onChange={(event) =>
                  set("worker_type", event.target.value as Draft["worker_type"])
                }
              >
                <option value="employee">Employee</option>
                <option value="contractor">Contractor</option>
              </select>
            </Field>
            <Field label="Work email" error={err("work_email")}>
              <input
                className="input"
                type="email"
                value={draft.work_email}
                onChange={(event) => set("work_email", event.target.value)}
                autoComplete="off"
              />
            </Field>
            <Field label="Personal email (optional)">
              <input
                className="input"
                type="email"
                value={draft.personal_email}
                onChange={(event) => set("personal_email", event.target.value)}
                autoComplete="off"
              />
            </Field>
            <Field label="Phone (optional)">
              <input
                className="input"
                type="tel"
                value={draft.phone}
                onChange={(event) => set("phone", event.target.value)}
                autoComplete="off"
              />
            </Field>
          </div>
        )}
        {step === 1 && (
          <div className="form-grid">
            <Field label="Role">
              <select
                className="input"
                value={draft.role}
                onChange={(event) =>
                  set("role", event.target.value as Draft["role"])
                }
              >
                <option value="engineer">Engineer</option>
                <option value="operations_associate">
                  Operations associate
                </option>
                <option value="sales_associate">Sales associate</option>
              </select>
            </Field>
            <Field label="Designation" error={err("designation")}>
              <input
                className="input"
                value={draft.designation}
                onChange={(event) => set("designation", event.target.value)}
              />
            </Field>
            <Field label="Department" error={err("department_id")}>
              <select
                className="input"
                value={draft.department_id}
                onChange={(event) => set("department_id", event.target.value)}
              >
                <option value="">Choose a department</option>
                {reference.departments.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Location" error={err("location_id")}>
              <select
                className="input"
                value={draft.location_id}
                onChange={(event) =>
                  set("location_id", event.target.value as Draft["location_id"])
                }
              >
                <option value="">Choose a location</option>
                {reference.locations.map((item) => (
                  <option key={item} value={item}>
                    {locationLabel(item)} ({item})
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Work mode">
              <select
                className="input"
                value={draft.work_mode}
                onChange={(event) =>
                  set("work_mode", event.target.value as Draft["work_mode"])
                }
              >
                <option value="office">Office</option>
                <option value="remote">Remote</option>
              </select>
            </Field>
            <Field label="Start date" error={err("start_date")}>
              <input
                className="input"
                type="date"
                value={draft.start_date}
                onChange={(event) => set("start_date", event.target.value)}
              />
            </Field>
          </div>
        )}
        {step === 2 && (
          <div className="form-grid">
            <Field label="Manager" error={err("manager_user_id")}>
              <select
                className="input"
                value={draft.manager_user_id}
                onChange={(event) => set("manager_user_id", event.target.value)}
              >
                <option value="">Choose a manager</option>
                {managers.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.display_name}
                  </option>
                ))}
              </select>
            </Field>
            <Field
              label="Employee login (optional)"
              hint="Links this hire to an unused employee account."
            >
              <select
                className="input"
                value={draft.employee_user_id}
                onChange={(event) =>
                  set("employee_user_id", event.target.value)
                }
              >
                <option value="">No login yet</option>
                {reference.available_employee_user_ids.map((userId) => (
                  <option key={userId} value={userId}>
                    {nameOf(userId)} ({userId})
                  </option>
                ))}
              </select>
            </Field>
          </div>
        )}
        {step === 3 && (
          <>
            <Facts
              items={[
                ["Name", draft.display_name],
                ["Worker type", humanize(draft.worker_type)],
                ["Work email", draft.work_email],
                ["Personal email", draft.personal_email || "Not given"],
                ["Phone", draft.phone || "Not given"],
                ["Role", humanize(draft.role)],
                ["Designation", draft.designation],
                ["Department", department?.name ?? draft.department_id],
                ["Location", locationLabel(draft.location_id)],
                ["Work mode", humanize(draft.work_mode)],
                ["Start date", draft.start_date],
                ["Manager", nameOf(draft.manager_user_id)],
                [
                  "Employee login",
                  draft.employee_user_id
                    ? nameOf(draft.employee_user_id)
                    : "No login yet",
                ],
              ]}
            />
            <p className="muted small">
              Creating the employee generates the onboarding plan from the
              approved policy.
            </p>
            {policyBlocked ? (
              <Notice
                tone="bad"
                title="HR policy review is required. No employee was created."
              >
                <p>{action.error?.message}</p>
                <p>
                  The approved policy does not cover this profile, so no plan
                  can be generated. Go back and correct the profile, or have the
                  policy reviewed.
                </p>
              </Notice>
            ) : (
              <ActionError error={action.error} />
            )}
          </>
        )}
        <div className="form-actions">
          {step > 0 && (
            <button
              type="button"
              className="btn"
              onClick={() => {
                action.clear();
                setStep((value) => value - 1);
              }}
            >
              Back
            </button>
          )}
          {step < 3 ? (
            <button type="submit" className="btn btn-primary">
              Continue
            </button>
          ) : (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => void submit()}
              disabled={action.pending}
            >
              {action.pending ? "Creating" : "Create employee and plan"}
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

export function CreateHirePage() {
  const reference = useResource("reference", (signal) => api.reference(signal));
  return (
    <>
      <PageHeader
        title="New employee"
        description="Four steps. Nothing is saved until the last one."
      />
      <DataState resource={reference}>
        {(data) => <Wizard reference={data} />}
      </DataState>
    </>
  );
}
