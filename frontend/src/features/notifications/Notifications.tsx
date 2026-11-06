import { api } from "../../shared/api";
import type { Notification } from "../../shared/api-types";
import { formatDateTime, humanize } from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import { hireHref } from "../../shared/routes";
import { useShell, useUser } from "../../shared/session-context";
import {
  ActionError,
  DataState,
  EmptyState,
  PageHeader,
  Section,
} from "../../shared/ui";
import { AnswerForm } from "./AnswerForm";

function NotificationRow({
  item,
  onChanged,
}: {
  item: Notification;
  onChanged: () => void;
}) {
  const user = useUser();
  const action = useAction();
  const link =
    item.hire_id &&
    (user.role === "EMPLOYEE" ? "#/portal" : hireHref(item.hire_id));

  async function markRead() {
    const result = await action.run(() => api.markRead(item.id));
    if (result.ok) onChanged();
  }

  return (
    <li className="notification" data-unread={!item.read || undefined}>
      <div className="notification-body">
        <p className="notification-title">
          {!item.read && <span className="unread-tag">Unread</span>}
          {item.title}
        </p>
        <p>{item.body}</p>
        <p className="muted small">
          {humanize(item.type)} ·{" "}
          <time className="num" dateTime={item.created_at}>
            {formatDateTime(item.created_at)}
          </time>
          {link && (
            <>
              {" · "}
              <a href={link}>Open</a>
            </>
          )}
        </p>
        <ActionError error={action.error} />
      </div>
      {!item.read && (
        <button
          type="button"
          className="btn btn-sm"
          disabled={action.pending}
          onClick={() => void markRead()}
        >
          Mark read
        </button>
      )}
    </li>
  );
}

export function NotificationsPage() {
  const { refreshUnread } = useShell();
  const notifications = useResource("notifications", (signal) =>
    api.notifications(signal),
  );
  const questions = useResource("questions", (signal) => api.questions(signal));

  return (
    <>
      <PageHeader title="Notifications" />
      <Section
        title="Questions waiting for you"
        description="An investigation asked you this. Your answer is information for it, not an approval. Official records do not change."
      >
        <DataState
          resource={questions}
          isEmpty={(data) => data.items.length === 0}
          empty="No questions are waiting for you."
        >
          {(data) => (
            <ul className="stack">
              {data.items.map((question) => (
                <li key={question.id} className="question">
                  <p className="question-text">{question.text}</p>
                  <p className="muted small">
                    Case <span className="mono">{question.case_id}</span>
                  </p>
                  <AnswerForm
                    questionId={question.id}
                    onAnswered={questions.reload}
                  />
                </li>
              ))}
            </ul>
          )}
        </DataState>
      </Section>
      <Section title="All notifications">
        <DataState resource={notifications} rows={6}>
          {(data) =>
            data.items.length === 0 ? (
              <EmptyState>No notifications yet.</EmptyState>
            ) : (
              <ul className="notification-list">
                {data.items.map((item) => (
                  <NotificationRow
                    key={item.id}
                    item={item}
                    onChanged={() => {
                      notifications.reload();
                      refreshUnread();
                    }}
                  />
                ))}
              </ul>
            )
          }
        </DataState>
      </Section>
    </>
  );
}
