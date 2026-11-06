import { type SourceOf, api } from "../../shared/api";
import { useAction, useResource } from "../../shared/hooks";
import { hireHref } from "../../shared/routes";
import { useUser } from "../../shared/session-context";
import {
  ActionError,
  DataState,
  DataTable,
  Notice,
  PageHeader,
} from "../../shared/ui";

type Record = SourceOf<"payroll">;
type Flag =
  | "bank_submitted"
  | "tax_submitted"
  | "profile_created"
  | "setup_confirmed";

const FLAGS: [Flag, string][] = [
  ["bank_submitted", "Bank form submitted"],
  ["tax_submitted", "Tax form submitted"],
  ["profile_created", "Profile created"],
  ["setup_confirmed", "Setup confirmed"],
];

function Toggles({
  record,
  canEdit,
  onChanged,
}: {
  record: Record;
  canEdit: boolean;
  onChanged: () => void;
}) {
  const action = useAction();
  const hireId = record.hire_id;

  async function toggle(flag: Flag, value: boolean) {
    if (!hireId) return;
    const payload = { ...record.payload, [flag]: value };
    // The server refuses a confirmed setup without a profile, so keep the two consistent.
    if (flag === "profile_created" && !value) payload.setup_confirmed = false;
    const result = await action.run(() =>
      api.writeSource(hireId, record.id, {
        expected_version: record.version,
        payload,
      }),
    );
    if (result.ok) onChanged();
  }

  return (
    <>
      <div className="toggles">
        {FLAGS.map(([flag, label]) => (
          <label key={flag} className="toggle">
            <input
              type="checkbox"
              checked={Boolean(record.payload[flag])}
              disabled={
                !canEdit ||
                action.pending ||
                (flag === "setup_confirmed" && !record.payload.profile_created)
              }
              onChange={(event) => void toggle(flag, event.target.checked)}
            />
            {label}
          </label>
        ))}
      </div>
      <ActionError error={action.error} onReload={onChanged} />
    </>
  );
}

export function PayrollPage() {
  const user = useUser();
  const canEdit = user.role === "PAYROLL";
  const records = useResource("sources:payroll", (signal) =>
    api.sources("payroll", signal),
  );
  return (
    <>
      <PageHeader
        title="Payroll"
        description={
          canEdit
            ? "Track setup for each employee."
            : "Read-only for your role."
        }
      />
      <Notice tone="info">
        Only submission status is tracked. No account numbers are stored here.
      </Notice>
      <DataState
        resource={records}
        isEmpty={(data) => data.length === 0}
        empty="No payroll records are in your scope."
      >
        {(data) => (
          <DataTable
            caption="Payroll records"
            rowKey={(item) => item.id}
            rows={data}
            minWidth={560}
            columns={[
              {
                header: "Employee",
                width: "200px",
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
                header: "Setup",
                render: (item) => (
                  <Toggles
                    record={item}
                    canEdit={canEdit}
                    onChanged={records.reload}
                  />
                ),
              },
            ]}
          />
        )}
      </DataState>
    </>
  );
}
