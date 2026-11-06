import { useState } from "react";
import { type SourceOf, api } from "../../shared/api";
import { humanize } from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import { hireHref } from "../../shared/routes";
import { useUser } from "../../shared/session-context";
import {
  ActionError,
  Badge,
  DataState,
  DataTable,
  PageHeader,
} from "../../shared/ui";

type Benefit = SourceOf<"benefits">;
type State = Benefit["payload"]["state"];
const STATES: State[] = ["NOT_INVITED", "INVITED", "ENROLLED", "DECLINED"];

function StateSelector({
  record,
  onChanged,
}: {
  record: Benefit;
  onChanged: () => void;
}) {
  const [state, setState] = useState<State>(record.payload.state);
  const action = useAction();
  const hireId = record.hire_id;

  async function save() {
    if (!hireId) return;
    const result = await action.run(() =>
      api.writeSource(hireId, record.id, {
        expected_version: record.version,
        payload: { ...record.payload, state },
      }),
    );
    if (result.ok) onChanged();
  }

  return (
    <div className="row-action">
      <span className="inline-controls">
        <label className="sr-only" htmlFor={`benefit-${record.id}`}>
          Benefits state for {record.hire_name}
        </label>
        <select
          id={`benefit-${record.id}`}
          className="input input-sm"
          value={state}
          onChange={(event) => setState(event.target.value as State)}
        >
          {STATES.map((value) => (
            <option key={value} value={value}>
              {humanize(value)}
            </option>
          ))}
        </select>
        <button
          type="button"
          className="btn btn-sm"
          disabled={action.pending || state === record.payload.state}
          onClick={() => void save()}
        >
          Save
        </button>
      </span>
      <ActionError error={action.error} onReload={onChanged} />
    </div>
  );
}

export function BenefitsPage() {
  const user = useUser();
  const canEdit = user.role === "BENEFITS";
  const records = useResource("sources:benefits", (signal) =>
    api.sources("benefits", signal),
  );
  return (
    <>
      <PageHeader
        title="Benefits"
        description={
          canEdit
            ? "Record each employee's enrolment state."
            : "Read-only for your role."
        }
      />
      <DataState
        resource={records}
        isEmpty={(data) => data.length === 0}
        empty="No benefits records are in your scope."
      >
        {(data) => (
          <DataTable
            caption="Benefits records"
            rowKey={(item) => `${item.id}:${item.version}`}
            rows={data}
            minWidth={520}
            columns={[
              {
                header: "Employee",
                render: (item) =>
                  item.hire_id ? (
                    <a href={hireHref(item.hire_id)}>
                      {item.hire_name ?? item.hire_id}
                    </a>
                  ) : (
                    "None"
                  ),
              },
              {
                header: "Current state",
                render: (item) => (
                  <Badge
                    tone={
                      item.payload.state === "ENROLLED" ||
                      item.payload.state === "DECLINED"
                        ? "ok"
                        : "warn"
                    }
                  >
                    {humanize(item.payload.state)}
                  </Badge>
                ),
              },
              ...(canEdit
                ? [
                    {
                      header: "Change",
                      render: (item: Benefit) => (
                        <StateSelector
                          record={item}
                          onChanged={records.reload}
                        />
                      ),
                    },
                  ]
                : []),
            ]}
          />
        )}
      </DataState>
    </>
  );
}
