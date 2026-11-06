import { useState } from "react";
import { api } from "../../shared/api";
import type { Escalation, KnowledgeDocument } from "../../shared/api-types";
import { formatDateTime, humanize } from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import {
  ActionError,
  Badge,
  DataState,
  DataTable,
  Field,
  Notice,
  PageHeader,
  Section,
} from "../../shared/ui";

const LEVELS: KnowledgeDocument["access_level"][] = [
  "GENERAL",
  "MANAGER",
  "IT",
  "PAYROLL",
  "BENEFITS",
  "HR",
];

function UploadForm({ onUploaded }: { onUploaded: () => void }) {
  const [title, setTitle] = useState("");
  const [level, setLevel] =
    useState<KnowledgeDocument["access_level"]>("GENERAL");
  const [file, setFile] = useState<File | null>(null);
  const [inputKey, setInputKey] = useState(0);
  const [done, setDone] = useState(false);
  const action = useAction();

  async function submit() {
    if (!file) return;
    setDone(false);
    const result = await action.run(() =>
      api.uploadKnowledge(title.trim(), level, file),
    );
    if (result.ok) {
      setTitle("");
      setFile(null);
      setInputKey((value) => value + 1);
      setDone(true);
      onUploaded();
    }
  }

  return (
    <section className="form-panel" aria-label="Upload a draft">
      <h2 className="panel-title">Upload a draft</h2>
      <div className="form-grid">
        <Field label="Title">
          <input
            className="input"
            value={title}
            maxLength={200}
            onChange={(event) => setTitle(event.target.value)}
          />
        </Field>
        <Field label="Who may read it">
          <select
            className="input"
            value={level}
            onChange={(event) =>
              setLevel(event.target.value as KnowledgeDocument["access_level"])
            }
          >
            {LEVELS.map((item) => (
              <option key={item} value={item}>
                {humanize(item)}
              </option>
            ))}
          </select>
        </Field>
        <Field label="File" hint="Markdown or text, up to 512 KB.">
          <input
            key={inputKey}
            className="file-input"
            type="file"
            accept=".md,.txt"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </Field>
      </div>
      <ActionError error={action.error} />
      {done && (
        <Notice tone="info" title="Draft uploaded">
          It is not searchable until it is approved.
        </Notice>
      )}
      <div className="form-actions">
        <button
          type="button"
          className="btn btn-primary"
          disabled={!title.trim() || !file || action.pending}
          onClick={() => void submit()}
        >
          {action.pending ? "Uploading" : "Upload draft"}
        </button>
      </div>
    </section>
  );
}

function ApproveButton({
  document,
  onChanged,
}: {
  document: KnowledgeDocument;
  onChanged: () => void;
}) {
  const action = useAction();
  async function approve() {
    const result = await action.run(() =>
      api.approveKnowledge(document.id, document.version),
    );
    if (result.ok) onChanged();
  }
  return (
    <div className="row-action">
      <button
        type="button"
        className="btn btn-sm"
        disabled={action.pending}
        onClick={() => void approve()}
      >
        Approve
      </button>
      <ActionError error={action.error} onReload={onChanged} />
    </div>
  );
}

function statusTone(status: KnowledgeDocument["status"]) {
  if (status === "APPROVED") return "ok";
  if (status === "DRAFT") return "warn";
  return "muted";
}

function EscalationRow({
  item,
  onChanged,
}: {
  item: Escalation;
  onChanged: () => void;
}) {
  const [answer, setAnswer] = useState("");
  const action = useAction();
  async function submit() {
    const result = await action.run(() =>
      api.answerEscalation(item.id, answer.trim()),
    );
    if (result.ok) {
      setAnswer("");
      onChanged();
    }
  }
  return (
    <li className="question">
      <div className="block-head">
        <p className="question-text">{item.question}</p>
        <Badge tone={item.state === "ANSWERED" ? "ok" : "warn"}>
          {humanize(item.state)}
        </Badge>
      </div>
      <p className="muted small">
        From {item.raised_by_name} · {formatDateTime(item.created_at)}
      </p>
      {item.resolution ? (
        <p>Answer: {item.resolution}</p>
      ) : (
        <div className="answer-form">
          <Field label="Answer">
            <textarea
              className="input"
              rows={2}
              value={answer}
              onChange={(event) => setAnswer(event.target.value)}
            />
          </Field>
          <ActionError error={action.error} onReload={onChanged} />
          <button
            type="button"
            className="btn btn-sm btn-primary"
            disabled={!answer.trim() || action.pending}
            onClick={() => void submit()}
          >
            {action.pending ? "Sending" : "Send answer"}
          </button>
        </div>
      )}
    </li>
  );
}

export function KnowledgePage() {
  const documents = useResource("knowledge", (signal) =>
    api.knowledgeDocuments(signal),
  );
  const escalations = useResource("escalations", (signal) =>
    api.escalations(signal),
  );
  return (
    <>
      <PageHeader
        title="Knowledge base"
        description="Drafts are not searchable. The assistant can only read approved documents, filtered by the reader's role."
      />
      <UploadForm onUploaded={documents.reload} />
      <Section title="Documents">
        <DataState
          resource={documents}
          isEmpty={(data) => data.items.length === 0}
          empty="No knowledge documents yet."
        >
          {(data) => (
            <DataTable
              caption="Knowledge documents"
              rowKey={(item) => `${item.id}:${item.version}`}
              rows={data.items}
              minWidth={720}
              columns={[
                { header: "Title", render: (item) => item.title },
                {
                  header: "Version",
                  numeric: true,
                  render: (item) => <span className="num">{item.version}</span>,
                },
                {
                  header: "Access",
                  render: (item) => humanize(item.access_level),
                },
                {
                  header: "Status",
                  render: (item) => (
                    <Badge tone={statusTone(item.status)}>
                      {humanize(item.status)}
                    </Badge>
                  ),
                },
                {
                  header: "Passages",
                  numeric: true,
                  render: (item) => (
                    <span className="num">{item.chunk_count}</span>
                  ),
                },
                {
                  header: "Created",
                  render: (item) => (
                    <span className="num">
                      {formatDateTime(item.created_at)}
                    </span>
                  ),
                },
                {
                  header: "Action",
                  render: (item) =>
                    item.status === "DRAFT" ? (
                      <ApproveButton
                        document={item}
                        onChanged={documents.reload}
                      />
                    ) : null,
                },
              ]}
            />
          )}
        </DataState>
      </Section>
      <Section
        title="Questions sent to HR"
        description="People asked these because the assistant could not answer."
      >
        <DataState
          resource={escalations}
          isEmpty={(data) => data.items.length === 0}
          empty="No questions have been sent to HR."
        >
          {(data) => (
            <ul className="stack">
              {[...data.items]
                .sort(
                  (a, b) =>
                    Number(a.state === "ANSWERED") -
                    Number(b.state === "ANSWERED"),
                )
                .map((item) => (
                  <EscalationRow
                    key={item.id}
                    item={item}
                    onChanged={escalations.reload}
                  />
                ))}
            </ul>
          )}
        </DataState>
      </Section>
    </>
  );
}
