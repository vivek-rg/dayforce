import { useState } from "react";
import { api } from "../../shared/api";
import type { TemporaryPassword } from "../../shared/api-types";
import { formatDateTime, humanize } from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import {
  ActionError,
  Badge,
  DataState,
  DataTable,
  Facts,
  Notice,
  PageHeader,
  Section,
} from "../../shared/ui";

function PasswordResets() {
  const resets = useResource("password-resets", (signal) =>
    api.passwordResets(signal),
  );
  const [issued, setIssued] = useState<TemporaryPassword | null>(null);
  const action = useAction();

  async function issue(resetId: string) {
    const result = await action.run(() => api.issueTemporaryPassword(resetId));
    if (result.ok) {
      setIssued(result.value);
      resets.reload();
    }
  }

  return (
    <Section
      title="Password reset requests"
      description="Give the person their temporary password directly. It is shown only once."
    >
      {issued && (
        <Notice
          tone="info"
          title={`Temporary password for ${issued.display_name}`}
        >
          <span className="mono">{issued.temporary_password}</span>
        </Notice>
      )}
      <ActionError error={action.error} onReload={resets.reload} />
      <DataState
        resource={resets}
        isEmpty={(data) => data.items.length === 0}
        empty="No password reset requests."
      >
        {(data) => (
          <DataTable
            caption="Password reset requests"
            rowKey={(item) => item.id}
            rows={data.items}
            columns={[
              { header: "Name", render: (item) => item.display_name },
              { header: "Email", render: (item) => item.email ?? "None" },
              { header: "Role", render: (item) => humanize(item.role) },
              {
                header: "Requested",
                render: (item) => formatDateTime(item.created_at),
              },
              {
                header: "Action",
                render: (item) => (
                  <button
                    type="button"
                    className="btn btn-sm"
                    disabled={action.pending}
                    onClick={() => void issue(item.id)}
                  >
                    Create temporary password
                  </button>
                ),
              },
            ]}
          />
        )}
      </DataState>
    </Section>
  );
}

export function SettingsPage() {
  const health = useResource("health-ai", (signal) => api.aiHealth(signal));
  return (
    <>
      <PageHeader
        title="Settings"
        description="Model status and password reset requests."
      />
      <Section title="Model status">
        <DataState resource={health}>
          {(data) => (
            <>
              <Facts
                items={[
                  ["Provider", <span className="mono">{data.provider}</span>],
                  ["Model", <span className="mono">{data.model}</span>],
                  [
                    "Available",
                    <Badge tone={data.available ? "ok" : "muted"}>
                      {data.available ? "Yes" : "No"}
                    </Badge>,
                  ],
                  [
                    "Type",
                    data.is_stub ? (
                      <Badge tone="warn">Offline rules, not AI</Badge>
                    ) : data.available ? (
                      "Configured model"
                    ) : (
                      "None configured"
                    ),
                  ],
                ]}
              />
              <Notice tone="info">{data.detail}</Notice>
            </>
          )}
        </DataState>
      </Section>
      <PasswordResets />
    </>
  );
}
