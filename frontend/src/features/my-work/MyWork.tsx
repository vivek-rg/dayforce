import { useState } from "react";
import { api } from "../../shared/api";
import { categoryLabel, humanize } from "../../shared/format";
import { useResource } from "../../shared/hooks";
import { filterTasks } from "../../shared/logic";
import {
  DataState,
  EmptyState,
  Field,
  Notice,
  PageHeader,
} from "../../shared/ui";
import { TaskRow } from "./TaskRow";

const STATUSES = [
  "NOT_STARTED",
  "IN_PROGRESS",
  "PENDING_APPROVAL",
  "BLOCKED",
  "OVERDUE",
  "COMPLETED",
];

export function MyWorkPage() {
  const tasks = useResource("my-work", (signal) => api.myWork(signal));
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");

  return (
    <>
      <PageHeader title="Tasks" description="Work assigned to you." />
      <Notice tone="info" title="Completing a task records a claim.">
        Proof comes separately, from evidence. A task can be complete and still
        unproven.
      </Notice>
      <DataState
        resource={tasks}
        isEmpty={(data) => data.items.length === 0}
        empty="No tasks are assigned to you."
      >
        {(data) => {
          const rows = filterTasks(data.items, { search, status, category });
          const categories = [
            ...new Set(data.items.map((task) => task.category)),
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
                    placeholder="Task or employee"
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
                <Field label="Category">
                  <select
                    className="input"
                    value={category}
                    onChange={(event) => setCategory(event.target.value)}
                  >
                    <option value="">All categories</option>
                    {categories.map((value) => (
                      <option key={value} value={value}>
                        {categoryLabel(value)}
                      </option>
                    ))}
                  </select>
                </Field>
              </div>
              {rows.length === 0 ? (
                <EmptyState>No tasks match these filters.</EmptyState>
              ) : (
                <ul className="task-list">
                  {rows.map((task) => (
                    <TaskRow
                      key={task.id}
                      task={task}
                      plan={data.items}
                      onChanged={tasks.reload}
                      showHire
                      showCategory
                    />
                  ))}
                </ul>
              )}
            </>
          );
        }}
      </DataState>
    </>
  );
}
