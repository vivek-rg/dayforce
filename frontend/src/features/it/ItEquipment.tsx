import { useState } from "react";
import { type SourceOf, api } from "../../shared/api";
import type { Hire, Proposal } from "../../shared/api-types";
import { accessItemLabel, humanize, locationLabel } from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import { hireHref } from "../../shared/routes";
import { useUser } from "../../shared/session-context";
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

type Device = SourceOf<"equipment">;
type Access = SourceOf<"it_access">;

function stateTone(state: Device["payload"]["state"]) {
  if (state === "HANDED_OVER") return "ok";
  if (state === "RESERVED") return "warn";
  return "info";
}

function HandoverControl({
  device,
  onChanged,
}: {
  device: Device;
  onChanged: () => void;
}) {
  const [confirming, setConfirming] = useState(false);
  const action = useAction();
  const hireId = device.hire_id;
  if (!hireId) return null;

  async function record(hire: string) {
    const result = await action.run(() =>
      api.writeSource(hire, device.id, {
        expected_version: device.version,
        payload: {
          ...device.payload,
          state: "HANDED_OVER",
          assignee_hire_id: hire,
          handover_at: new Date().toISOString(),
        },
      }),
    );
    setConfirming(false);
    if (result.ok) onChanged();
  }

  return (
    <div className="row-action">
      {confirming ? (
        <>
          <span className="small">The person has collected it?</span>
          <button
            type="button"
            className="btn btn-sm btn-primary"
            disabled={action.pending}
            onClick={() => void record(hireId)}
          >
            Confirm handover
          </button>
          <button
            type="button"
            className="btn btn-sm"
            onClick={() => setConfirming(false)}
          >
            Cancel
          </button>
        </>
      ) : (
        <button
          type="button"
          className="btn btn-sm"
          onClick={() => setConfirming(true)}
        >
          Record handover
        </button>
      )}
      <ActionError error={action.error} onReload={onChanged} />
    </div>
  );
}

function ProvisionControl({
  record,
  onChanged,
}: {
  record: Access;
  onChanged: () => void;
}) {
  const action = useAction();
  const hireId = record.hire_id;
  if (!hireId) return null;

  async function mark(hire: string) {
    const result = await action.run(() =>
      api.writeSource(hire, record.id, {
        expected_version: record.version,
        payload: { ...record.payload, state: "PROVISIONED" },
      }),
    );
    if (result.ok) onChanged();
  }

  return (
    <div className="row-action">
      <button
        type="button"
        className="btn btn-sm"
        disabled={action.pending}
        onClick={() => void mark(hireId)}
      >
        Mark provisioned (simulated)
      </button>
      <ActionError error={action.error} onReload={onChanged} />
    </div>
  );
}

