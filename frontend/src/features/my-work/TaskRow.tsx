import { useState } from "react";
import { api } from "../../shared/api";
import type { Task, UserSummary } from "../../shared/api-types";
import { categoryLabel, formatDate } from "../../shared/format";
import { useAction } from "../../shared/hooks";
import {
  canComplete,
  canReassign,
  canStart,
  dependencyNote,
} from "../../shared/logic";
import { hireHref } from "../../shared/routes";
import { useUser } from "../../shared/session-context";
import { ActionError, ClaimProof } from "../../shared/ui";

export function TaskRow({
  task,
  plan,
  onChanged,
  showHire,
  showCategory,
  users,
}: {
  task: Task;
  /** The surrounding plan, used to name prerequisites. */
  plan?: Task[];
  onChanged: () => void;
  showHire?: boolean;
  showCategory?: boolean;
  /** When given, the reassign control appears. HR only. */
  users?: UserSummary[];
}) {
  const user = useUser();
  const action = useAction();
  const [owner, setOwner] = useState("");
  const note = dependencyNote(task, plan ?? []);
  const hireLink =
    user.role === "EMPLOYEE" ? "#/portal" : hireHref(task.hire_id);

  async function perform(work: () => Promise<Task>) {
    const result = await action.run(work);
    if (result.ok) {
      setOwner("");
      onChanged();
    }
  }

  return (
    <li className="task" data-critical={task.critical || undefined}>
      <div className="task-main">
        <p className="task-title">
          {task.title}
          {task.critical && <span className="task-critical">Critical</span>}
        </p>
        {task.description && (
          <p className="task-description">{task.description}</p>
        )}
        {note && <p className="task-note">{note}</p>}
        {showHire && (
          <p className="task-hire">
            <a href={hireLink}>{task.hire_name}</a>
            {showCategory && ` · ${categoryLabel(task.category)}`}
          </p>
        )}
      </div>
      <ClaimProof task={task} />
      <dl className="task-meta">
        <div>
          <dt>Owner</dt>
          <dd>{task.owner_name}</dd>
        </div>
        <div>
          <dt>Due</dt>
          <dd className="num">{formatDate(task.due_date)}</dd>
        </div>
      </dl>
      <div className="task-actions">
        {canStart(task, user.id) && (
          <button
            type="button"
            className="btn btn-sm"
            disabled={action.pending}
            onClick={() =>
              void perform(() => api.startTask(task.id, task.version))
            }
          >
            Start
          </button>
        )}
        {canComplete(task, user.id) && (
          <button
            type="button"
            className="btn btn-sm btn-primary"
            disabled={action.pending}
            title="Records your claim. Proof comes from evidence."
            onClick={() =>
              void perform(() => api.completeTask(task.id, task.version))
            }
          >
            Mark complete
          </button>
        )}
        {users && canReassign(task) && (
          <span className="reassign">
            <label className="sr-only" htmlFor={`owner-${task.id}`}>
              New owner for {task.title}
            </label>
            <select
              id={`owner-${task.id}`}
              className="input input-sm"
              value={owner}
              onChange={(event) => setOwner(event.target.value)}
            >
              <option value="">Reassign to</option>
              {users
                .filter((item) => item.id !== task.owner_user_id)
                .map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.display_name}
                  </option>
                ))}
            </select>
            <button
              type="button"
              className="btn btn-sm"
              disabled={!owner || action.pending}
              onClick={() =>
                void perform(() =>
                  api.reassignTask(task.id, task.version, owner),
                )
              }
            >
              Reassign
            </button>
          </span>
        )}
      </div>
      {action.error && (
        <div className="task-error">
          <ActionError error={action.error} onReload={onChanged} />
        </div>
      )}
    </li>
  );
}
