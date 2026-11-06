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

type Course = SourceOf<"training">;

function CompleteControl({
  record,
  onChanged,
}: {
  record: Course;
  onChanged: () => void;
}) {
  const action = useAction();
  const hireId = record.hire_id;

  async function complete() {
    if (!hireId) return;
    const result = await action.run(() =>
      api.writeSource(hireId, record.id, {
        expected_version: record.version,
        payload: { ...record.payload, state: "COMPLETED" },
      }),
    );
    if (result.ok) onChanged();
  }

  return (
    <div className="row-action">
      <button
        type="button"
        className="btn btn-sm"
        disabled={action.pending}
        onClick={() => void complete()}
      >
        Mark completed
      </button>
      <ActionError error={action.error} onReload={onChanged} />
    </div>
  );
}

export function TrainingPage() {
  const user = useUser();
  const canEdit = user.role === "TRAINING";
  const records = useResource("sources:training", (signal) =>
    api.sources("training", signal),
  );
  return (
    <>
      <PageHeader
        title="Training"
        description={
          canEdit
            ? "This records completion. It does not measure competence."
            : "Read-only for your role."
        }
      />
      <DataState
        resource={records}
        isEmpty={(data) => data.length === 0}
        empty="No training records are in your scope."
      >
        {(data) => (
          <DataTable
            caption="Training records"
            rowKey={(item) => item.id}
            rows={data}
            minWidth={560}
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
                header: "Course",
                render: (item) => humanize(item.payload.course_id),
              },
              {
                header: "State",
                render: (item) => (
                  <Badge
                    tone={item.payload.state === "COMPLETED" ? "ok" : "warn"}
                  >
                    {humanize(item.payload.state)}
                  </Badge>
                ),
              },
              ...(canEdit
                ? [
                    {
                      header: "Action",
                      render: (item: Course) =>
                        item.payload.state === "ASSIGNED" ? (
                          <CompleteControl
                            record={item}
                            onChanged={records.reload}
                          />
                        ) : null,
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
