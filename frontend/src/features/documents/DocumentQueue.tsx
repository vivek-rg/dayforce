import { useState } from "react";
import { ApiError, api, downloadDocument } from "../../shared/api";
import type { Document, DocumentExtraction } from "../../shared/api-types";
import {
  documentCategoryLabel,
  documentTone,
  formatBytes,
  formatDateTime,
  humanize,
  locationLabel,
} from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import { hireHref } from "../../shared/routes";
import {
  ActionError,
  AdvisoryPanel,
  Badge,
  DataState,
  EmptyState,
  Facts,
  Field,
  Notice,
  PageHeader,
} from "../../shared/ui";

const MANUAL_CODES = [
  "AI_UNAVAILABLE",
  "AI_BLOCKED_SENSITIVE",
  "NO_TEXT_LAYER",
];

function ExtractionView({ extraction }: { extraction: DocumentExtraction }) {
  return (
    <AdvisoryPanel
      model={extraction.model}
      isStub={extraction.is_stub}
      title="Extraction"
    >
      {extraction.mismatches.length > 0 && (
        <div className="mismatches" role="alert">
          <h4>
            {extraction.mismatches.length}{" "}
            {extraction.mismatches.length === 1 ? "mismatch" : "mismatches"}{" "}
            with the profile
          </h4>
          <ul>
            {extraction.mismatches.map((item) => (
              <li key={item.field}>
                <span className="mismatch-field">{humanize(item.field)}</span>
                <span>
                  Document: <strong>{item.document_value}</strong>
                </span>
                <span>
                  Profile: <strong>{item.profile_value}</strong>
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
      <p>{extraction.summary}</p>
      <p className="muted small">
        Suggested category:{" "}
        {documentCategoryLabel(extraction.suggested_category)} · Run{" "}
        <span className="mono">{extraction.ai_run_id}</span> ·{" "}
        {formatDateTime(extraction.created_at)}
      </p>
      <h4 className="eyebrow">Fields, with the exact quote</h4>
      {extraction.fields.length ? (
        <ul className="extracted">
          {extraction.fields.map((field) => (
            <li key={`${field.name}:${field.value}`}>
              <span className="extracted-name">{humanize(field.name)}</span>
              <span className="extracted-value">{field.value}</span>
              <blockquote>{field.quote}</blockquote>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted small">No fields were extracted.</p>
      )}
      <h4 className="eyebrow">Missing</h4>
      {extraction.missing.length ? (
        <ul className="plain-list">
          {extraction.missing.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted small">Nothing was reported missing.</p>
      )}
    </AdvisoryPanel>
  );
}

function ExtractionSection({
  document,
  onDocumentChanged,
}: {
  document: Document;
  onDocumentChanged: () => void;
}) {
  const latest = useResource(`extraction:${document.id}`, (signal) =>
    api.latestExtraction(document.id, signal),
  );
  const action = useAction();
  const manual =
    action.error instanceof ApiError &&
    MANUAL_CODES.includes(action.error.code);

  async function run() {
    const result = await action.run(() => api.runExtraction(document.id));
    if (result.ok) {
      latest.reload();
      // Extraction moves a submitted document to under review, which bumps its version.
      onDocumentChanged();
    }
  }

  return (
    <div className="panel-block">
      <div className="block-head">
        <h3>AI extraction</h3>
        <button
          type="button"
          className="btn btn-sm"
          disabled={action.pending}
          onClick={() => void run()}
        >
          {action.pending ? "Extracting" : "Run AI extraction"}
        </button>
      </div>
      {manual ? (
        <Notice tone="info" title="Manual review continues">
          {action.error?.message}
        </Notice>
      ) : (
        <ActionError error={action.error} />
      )}
      <DataState resource={latest} rows={3}>
        {(extraction) =>
          extraction ? (
            <ExtractionView extraction={extraction} />
          ) : (
            <EmptyState>No extraction has run for this document.</EmptyState>
          )
        }
      </DataState>
    </div>
  );
}

function ReviewForm({
  document,
  onReviewed,
  onReload,
}: {
  document: Document;
  onReviewed: () => void;
  onReload: () => void;
}) {
  const [reason, setReason] = useState("");
  const [missingReason, setMissingReason] = useState(false);
  const action = useAction();

  async function submit(
    decision: "VERIFY" | "REJECT" | "REQUEST_RESUBMISSION",
  ) {
    if (decision !== "VERIFY" && !reason.trim()) {
      setMissingReason(true);
      return;
    }
    setMissingReason(false);
    const result = await action.run(() =>
      api.reviewDocument(document.id, {
        decision,
        reason: reason.trim(),
        expected_version: document.version,
      }),
    );
    if (result.ok) onReviewed();
  }

  return (
    <div className="panel-block">
      <h3>Your review</h3>
      <p className="muted small">
        AI cannot verify a document. Only a person can, and this decision is
        recorded under your name.
      </p>
      <Field
        label="Reason"
        hint="Required to reject or request resubmission. The employee sees it."
        error={
          missingReason
            ? "Give a reason so the employee knows what to fix."
            : null
        }
      >
        <textarea
          className="input"
          rows={2}
          value={reason}
          onChange={(event) => setReason(event.target.value)}
        />
      </Field>
      <ActionError error={action.error} onReload={onReload} />
      <div className="decision-buttons">
        <button
          type="button"
          className="btn btn-primary"
          disabled={action.pending}
          onClick={() => void submit("VERIFY")}
        >
          Verify
        </button>
        <button
          type="button"
          className="btn"
          disabled={action.pending}
          onClick={() => void submit("REJECT")}
        >
          Reject
        </button>
        <button
          type="button"
          className="btn"
          disabled={action.pending}
          onClick={() => void submit("REQUEST_RESUBMISSION")}
        >
          Request resubmission
        </button>
      </div>
    </div>
  );
}

function DocumentDetail({
  document,
  onReviewed,
  onReload,
}: {
  document: Document;
  onReviewed: () => void;
  onReload: () => void;
}) {
  const download = useAction();
  return (
    <div className="detail">
      <div className="block-head">
        <h2>{documentCategoryLabel(document.category)}</h2>
        <button
          type="button"
          className="btn btn-sm"
          disabled={download.pending}
          onClick={() =>
            void download.run(() =>
              downloadDocument(document.id, document.original_name),
            )
          }
        >
          {download.pending ? "Downloading" : "Download"}
        </button>
      </div>
      <ActionError error={download.error} />
      <Facts
        items={[
          [
            "Employee",
            <a href={hireHref(document.hire_id, "documents")}>
              {document.hire_name}
            </a>,
          ],
          [
            "State",
            <Badge tone={documentTone(document.state)}>
              {humanize(document.state)}
            </Badge>,
          ],
          ["File", document.original_name],
          ["Type", document.mime_type],
          [
            "Size",
            <span className="num">{formatBytes(document.size_bytes)}</span>,
          ],
          [
            "Text layer",
            document.text_available
              ? "Readable text found"
              : "No readable text",
          ],
          [
            "Declared location",
            document.declared_location_id
              ? locationLabel(document.declared_location_id)
              : "Not read",
          ],
          [
            "Submitted",
            <span className="num">{formatDateTime(document.created_at)}</span>,
          ],
          ["Version", <span className="num">{document.version}</span>],
        ]}
      />
      <ExtractionSection document={document} onDocumentChanged={onReload} />
      <ReviewForm
        key={document.id}
        document={document}
        onReviewed={onReviewed}
        onReload={onReload}
      />
    </div>
  );
}

export function DocumentQueuePage() {
  const queue = useResource("documents-queue", (signal) =>
    api.documentQueue(signal),
  );
  const [selectedId, setSelectedId] = useState<string | null>(null);

  return (
    <>
      <PageHeader
        title="Document verification"
        description="AI can read and suggest. It cannot verify. Only people can."
      />
      <DataState
        resource={queue}
        isEmpty={(data) => data.items.length === 0}
        empty="No documents are waiting for review."
      >
        {(data) => {
          const selected = data.items.find((item) => item.id === selectedId);
          return (
            <div className="master-detail">
              <ul className="queue" aria-label="Documents to review">
                {data.items.map((item) => (
                  <li key={item.id}>
                    <button
                      type="button"
                      className="queue-item"
                      aria-pressed={item.id === selectedId}
                      onClick={() => setSelectedId(item.id)}
                    >
                      <span className="queue-title">{item.hire_name}</span>
                      <span className="queue-sub">
                        {documentCategoryLabel(item.category)}
                      </span>
                      <Badge tone={documentTone(item.state)}>
                        {humanize(item.state)}
                      </Badge>
                    </button>
                  </li>
                ))}
              </ul>
              {selected ? (
                <DocumentDetail
                  key={selected.id}
                  document={selected}
                  onReload={queue.reload}
                  onReviewed={() => {
                    setSelectedId(null);
                    queue.reload();
                  }}
                />
              ) : (
                <EmptyState>Choose a document to review it.</EmptyState>
              )}
            </div>
          );
        }}
      </DataState>
    </>
  );
}
