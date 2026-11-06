import { api } from "../../shared/api";
import { formatDateTime, humanize } from "../../shared/format";
import { useResource } from "../../shared/hooks";
import { DataState } from "../../shared/ui";

export function HistoryTab({ hireId }: { hireId: string }) {
  const history = useResource(`history:${hireId}`, (signal) =>
    api.history(hireId, signal),
  );
  return (
    <DataState
      resource={history}
      isEmpty={(data) => data.items.length === 0}
      empty="No history is recorded."
    >
      {(data) => (
        <ol className="log">
          {data.items.map((event) => (
            <li key={event.id} className="log-row">
              <time className="log-time num" dateTime={event.created_at}>
                {formatDateTime(event.created_at)}
              </time>
              <span className="log-text">
                <span className="log-type">{humanize(event.event_type)}</span>
                {event.summary}
                {event.actor_user_id && (
                  <span className="mono muted"> {event.actor_user_id}</span>
                )}
              </span>
            </li>
          ))}
        </ol>
      )}
    </DataState>
  );
}
