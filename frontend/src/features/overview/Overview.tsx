import { useState } from "react";
import { api } from "../../shared/api";
import type { Overview } from "../../shared/api-types";
import {
  formatDate,
  formatDateTime,
  humanize,
  locationLabel,
} from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import { hireHref } from "../../shared/routes";
import {
  ActionError,
  BarList,
  DataState,
  DataTable,
  EmptyState,
  Notice,
  PageHeader,
  Section,
  Stat,
} from "../../shared/ui";

function Exceptions({ data }: { data: Overview }) {
  return (
    <section className="exceptions" aria-label="Exceptions">
      <a className="exception exception-claims" href="#/insights">
        <span className="exception-value num">{data.claims_without_proof}</span>
        <span className="exception-label">Claims without proof</span>
        <span className="exception-note">
          Tasks marked complete where evidence is unknown or blocked.
        </span>
      </a>
      <a className="exception" href="#/hires">
        <span className="exception-value num">{data.tasks_overdue}</span>
        <span className="exception-label">Overdue tasks</span>
        <span className="exception-note">
          Past their due date and still open.
        </span>
      </a>
      <a className="exception" href="#/documents">
        <span className="exception-value num">{data.documents_awaiting}</span>
        <span className="exception-label">Documents awaiting review</span>
        <span className="exception-note">Only a person can verify these.</span>
      </a>
    </section>
  );
}

export function OverviewPage() {
  const overview = useResource("overview", (signal) => api.overview(signal));
  const sweep = useAction();
  const [created, setCreated] = useState<number | null>(null);

  async function runSweep() {
    setCreated(null);
    const result = await sweep.run(() => api.sweep());
    if (result.ok) {
      setCreated(result.value.notifications_created);
      overview.reload();
    }
  }

  return (
    <>
      <PageHeader
        title="Onboarding overview"
        description="Exceptions first. Completed work is shown as a claim until evidence proves it."
        actions={
          <button
            type="button"
            className="btn"
            onClick={() => void runSweep()}
            disabled={sweep.pending}
          >
            {sweep.pending ? "Running check" : "Run escalation check"}
          </button>
        }
      />
      <ActionError error={sweep.error} />
      {created !== null && (
        <Notice tone="info">
          Escalation check finished. {created}{" "}
          {created === 1 ? "notification" : "notifications"} created.
        </Notice>
      )}
      <DataState resource={overview} rows={8}>
        {(data) => (
          <>
            <Exceptions data={data} />
            <div className="stats-line">
              <Stat label="In progress" value={data.onboarding_in_progress} />
              <Stat label="Completed" value={data.onboarding_completed} />
              <Stat label="Total employees" value={data.total_employees} />
              <Stat label="Tasks open" value={data.tasks_pending} />
              <Stat
                label="Average days to complete"
                value={data.average_completion_days ?? "No data"}
              />
            </div>
            <div className="grid-3">
              <Section title="By department">
                {data.by_department.length ? (
                  <BarList items={data.by_department} />
                ) : (
                  <EmptyState>No employees yet.</EmptyState>
                )}
              </Section>
              <Section title="By location">
                {data.by_location.length ? (
                  <BarList
                    items={data.by_location.map((item) => ({
                      label: locationLabel(item.label),
                      count: item.count,
                    }))}
                  />
                ) : (
                  <EmptyState>No employees yet.</EmptyState>
                )}
              </Section>
              <Section
                title="Equipment states"
                description="Reserved is not handed over."
              >
                {data.equipment.length ? (
                  <BarList
                    items={data.equipment.map((item) => ({
                      label: humanize(item.label),
                      count: item.count,
                    }))}
                  />
                ) : (
                  <EmptyState>No equipment records.</EmptyState>
                )}
              </Section>
            </div>
            <div className="grid-2">
              <Section title="Upcoming joiners">
                {data.upcoming.length ? (
                  <DataTable
                    caption="Upcoming joiners"
                    minWidth={360}
                    rowKey={(row) => row.hire_id}
                    rows={data.upcoming}
                    columns={[
                      {
                        header: "Name",
                        render: (row) => (
                          <a href={hireHref(row.hire_id)}>{row.display_name}</a>
                        ),
                      },
                      {
                        header: "Start date",
                        render: (row) => (
                          <span className="num">
                            {formatDate(row.start_date)}
                          </span>
                        ),
                      },
                      {
                        header: "Location",
                        render: (row) => locationLabel(row.location_id),
                      },
                    ]}
                  />
                ) : (
                  <EmptyState>No upcoming joiners.</EmptyState>
                )}
              </Section>
              <Section title="Recent activity">
                {data.recent.length ? (
                  <ol className="log">
                    {data.recent.map((event) => (
                      <li key={event.id} className="log-row">
                        <time
                          className="log-time num"
                          dateTime={event.created_at}
                        >
                          {formatDateTime(event.created_at)}
                        </time>
                        <span className="log-text">
                          <span className="log-type">
                            {humanize(event.event_type)}
                          </span>
                          {event.summary}
                        </span>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <EmptyState>No activity yet.</EmptyState>
                )}
              </Section>
            </div>
          </>
        )}
      </DataState>
    </>
  );
}
