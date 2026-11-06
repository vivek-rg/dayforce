import { useState } from "react";
import { api } from "../../shared/api";
import type { Hire, Plan } from "../../shared/api-types";
import {
  formatDate,
  humanize,
  locationLabel,
  onboardingTone,
} from "../../shared/format";
import { type Resource, useResource } from "../../shared/hooks";
import { planLedger } from "../../shared/logic";
import { type HireTab, hireHref } from "../../shared/routes";
import { useUser } from "../../shared/session-context";
import {
  Badge,
  DataState,
  Facts,
  LedgerRail,
  PageHeader,
  Tabs,
} from "../../shared/ui";
import { DocumentsTab } from "./DocumentsTab";
import { EditHire } from "./EditHire";
import { EvidenceTab } from "./EvidenceTab";
import { HistoryTab } from "./HistoryTab";
import { InvestigationTab } from "./InvestigationTab";
import { LocationChange } from "./LocationChange";
import { PlanTab } from "./PlanTab";
import { TimelineTab } from "./TimelineTab";

const TABS: { id: HireTab; label: string }[] = [
  { id: "plan", label: "Plan" },
  { id: "timeline", label: "Timeline" },
  { id: "evidence", label: "Evidence" },
  { id: "documents", label: "Documents" },
  { id: "investigation", label: "Investigation" },
  { id: "history", label: "History" },
];

function Summary({ hire, plan }: { hire: Hire; plan: Resource<Plan> }) {
  return (
    <div className="profile-summary">
      <Facts
        items={[
          ["Employee code", <span className="mono">{hire.employee_code}</span>],
          ["Designation", hire.designation],
          ["Role", humanize(hire.role)],
          ["Worker type", humanize(hire.worker_type)],
          [
            "Location",
            `${locationLabel(hire.location_id)} (${hire.work_mode})`,
          ],
          [
            "Start date",
            <span className="num">{formatDate(hire.start_date)}</span>,
          ],
          ["Work email", hire.work_email],
          ["Employment", humanize(hire.employment_status)],
        ]}
      />
      <div className="profile-ledger">
        <h2 className="eyebrow">Claimed vs proven</h2>
        {plan.data ? (
          <LedgerRail ledger={planLedger(plan.data.tasks)} />
        ) : (
          <p className="muted small">
            {plan.error ? "Plan unavailable." : "Loading plan."}
          </p>
        )}
      </div>
    </div>
  );
}

export function HireWorkspacePage({
  hireId,
  tab,
}: {
  hireId: string;
  tab: HireTab;
}) {
  const user = useUser();
  const hire = useResource(`hire:${hireId}`, (signal) =>
    api.hire(hireId, signal),
  );
  const plan = useResource(`plan:${hireId}`, (signal) =>
    api.plan(hireId, signal),
  );
  const [proposing, setProposing] = useState(false);
  const [editing, setEditing] = useState(false);

  function reloadAll() {
    hire.reload();
    plan.reload();
  }

  return (
    <DataState resource={hire} rows={8}>
      {(data) => (
        <>
          <p className="crumb">
            <a href="#/hires">Employees</a>
          </p>
          <PageHeader
            title={data.display_name}
            description={
              <Badge tone={onboardingTone(data.onboarding_status)}>
                Onboarding: {humanize(data.onboarding_status)}
              </Badge>
            }
            actions={
              user.role === "HR" && (
                <>
                  <button
                    type="button"
                    className="btn"
                    aria-expanded={editing}
                    onClick={() => setEditing((value) => !value)}
                  >
                    Edit details
                  </button>
                  <button
                    type="button"
                    className="btn"
                    aria-expanded={proposing}
                    onClick={() => setProposing((value) => !value)}
                  >
                    Propose location change
                  </button>
                </>
              )
            }
          />
          {editing && (
            <EditHire
              key={data.profile_version}
              hire={data}
              onSaved={() => {
                setEditing(false);
                reloadAll();
              }}
            />
          )}
          {proposing && (
            <LocationChange
              hire={data}
              plan={plan.data}
              onChanged={reloadAll}
            />
          )}
          <Summary hire={data} plan={plan} />
          <Tabs
            label="Employee profile"
            tabs={TABS}
            active={tab}
            onSelect={(next) => {
              window.location.hash = hireHref(hireId, next as HireTab);
            }}
          />
          <div className="tab-panel" role="tabpanel" aria-label="Selected tab">
            {tab === "plan" && <PlanTab plan={plan} onChanged={reloadAll} />}
            {tab === "timeline" && <TimelineTab plan={plan} hire={data} />}
            {tab === "evidence" && <EvidenceTab hireId={hireId} plan={plan} />}
            {tab === "documents" && <DocumentsTab hireId={hireId} />}
            {tab === "investigation" && (
              <InvestigationTab hireId={hireId} onChanged={reloadAll} />
            )}
            {tab === "history" && <HistoryTab hireId={hireId} />}
          </div>
        </>
      )}
    </DataState>
  );
}
