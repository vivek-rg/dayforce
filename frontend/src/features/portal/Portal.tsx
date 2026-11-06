import { useRef, useState } from "react";
import { api } from "../../shared/api";
import type { Document, Hire, Plan } from "../../shared/api-types";
import {
  DOCUMENT_CATEGORIES,
  categoryLabel,
  documentCategoryLabel,
  documentTone,
  formatDate,
  formatDateTime,
  humanize,
} from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import {
  UPLOAD_ACCEPT,
  currentDocument,
  groupByCategory,
  latestReviewReason,
  nextStep,
  planLedger,
  uploadProblem,
} from "../../shared/logic";
import { useUser } from "../../shared/session-context";
import {
  ActionError,
  Badge,
  ClaimProof,
  DataState,
  EmptyState,
  LedgerRail,
  Notice,
  PageHeader,
  Section,
} from "../../shared/ui";
import { TaskRow } from "../my-work/TaskRow";

function NextAction({
  plan,
  documents,
  onChanged,
  onGoToDocuments,
}: {
  plan: Plan;
  documents: Document[];
  onChanged: () => void;
  onGoToDocuments: () => void;
}) {
  const user = useUser();
  const action = useAction();
  const step = nextStep(plan.tasks, documents, user.id);

  async function perform(work: () => Promise<unknown>) {
    const result = await action.run(work);
    if (result.ok) onChanged();
  }

  let title = "You have nothing to do right now.";
  let detail =
    "Your tasks are claimed. People and independent checks are working through the proof.";
  let controls = null;
  if (step.kind === "resubmit") {
    title = `Send your ${documentCategoryLabel(step.document.category)} again`;
    detail =
      latestReviewReason(step.document) ??
      "HR asked for this document to be sent again.";
    controls = (
      <button
        type="button"
        className="btn btn-primary"
        onClick={onGoToDocuments}
      >
        Go to documents
      </button>
    );
  } else if (step.kind === "waiting") {
    title = `Waiting: ${step.task.title}`;
    detail =
      "This opens when the task before it is finished. You don't need to do anything yet.";
  } else if (step.kind === "task") {
    const { task } = step;
    title = task.title;
    detail = `Due ${formatDate(task.due_date)}. ${task.description}`;
    controls = (
      <>
        {task.category === "documents" && (
          <button type="button" className="btn" onClick={onGoToDocuments}>
            Go to documents
          </button>
        )}
        {task.work_state === "PENDING" && (
          <button
            type="button"
            className="btn"
            disabled={action.pending}
            onClick={() =>
              void perform(() => api.startTask(task.id, task.version))
            }
          >
            Start
          </button>
        )}
        <button
          type="button"
          className="btn btn-primary"
          disabled={action.pending}
          onClick={() =>
            void perform(() => api.completeTask(task.id, task.version))
          }
        >
          Mark complete
        </button>
      </>
    );
  }

  return (
    <section className="hero" aria-label="Your next action">
      <p className="eyebrow">Your next action</p>
      <h2 className="hero-title">{title}</h2>
      <p className="hero-detail">{detail}</p>
      {step.kind === "task" && <ClaimProof task={step.task} />}
      <ActionError error={action.error} onReload={onChanged} />
      {controls && <div className="hero-actions">{controls}</div>}
    </section>
  );
}

