import { type KeyboardEvent, type ReactNode, useId, useRef } from "react";
import { ApiError } from "./api";
import type { CheckResult, DisplayStatus, Evidence, Task } from "./api-types";
import {
  type Tone,
  checkLabel,
  displayStatusTone,
  evidenceTone,
  factValue,
  formatDateTime,
  humanize,
  reasonText,
} from "./format";
import type { Resource } from "./hooks";
import { type PlanLedger, claimProof } from "./logic";

export function Badge({ tone, children }: { tone: Tone; children: ReactNode }) {
  return (
    <span className="badge" data-tone={tone}>
      <span className="badge-dot" aria-hidden="true" />
      {children}
    </span>
  );
}

export function StatusBadge({ status }: { status: DisplayStatus }) {
  return <Badge tone={displayStatusTone(status)}>{humanize(status)}</Badge>;
}

export function EvidenceBadge({
  result,
}: {
  result: CheckResult | null | undefined;
}) {
  return (
    <Badge tone={evidenceTone(result)}>
      {result ? humanize(result) : "No check"}
    </Badge>
  );
}

/** The signature. A claim and its proof, joined only when the proof really exists. */
export function ClaimProof({
  task,
}: {
  task: Pick<
    Task,
    "work_state" | "display_status" | "evidence_result" | "check_type"
  >;
}) {
  const view = claimProof(task);
  return (
    <div className="cp" data-verdict={view.verdict}>
      <div className="cp-cells">
        <span className="cp-cell cp-claim" data-tone={view.claimTone}>
          <span className="cp-key">Claim</span>
          <span className="cp-value">{view.claim}</span>
        </span>
        <span className="cp-seam" aria-hidden="true" />
        <span className="cp-cell cp-proof" data-result={view.result}>
          <span className="cp-key">Proof</span>
          <span className="cp-value">{view.proof}</span>
        </span>
      </div>
      {view.flag && <span className="cp-flag">{view.flag}</span>}
    </div>
  );
}

/** Claimed versus proven for a whole plan, on the same scale. */
export function LedgerRail({ ledger }: { ledger: PlanLedger }) {
  const percent = (value: number) =>
    ledger.total ? `${(value / ledger.total) * 100}%` : "0%";
  return (
    <div className="rail">
      <div className="rail-row">
        <span className="rail-label">Claimed</span>
        <span className="rail-track">
          <span
            className="rail-fill rail-claim"
            style={{ width: percent(ledger.claimed) }}
          />
        </span>
        <span className="num rail-count">
          {ledger.claimed}/{ledger.total}
        </span>
      </div>
      <div className="rail-row">
        <span className="rail-label">Proven</span>
        <span className="rail-track">
          <span
            className="rail-fill rail-proof"
            style={{ width: percent(ledger.proven) }}
          />
          <span
            className="rail-fill rail-gap"
            style={{ width: percent(ledger.gaps) }}
          />
        </span>
        <span className="num rail-count">
          {ledger.proven}/{ledger.total}
        </span>
      </div>
      <p className="rail-note">
        {ledger.gaps > 0 ? (
          <strong>
            {ledger.gaps} {ledger.gaps === 1 ? "claim" : "claims"} without
            proof.
          </strong>
        ) : (
          "No unproven claims."
        )}
        {ledger.noCheck > 0 &&
          ` ${ledger.noCheck} completed ${ledger.noCheck === 1 ? "task has" : "tasks have"} no independent check.`}
      </p>
    </div>
  );
}

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <header className="page-header">
      <div className="page-heading">
        <h1>{title}</h1>
        {description && <p className="page-description">{description}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </header>
  );
}

export function Section({
  title,
  description,
  actions,
  children,
}: {
  title: string;
  description?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="section">
      <div className="section-header">
        <div>
          <h2>{title}</h2>
          {description && <p className="section-description">{description}</p>}
        </div>
        {actions && <div className="section-actions">{actions}</div>}
      </div>
      {children}
    </section>
  );
}

export function Skeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="skeleton" role="status" aria-label="Loading">
      {Array.from({ length: rows }, (_, index) => (
        <span key={index} className="skeleton-row" />
      ))}
    </div>
  );
}

export function EmptyState({
  children,
  action,
}: {
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="state state-empty">
      <p>{children}</p>
      {action}
    </div>
  );
}

