import type { Evidence, PlanDiff, Task } from "../../shared/api-types";
import { checkLabel } from "../../shared/format";

function DiffGroup({
  title,
  items,
  describe,
}: {
  title: string;
  items: string[];
  describe?: (id: string) => string | undefined;
}) {
  return (
    <div className="diff-group">
      <h4>
        {title} <span className="num muted">{items.length}</span>
      </h4>
      {items.length === 0 ? (
        <p className="muted small">None</p>
      ) : (
        <ul className="plain-list">
          {items.map((item) => {
            const name = describe?.(item);
            return (
              <li key={item}>
                {name ? (
                  <>
                    {name} <span className="mono muted">{item}</span>
                  </>
                ) : (
                  <span className={describe ? "mono" : undefined}>{item}</span>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

/** `create` holds task titles from policy; the other lists hold record IDs from the server. */
export function PlanDiffView({
  diff,
  tasks,
  checks,
}: {
  diff: PlanDiff;
  tasks?: Task[];
  checks?: Evidence[];
}) {
  const taskTitle = (id: string) =>
    tasks?.find((task) => task.id === id)?.title;
  const checkName = (id: string) => {
    const check = checks?.find((item) => item.id === id);
    return check ? checkLabel(check.check_type) : undefined;
  };
  return (
    <div className="diff" aria-label="Plan impact">
      <DiffGroup title="Tasks to create" items={diff.create} />
      <DiffGroup
        title="Tasks to cancel"
        items={diff.cancel}
        describe={taskTitle}
      />
      <DiffGroup
        title="Tasks kept"
        items={diff.preserve}
        describe={taskTitle}
      />
      <DiffGroup
        title="Checks invalidated"
        items={diff.invalidate_checks}
        describe={checkName}
      />
    </div>
  );
}