function UploadRow({
  hireId,
  category,
  label,
  document,
  onUploaded,
}: {
  hireId: string;
  category: Document["category"];
  label: string;
  document: Document | undefined;
  onUploaded: () => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [inputKey, setInputKey] = useState(0);
  const action = useAction();
  const problem = file ? uploadProblem(file) : null;
  const reason = document && latestReviewReason(document);
  const sentBack =
    document?.state === "REJECTED" ||
    document?.state === "RESUBMISSION_REQUESTED";

  async function upload() {
    if (!file) return;
    const result = await action.run(() =>
      api.uploadHireDocument(hireId, category, file),
    );
    if (result.ok) {
      setFile(null);
      setInputKey((value) => value + 1);
      onUploaded();
    }
  }

  return (
    <li className="upload-row">
      <div className="upload-info">
        <p className="upload-label">{label}</p>
        {document ? (
          <>
            <Badge tone={documentTone(document.state)}>
              {humanize(document.state)}
            </Badge>
            <p className="muted small">
              {document.original_name} · {formatDateTime(document.created_at)}
            </p>
          </>
        ) : (
          <Badge tone="muted">Not submitted</Badge>
        )}
        {sentBack && reason && (
          <p className="upload-reason">HR said: {reason}</p>
        )}
      </div>
      {document?.state === "VERIFIED" ? (
        <p className="muted small">Verified by HR. Nothing more is needed.</p>
      ) : (
        <div className="upload-controls">
          <label className="sr-only" htmlFor={`file-${category}`}>
            File for {label}
          </label>
          <input
            key={inputKey}
            id={`file-${category}`}
            className="file-input"
            type="file"
            accept={UPLOAD_ACCEPT}
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <button
            type="button"
            className="btn btn-sm"
            disabled={!file || Boolean(problem) || action.pending}
            onClick={() => void upload()}
          >
            {action.pending ? "Uploading" : document ? "Replace" : "Upload"}
          </button>
          {problem && <p className="field-error">{problem}</p>}
        </div>
      )}
      {action.error && (
        <div className="upload-error">
          <ActionError error={action.error} />
        </div>
      )}
    </li>
  );
}

function PortalBody({ hire }: { hire: Hire }) {
  const plan = useResource(`plan:${hire.id}`, (signal) =>
    api.plan(hire.id, signal),
  );
  const documents = useResource(`documents:${hire.id}`, (signal) =>
    api.hireDocuments(hire.id, signal),
  );
  const documentsRef = useRef<HTMLDivElement>(null);

  function reloadAll() {
    plan.reload();
    documents.reload();
  }

  return (
    <>
      <DataState resource={plan} rows={4}>
        {(data) => (
          <div className="portal-top">
            <NextAction
              plan={data}
              documents={documents.data?.items ?? []}
              onChanged={reloadAll}
              onGoToDocuments={() => documentsRef.current?.scrollIntoView()}
            />
            <aside className="portal-side">
              <h2 className="eyebrow">Your progress</h2>
              <LedgerRail ledger={planLedger(data.tasks)} />
              <p className="muted small">
                Claimed means marked complete. Proven means an independent check
                confirmed it.
              </p>
              <a className="btn btn-block" href="#/assistant">
                Ask the assistant
              </a>
            </aside>
          </div>
        )}
      </DataState>
      <div ref={documentsRef}>
        <Section
          title="Your documents"
          description="PDF, PNG, JPEG or TXT, up to 5 MB. A person reviews each one."
        >
          <DataState resource={documents} rows={7}>
            {(data) => (
              <ul className="upload-list">
                {DOCUMENT_CATEGORIES.map((item) => (
                  <UploadRow
                    key={item.id}
                    hireId={hire.id}
                    category={item.id}
                    label={item.label}
                    document={currentDocument(data.items, item.id)}
                    onUploaded={reloadAll}
                  />
                ))}
              </ul>
            )}
          </DataState>
        </Section>
      </div>
      <Section
        title="Your checklist"
        description="Completing a task records your claim. Proof comes from evidence."
      >
        <DataState
          resource={plan}
          isEmpty={(data) => data.tasks.length === 0}
          empty="Your plan has no tasks yet."
        >
          {(data) =>
            groupByCategory(data.tasks).map(([category, tasks]) => (
              <section key={category} className="plan-group">
                <h3 className="plan-group-title">
                  {categoryLabel(category)}
                  <span className="num muted">{tasks.length}</span>
                </h3>
                <ul className="task-list">
                  {tasks.map((task) => (
                    <TaskRow
                      key={task.id}
                      task={task}
                      plan={data.tasks}
                      onChanged={reloadAll}
                    />
                  ))}
                </ul>
              </section>
            ))
          }
        </DataState>
      </Section>
    </>
  );
}

export function PortalPage() {
  const hires = useResource("hires", (signal) => api.hires(signal));
  return (
    <DataState resource={hires} rows={6}>
      {(data) => {
        const hire = data.items[0];
        if (!hire) {
          return (
            <>
              <PageHeader title="My onboarding" />
              <EmptyState>
                Your onboarding plan has not been created yet.
              </EmptyState>
              <Notice tone="info">
                HR will create it. You can still use the assistant.
              </Notice>
            </>
          );
        }
        return (
          <>
            <PageHeader
              title={`Welcome, ${hire.display_name}`}
              description={`You start on ${formatDate(hire.start_date)} as ${hire.designation}.`}
            />
            <PortalBody hire={hire} />
          </>
        );
      }}
    </DataState>
  );
}
