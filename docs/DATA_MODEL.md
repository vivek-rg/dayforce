# Data model v2

> **Revision R06.** Schema v2 adds `departments`, `documents`, `document_reviews`, `document_extractions`, `knowledge_documents`, `knowledge_chunks`, `knowledge_chunks_fts`, `ai_runs`, `hr_escalations`, `notifications`, `case_steps`, `login_attempts`, and read-only views over `source_records` (`equipment_assets_v`, `payroll_status_v`, `benefits_enrolments_v`, `training_assignments_v`). `hires`, `tasks`, `cases` and `work_items` gained columns, and categories gained `it_access`. `backend/app/shared/schema.sql` is the authority. An empty v1 file rebuilds automatically; one holding business rows is refused. The foundation text below still applies where it doesn't conflict. The LangGraph checkpoint section is replaced: application tables hold all agent state.

The executable initial schema is [`../backend/app/shared/schema.sql`](../backend/app/shared/schema.sql). It is applied on startup and covered by tests. Wire payloads/enums/bounds are defined in `backend/app/shared/contracts.py` and exhaustively rendered in `API_SPEC.md`. The foundation creates **no** users, hires, policies or business source records; only app_info is seeded. Feature implementation must not confuse schema presence with completed persistence behavior.

**Confirmed deployment decision:** SQLite remains the current engine for the user-selected local demo. All eight teammates use the same schema/fixture revision on independent local files. This explanation changes no table or wire contract. Cloud PostgreSQL (Neon/Supabase) would require reviewed SQL/driver/config/checkpointer changes, migrations and regression evidence; it is not enabled by changing DATABASE_PATH to a URL. See [database decision](DATABASE_DECISION.md). Migrations are required for evolving schemas on any engine; P26 owns that gate.

## Conventions

One fictional company per installation; no tenant claim. All IDs except singleton app_info are application-generated opaque text (suggest UUID hex with prefixes). Dates use `YYYY-MM-DD`; timestamps canonical UTC `YYYY-MM-DDTHH:MM:SSZ`. SQLite stores these as TEXT and booleans as constrained 0/1. Public versions are integers >=1; a source create request uniquely uses expected_version=0. JSON columns use `CHECK(json_valid(...))`; typed validation and referential/semantic checks still happen in application code. Store normalized scalar fields for authorization, ownership, versions and states; JSON is not an arbitrary update engine.

Use `shared.db.connect()` (foreign keys ON, 5-second busy timeout, parameterized SQL). Each context commits on success/rolls back on failure and closes its connection. Never share a connection across worker threads or hold a transaction across inference/human waits. Default journal mode is adequate for one local worker; WAL is optional after measurement, never a substitute for conditional writes. All database/checkpoint files are ignored and stored under `.runtime/` on local persistent disk.

## Tables and ownership

The exact columns, nullability, keys, checks and foreign keys are in schema.sql; this ledger explains every column group and JSON format.

