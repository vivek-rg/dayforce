import { useState } from "react";
import { type SourceOf, api } from "../../shared/api";
import type { Hire, Reference } from "../../shared/api-types";
import {
  formatDate,
  humanize,
  locationLabel,
  onboardingTone,
} from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import { hireHref } from "../../shared/routes";
import { useUser } from "../../shared/session-context";
import {
  ActionError,
  Badge,
  DataState,
  DataTable,
  EmptyState,
  Field,
  Notice,
  PageHeader,
  Progress,
  Section,
} from "../../shared/ui";
import { TaskRow } from "../my-work/TaskRow";

type PlanRecord = SourceOf<"manager">;

function PlanForm({
  hire,
  record,
  reference,
  onSaved,
}: {
  hire: Hire;
  record: PlanRecord | undefined;
  reference: Reference;
  onSaved: () => void;
}) {
  const [buddy, setBuddy] = useState(record?.payload.buddy_user_id ?? "");
  const [plan, setPlan] = useState(record?.payload.first_week_plan ?? "");
  const [saved, setSaved] = useState(false);
  const action = useAction();
  const buddies = reference.users.filter(
    (user) => user.id !== hire.employee_user_id,
  );

  async function save() {
    setSaved(false);
    const result = await action.run(() =>
      api.writeSource(hire.id, record?.id ?? `manager_${hire.id}_main`, {
        expected_version: record?.version ?? 0,
        payload: {
          category: "manager",
          buddy_user_id: buddy,
          first_week_plan: plan.trim(),
        },
      }),
    );
    if (result.ok) {
      setSaved(true);
      onSaved();
    }
  }

  return (
    <div className="stack">
      <div className="form-grid">
        <Field label="Buddy">
          <select
            className="input"
            value={buddy}
            onChange={(event) => setBuddy(event.target.value)}
          >
            <option value="">Choose a buddy</option>
            {buddies.map((user) => (
              <option key={user.id} value={user.id}>
                {user.display_name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="First-week plan">
          <textarea
            className="input"
            rows={3}
            value={plan}
            onChange={(event) => setPlan(event.target.value)}
          />
        </Field>
      </div>
      <ActionError error={action.error} onReload={onSaved} />
      {saved && (
        <Notice tone="ok" title="Recorded">
          The buddy and first-week plan are now evidence for this hire.
        </Notice>
      )}
      <div className="form-actions">
        <button
          type="button"
          className="btn btn-primary"
          disabled={!buddy || !plan.trim() || action.pending}
          onClick={() => void save()}
        >
          {action.pending ? "Saving" : "Record buddy and plan"}
        </button>
      </div>
    </div>
  );
}

function PlanSection({ hires }: { hires: Hire[] }) {
  const [hireId, setHireId] = useState("");
  const reference = useResource("reference", (signal) => api.reference(signal));
  const records = useResource("sources:manager", (signal) =>
    api.sources("manager", signal),
  );
  const hire = hires.find((item) => item.id === hireId);
  return (
    <Section
      title="Buddy and first-week plan"
      description="Recording this is what produces the evidence for the manager plan check."
    >
      <div className="form-panel">
        <Field label="Employee">
          <select
            className="input"
            value={hireId}
            onChange={(event) => setHireId(event.target.value)}
          >
            <option value="">Choose an employee</option>
            {hires.map((item) => (
              <option key={item.id} value={item.id}>
                {item.display_name}
              </option>
            ))}
          </select>
        </Field>
        {hire && (
          <DataState resource={records} rows={3}>
            {(items) =>
              reference.data ? (
                <PlanForm
                  key={hire.id}
                  hire={hire}
                  record={items.find((item) => item.hire_id === hire.id)}
                  reference={reference.data}
                  onSaved={records.reload}
                />
              ) : (
                <DataState resource={reference} rows={3}>
                  {() => null}
                </DataState>
              )
            }
          </DataState>
        )}
      </div>
    </Section>
  );
}

export function ManagerPage() {
  const user = useUser();
  const hires = useResource("hires", (signal) => api.hires(signal));
  const tasks = useResource("my-work", (signal) => api.myWork(signal));
  return (
    <>
      <PageHeader
        title="My team"
        description="Your hires, your tasks, and the plan you owe each new starter."
      />
      <Section title="My hires">
        <DataState
          resource={hires}
          isEmpty={(data) => data.items.length === 0}
          empty="No hires are assigned to you."
        >
          {(data) => (
            <DataTable
              caption="My hires"
              rowKey={(hire) => hire.id}
              rows={data.items}
              minWidth={700}
              columns={[
                {
                  header: "Employee",
                  render: (hire) => (
                    <a href={hireHref(hire.id)}>{hire.display_name}</a>
                  ),
                },
                {
                  header: "Location",
                  render: (hire) => locationLabel(hire.location_id),
                },
                {
                  header: "Start date",
                  render: (hire) => (
                    <span className="num">{formatDate(hire.start_date)}</span>
                  ),
                },
                {
                  header: "Status",
                  render: (hire) => (
                    <Badge tone={onboardingTone(hire.onboarding_status)}>
                      {humanize(hire.onboarding_status)}
                    </Badge>
                  ),
                },
                {
                  header: "Tasks claimed",
                  width: "170px",
                  render: (hire) => (
                    <Progress
                      value={hire.tasks_completed}
                      max={hire.tasks_total}
                      label={`${hire.tasks_completed}/${hire.tasks_total}`}
                    />
                  ),
                },
              ]}
            />
          )}
        </DataState>
      </Section>
      {hires.data && (
        <PlanSection
          hires={hires.data.items.filter(
            (hire) => hire.manager_user_id === user.id,
          )}
        />
      )}
      <Section
        title="My tasks"
        description="Completing a task records a claim. Proof comes from evidence."
      >
        <DataState resource={tasks} rows={3}>
          {(data) =>
            data.items.length === 0 ? (
              <EmptyState>No tasks are assigned to you.</EmptyState>
            ) : (
              <ul className="task-list">
                {data.items.map((task) => (
                  <TaskRow
                    key={task.id}
                    task={task}
                    plan={data.items}
                    onChanged={() => {
                      tasks.reload();
                      hires.reload();
                    }}
                    showHire
                  />
                ))}
              </ul>
            )
          }
        </DataState>
      </Section>
    </>
  );
}