export function DeniedState({ message }: { message?: string }) {
  return (
    <div className="state state-denied" role="alert">
      <p className="state-title">No access for your role</p>
      <p>{message ?? "Your role cannot perform this operation."}</p>
    </div>
  );
}

export function ErrorState({
  error,
  onRetry,
  retrying,
}: {
  error: Error;
  onRetry?: () => void;
  retrying?: boolean;
}) {
  if (error instanceof ApiError && error.status === 403) {
    return <DeniedState message={error.message} />;
  }
  return (
    <div className="state state-error" role="alert">
      <p className="state-title">This could not be loaded</p>
      <p>{error.message}</p>
      {onRetry && (
        <button
          type="button"
          className="btn btn-sm"
          onClick={onRetry}
          disabled={retrying}
        >
          {retrying ? "Retrying" : "Try again"}
        </button>
      )}
    </div>
  );
}

/** Every data view goes through this, so none can forget a loading, empty, error or 403 state. */
export function DataState<T>({
  resource,
  isEmpty,
  empty,
  rows,
  children,
}: {
  resource: Resource<T>;
  isEmpty?: (data: T) => boolean;
  empty?: ReactNode;
  rows?: number;
  children: (data: T) => ReactNode;
}) {
  const { data, error, loading, refreshing, reload } = resource;
  if (loading) return <Skeleton rows={rows} />;
  if (data === undefined) {
    return error ? (
      <ErrorState error={error} onRetry={reload} retrying={refreshing} />
    ) : (
      <Skeleton rows={rows} />
    );
  }
  return (
    <>
      {error && (
        <Notice tone="warn" title="Showing the last loaded data">
          {error.message}
        </Notice>
      )}
      {isEmpty?.(data) ? <EmptyState>{empty}</EmptyState> : children(data)}
    </>
  );
}

export type Column<T> = {
  header: string;
  render: (row: T) => ReactNode;
  numeric?: boolean;
  width?: string;
};