| Table | Columns / meaning | Owner |
|---|---|---|
| app_info | id=1 PK; project_name; schema_version=1 | P01/Track 1; sole seeded row |
| users | id PK; display_name; role enum; password_hash; active boolean | P02 |
| user_scopes | (user_id, hire_id) composite PK/FKs | P02; explicit authorization grant, HR not globally exempt |
| sessions | token_hash PK; user_id FK; expires_at UTC | P02; raw bearer tokens never persisted |
| hires | id PK; display_name; worker_type; role; location_id; work_mode; start_date; manager_user_id FK; nullable unique employee_user_id FK; profile_version; plan_version | P03; role/location enums in contract |
| policies | (id, version) PK; approved_by FK; effective_from/to; scope_json; sections_json; rules_json | P03; manual review before seed, append versions |
| tasks | id PK; hire_id FK; logical_key; category; title; owner_user_id FK; policy_id/version composite FK; rule_id; due_date; critical; work_state; version | P03; UNIQUE(hire_id,logical_key) |
| task_dependencies | (task_id, prerequisite_task_id) PK and task FKs, no self edge | P03; validate same hire and entire DAG acyclic |
| source_records | id PK; nullable hire_id FK (null for unassigned inventory); category; source_system; external_id; version; payload_json; observed_at; updated_by FK | P03; UNIQUE(source_system,external_id), separate from task claim |
| cases | id PK; hire_id FK; opened_by FK; message; state; unique thread_id; model_calls; tool_calls; version; created_at | P04; at most one active case/hire in MVP |
| evidence | id PK; hire_id FK; nullable case_id/source_record_id FKs; check_type; nullable source_version; profile_version; policy_id/version FK; result; reason_code; observed_json; checked_at; nullable expires_at | P03; append historical receipts |
| questions | id PK; case_id FK; dedupe_key; recipient_user_id FK; text; state; nullable answer/answered_by FK/answered_at | P04; UNIQUE(case_id,dedupe_key) |
| proposals | id PK; case_id FK; action_type; payload_json; evidence_ids_json; expected_versions_json; nullable plan_diff_json; reviewer_role; expires_at; created_at | P05; immutable after creation |
| decisions | proposal_id PK/FK; reviewer_user_id FK; decision; note; created_at | P05; one immutable decision/proposal |
| actions | id PK; unique proposal_id FK; state; observed_json; attempts; updated_at | P05; stable identity before effect |
| work_items | id PK; unique event_id; case_id FK; kind; state; attempts; nullable retry_at; updated_at | P04; persisted admission before graph call |
| audit_events | id PK; unique event_id; hire_id FK; nullable case_id/actor_user_id/action_id FKs; event_type; summary; created_at | Every service through P05 audit seam; sanitized summaries only |

## JSON records: exact supported shapes

Source payloads map **one-to-one** to API `SourcePayload`; do not maintain a second shape. Examples:

```json
{"category":"equipment","asset_tag":"LAPTOP_22","location_id":"BLR-DEMO","state":"RESERVED","assignee_hire_id":"H001","handover_at":null}
```

```json
{"category":"payroll","profile_created":true,"setup_confirmed":false}
```

Document payload: category, text, review_state (SUBMITTED/REVIEWED). Benefits: category, state (NOT_INVITED/INVITED/ENROLLED/DECLINED). Training: category, course_id, state (ASSIGNED/COMPLETED). Manager: category, buddy_user_id, first_week_plan. See API_SPEC for required/nullable fields and per-category authority. No salary, account, tax ID or medical fields exist.

Policy pack, reviewed before import:

```json
{
  "id":"NORTHSTAR_ONBOARDING","version":1,"approved_by":"U_HR",
  "effective_from":"2026-01-01","effective_to":null,
  "scope":{"locations":["HYD-DEMO","BLR-DEMO"],"worker_types":["employee","contractor"],"roles":["engineer","operations_associate"]},
  "sections":[{"id":"EQUIPMENT_1","text":"Office equipment handover needs IT confirmation; reservation is not handover."}],
  "rules":[{"id":"HANDOVER","category":"equipment","title":"Record equipment handover","when":{"worker_type":"employee","work_mode":"office"},"owner_role":"IT","due_calendar_days_before_start":0,"depends_on":[],"required_check":"device_handover_recorded","critical":true,"policy_section_id":"EQUIPMENT_1"}]
}
```

JSON columns store scope/sections/rules values, not the enclosing pack fields. This is a shape example, **not** a sufficient six-category approved pack. P03 must supply about 10–12 supported rules and validate IDs, conditions, ownership, dependencies and no overlapping conflicting applicability. No eval/exec or invented legislation. Required checks are supported named Python predicates, never executable text.

Proposal payload_json is exactly API `ActionPayload`, including action_type. SQL action_type must match it. expected_versions_json is API `ExpectedVersions`:

```json
{"profile_version":3,"plan_version":1,"policy_id":"NORTHSTAR_ONBOARDING","policy_version":1,"source_record_id":"EQ22","source_version":7}
```

