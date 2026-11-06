import { useState } from "react";
import { api } from "../../shared/api";
import {
  formatDate,
  humanize,
  locationLabel,
  onboardingTone,
} from "../../shared/format";
import { useResource } from "../../shared/hooks";
import { filterHires } from "../../shared/logic";
import { hireHref } from "../../shared/routes";
import { useUser } from "../../shared/session-context";
import {
  Badge,
  DataState,
  DataTable,
  EmptyState,
  Field,
  PageHeader,
  Progress,
} from "../../shared/ui";

const STATUSES = ["NOT_STARTED", "IN_PROGRESS", "BLOCKED", "COMPLETED"];

export function DirectoryPage() {
  const user = useUser();
  const hires = useResource("hires", (signal) => api.hires(signal));
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [location, setLocation] = useState("");

  return (
    <>
      <PageHeader
        title="Employees"
        description="Progress counts claims. Open a profile to see what evidence proves."
        actions={
          user.role === "HR" && (
            <a className="btn btn-primary" href="#/hires/new">
              New employee
            </a>
          )
        }
      />
      <DataState
        resource={hires}
        isEmpty={(data) => data.items.length === 0}
        empty="No employees are in your scope yet."
      >
        {(data) => {
          const rows = filterHires(data.items, { search, status, location });
          const locations = [
            ...new Set(data.items.map((hire) => hire.location_id)),
          ];
          return (
            <>
              <div className="filters">
                <Field label="Search">
                  <input
                    className="input"
                    type="search"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Name, code or designation"
                  />
                </Field>
                <Field label="Status">
                  <select
                    className="input"
                    value={status}
                    onChange={(event) => setStatus(event.target.value)}
                  >
                    <option value="">All statuses</option>
                    {STATUSES.map((value) => (
                      <option key={value} value={value}>
                        {humanize(value)}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Location">
                  <select
                    className="input"
                    value={location}
                    onChange={(event) => setLocation(event.target.value)}
                  >
                    <option value="">All locations</option>
                    {locations.map((value) => (
                      <option key={value} value={value}>
                        {locationLabel(value)}
                      </option>
                    ))}
                  </select>
                </Field>
              </div>
              {rows.length === 0 ? (
                <EmptyState>No employees match these filters.</EmptyState>
              ) : (
                <DataTable
                  caption="Employees"
                  rowKey={(hire) => hire.id}
                  rows={rows}
                  minWidth={820}
                  columns={[
                    {
                      header: "Employee",
                      render: (hire) => (
                        <>
                          <a href={hireHref(hire.id)}>{hire.display_name}</a>
                          <span className="cell-sub mono">
                            {hire.employee_code}
                          </span>
                        </>
                      ),
                    },
                    {
                      header: "Designation",
                      render: (hire) => hire.designation,
                    },
                    {
                      header: "Location",
                      render: (hire) => locationLabel(hire.location_id),
                    },
                    {
                      header: "Start date",
                      render: (hire) => (
                        <span className="num">
                          {formatDate(hire.start_date)}
                        </span>
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
                      width: "180px",
                      render: (hire) => (
                        <Progress
                          value={hire.tasks_completed}
                          max={hire.tasks_total}
                          label={`${hire.tasks_completed}/${hire.tasks_total}`}
                        />
                      ),
                    },
                    {
                      header: "Overdue",
                      numeric: true,
                      render: (hire) => (
                        <span
                          className="num"
                          data-alert={hire.tasks_overdue > 0 || undefined}
                        >
                          {hire.tasks_overdue}
                        </span>
                      ),
                    },
                  ]}
                />
              )}
            </>
          );
        }}
      </DataState>
    </>
  );
}
