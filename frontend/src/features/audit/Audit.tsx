import { useState } from "react";
import { api } from "../../shared/api";
import type { AuditEvent } from "../../shared/api-types";
import { formatDateTime, humanize } from "../../shared/format";
import { useResource } from "../../shared/hooks";
import {
  Badge,
  DataState,
  DataTable,
  EmptyState,
  Field,
  PageHeader,
  Section,
  Stat,
  Tabs,
} from "../../shared/ui";

function filterEvents(events: AuditEvent[], search: string) {
  const query = search.trim().toLowerCase();
  if (!query) return events;
  return events.filter((event) =>
    [
      event.event_type,
      event.summary,
      event.hire_id ?? "",
      event.actor_user_id ?? "",
    ]
      .join(" ")
      .toLowerCase()
      .includes(query),
  );
}

function AuditEvents() {
  const events = useResource("audit-events", (signal) =>
    api.auditEvents(signal),
  );
  const [search, setSearch] = useState("");
  return (
    <DataState
      resource={events}
      isEmpty={(data) => data.items.length === 0}
      empty="No audit events yet."
    >
      {(data) => {
        const rows = filterEvents(data.items, search);
        return (
          <>
            <div className="filters">
              <Field label="Search events">
                <input
                  className="input"
                  type="search"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </Field>
            </div>
            {rows.length === 0 ? (
              <EmptyState>No events match this search.</EmptyState>
            ) : (
              <DataTable
                caption="Audit events"
                rowKey={(item) => item.id}
                rows={rows}
                minWidth={820}
                columns={[
                  {
                    header: "Time",
                    width: "130px",
                    render: (item) => (
                      <span className="num">
                        {formatDateTime(item.created_at)}
                      </span>
                    ),
                  },
                  {
                    header: "Event",
                    render: (item) => humanize(item.event_type),
                  },
                  { header: "Summary", render: (item) => item.summary },
                  {
                    header: "Actor",
                    render: (item) => (
                      <span className="mono">
                        {item.actor_user_id ?? "System"}
                      </span>
                    ),
                  },
                  {
                    header: "Hire",
                    render: (item) => (
                      <span className="mono">{item.hire_id ?? "None"}</span>
                    ),
                  },
                ]}
              />
            )}
          </>
        );
      }}
    </DataState>
  );
}

function AiRuns() {
  const runs = useResource("ai-runs", (signal) => api.aiRuns(signal));
  return (
    <DataState
      resource={runs}
      isEmpty={(data) => data.items.length === 0}
      empty="No AI runs yet."
    >
      {(data) => (
        <DataTable
          caption="AI runs"
          rowKey={(item) => item.id}
          rows={data.items}
          minWidth={980}
          columns={[
            {
              header: "Time",
              render: (item) => (
                <span className="num">{formatDateTime(item.created_at)}</span>
              ),
            },
            {
              header: "Operation",
              render: (item) => <span className="mono">{item.operation}</span>,
            },
            {
              header: "Prompt",
              numeric: true,
              render: (item) => (
                <span className="num">v{item.prompt_version}</span>
              ),
            },
            { header: "Provider", render: (item) => item.provider },
            {
              header: "Model",
              render: (item) => <span className="mono">{item.model}</span>,
            },
            {
              header: "Status",
              render: (item) => (
                <Badge
                  tone={
                    item.status === "VALIDATED"
                      ? "ok"
                      : item.status === "ABSTAINED"
                        ? "muted"
                        : "bad"
                  }
                >
                  {humanize(item.status)}
                </Badge>
              ),
            },
            {
              header: "Validation",
              render: (item) => (
                <>
                  {item.validation_result}
                  {item.failure_reason && (
                    <span className="cell-sub mono">{item.failure_reason}</span>
                  )}
                </>
              ),
            },
            {
              header: "Attempts",
              numeric: true,
              render: (item) => <span className="num">{item.attempts}</span>,
            },
            {
              header: "Latency",
              numeric: true,
              render: (item) => (
                <span className="num">{item.latency_ms} ms</span>
              ),
            },
          ]}
        />
      )}
    </DataState>
  );
}

function Reliability() {
  const metrics = useResource("metrics", (signal) => api.metrics(signal));
  return (
    <DataState resource={metrics}>
      {(data) => (
        <>
          <div className="stats-line">
            <Stat label="API requests" value={data.api_requests} />
            <Stat label="p50" value={`${data.api_p50_ms} ms`} />
            <Stat label="p95" value={`${data.api_p95_ms} ms`} />
            <Stat label="API errors" value={data.api_errors} />
            <Stat
              label="Retrieval average"
              value={
                data.retrieval_average_ms === null ||
                data.retrieval_average_ms === undefined
                  ? "No data"
                  : `${data.retrieval_average_ms} ms`
              }
            />
            <Stat label="Failed work items" value={data.work_failed} />
            <Stat label="Failed actions" value={data.actions_failed} />
            <Stat
              label="Task completion rate"
              value={`${Math.round(data.task_completion_rate * 100)}%`}
            />
          </div>
          <Section title="AI operations">
            {data.operations.length === 0 ? (
              <EmptyState>No AI operations yet.</EmptyState>
            ) : (
              <DataTable
                caption="AI operations"
                rowKey={(item) => item.operation}
                rows={data.operations}
                minWidth={760}
                columns={[
                  {
                    header: "Operation",
                    render: (item) => (
                      <span className="mono">{item.operation}</span>
                    ),
                  },
                  ...(
                    [
                      ["Runs", "runs"],
                      ["Validated", "validated"],
                      ["Abstained", "abstained"],
                      ["Rejected", "rejected"],
                      ["Unavailable", "unavailable"],
                      ["Tokens", "total_tokens"],
                    ] as const
                  ).map(([header, key]) => ({
                    header,
                    numeric: true,
                    render: (item: (typeof data.operations)[number]) => (
                      <span className="num">{item[key]}</span>
                    ),
                  })),
                  {
                    header: "Average latency",
                    numeric: true,
                    render: (item) => (
                      <span className="num">
                        {Math.round(item.average_latency_ms)} ms
                      </span>
                    ),
                  },
                ]}
              />
            )}
          </Section>
        </>
      )}
    </DataState>
  );
}

export function AuditPage() {
  const [tab, setTab] = useState("events");
  return (
    <>
      <PageHeader
        title="Audit and reliability"
        description="What happened, who did it, and how the AI harness behaved."
      />
      <Tabs
        label="Audit views"
        active={tab}
        onSelect={setTab}
        tabs={[
          { id: "events", label: "Audit events" },
          { id: "runs", label: "AI runs" },
          { id: "metrics", label: "Reliability" },
        ]}
      />
      <div className="tab-panel" role="tabpanel" aria-label="Selected tab">
        {tab === "events" && <AuditEvents />}
        {tab === "runs" && <AiRuns />}
        {tab === "metrics" && <Reliability />}
      </div>
    </>
  );
}