evidence_ids_json is a JSON array of scoped immutable evidence IDs. plan_diff_json is null or API `PlanDiff` (create task-title strings, cancel/preserve task IDs, invalidate_checks evidence IDs). A location proposal needs a concrete diff; reservation may use null. Source/versions must be both null or both present; reservation requires both and must reference payload equipment_record_id. Cross-hire/cross-source evidence cannot support a proposal. IDs in JSON require application-level scope/existence/meaning validation; SQL JSON validity does not enforce these references.

observed_json in evidence/actions is a sanitized object of string/number/boolean/null facts (same shape as Evidence.observed); no raw model reasoning. Audit summary is limited to 500 characters. No secret/private data in audit context.

## Lifecycle and hard invariants

- Task state: PENDING / WAITING_DEPENDENCY / IN_PROGRESS / COMPLETED / CANCELLED. Complete requires configured prerequisites, owner and expected version; never rewrites a source record.
- Check result: VERIFIED / BLOCKED / UNKNOWN / NOT_APPLICABLE, independent of task state. Freshness is computed from relevant profile/source/policy versions and expiry; don't mutate a historical receipt to change its result. Dashboard uses only currently applicable checks.
- Case: OPEN → INVESTIGATING → WAITING_HUMAN or WAITING_APPROVAL → INVESTIGATING/EXECUTING → RESOLVED or ESCALATED. A resolved reservation case may still have an incomplete handover task. Late answers or invalid transitions return 409.
- Work: PENDING → RUNNING → DONE or FAILED; on crash reclaim/reconcile uncertain work before retry. Durable unique event IDs keep replay from creating duplicate questions/actions. Only one active case run at a time.
- Action: PENDING → RUNNING → SUCCEEDED / FAILED / UNKNOWN. Persist ID before attempt; write conditional state change, action outcome and sanitized audit atomically for local sources. Read back; no success solely from a model statement. A local update with wrong expected version must affect zero rows and produce a conflict, never an overwrite.
- Approved location change updates profile + affected future plan + version increments atomically, preserves completed unrelated work and history, invalidates relevant evidence, and cancels superseded future work. Never delete old payroll/document/equipment facts.
- No schema cascades silently delete user history. No destructive seed/reset command is supplied. Demo seed must refuse a nonempty business database. New incompatible schema requires a numbered, reviewed migration under shared/ plus updated version/tests; CREATE IF NOT EXISTS is not a migration strategy.

## Identity and cross-module seams

P02 exposes `require_user()` as the FastAPI authentication dependency returning shared `User`, and `require_hire_scope(user, hire_id)` raising sanitized errors. Owners must call authorization before data/model context is loaded. Category-specific fields remain separately filtered after hire access.

P03 exposes `create_plan(Connection, Hire) -> Plan`, `preview_location_change(Connection, hire_id, Location) -> PlanDiff`, and `check_hire(Connection, hire_id) -> list[Evidence]`. P05 exposes `save_proposal(Connection, InvestigationContext, ActionPayload, evidence_ids) -> Proposal` and `execute_approved_action(action_id) -> ActionResult`. P04's worker calls the executor only for queued approved actions. `dispatch_read(tool_name, InvestigationContext) -> ToolObservation` and `generate_next_step(messages, schema) -> NextStep` freeze the agent boundary. These seams currently raise NotImplementedError; their shared return types are already defined, not private second DTOs. Track 1 reviews any signature change.

InvestigationContext contains the server-established User, hire_id and case_id; it is never accepted as authority from a browser/model. ToolObservation contains sanitized evidence/facts plus explicitly untrusted text. ActionResult contains stable action_id, exact state, sanitized observed facts and resulting evidence; a worker must not equate an absent/UNKNOWN result with success. These are internal models in the generated contract appendix, not public endpoints. Revalidate the context's current authority at each use rather than trusting its old User snapshot.

## Checkpoint boundary

LangGraph framework-owned tables live in CHECKPOINT_PATH, not schema.sql. SQLite checkpointer writes and app database writes are **not one transaction**. Application questions, decisions, action IDs and budgets are authoritative. P04 must reconcile the gap using stable event IDs and fresh current permission/context. Do not add checkpointer internals or transcripts to public APIs.
