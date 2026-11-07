# Data model v2 — current storage guide

**Authority:** [backend/app/shared/schema.sql](../backend/app/shared/schema.sql) defines exact columns, constraints, indexes and views. [contracts.py](../backend/app/shared/contracts.py) defines wire shapes; [API_SPEC.md](API_SPEC.md) is generated. This explanatory guide changes no schema or API. It replaces obsolete foundation-only/checkpointer prose.

One fictional company per installation, standard-library SQLite, independent local files per teammate. Setup, private uploads/backups and hosting limits live in the [root guide](../README.md#data-and-backups); all unfinished work lives in [the active plan](decisions/2026-11-07-improvement-plan.md).

## Conventions and initialization

- Application-generated opaque TEXT IDs, ISO date strings and UTC timestamps; JSON columns use json_valid checks, but syntax validity is not authorization or semantic validation.
- Numeric versions are positive; source creation uses the contract’s expected_version=0 convention. Public enums/fields come from Pydantic, not a second handwritten type system.
- shared.db.connect enables foreign keys and a five-second lock timeout; per-operation connections commit on success, roll back on failure and close. Parameterized SQL only. Never hold a transaction across inference/network/human waits.
- Startup initializes schema and one app_info row with **schema_version=2**. It does not seed users or hires. Explicit fixtures/seed.py populates an empty synthetic installation and refuses existing users.
- An empty v1 database may be rebuilt; v1 business data and unsupported/newer schemas are refused. There is no general migration runner. Never delete/reseed working data as an upgrade.
- DB and uploads are private ignored files. Agent state is in application tables: **there is no runtime LangGraph checkpoint database or CHECKPOINT_PATH**.

## Table groups

This is a responsibility map, not a duplicate column-by-column schema.

| Tables                                                      | Stored responsibility and important relationship                                                                                                      |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| app_info                                                    | Singleton product/schema identity; readiness checks schema version                                                                                    |
| users, sessions, user_scopes                                | User email/display name/role/password hash/active flag; hashed expiring bearer sessions; explicit user-to-hire scope                                  |
| login_attempts, password_resets                             | Login failure/lockout and one open HR-mediated reset request per user                                                                                 |
| departments, hires                                          | Employee identity/profile, linked account/manager/department, start/location/work mode/status and profile/plan versions                               |
| policies                                                    | Append-versioned approved rule pack, effective dates, scope/sections/rules JSON and approver                                                          |
| tasks, task_dependencies                                    | Owned category/rule tasks, due dates/priority/check type/work state/version and prerequisite graph; unique hire/logical_key                           |
| source_records                                              | Separately versioned source facts, category/source identity, observation time and updating actor; unassigned inventory may have null hire             |
| evidence                                                    | Append-only checked receipts referencing hire/case/source version, profile/policy version, result/reason/observed facts/time/expiry                   |
| documents, document_reviews                                 | Private storage key/hash/size/MIME/name, upload/review state and version; human review history; duplicate hire/category/hash constraint               |
| document_extractions                                        | Advisory fields/missing/mismatch/summary linked to a document and AI run—not a human verification                                                     |
| knowledge_documents, knowledge_chunks, knowledge_chunks_fts | Approved/versioned access-controlled knowledge and section/chunk references; FTS5 porter/unicode61 index, not vector embeddings                       |
| hr_escalations                                              | Unsupported assistant question, raiser, optional AI run and human resolution                                                                          |
| cases, case_steps                                           | Scoped case kind/state/opening actor/version, persisted model/read counters and ordered steps; at most one nonterminal case per hire                  |
| questions                                                   | Intended recipient, dedupe key, question/state/answer/actor/time; unique case/key                                                                     |
| proposals                                                   | Immutable CHANGE_WORK_LOCATION or RESERVE_EQUIPMENT payload, supporting evidence IDs, expected versions, optional plan diff, reviewer role and expiry |
| decisions                                                   | One immutable reviewer decision/note per proposal                                                                                                     |
| actions                                                     | Stable unique proposal/action identity, state/attempts/read-back observed facts                                                                       |
| work_items                                                  | Stable unique event ID, case/kind/action link, state/attempts/retry time for worker admission/resume/execution                                        |
| audit_events                                                | Stable unique event identity and scoped sanitized domain summary with optional actor/case/action links                                                |
| ai_runs                                                     | Operation/prompt version/provider/model, scoped references/chunks, validation/status/failure, attempts/token counts/latency; not full prompt storage  |
| notifications                                               | Intended user and optional hire/task, type/body/read time and per-user dedupe key                                                                     |

Schema categories include documents, equipment, it_access, payroll, benefits, training and manager. Product onboarding covers six official areas, with IT access alongside equipment; seven categories are not seven AI agents.

Read-only views equipment_assets_v, payroll_status_v, benefits_enrolments_v and training_assignments_v project source_records JSON. They are **not** external system integrations or independently synchronized stores. View columns do not add accepted write fields to an API. Payroll stores sanitized status flags, not actual financial account values.

## Evidence and state semantics

- Task progress: PENDING / WAITING_DEPENDENCY / IN_PROGRESS / COMPLETED / CANCELLED. Completing an owned task requires valid version/state/prerequisites; it does not manufacture source records.
- Evidence: VERIFIED / BLOCKED / UNKNOWN / NOT_APPLICABLE. Freshness depends on relevant versions/expiry; retain old receipts rather than rewriting them into current truth. Missing/stale/unavailable evidence is UNKNOWN. A real supported mismatch is BLOCKED; not-applicable needs an approved rule.
- Documents: SUBMITTED / UNDER_REVIEW / VERIFIED / REJECTED / RESUBMISSION_REQUESTED / SUPERSEDED. Only a permitted human review verifies a document; extraction is advisory. Private file content is not served through the static asset tree.
- Cases: OPEN / INVESTIGATING / WAITING_HUMAN / WAITING_APPROVAL / EXECUTING / RESOLVED / ESCALATED. These are supported states, not a promise every transition is allowed. Resolving a reservation investigation does not imply onboarding or handover completion.
- Work items: PENDING / RUNNING / DONE / FAILED. The worker claims/reconciles stored work, not an in-memory-only conversation. Persisted counters and stable IDs protect resumed work; the current active-time deadline is recomputed for a run segment, not a persisted whole-case SLA.
- Actions: PENDING / RUNNING / SUCCEEDED / FAILED / UNKNOWN. Approval queues execution; it is not success. The current scope/actor/versions/expiry/decision must still be valid at execution. Local source mutation, result and audit use conditional transactions and read-back. Future external effects need reconciliation; no distributed exactly-once guarantee.

### Exact JSON and referential validation

Source payloads correspond to the canonical SourcePayload union, including the category discriminant. Proposal payload_json corresponds to ActionPayload and action_type; expected_versions_json to ExpectedVersions; evidence_ids_json is a scoped array; plan_diff_json follows PlanDiff. Do not invent a new document/payroll/equipment JSON schema in prose or cast extra fields around Pydantic.

JSON-valid IDs still need application-level existence, hire scope, source/evidence meaning and version checks. Cross-hire or unrelated evidence cannot justify a proposal. A location change previews affected future work, preserves unrelated completed work/history and invalidates relevant checks. Reservation needs the exact equipment source/version; reserving does not write a handover event.

## Internal service seams and authorization

Implemented functions are in auth/service.py and permissions.py (identity/scope), planning/service.py (plan/location preview), evidence/service.py (checks), actions/service.py (proposal/execution), agent/tools.py (read dispatch) and agent/model_client.py (typed next step). They are not foundation stubs. Use their actual source signatures; do not copy an old planned signature into a caller. Shared seam changes require integrator/affected-owner review.

InvestigationContext is established by trusted code from current identity, hire and case. It is not authority supplied by a model/browser. Tool observations separate structured facts/evidence from untrusted source prose. Current identity/scope is revalidated on resume/read/execution; privileged transcripts are not lower-role response payloads.

AI-run logging stores references/measurements rather than complete prompts, but persisted case steps can include permitted untrusted synthetic text and human answers. The full DB, documents and stopped backups therefore remain private. Never put real credentials/identity/bank/medical data in fixtures, logs, screenshots or source.

## Persistence and change gate

The application DB owns questions, answers, budgets, proposal/decision/action identities, waits and audit history. A DB-only backup is incomplete because documents live in a sibling directory. File persistence and SQLite transactions are not one atomic storage system; a crash can leave orphan files. Preserve and reconcile them rather than deleting blindly.

No schema change is included in this documentation consolidation. Any future migration or immutable model/config snapshot needs a reviewed versioned design, supported-source/rollback tests, stopped backup/restore evidence and regenerated contracts when wire fields change. Keep scope, evidence truth, human approvals and conditional write/read-back intact.
