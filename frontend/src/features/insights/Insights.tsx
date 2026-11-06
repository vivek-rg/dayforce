import { useState } from "react";
import { ApiError, api } from "../../shared/api";
import type { InsightSummary } from "../../shared/api-types";
import { useAction, useResource } from "../../shared/hooks";
import {
  ActionError,
  AdvisoryPanel,
  DataState,
  Notice,
  PageHeader,
  Section,
} from "../../shared/ui";

export function InsightsPage() {
  const metrics = useResource("insights", (signal) =>
    api.insightMetrics(signal),
  );
  const [summary, setSummary] = useState<InsightSummary | null>(null);
  const action = useAction();
  const unavailable =
    action.error instanceof ApiError && action.error.code === "AI_UNAVAILABLE";

  async function generate() {
    const result = await action.run(() => api.insightSummary());
    if (result.ok) setSummary(result.value);
  }

  return (
    <>
      <PageHeader
        title="AI insights"
        description="Numbers come from application data, not a model. A model may only phrase them."
        actions={
          <button
            type="button"
            className="btn"
            disabled={action.pending}
            onClick={() => void generate()}
          >
            {action.pending ? "Generating" : "Generate AI summary"}
          </button>
        }
      />
      {unavailable ? (
        <Notice tone="info" title="No AI summary right now">
          {action.error?.message}
        </Notice>
      ) : (
        <ActionError error={action.error} />
      )}
      {summary && (
        <AdvisoryPanel
          model={summary.model}
          isStub={summary.is_stub}
          title="Summary"
        >
          <p>{summary.summary}</p>
          {summary.recommendations.length > 0 && (
            <>
              <h4 className="eyebrow">Recommendations</h4>
              <ul className="plain-list stack-sm">
                {summary.recommendations.map((item) => (
                  <li key={item.text}>
                    {item.text}{" "}
                    <span className="mono muted small">
                      {item.evidence_refs.join(", ")}
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
          <p className="muted small">
            Run <span className="mono">{summary.ai_run_id}</span>. A person
            decides what to do.
          </p>
        </AdvisoryPanel>
      )}
      <Section
        title="Computed metrics"
        description="Always available, with AI on or off."
      >
        <DataState
          resource={metrics}
          isEmpty={(data) => data.metrics.length === 0}
          empty="No metrics yet."
        >
          {(data) => (
            <ul className="metric-list">
              {data.metrics.map((metric) => (
                <li key={metric.id} className="metric">
                  <span className="metric-value num">{metric.value}</span>
                  <div className="metric-body">
                    <p className="metric-label">{metric.label}</p>
                    {metric.evidence.length > 0 ? (
                      <details>
                        <summary className="small">
                          Evidence ({metric.evidence.length}
                          {metric.value > metric.evidence.length
                            ? ` of ${metric.value}`
                            : ""}
                          )
                        </summary>
                        <ul className="plain-list">
                          {metric.evidence.map((item) => (
                            <li key={item.ref}>
                              {item.label}{" "}
                              <span className="mono muted small">
                                {item.ref}
                              </span>
                            </li>
                          ))}
                        </ul>
                      </details>
                    ) : (
                      <p className="muted small">
                        No records behind this number.
                      </p>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </DataState>
      </Section>
    </>
  );
}
