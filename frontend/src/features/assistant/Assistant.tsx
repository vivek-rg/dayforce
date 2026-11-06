import {
  type Dispatch,
  type FormEvent,
  type SetStateAction,
  useState,
} from "react";
import { api } from "../../shared/api";
import type { AssistantAnswer, Citation } from "../../shared/api-types";
import { formatDateTime, humanize } from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import {
  ActionError,
  AdvisoryPanel,
  Badge,
  DataState,
  EmptyState,
  Field,
  Notice,
  PageHeader,
  Section,
} from "../../shared/ui";

export type AssistantTurn = {
  id: number;
  question: string;
  answer: AssistantAnswer;
};

function CitationCard({ citation }: { citation: Citation }) {
  return (
    <details className="citation">
      <summary>
        <span>{citation.title}</span>
        <span className="muted small">
          v{citation.version} · {citation.section_ref}
        </span>
      </summary>
      <blockquote>{citation.quote}</blockquote>
    </details>
  );
}

const STATUS_TONE = {
  ANSWERED: "ok",
  PARTIAL: "warn",
  NOT_FOUND: "muted",
  OUT_OF_SCOPE: "muted",
  UNAVAILABLE: "bad",
} as const;

function Answer({
  turn,
  onEscalated,
}: {
  turn: AssistantTurn;
  onEscalated: () => void;
}) {
  const { answer, question } = turn;
  const [sent, setSent] = useState(false);
  const action = useAction();

  async function sendToHr() {
    const result = await action.run(() =>
      api.escalate(question, answer.ai_run_id),
    );
    if (result.ok) {
      setSent(true);
      onEscalated();
    }
  }

  return (
    <li className="turn">
      <p className="turn-question">{question}</p>
      <AdvisoryPanel model={answer.model} isStub={answer.is_stub}>
        <div className="turn-status">
          <Badge tone={STATUS_TONE[answer.status]}>
            {humanize(answer.status)}
          </Badge>
          <span>{answer.message}</span>
        </div>
        {answer.status === "PARTIAL" && answer.uncertainty && (
          <Notice tone="warn" title="What is uncertain">
            {answer.uncertainty}
          </Notice>
        )}
        {answer.claims.length > 0 && (
          <ul className="claims">
            {answer.claims.map((claim) => (
              <li key={claim.text} className="claim">
                <p>{claim.text}</p>
                {claim.citations.length > 0 && (
                  <div className="citations">
                    {claim.citations.map((citation) => (
                      <CitationCard
                        key={`${citation.chunk_id}:${citation.quote}`}
                        citation={citation}
                      />
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
        {answer.status === "UNAVAILABLE" && answer.sources.length > 0 && (
          <div className="sources">
            <h4 className="eyebrow">
              Relevant approved sources. These are not an answer.
            </h4>
            <div className="citations">
              {answer.sources.map((citation) => (
                <CitationCard key={citation.chunk_id} citation={citation} />
              ))}
            </div>
          </div>
        )}
        <ActionError error={action.error} />
        {answer.suggest_escalation &&
          (sent ? (
            <p className="muted small">
              Sent to HR. Their answer appears below.
            </p>
          ) : (
            <div>
              <button
                type="button"
                className="btn btn-sm"
                disabled={action.pending}
                onClick={() => void sendToHr()}
              >
                Send to HR
              </button>
            </div>
          ))}
      </AdvisoryPanel>
    </li>
  );
}

export function AssistantPage({
  turns,
  setTurns,
}: {
  turns: AssistantTurn[];
  setTurns: Dispatch<SetStateAction<AssistantTurn[]>>;
}) {
  const [question, setQuestion] = useState("");
  const ask = useAction();
  const escalations = useResource("my-escalations", (signal) =>
    api.myEscalations(signal),
  );

  async function submit(event: FormEvent) {
    event.preventDefault();
    const text = question.trim();
    if (!text) return;
    const result = await ask.run(() => api.ask(text));
    if (result.ok) {
      setTurns((current) => [
        ...current,
        { id: current.length + 1, question: text, answer: result.value },
      ]);
      setQuestion("");
    }
  }

  return (
    <>
      <PageHeader
        title="Knowledge assistant"
        description="Answers come only from approved documents your role may read, with the exact quote. It is advice to check, not a decision."
      />
      <div className="assistant">
        {turns.length === 0 ? (
          <EmptyState>
            Ask about a policy, for example the leave policy.
          </EmptyState>
        ) : (
          <ol className="turns" aria-live="polite">
            {turns.map((turn) => (
              <Answer
                key={turn.id}
                turn={turn}
                onEscalated={escalations.reload}
              />
            ))}
          </ol>
        )}
        <form className="ask-form" onSubmit={(event) => void submit(event)}>
          <Field label="Your question">
            <textarea
              className="input"
              rows={2}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
          </Field>
          <ActionError error={ask.error} />
          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!question.trim() || ask.pending}
            >
              {ask.pending ? "Asking" : "Ask"}
            </button>
          </div>
        </form>
      </div>
      <Section title="My questions sent to HR">
        <DataState
          resource={escalations}
          isEmpty={(data) => data.items.length === 0}
          empty="You have not sent any questions to HR."
        >
          {(data) => (
            <ul className="stack">
              {data.items.map((item) => (
                <li key={item.id} className="question">
                  <div className="block-head">
                    <p className="question-text">{item.question}</p>
                    <Badge tone={item.state === "ANSWERED" ? "ok" : "warn"}>
                      {humanize(item.state)}
                    </Badge>
                  </div>
                  <p className="muted small">
                    {formatDateTime(item.created_at)}
                  </p>
                  {item.resolution && <p>HR answered: {item.resolution}</p>}
                </li>
              ))}
            </ul>
          )}
        </DataState>
      </Section>
    </>
  );
}
