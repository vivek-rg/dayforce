import { api } from "../../shared/api";
import { useResource } from "../../shared/hooks";
import {
  Badge,
  DataState,
  Facts,
  Notice,
  PageHeader,
  Section,
} from "../../shared/ui";

export function SettingsPage() {
  const health = useResource("health-ai", (signal) => api.aiHealth(signal));
  return (
    <>
      <PageHeader
        title="Settings"
        description="Read-only. The model is configured on the server."
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
    </>
  );
}
