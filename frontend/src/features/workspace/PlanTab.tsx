import { api } from "../../shared/api";
import type { Plan } from "../../shared/api-types";
import { categoryLabel } from "../../shared/format";
import { type Resource, useResource } from "../../shared/hooks";
import { groupByCategory } from "../../shared/logic";
import { useUser } from "../../shared/session-context";
import { DataState } from "../../shared/ui";
import { TaskRow } from "../my-work/TaskRow";

export function PlanTab({
  plan,
  onChanged,
}: {
  plan: Resource<Plan>;
  onChanged: () => void;
}) {
  const user = useUser();
  const isHr = user.role === "HR";
  const reference = useResource(isHr ? "reference" : null, (signal) =>
    api.reference(signal),
  );
  return (
    <DataState
      resource={plan}
      isEmpty={(data) => data.tasks.length === 0}
      empty="No tasks are visible to your role in this plan."
    >
      {(data) => (
        <>
          <p className="muted small">
            Plan version <span className="num">{data.plan_version}</span>. Each
            task shows the claim and the proof separately.
          </p>
          {groupByCategory(data.tasks).map(([category, tasks]) => (
            <section key={category} className="plan-group">
              <h2 className="plan-group-title">
                {categoryLabel(category)}
                <span className="num muted">{tasks.length}</span>
              </h2>
              <ul className="task-list">
                {tasks.map((task) => (
                  <TaskRow
                    key={task.id}
                    task={task}
                    plan={data.tasks}
                    onChanged={onChanged}
                    users={reference.data?.users}
                  />
                ))}
              </ul>
            </section>
          ))}
        </>
      )}
    </DataState>
  );
}
