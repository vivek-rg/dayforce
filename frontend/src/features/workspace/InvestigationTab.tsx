import { useState } from "react";
import { api } from "../../shared/api";
import type { Case } from "../../shared/api-types";
import { caseTone, formatDateTime, humanize } from "../../shared/format";
import { useAction, useInterval, useResource } from "../../shared/hooks";
import { useShell, useUser } from "../../shared/session-context";
import {
  ActionError,
  AdvisoryPanel,
  Badge,
  DataState,
  EmptyState,
  EvidenceCard,
  Field,
  Section,
  Stat,
} from "../../shared/ui";
import { AnswerForm } from "../notifications/AnswerForm";
import { ProposalCard } from "../review/ProposalCard";

const TERMINAL: Case["state"][] = ["RESOLVED", "ESCALATED"];
const POLL_MS = 3000;

function CaseDetail({
  caseId,
  onChanged,
}: {
  caseId: string;
  onChanged: () => void;
}) {
  const user = useUser();
  const { aiHealth } = useShell();
  const detail = useResource(`case:${caseId}`, (signal) =>
    api.getCase(caseId, signal),
  );
  const live =
    detail.data !== undefined && !TERMINAL.includes(detail.data.state);
  useInterval(detail.reload, live ? POLL_MS : null);

  return (
    <DataState resource={detail} rows={6}>
      {(data) => {
        const body = (
          <>
            <div className="case-head">
              <Badge tone={caseTone(data.state)}>{humanize(data.state)}</Badge>
              <span className="muted small">
                {humanize(data.kind)} · <span className="mono">{data.id}</span>
              </span>
              {live && (
                <span className="muted small">Updating every few seconds.</span>
              )}
            </div>
            <p className="case-message">{data.message}</p>
            <div className="stats-line">
              <Stat label="Model calls" value={data.model_calls} />
              <Stat label="Tool calls" value={data.tool_calls} />
              <Stat label="Questions" value={data.questions.length} />
              <Stat label="Proposals" value={data.proposals.length} />
            </div>
            <p className="muted small">
              The investigation transcript is not exposed. You see sanitized
              events, the questions it asked and its proposals. It cannot
              approve anything.
            </p>
          </>
        );
        return (
          <div className="case-detail">
            {aiHealth ? (
              <AdvisoryPanel
                model={aiHealth.model}
                isStub={aiHealth.is_stub}
                title="Investigation"
              >
                {body}
              </AdvisoryPanel>
            ) : (
              <div className="advisory">
                <div className="advisory-head">
                  <span className="advisory-tag">Advisory</span>
                </div>
                <div className="advisory-body">{body}</div>
              </div>
            )}
            <Section title="Questions">
              {data.questions.length ? (
                <ul className="stack">
                  {data.questions.map((question) => (
                    <li key={question.id} className="question">
                      <p className="question-text">{question.text}</p>
                      <p className="muted small">
                        {humanize(question.state)} · For{" "}
                        <span className="mono">
                          {question.recipient_user_id}
                        </span>
                      </p>
                      {question.answer && <p>Answer: {question.answer}</p>}
                      {question.state === "PENDING" &&
                        question.recipient_user_id === user.id && (
                          <AnswerForm
                            questionId={question.id}
                            onAnswered={detail.reload}
                          />
                        )}
                    </li>
                  ))}
                </ul>
              ) : (
                <EmptyState>No questions were asked.</EmptyState>
              )}
            </Section>
            <Section title="Proposals">
              {data.proposals.length ? (
                <div className="stack">
                  {data.proposals.map((proposal) => (
                    <ProposalCard
                      key={proposal.id}
                      proposal={proposal}
                      onChanged={() => {
                        detail.reload();
                        onChanged();
                      }}
                    />
                  ))}
                </div>
              ) : (
                <EmptyState>No proposals yet.</EmptyState>
              )}
            </Section>
            <Section title="Current evidence for this hire">
              {data.evidence.length ? (
                <div className="evidence-list">
                  {data.evidence.map((evidence) => (
                    <EvidenceCard key={evidence.id} evidence={evidence} />
                  ))}
                </div>
              ) : (
                <EmptyState>No evidence yet.</EmptyState>
              )}
            </Section>
            <Section title="Sanitized timeline">
              {data.timeline.length ? (
                <ol className="log">
                  {data.timeline.map((event) => (
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
                <EmptyState>No events yet.</EmptyState>
              )}
            </Section>
          </div>
        );
      }}
    </DataState>
  );
}

export function InvestigationTab({
  hireId,
  onChanged,
}: {
  hireId: string;
  onChanged: () => void;
}) {
  const cases = useResource(`cases:${hireId}`, (signal) =>
    api.hireCases(hireId, signal),
  );
  const [message, setMessage] = useState("");
  const [picked, setPicked] = useState<string | null>(null);
  const action = useAction();

  async function open() {
    const result = await action.run(() => api.openCase(hireId, message.trim()));
    if (result.ok) {
      setMessage("");
      setPicked(result.value.case_id);
      cases.reload();
    }
  }

  return (
    <DataState resource={cases} rows={5}>
      {(data) => {
        const selected = picked ?? data.items[0]?.id ?? null;
        return (
          <>
            <section className="form-panel" aria-label="Open an investigation">
              <h2 className="panel-title">Open an investigation</h2>
              <p className="muted small">
                Describe what looks wrong. It reads permitted evidence, may ask
                a responsible person, and may propose a narrow fix for a person
                to approve.
              </p>
              <Field label="What should be investigated?">
                <textarea
                  className="input"
                  rows={3}
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                />
              </Field>
              <ActionError error={action.error} onReload={cases.reload} />
              <div className="form-actions">
                <button
                  type="button"
                  className="btn btn-primary"
                  disabled={!message.trim() || action.pending}
                  onClick={() => void open()}
                >
                  {action.pending ? "Opening" : "Open investigation"}
                </button>
              </div>
            </section>
            {data.items.length > 1 && (
              <Field label="Case">
                <select
                  className="input"
                  value={selected ?? ""}
                  onChange={(event) => setPicked(event.target.value)}
                >
                  {data.items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.id}: {humanize(item.state)}
                    </option>
                  ))}
                </select>
              </Field>
            )}
            {selected ? (
              <CaseDetail
                key={selected}
                caseId={selected}
                onChanged={onChanged}
              />
            ) : (
              <EmptyState>No investigations yet.</EmptyState>
            )}
          </>
        );
      }}
    </DataState>
  );
}
