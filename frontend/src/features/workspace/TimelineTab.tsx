import type { Hire, Plan } from "../../shared/api-types";
import { formatDate } from "../../shared/format";
import type { Resource } from "../../shared/hooks";
import { buildTimeline, offsetLabel, todayIso } from "../../shared/logic";
import { ClaimProof, DataState } from "../../shared/ui";

export function TimelineTab({
  plan,
  hire,
}: {
  plan: Resource<Plan>;
  hire: Hire;
}) {
  return (
    <DataState
      resource={plan}
      isEmpty={(data) => data.tasks.length === 0}
      empty="No tasks are visible to your role in this plan."
    >
      {(data) => (
        <>
          <p className="muted small">
            Ordered by due date. Offsets count calendar days from the start
            date, {formatDate(hire.start_date)}.
          </p>
          <ol className="timeline">
            {buildTimeline(data.tasks, hire.start_date, todayIso()).map(
              (entry) =>
                entry.kind === "milestone" ? (
                  <li key={entry.id} className="timeline-row is-milestone">
                    <span className="timeline-offset num">
                      {offsetLabel(entry.offset)}
                    </span>
                    <span className="timeline-marker" aria-hidden="true" />
                    <span className="timeline-body">
                      <strong>{entry.label}</strong>
                      <span className="num muted">
                        {" "}
                        {formatDate(entry.date)}
                      </span>
                    </span>
                  </li>
                ) : (
                  <li key={entry.id} className="timeline-row">
                    <span className="timeline-offset num">
                      {offsetLabel(entry.offset)}
                    </span>
                    <span className="timeline-marker" aria-hidden="true" />
                    <div className="timeline-body timeline-task">
                      <div>
                        <p className="task-title">{entry.task.title}</p>
                        <p className="muted small">
                          {entry.task.owner_name} ·{" "}
                          <span className="num">{formatDate(entry.date)}</span>
                        </p>
                      </div>
                      <ClaimProof task={entry.task} />
                    </div>
                  </li>
                ),
            )}
          </ol>
        </>
      )}
    </DataState>
  );
}