export function DataTable<T>({
  caption,
  columns,
  rows,
  rowKey,
  minWidth = 640,
}: {
  caption: string;
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  minWidth?: number;
}) {
  return (
    <div className="table-wrap" role="region" aria-label={caption} tabIndex={0}>
      <table className="table" style={{ minWidth }}>
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                key={column.header}
                scope="col"
                className={column.numeric ? "is-num" : undefined}
                style={column.width ? { width: column.width } : undefined}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={rowKey(row)}>
              {columns.map((column) => (
                <td
                  key={column.header}
                  className={column.numeric ? "is-num" : undefined}
                >
                  {column.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export type TabItem = { id: string; label: string };

export function Tabs({
  label,
  tabs,
  active,
  onSelect,
}: {
  label: string;
  tabs: TabItem[];
  active: string;
  onSelect: (id: string) => void;
}) {
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});
  const baseId = useId();

  function onKeyDown(event: KeyboardEvent, index: number) {
    const move = { ArrowRight: 1, ArrowLeft: -1 }[event.key];
    if (!move) return;
    event.preventDefault();
    const next = tabs[(index + move + tabs.length) % tabs.length];
    onSelect(next.id);
    refs.current[next.id]?.focus();
  }

  return (
    <div className="tabs" role="tablist" aria-label={label}>
      {tabs.map((tab, index) => (
        <button
          key={tab.id}
          id={`${baseId}-${tab.id}`}
          ref={(element) => {
            refs.current[tab.id] = element;
          }}
          type="button"
          role="tab"
          className="tab"
          aria-selected={tab.id === active}
          tabIndex={tab.id === active ? 0 : -1}
          onClick={() => onSelect(tab.id)}
          onKeyDown={(event) => onKeyDown(event, index)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export function Field({
  label,
  hint,
  error,
  children,
}: {
  label: string;
  hint?: ReactNode;
  error?: string | null;
  children: ReactNode;
}) {
  return (
    <label className="field" data-invalid={error ? "true" : undefined}>
      <span className="field-label">{label}</span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
      {error && <span className="field-error">{error}</span>}
    </label>
  );
}

export function Notice({
  tone,
  title,
  children,
  action,
}: {
  tone: Tone;
  title?: string;
  children?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div
      className="notice"
      data-tone={tone}
      role={tone === "bad" ? "alert" : "status"}
    >
      <div className="notice-body">
        {title && <p className="notice-title">{title}</p>}
        {children && <div className="notice-text">{children}</div>}
      </div>
      {action}
    </div>
  );
}

/** Shows a failed action's server message, including field-level details. */
export function ActionError({
  error,
  onReload,
}: {
  error: Error | null;
  onReload?: () => void;
}) {
  if (!error) return null;
  const conflict = error instanceof ApiError && error.status === 409;
  const denied = error instanceof ApiError && error.status === 403;
  const details = error instanceof ApiError ? error.details : [];
  return (
    <Notice
      tone="bad"
      title={
        denied
          ? "Your role cannot do this"
          : conflict
            ? "This was not saved"
            : undefined
      }
      action={
        conflict && onReload ? (
          <button type="button" className="btn btn-sm" onClick={onReload}>
            Reload
          </button>
        ) : undefined
      }
    >
      <p>{error.message}</p>
      {details.length > 0 && (
        <ul className="plain-list">
          {details.map((detail) => (
            <li key={`${detail.field}:${detail.message}`}>
              <span className="mono">{detail.field}</span>: {detail.message}
            </li>
          ))}
        </ul>
      )}
    </Notice>
  );
}

export function Progress({
  value,
  max,
  label,
}: {
  value: number;
  max: number;
  label: string;
}) {
  return (
    <span className="progress">
      <span className="progress-track">
        <span
          className="progress-fill"
          style={{ width: max ? `${(value / max) * 100}%` : "0%" }}
        />
      </span>
      <span className="num progress-label">{label}</span>
    </span>
  );
}

export function BarList({
  items,
}: {
  items: { label: string; count: number }[];
}) {
  const max = Math.max(1, ...items.map((item) => item.count));
  return (
    <ul className="bars">
      {items.map((item) => (
        <li key={item.label} className="bar-row">
          <span className="bar-label">{item.label}</span>
          <span className="bar-track" aria-hidden="true">
            <span
              className="bar-fill"
              style={{ width: `${(item.count / max) * 100}%` }}
            />
          </span>
          <span className="num bar-count">{item.count}</span>
        </li>
      ))}
    </ul>
  );
}

export function Facts({ items }: { items: [string, ReactNode][] }) {
  return (
    <dl className="facts">
      {items.map(([term, value]) => (
        <div key={term} className="fact">
          <dt>{term}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

export function Stat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="stat">
      <span className="stat-value num">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

/** Mandatory wrapper for anything a model produced. */
export function AdvisoryPanel({
  model,
  isStub,
  title,
  children,
}: {
  model: string;
  isStub: boolean;
  title?: string;
  children: ReactNode;
}) {
  return (
    <div className="advisory">
      <div className="advisory-head">
        <span className="advisory-tag">Advisory</span>
        {title && <span className="advisory-title">{title}</span>}
        <span className="advisory-meta">
          Model <span className="mono">{model}</span>
        </span>
        {isStub && <span className="advisory-stub">Offline rules, not AI</span>}
      </div>
      <div className="advisory-body">{children}</div>
    </div>
  );
}

export function EvidenceCard({ evidence }: { evidence: Evidence }) {
  const facts = Object.entries(evidence.observed);
  return (
    <article className="evidence" data-result={evidence.result}>
      <header className="evidence-head">
        <h3>{checkLabel(evidence.check_type)}</h3>
        <EvidenceBadge result={evidence.result} />
      </header>
      <p className="evidence-reason">
        {reasonText(evidence.reason_code)}{" "}
        <span className="mono muted">{evidence.reason_code}</span>
      </p>
      {facts.length > 0 ? (
        <dl className="observed">
          {facts.map(([key, value]) => (
            <div key={key}>
              <dt>{humanize(key)}</dt>
              <dd className="mono">{factValue(value)}</dd>
            </div>
          ))}
        </dl>
      ) : (
        <p className="muted small">No facts were observed.</p>
      )}
      <p className="evidence-meta">
        Checked{" "}
        <time dateTime={evidence.checked_at}>
          {formatDateTime(evidence.checked_at)}
        </time>
        {" · "}
        <span className="mono">{evidence.id}</span>
        {" · "}Policy{" "}
        <span className="mono">
          {evidence.policy_id} v{evidence.policy_version}
        </span>
        {" · "}Profile v{evidence.profile_version}
      </p>
    </article>
  );
}