function RequestForm({
  hires,
  devices,
  onChanged,
}: {
  hires: Hire[];
  devices: Device[];
  onChanged: () => void;
}) {
  const [hireId, setHireId] = useState("");
  const [deviceId, setDeviceId] = useState("");
  const [created, setCreated] = useState<Proposal | null>(null);
  const action = useAction();
  const hire = hires.find((item) => item.id === hireId);
  const available = devices.filter(
    (item) =>
      item.hire_id === null &&
      item.payload.state === "AVAILABLE" &&
      item.payload.location_id === hire?.location_id,
  );

  async function submit() {
    setCreated(null);
    const result = await action.run(() =>
      api.equipmentRequest(hireId, deviceId),
    );
    if (result.ok) {
      setCreated(result.value);
      setDeviceId("");
      onChanged();
    }
  }

  return (
    <section className="form-panel" aria-label="Request a device">
      <h2 className="panel-title">Request a device</h2>
      <p className="muted small">
        A request creates a proposal for IT approval. It reserves nothing by
        itself.
      </p>
      <div className="form-grid">
        <Field label="Employee">
          <select
            className="input"
            value={hireId}
            onChange={(event) => {
              setHireId(event.target.value);
              setDeviceId("");
            }}
          >
            <option value="">Choose an employee</option>
            {hires.map((item) => (
              <option key={item.id} value={item.id}>
                {item.display_name} ({locationLabel(item.location_id)})
              </option>
            ))}
          </select>
        </Field>
        <Field
          label="Available device"
          hint={
            hire && available.length === 0
              ? `No device is available in ${locationLabel(hire.location_id)}.`
              : "Only devices at the employee's approved location are listed."
          }
        >
          <select
            className="input"
            value={deviceId}
            disabled={!hire}
            onChange={(event) => setDeviceId(event.target.value)}
          >
            <option value="">Choose a device</option>
            {available.map((item) => (
              <option key={item.id} value={item.id}>
                {item.payload.asset_tag}: {item.payload.asset_name}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <ActionError error={action.error} onReload={onChanged} />
      {created && (
        <Notice tone="info" title="Proposal created. Nothing is reserved yet.">
          It is waiting for {created.reviewer_role} in the{" "}
          <a href="#/review">Review inbox</a>.
        </Notice>
      )}
      <div className="form-actions">
        <button
          type="button"
          className="btn btn-primary"
          disabled={!hireId || !deviceId || action.pending}
          onClick={() => void submit()}
        >
          {action.pending ? "Requesting" : "Request device"}
        </button>
      </div>
    </section>
  );
}

const ACCESS_OPTIONS = [
  "CORPORATE_EMAIL",
  "VPN",
  "APPLICATION_ACCESS",
  "REQUIRED_SOFTWARE",
] as const;

function AccessRequestForm({
  hires,
  onChanged,
}: {
  hires: Hire[];
  onChanged: () => void;
}) {
  const [hireId, setHireId] = useState("");
  const [item, setItem] = useState<(typeof ACCESS_OPTIONS)[number]>("VPN");
  const [detail, setDetail] = useState("");
  const [done, setDone] = useState(false);
  const action = useAction();

  async function submit() {
    setDone(false);
    const result = await action.run(() =>
      api.accessRequest(hireId, { item, detail }),
    );
    if (result.ok) {
      setDone(true);
      setDetail("");
      onChanged();
    }
  }

  return (
    <section className="form-panel" aria-label="Request access">
      <h2 className="panel-title">Request access (simulated)</h2>
      <p className="muted small">
        This records a request. No real account or system is touched.
      </p>
      <div className="form-grid">
        <Field label="Employee">
          <select
            className="input"
            value={hireId}
            onChange={(event) => setHireId(event.target.value)}
          >
            <option value="">Choose an employee</option>
            {hires.map((hire) => (
              <option key={hire.id} value={hire.id}>
                {hire.display_name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Access">
          <select
            className="input"
            value={item}
            onChange={(event) =>
              setItem(event.target.value as (typeof ACCESS_OPTIONS)[number])
            }
          >
            {ACCESS_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {accessItemLabel(option)}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Detail (optional)">
          <input
            className="input"
            maxLength={200}
            value={detail}
            onChange={(event) => setDetail(event.target.value)}
          />
        </Field>
      </div>
      <ActionError error={action.error} onReload={onChanged} />
      {done && <Notice tone="info" title="Access request recorded." />}
      <div className="form-actions">
        <button
          type="button"
          className="btn btn-primary"
          disabled={!hireId || action.pending}
          onClick={() => void submit()}
        >
          {action.pending ? "Requesting" : "Request access"}
        </button>
      </div>
    </section>
  );
}

export function ItEquipmentPage() {
  const user = useUser();
  const isIt = user.role === "IT";
  const equipment = useResource("sources:equipment", (signal) =>
    api.sources("equipment", signal),
  );
  const access = useResource("sources:it_access", (signal) =>
    api.sources("it_access", signal),
  );
  const hires = useResource(isIt ? "hires" : null, (signal) =>
    api.hires(signal),
  );

  return (
    <>
      <PageHeader
        title="IT and equipment"
        description={
          isIt
            ? "Reserved means set aside. Only a recorded handover proves someone has the device."
            : "Read-only for HR. Only IT records changes. Reserved is not handed over."
        }
      />
      <Section title="Assets">
        <DataState
          resource={equipment}
          isEmpty={(data) => data.length === 0}
          empty="No equipment records."
        >
          {(data) => (
            <DataTable
              caption="Equipment assets"
              rowKey={(item) => item.id}
              rows={data}
              minWidth={isIt ? 960 : 800}
              columns={[
                {
                  header: "Asset ID",
                  render: (item) => (
                    <span className="mono">{item.payload.asset_tag}</span>
                  ),
                },
                {
                  header: "Name",
                  render: (item) => item.payload.asset_name || "Not set",
                },
                {
                  header: "Type",
                  render: (item) => item.payload.asset_type || "Not set",
                },
                {
                  header: "Serial",
                  render: (item) => (
                    <span className="mono">
                      {item.payload.serial_number || "Not set"}
                    </span>
                  ),
                },
                {
                  header: "Location",
                  render: (item) => locationLabel(item.payload.location_id),
                },
                {
                  header: "State",
                  render: (item) => (
                    <Badge tone={stateTone(item.payload.state)}>
                      {humanize(item.payload.state)}
                    </Badge>
                  ),
                },
                {
                  header: "Assignee",
                  render: (item) =>
                    item.hire_id ? (
                      <a href={hireHref(item.hire_id)}>
                        {item.hire_name ?? item.hire_id}
                      </a>
                    ) : (
                      <span className="muted">None</span>
                    ),
                },
                ...(isIt
                  ? [
                      {
                        header: "Action",
                        render: (item: Device) =>
                          item.payload.state === "RESERVED" ? (
                            <HandoverControl
                              device={item}
                              onChanged={equipment.reload}
                            />
                          ) : null,
                      },
                    ]
                  : []),
              ]}
            />
          )}
        </DataState>
      </Section>
      <Section
        title="Access requests"
        description="Simulated. No real system is contacted."
      >
        <DataState
          resource={access}
          isEmpty={(data) => data.length === 0}
          empty="No access requests."
        >
          {(data) => (
            <DataTable
              caption="Access requests"
              rowKey={(item) => item.id}
              rows={data}
              columns={[
                {
                  header: "Employee",
                  render: (item) =>
                    item.hire_id ? (
                      <a href={hireHref(item.hire_id)}>
                        {item.hire_name ?? item.hire_id}
                      </a>
                    ) : (
                      "None"
                    ),
                },
                {
                  header: "Item",
                  render: (item) => accessItemLabel(item.payload.item),
                },
                {
                  header: "Detail",
                  render: (item) => item.payload.detail || "None",
                },
                {
                  header: "State",
                  render: (item) => (
                    <Badge
                      tone={
                        item.payload.state === "PROVISIONED" ? "ok" : "warn"
                      }
                    >
                      {humanize(item.payload.state)}
                      {item.payload.state === "PROVISIONED" && " (simulated)"}
                    </Badge>
                  ),
                },
                ...(isIt
                  ? [
                      {
                        header: "Action",
                        render: (item: Access) =>
                          item.payload.state === "REQUESTED" ? (
                            <ProvisionControl
                              record={item}
                              onChanged={access.reload}
                            />
                          ) : null,
                      },
                    ]
                  : []),
              ]}
            />
          )}
        </DataState>
      </Section>
      {isIt && (
        <DataState resource={hires} rows={2}>
          {(data) => (
            <RequestForm
              hires={data.items}
              devices={equipment.data ?? []}
              onChanged={equipment.reload}
            />
          )}
        </DataState>
      )}
      {isIt && hires.data && (
        <AccessRequestForm hires={hires.data.items} onChanged={access.reload} />
      )}
    </>
  );
}
