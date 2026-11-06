# DayOne Proof — 28-phase build and verification board

## Read this before copying a prompt

**Working now:** P01 foundation only. **Planned:** P02–P28. Phase count means smaller accountable work packages, not extra services or a claim that all of this fits one sitting. Keep P01–P13 IDs so existing source TODOs/handoffs still make sense; P14–P28 extend the original plan. Follow dependencies, **not numeric order**.

For each phase: understand its problem → claim owner → follow the task list → copy its prompt → run checks → attach sanitized proof → update checklist/status. Use [TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md) for commands, SQLite, screenshots/PR evidence and the common prompt wrapper. Any valid branch name is allowed. No agent/tool is exempt from the same tests.

**Status vocabulary:** not started / in progress / blocked (reason + owner) / implemented, verification pending / done. `[x]` means the relevant check really passed. Stub transport tests never establish real-model quality. Record the commit, exact commands, fixture/schema/config versions and evidence link in CHANGES or the PR. No screenshots of `.env`, credentials or private employee data.

**Current documentation revision R01:** [x] provider/phase/team instructions expanded; verification results in CHANGES. This is a documentation task, not completion of any runtime phase. Write boundary: AGENTS.md, PHASES.md, CHANGES.md, README.md, docs/README.md, docs/ASSUMPTIONS.md, docs/PROVIDERS.md, docs/TEAM_WORKFLOW.md and fixtures/README.md only. Canonical contracts, runtime source, generated files and secrets are unchanged.

**Foundation review R02:** [x] setup/configuration review and handoff corrections verified; exact results and remaining limits in CHANGES.md and docs/VERIFICATION.md. Write boundary: .env.example, .gitignore, README.md, PHASES.md, CHANGES.md, backend/README.md, frontend/README.md, evals/README.md, docs/TEAM_WORKFLOW.md, docs/VERIFICATION.md and docs/SUBMISSION_CHECKLIST.md. No business features, canonical/generated contracts, dependencies, existing databases or private `.env` changes. Temporary verification artifacts stay outside the repository.

**Current policy revision R03:** [x] clarified provider/artifact scope and user-confirmed local-demo database decision documented and verified; results in CHANGES.md. Write boundary: .gitignore, .env.example, AGENTS.md, README.md, PHASES.md, CHANGES.md, backend/README.md, frontend/README.md, evals/README.md, fixtures/README.md, resume/README.md, video/README.md, video/VIDEO_LINK.md, ppt/README.md, docs/README.md, docs/ASSUMPTIONS.md, docs/DATA_MODEL.md (explanation only), docs/PROVIDERS.md, docs/TEAM_WORKFLOW.md, docs/DATABASE_DECISION.md, docs/DEMO_PLAN.md, docs/SUBMISSION_CHECKLIST.md and docs/VERIFICATION.md. Runtime source, canonical schema/types, generated contracts, existing databases and private .env remain unchanged. Historical CHANGES/verification entries and original source guide/PDF remain records, not current scope authority.

**Foundation CI fix R04:** [x] reproduced and fixed Python 3.12/3.13 HTTP 422 description drift; regression failed before the fix and all 16 backend tests pass on both interpreters afterward. Full npm check passes; hosted CI rerun is still required. Write boundary: backend/app/main.py (shared response description only), backend/tests/test_contracts.py, PHASES.md, CHANGES.md and docs/VERIFICATION.md; generated docs/API_SPEC.md, docs/openapi.json and frontend/src/shared/api-types.ts only via the existing exporter if regeneration actually changes them. Regeneration produced no file changes. No business behavior, dependency, schema, auth or provider changes.

**Foundation CI fix R05:** [x] repaired npm-generated Rollup/esbuild platform metadata without upgrading existing package versions; regression guard failed on the old lockfile and now passes. Full check and clean Windows frontend lint/tests/build passed; a Linux-targeted clean install contains the required GNU binaries, but hosted Ubuntu execution still needs rerunning. Write boundary: package-lock.json (npm-generated), package.json (lockfile check wiring only), scripts/check-lockfile.mjs, PHASES.md, CHANGES.md and docs/VERIFICATION.md. Remain on fix/portable-openapi-snapshot; no further branches. No runtime/business/API/schema/dependency-version changes.

## Dependency lanes and ownership

| Lane | Build order / who can start |
|---|---|
| Foundation | P01 done → all eight members replay setup; P14 prepares DB/fixture handoff after P03 |
| Core backend | P02 (Track 1), P03 (4), P04 (6), P05 (5) can develop isolated slices after P01; live authorization and cross-module checks wait for dependencies |
| Core UI | P06 (2), P07 (3) against frozen mocked contracts; integrated acceptance needs real backend |
| Provider contracts/data durability | P15 (1, reviewed by 6/7) → P26 if persistent changes are required → P16 (6); no private schema on adapter branches |
| Provider adapters | P16 → P17 local and P18 Groq/common transport → P19 Cerebras, P20 Mistral, P21 Gemini, P22 OpenRouter; separate adapter files may run in parallel only after explicit claims. P23 verifies shared free-tier/cost eligibility after those adapters |
| Model picker | P15/P16 + at least one tested adapter + P02 → P24 (2, root wiring by 1); P25 (7) evaluates all requested paths with available accounts |
| Quality | P08 drafts early; P09 integrates P02–P08 plus one actual validated provider early; P25/P26/P28 complete broader release evidence |
| Finish | P09 → P10 → P11 → P12 → P13; final P13 includes P14–P26/P28 delivery or explicit documented team-approved deferrals, never silently checked boxes |
| Improvements | P27 is used whenever a better architecture is proposed; not a prerequisite forcing an unnecessary refactor |

P04 owns case/agent behavior, P16 the provider registry/discovery, P17–P22 their named adapters, P23 the shared eligibility gate, P24 the selector and P25 live comparisons. They do **not** each reimplement `model_client.py`. P16 lands the shared dispatcher once; later adapter phases edit only reserved provider files. P23's focused catalog changes are serialized after P16, never concurrent with another catalog writer. Track 1 owns router mounting, config, generated contracts and DB migrations. Record exact subfile ownership before concurrent work. Every added phase allows only its stated files plus its own coordination entries.

**Database decision confirmed with the user:** keep SQLite for the local submission and identical setup commands on all eight laptops; no shared live DB or cloud account is required. P14 provides the common fixture baseline; P26 remains a real schema-upgrade gate, not a mandatory cloud rewrite. Read docs/DATABASE_DECISION.md for SQLite/PostgreSQL/Supabase/Neon/MongoDB trade-offs and the conditional future migration plan.

## Time budget and team assignment

| Elapsed hours from now | Focus / exit gate |
|---|---|
| 0–2 | P01 foundation review/clone check, claim eight tracks, agree contracts; no feature branches without reading specs |
| 2–14 | Parallel P02–P08; Track 8 drafts P13 assets/policies immediately; merge thin tested slices, not eight final-hour PRs |
| 14–22 | P09 integrated journey, real-model evaluation, negative/restart tests; fix safety blockers first |
| 22–25 | P10 demo polish and P11 local deployment rehearsal; P12 README finalization |
| 25–27 | P13 final assets, recording rehearsal, fix blockers only |
| 27–30 | **Code freeze ~3 hours before deadline**; final recording/upload, clean-clone check, link/permission verification; no new features |

Track 1 = integration lead/auth; Track 2 = overview/workspace UI; Track 3 = my-work/review UI; Track 4 = data/planning/checks; Track 5 = approval/actions; Track 6 = agent/cases/providers/worker; Track 7 = independent quality/eval; Track 8 = product/fixtures review/docs/submission. Replace **Owner name: unclaimed** with your real name only after coordinating. The setup agent is not a ninth teammate. Provider phases can be reassigned to available members with explicit non-overlapping files; do not leave all adapters as one last-hour Track 6 batch.

P01 must be complete first. P02–P08 can start together against reviewed contracts, but final feature verification needs their listed dependencies. P09's final core gate waits for all of them and one live validated adapter; integrate thin slices earlier. P15 is the reviewed provider-contract extension, not permission to silently change old contracts. P10 → P11 → P12 → final P13 gate. Asset drafting/consent collection can run from hour 0. Maintain one app with eight people; do not add eight services/agents.

The original 30-hour schedule above is a prioritization guide, **not an estimate that 15 additional phases cost nothing**. Re-estimate remaining time with the team. Deliver the core journey plus one safe model path early, then requested adapters/selection and broader evidence. If time runs out, record exactly what was deferred and obtain team agreement; do not weaken safety or hide unfinished provider support. Freeze new features three hours before the actual submission deadline.

**Shared coordination exception for every phase:** append only your entry in CHANGES.md and edit only your own PHASES block. No full-file formatting. Specs/lockfiles/shared types are Track 1 only; propose a contract change rather than silently editing it. Mark `[x]` only after the runnable done checks pass; identify stub versus live-model evidence.

## P01 — Foundation and frozen handoff

**Problem:** teammates need a real runnable starting point, not a diagram or fake business success.

**Task checklist (historical verification; do not mark later features done):**
- [x] Pin installs and initialize non-destructive SQLite foundation.
- [x] Export target contracts and honest 501 feature seams.
- [x] Run automated checks and dev/built HTTP smoke.
- [x] Record fresh-source results and limitations in docs/VERIFICATION.md.

- **Goal:** let anyone run a real browser → API → SQLite slice and work from the same contracts.
- **Owner track:** setup/integration lead; prerequisite to all others.
- **May touch:** initial root config/instructions, scripts/, backend/, frontend/, docs/, fixtures/README.md, evals/README.md, resume/, video/, ppt/; original input documents read-only.
- **Must NOT touch:** original final guide/PDF contents, real secrets/resumes, remote accounts, business feature implementation.
- **Expected outcome:** pinned installs, generated types/OpenAPI, module stubs, honest 501 routes, smoke/tests/CI and coordination docs.
- **Done when:** `npm ci`, pinned Python install, `npm run check`; `npm run dev` then `npm run smoke`; built local start smoke; isolated fresh-source reproduction documented in docs/VERIFICATION.md.
- **Status:** [x] done (foundation verification in docs/VERIFICATION.md). **Owner name:** setup agent.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Build/recheck P01 foundation only, using Topic_3_Final_Guide.md and the local challenge PDF. Keep React/TypeScript/Vite, FastAPI/Pydantic, SQLite and future LangGraph/local-or-hosted model seams. Within P01's named folders create only health/bootstrap behavior, shared wire/SQL contracts, separate owner modules with TODO stubs, CI and run/install/test scripts. Business endpoints must return 501 FEATURE_NOT_IMPLEMENTED and must never pretend to authenticate, approve or run AI. Preserve input documents and all user work. Verify from an isolated fresh-source copy using the README steps, record actual checks/limits in docs/VERIFICATION.md, append CHANGES.md and finish only P01's status. Do not begin P02–P28 features or buy/create external services.
```

## P02 — Demo identity and permissions

**Problem:** browser-supplied roles or IDs must not grant access to another hire.

**Task checklist:**
- [ ] Implement password verification, bounded login attempts and hashed expiring sessions.
- [ ] Implement current-user/scope seams and logout; no permissive fallback.
- [ ] Prove 401/403/404 distinctions, expiry, revocation and inactive-user denial.
- [ ] Attach isolated test evidence, run full checks and hand off exact auth usage.

- **Goal:** make the server, not the browser/model, decide who can see/do what.
- **Owner track:** 1; can start after P01 alongside P03–P08. Needed for integrated acceptance of P03/P04/P05.
- **May touch:** backend/app/auth/, backend/tests/test_auth.py; own coordination entries.
- **Must NOT touch:** shared contracts/schema, main.py, frontend, fixtures seed, other backend modules, locks/specs.
- **Expected outcome:** hashed-password login, eight-hour hashed bearer sessions, logout/me, require_user and require_hire_scope seams; no default credentials.
- **Done when:** `node scripts/python.mjs -m pytest backend/tests/test_auth.py -q` covers invalid/expired/revoked/inactive sessions, missing token 401, cross-hire 404, wrong operation 403; `npm run check` stays green.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Implement P02 only in backend/app/auth/ and backend/tests/test_auth.py. Follow docs/API_SPEC.md and DATA_MODEL.md: POST /api/sessions accepts {user_id,password}, returns Session with token_type=bearer; GET /api/me returns User; DELETE /api/sessions/current is 204. Verify active seeded users using salted password hashes (stdlib scrypt is sufficient); issue random opaque tokens and store only token hashes, user_id and eight-hour UTC expires_at. Do not invent default passwords or public registration. Provide require_user() FastAPI dependency returning shared User and require_hire_scope(user,hire_id); re-read active identity/current scopes, no role header/global HR bypass. Missing/expired credentials=401; unknown/out-of-scope hire=404; known in-scope forbidden operation=403. Bound failed login attempts locally and never log passwords/tokens. Tests create isolated users/scopes directly using shared DB helpers, not real fixtures or model calls. Do not edit another module to adopt the dependency: notify its owner. Run the done checks, append your exact changes/tests to CHANGES.md and update P02 only.
```

## P03 — Approved plans, source records and evidence checks

**Problem:** ordinary onboarding needs six real categories, and a completion claim is not independent proof.

**Task checklist:**
- [ ] Review synthetic policies/fixtures with Track 8; seed an empty DB safely.
- [ ] Implement approved plan selection, owners/deadlines/dependencies and pure location preview.
- [ ] Implement scoped task/source writes and fresh deterministic evidence semantics.
- [ ] Test all six categories, unsupported rules/cycles, stale writes and repeat-seed refusal.
- [ ] Hand fixture/schema versions and safe run instructions to P14; attach tests/full checks.

- **Goal:** normal onboarding works across all six areas without needing AI.
- **Owner track:** 4; parallel after P01. Track 8 reviews pack text; P02 needed to finalize route permissions.
- **May touch:** backend/app/planning/, backend/app/evidence/, fixtures/, backend/tests/test_planning.py, backend/tests/test_evidence.py.
- **Must NOT touch:** shared schema/types, auth/actions/agent modules, frontend, generated specs/locks.
- **Expected outcome:** safe synthetic seed, six-category approved plan, source updates and exact evidence semantics, pure location-diff seam.
- **Done when:** `node scripts/python.mjs -m pytest backend/tests/test_planning.py backend/tests/test_evidence.py -q`; `node scripts/python.mjs fixtures/seed.py` succeeds on a dedicated empty demo DB and a second run refuses to overwrite; `npm run check`.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Implement P03 only in backend/app/planning/, backend/app/evidence/, fixtures/ and tests/test_planning.py/test_evidence.py under backend. Read shared/schema.sql and contracts.py plus API_SPEC/DATA_MODEL. Implement mounted hire/list/plan/my-work/task-complete/check/source routes exactly. Approved rules choose tasks, owners, calendar-day dates and prerequisites; validate pack scope, effective dates, supported predicates and DAG cycles. No model-generated eligibility. Implement service seams create_plan(connection,hire), preview_location_change(connection,hire_id,location_id) and check_hire(connection,hire_id) with shared models; the preview is pure. Validate category-specific source permissions/fields and expected versions. Complete task changes only work state; separate source observations determine VERIFIED/BLOCKED/UNKNOWN/NOT_APPLICABLE. Reservation is not handover; missing handover evidence is UNKNOWN. Preserve historical receipts and unrelated completed training on location impact. Seed six fictional hires and 10–12 reviewed rules over both locations/roles, with all six categories, no eval answers; Priya profile=HYD-DEMO, offer=BLR-DEMO, equipment reservation/no handover, one compatible Bengaluru device. Seed uses private DEMO_PASSWORD hash and refuses nonempty business DB, no destructive reset. Use auth seams when available; never add permissive fallback. Cover healthy/contractor/unsupported-policy/cycle/wrong-owner/stale/freshness cases. Run checks, append log and update P03 only.
```

## P04 — Bounded investigation, selected local/hosted model and durable waits

**Problem:** an investigation must interpret permitted records and survive a human wait without losing limits or authority.

**Task checklist:**
- [ ] Implement scoped cases/questions/work queue and allowlisted reads.
- [ ] Persist graph waits and application-owned counters; revalidate identity on resume.
- [ ] Enforce output validation, attempted-call/read/time budgets and safe escalation.
- [ ] Connect the shared model seam to P16–P23 adapters; do not duplicate their discovery/transports.
- [ ] Prove two-process restart, injection/scope denial and provider failure; separate live evidence.

- **Goal:** AI investigates actual permitted evidence and can pause/restart safely.
- **Owner track:** 6; starts in parallel on P01 contracts; final integration needs P02/P03 and P05 proposal/executor seams.
- **May touch:** backend/app/agent/ excluding provider files reserved to P16–P23, backend/app/cases/, backend/tests/test_agent.py, backend/tests/test_cases.py.
- **Must NOT touch:** auth/planning/evidence/actions implementations, shared types/schema, frontend, eval answer keys, locks.
- **Expected outcome:** cases/questions/work queue, LangGraph persistence and scoped allowlisted reads using the P16 provider seam; model cannot approve/execute. One validated P17–P22 adapter is required for the live gate; P23 verifies its cost/eligibility controls.
- **Done when:** `node scripts/python.mjs -m pytest backend/tests/test_agent.py backend/tests/test_cases.py -q`; two-process waiting-case restart test passes; real selected-provider smoke is recorded separately, missing provider is not passed; `npm run check`.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Implement P04 only in its allowed files, excluding provider files reserved
to P16–P23. Read docs/PROVIDERS.md. Use shared NextStep object envelope:
{next_step:{step:'read',tool:'get_equipment_status',reason_summary:'Check assignment'}}.
No model-supplied hire IDs/read arguments or SQL/URL tool. Server binds the
current case/hire/actor, revalidates scope after waits and filters restricted
fields before inference. Model chooses read/ask/propose/finish/escalate;
code handles permissions and exact verification. Match API_SPEC routes.
Persist admission work and application-owned counters (12 attempted model
calls, 16 reads), per-call 30s and active-run 90s limits across resume. Count
SDK retries; allow one bounded repair only. Use a separate SQLite LangGraph
checkpointer; thread ID is not authority. Deduplicate questions, enforce the
exact intended recipient, save then interrupt and replay with fresh context.
Consume generate_next_step through P16 and a selected P17–P22 adapter under
the shared P23 eligibility gate; stub the seam only in tests until it lands.
No silent cloud fallback. P15/P26 own provider snapshot persistence. No
built-in browsing/execution or raw reasoning logs. Worker claims one case
run, reconciles crashes and calls P05 only for persisted approved EXECUTE
work. Return provider failure/escalation honestly; keep manual tasks usable.
Test malformed output, 429/timeout/invalid key, injections, wrong scope and
persisted budgets/restart with stub transport. Request main.py worker wiring
from Track 1. Run checks, record live availability separately, update P04/log.
```

## P05 — Exact approval and safe local action

**Problem:** an approval is unsafe if it can authorize a different payload, stale inventory or repeated effects.

**Task checklist:**
- [ ] Store immutable proposals/diffs/versions and correct HR/IT reviewer.
- [ ] Persist deduplicated decisions and stable queued action/event identities.
- [ ] Revalidate and conditionally execute atomically; preserve unrelated work/history.
- [ ] Read back exact outcomes; test stale/expired/wrong-role/race/restart/duplicate paths.
- [ ] Attach tests/full checks; never call a reservation a delivery.

- **Goal:** only the correct reviewed change happens once, with fresh proof.
- **Owner track:** 5; parallel with isolated DB tests after P01; needs P02/P03 seams for integrated verification.
- **May touch:** backend/app/actions/, backend/tests/test_actions.py.
- **Must NOT touch:** agent/worker, auth/planning/evidence internals, shared schema/contracts, UI, locks/specs.
- **Expected outcome:** immutable proposal/decision, HR/IT-specific review, conditional execution/deduplication and read-back audit.
- **Done when:** `node scripts/python.mjs -m pytest backend/tests/test_actions.py -q` proves wrong-role, cross-hire, stale/expired proposal, inventory race, duplicate/restart protection; `npm run check`.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Implement P05 only in backend/app/actions/ and backend/tests/test_actions.py. Use shared ActionPayload/Proposal/ExpectedVersions, schema.sql and exact API_SPEC routes: GET review-inbox, POST hires/{id}/change-previews, POST proposals/{id}/decisions. Only CHANGE_WORK_LOCATION (HR) and RESERVE_EQUIPMENT (IT) exist. Implement save_proposal(connection,context,payload,evidence_ids) and execute_approved_action(action_id) for P04. Server derives reviewer/versions/policy/expiry from scoped current records, validates citation meaning and prerequisites, stores immutable payload/diff. Question answers are not approvals. Same decision retry returns original IDs; conflicting decision=409. Approval commits decision+stable action+unique EXECUTE event before worker execution. Recheck identity, scope, exact proposal, expiry/profile/plan/policy/source versions inside local transaction, conditional update must affect one row; no separate check/update race. Location applies P03 diff atomically and preserves old history/unrelated completion. Reservation cannot assign another hire's occupied device. Unique action identity prevents duplicate local effects; read back source state and create sanitized audit/evidence, never 'delivered' for RESERVED. Use isolated DB fixtures and existing seams, no permissive auth fallback or direct model execution. Run done checks, append CHANGES entry and update P05 only.
```

## P06 — Hire overview and evidence workspace UI

**Problem:** users need to see owners and independent evidence, not an unexplained readiness score.

**Task checklist:**
- [ ] Build typed hire list/create and six-category plan/workspace components.
- [ ] Display completion versus evidence, timestamps and responsible owners clearly.
- [ ] Add accessible forms and loading/empty/denied/stale/501/unavailable states.
- [ ] Test mocked API behavior, hand exports to integrator, then verify live routes.
- [ ] Attach sanitized UI proof and tests/build/full-check results.

- **Goal:** judges can see the normal plan and why a completed task is not proof.
- **Owner track:** 2; parallel after P01 using mocked fetch; live acceptance after P02/P03/P04.
- **May touch:** frontend/src/features/overview/, frontend/src/features/workspace/ (including co-located tests/CSS).
- **Must NOT touch:** App.tsx, main.tsx, global styles, shared client/generated types, other feature folders, package locks.
- **Expected outcome:** exported Overview and HireWorkspace components consuming frozen types, clear task/evidence/current-owner states.
- **Done when:** `npm run test --workspace frontend` and `npm run build`; visible authenticated hire creation/list/plan/case workflow after integrator wires modules; no fake success for 501.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Implement P06 only in frontend/src/features/overview/ and frontend/src/features/workspace/, with their own tests and scoped CSS. Import generated shared api-types; use shared HTTP boundary, request auth/session plumbing from Track 1 rather than inventing a role header. Export Overview and HireWorkspace with explicit typed props for selected hire/token/navigation callbacks if needed; propose interface to integrator. Implement GET /api/hires, POST /api/hires HireCreate form and GET /api/hires/{id}/plan plus authorized case display/open/check actions per API_SPEC. Show all six categories, owners/deadlines/dependencies, COMPLETED separately from VERIFIED/UNKNOWN, timestamps/source IDs and exact 'reserved; collection pending'. No percentage readiness score. Include labeled inputs, keyboard focus, loading/empty/401/403/404/409/501/unavailable states; escape text, no raw HTML. Use mocked transport only in tests and label unavailable features, not fake records in production screens. Do not edit root wiring/shared styles or add dependencies. Run tests/build, hand typed export usage to Track 1, log and update P06 only.
```

## P07 — My work, clarification and review UI

**Problem:** people must distinguish a question answer, an approval and a confirmed executed result.

**Task checklist:**
- [ ] Build login/my-work/task completion and intended-recipient clarification UI.
- [ ] Build exact HR/IT review with evidence, versions, expiry and location diff.
- [ ] Show queued/rejected/stale states; never auto-approve after conflict or assume execution.
- [ ] Test keyboard/forms/errors and repeated submissions; hand exports to Track 1.
- [ ] Attach tests and live employee/HR/IT screenshots without secrets.

- **Goal:** employee/HR/IT can hand work to the right person and review exact changes.
- **Owner track:** 3; parallel after P01 using mocked fetch; live acceptance after P02/P04/P05.
- **May touch:** frontend/src/features/my-work/, frontend/src/features/review/ (co-located tests/CSS allowed).
- **Must NOT touch:** other feature modules, App/main/global styles/shared types/client, backend, lockfiles.
- **Expected outcome:** exported MyWork/ReviewInbox components and demo login form, clear waiting/denied/stale/rejected/pending-action UX.
- **Done when:** `npm run test --workspace frontend` and `npm run build`; HR and IT see distinct scoped reviews in integrated app, answer is never mistaken for approval.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Implement P07 only in frontend/src/features/my-work/ and frontend/src/features/review/, including tests/scoped CSS. Consume shared generated API models and API_SPEC: POST sessions, GET me/my-work, task completion with expected_version, intended question response, GET review-inbox and exact proposal decisions. Keep token only in shared in-memory session props, never localStorage or a role claim; Track 1 owns global session/API wiring. Export components with typed props/callbacks and hand them to integrator. Show exact action payload, evidence refs, input versions, HR vs IT approver and location plan diff. After APPROVE show queued/pending until polled read-back establishes outcome; REJECT does not run action. Disable duplicate submissions but server must still dedupe. A 409 requires fresh review, not auto re-approval. A clarification response is not an official profile mutation. Native labels/buttons, non-color statuses, loading/empty/denied/expired/501/unavailable, escaped text. No real secrets or browser model-key UI. Run tests/build; log and update P07 only.
```

## P08 — Independent evaluation and security acceptance pack

**Problem:** a scripted happy path cannot show whether the harness remains safe on unseen input.

**Task checklist:**
- [ ] Create held-out scenarios/answer keys separate from runtime/model inputs.
- [ ] Test permission, stale/duplicate, injection, outage and restart controls.
- [ ] Compare a rules-only baseline; define semantic outcomes, not exact model phrasing.
- [ ] Run real selected-provider evaluation separately from stubbed control tests.
- [ ] Record genuine results/limits; hand the common model matrix to P25.

- **Goal:** show measured evidence instead of scripted success.
- **Owner track:** 7; can draft immediately after P01, integrate tests as other tracks land.
- **May touch:** evals/, backend/tests/test_acceptance.py, docs/EVALUATION.md.
- **Must NOT touch:** runtime fixtures/feature source/shared schema/prompts, other owners' tests, CI/locks.
- **Expected outcome:** independent scenarios/answer keys, provider-labeled runner/results and rubric-based acceptance assertions.
- **Done when:** `node scripts/python.mjs -m pytest backend/tests/test_acceptance.py -q`; `node scripts/python.mjs evals/run.py --provider ollama` or hosted records actual measured results; missing model is not scored passed; `npm run check`.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Implement P08 only in evals/, backend/tests/test_acceptance.py and docs/EVALUATION.md. Build independent scenarios, separate answer keys and run.py per evals/README.md using frozen API/data contracts. Cover healthy/contractor/operations, conflicting location, ambiguous date, missing evidence, unavailable source, prompt injection, wrong role/hire, stale inventory, duplicate action and restart waiting. Hold out variants from runtime author. No is_broken/expected_action leaks into fixtures/model context, no name-based detection. API integration tests can use deterministic model stubs to assess controls but must separately run real-model evaluation. Same smoke set for local/hosted, explicit provider/model/prompt/fixture versions, semantic evidence support, safe abstention, latency/calls and failure notes. Missing keys/models = not run, not success; no exact wording/tool-order assertions when multiple safe paths exist. Compare simple checklist/rules-only baseline to avoid crediting AI for ID comparisons. Do not repair runtime code in this phase: send failing case to owner. Run checks, report genuine failures, log and update P08 only.
```

## P09 — Integration and end-to-end journey

**Problem:** independently tested folders can still fail as one authenticated application.

**Task checklist:**
- [ ] Merge thin slices, wire session/navigation and one worker without broad owner-file edits.
- [ ] Run normal plan and Priya clarification/pause/review/reservation/read-back journey.
- [ ] Use at least one real validated P17–P22 model; verify P23 eligibility controls and do not block early integration on every account.
- [ ] Repeat with wrong scope/role, stale approval, duplicate decision and restart.
- [ ] Record integrated commit and actual automated/manual results; include P24 when ready.

- **Goal:** make independently built modules behave as one product.
- **Owner track:** 1; integration begins with thin merges early, final gate after P02–P08.
- **May touch:** backend/app/main.py, frontend/src/App.tsx, frontend/src/main.tsx, frontend/src/styles.css, frontend/src/shared/api.ts, backend/tests/test_integration.py, docs/INTEGRATION.md; shared contracts/config/scripts only for reviewed wiring changes logged as revisions.
- **Must NOT touch:** another track's feature internals/tests without a specifically extended written boundary; private data/assets; no broad refactor.
- **Expected outcome:** wired session/navigation, worker lifecycle, real six-category journey, secure failure states and a recorded merge commit/result.
- **Done when:** `npm run check`; `node scripts/python.mjs -m pytest backend/tests/test_integration.py -q`; `npm run dev` + `npm run smoke`; manual full HR/employee/IT journey including restart/stale/duplicate checks.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
As Track 1 integrate P09 only in the explicitly allowed root wiring/client/style/test/doc files. Merge P02–P08 small PRs; keep every independent PHASES/CHANGES update. Wire typed feature exports, an in-memory bearer session, relative /api client headers, one local worker startup/shutdown, and orderly cancellation without bypassing auth. Preserve health/bootstrap and no model-key frontend handling. Run the real Priya flow: create six-category plan, conflict evidence, actual selected-model investigation, persisted question/restart/authorized reply, exact review, separate IT approval, conditional reservation/read-back showing collection pending. Test healthy hire and wrong role/hire, stale approval and repeated decision. Fix interface drift through canonical schemas+generated specs/types with a logged revision and affected-owner notice, not ad hoc JSON mapping. Send domain bugs to their owner unless the task boundary is explicitly extended. Record manual and automated results in docs/INTEGRATION.md, run done checks, log and update P09 only. Stop if a safety gate fails; do not simulate success.
```

## P10 — Demo polish without new scope

**Problem:** working behavior is hard to judge if the UI hides waiting states or is inaccessible.

**Task checklist:**
- [ ] Fix evidence/outcome/owner labels and all relevant empty/error/waiting states.
- [ ] Test keyboard, focus, long text, 390px and 1440px layouts.
- [ ] Include P24 selector states once integrated, without exposing credentials.
- [ ] Attach screenshots and tests/build results; rehearse the ten-minute journey.

- **Goal:** make the integrated journey readable and accessible in a recording.
- **Owner track:** 2 leads, Track 3 contributes separate assigned folder PRs; after P09.
- **May touch:** frontend/src/features/overview/, workspace/, and model-settings/ after P24 lands; Track 3 only its own my-work/review folders; docs/DEMO_PLAN.md. Claim exact folders before concurrent polish.
- **Must NOT touch:** backend/contracts/shared/root styling or routing unless Track 1 separately assigns it; no new features/frameworks.
- **Expected outcome:** clear source/outcome labels, complete keyboard/error states and ten-minute rehearsal path.
- **Done when:** `npm run test --workspace frontend`, `npm run build`; manually check 390px/1440px, keyboard tab/focus, long text, waiting/empty/error/stale states without overlap or false success.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Polish P10 only in the phase's explicitly owned feature folders and docs/DEMO_PLAN.md after P09 works. Coordinate Track 2/3 folder boundaries before touching code; no shared CSS/routing edits or backend changes. Keep the evidence-first language and synthetic labels. Show owners, timestamps, waiting questions, exact HR/IT review and reservation-not-delivery status. Verify loading, empty, long text, denied, stale, model-outage and rejected states; keyboard focus/labels and text+color status. Test 390px and 1440px and rehearse ten minutes. Do not invent readiness metrics or hide incomplete behavior. Run frontend tests/build, record visible checks/limits, append CHANGES and update P10 only.
```

## P11 — Local deployment and clean-clone rehearsal

**Problem:** the recording must start reproducibly on a clean machine, not only a developer's warmed-up folder.

**Task checklist:**
- [ ] Reinstall from fresh source with independent dependencies and local DB.
- [ ] Verify dev and built loopback origins, health/bootstrap and safe missing-model behavior.
- [ ] Check persistence, P26 upgrade procedure if needed, secrets and static-file isolation.
- [ ] Record exact commands/platform and tested selected provider; observe P28 teammate replay.

- **Goal:** the recording machine starts reliably without an exposed public server.
- **Owner track:** 1 with Track 7 observing; after P09/P10; no cloud deployment needed.
- **May touch:** scripts/, .env.example, .gitignore, root package.json/lock and CI only for verified deployment fixes; backend/app/main.py static serving/lifecycle; docs/VERIFICATION.md.
- **Must NOT touch:** feature business logic, secrets/accounts, original inputs, generated types except reviewed contract regeneration.
- **Expected outcome:** fresh installation, built same-origin frontend/API, local persistent DB, no credentials/assets leaked, documented provider setup.
- **Done when:** fresh-source/clone `npm ci`, pinned Python install, `npm run check`, `npm run build`, `npm start`; second terminal `SMOKE_BASE_URL=http://127.0.0.1:8000 npm run smoke` (PowerShell env syntax in README); restart manual check.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Verify/fix P11 local release only in the allowed launch/config/static/lifecycle files and docs/VERIFICATION.md. No public host/subscription is required. Reproduce README from a fresh clone/source copy with a new .venv and npm ci, not reused node_modules. Build frontend, run npm start on 127.0.0.1:8000 and smoke both health/bootstrap and page. Seed only dedicated synthetic DB using the reviewed safe command; restart preserves work. Verify the selected model/key privately, expose no .env/files/headers, and show graceful missing-model fallback. Record exact OS/runtime versions, commands/results and untested platforms. Check no working app is accidentally exposed by Vite or API on 0.0.0.0. Do not claim Docker/cloud/production readiness. Run done checks, append log and update P11 only.
```

## P12 — Beginner README and evidence finalization

**Problem:** hidden local commands and outdated claims stop teammates/judges reproducing the app.

**Task checklist:**
- [ ] Update tested install/run/seed/model commands for supported shells.
- [ ] Align README, provider guide and team DB instructions with actual P14–P26 behavior.
- [ ] Keep implemented/planned/live-tested distinctions and genuine metrics/links.
- [ ] Have another teammate replay setup (P28); record gaps and final checks.

- **Goal:** a judge/teammate can understand and reproduce the actual delivered app.
- **Owner track:** 8; draft anytime, final after P11.
- **May touch:** README.md, docs/README.md, docs/DEMO_PLAN.md, docs/ASSUMPTIONS.md, docs/TEAM_WORKFLOW.md, docs/PROVIDERS.md, docs/EVALUATION.md (coordinate with Track 7 and provider owners; serialize shared doc edits).
- **Must NOT touch:** generated API_SPEC/OpenAPI, canonical data model without Track 1 review, code/locks, original guide/PDF, personal assets without consent.
- **Expected outcome:** tested commands, architecture/limits, actual video/presentation links, real metrics and manual setup checklist.
- **Done when:** another teammate follows README with no hidden commands; `npm run check` still passes; every claimed feature/metric/link matches verified commit and docs/VERIFICATION.md.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Finalize P12 only in its allowed prose documents, coordinating EVALUATION.md with Track 7. Read actual P09/P11/P08 results before claiming completion. README needs exact clone/install/env/dev/test/build/start/seed/model commands for Windows and macOS/Linux, prerequisites, one local origin, actual implemented feature list and honest limitations. Preserve team branch/small-PR/Track 1 integrator instructions and folder map including resume/video/ppt. Explain optional Ollama download or hosted key and no default paid subscription, synthetic systems/privacy boundaries, official five-slide/ten-minute deliverables and marking evidence. Link actual evaluation results and video/presentation; do not replace pending assets with fake URLs. Have an independent teammate replay setup, record genuine gaps, run checks, log and update P12 only.
```

## P13 — Submission assets and final checklist

**Problem:** a working prototype still needs accessible, consented, accurate submission assets.

**Task checklist:**
- [ ] Review delivery status including additional provider/DB/setup phases; list approved deferrals honestly.
- [ ] Collect eight members' resume publication consent and actual files.
- [ ] Create exactly five final slides with PPTX/PDF and a real ten-minute recording.
- [ ] Verify judge playback/links, sanitize secrets, record frozen commit and final checks.
- [ ] Mark done only when actual required assets and final verification exist.

- **Goal:** publish a complete accessible submission, with consent and no secrets.
- **Owner track:** 8; drafts/consent start in parallel after P01, final gate after P12 and hour-27 freeze.
- **May touch:** resume/, video/, ppt/, docs/SUBMISSION_CHECKLIST.md and README.md submission links only.
- **Must NOT touch:** frozen feature code/config/contracts/locks, private member files without consent, original inputs; no fake assets or automatic public uploads.
- **Expected outcome:** eight consented real resumes, accessible ten-minute recording/link, final five-slide PPTX + PDF and checked README links.
- **Done when:** eight correctly named consented resumes, actual video playback permission tested, five slides exported to PDF, README paths/link destinations open, `npm run check` on recorded commit; no secret appears in assets.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, and CHANGES.md first. Work only on this phase.
Complete P13 only in resume/, video/, ppt/, docs/SUBMISSION_CHECKLIST.md and root README submission links. Do not fabricate resumes, slides, recording or URLs. Collect each of eight members' permission before intentionally adding firstname_lastname_resume.pdf; a public repo exposes private contacts. Build exactly five final slides per ppt/README.md and export dayone_proof_final.pptx/.pdf. Record the actual local end-to-end workflow for ten minutes from the frozen verified commit; disclose simulated sources and selected provider, show safety/evaluation evidence. Keep model keys/.env/private tabs out. Git rejects ordinary files >100 MiB; use LFS or Google Drive/YouTube/GitHub Release for large video, put real accessible URL/commit/duration/date in video/VIDEO_LINK.md and root README link. Verify playback as a judge and every artifact path. No purchase, account creation or public upload without team authorization. Run final checks, record remaining missing real assets honestly, append CHANGES and mark P13 done only when real submission assets exist.
```

## P14 — Reproducible local database and synthetic-data handoff

- **Problem:** eight laptops need the same reviewed starting story without sharing mutable SQLite files or passwords.
- **Owner track:** 4 implementation; 8 documentation/review, with separate file claims. **Depends on:** P01; seed acceptance waits for P03.
- **May touch:** fixtures/README.md, fixtures/seed.py, backend/tests/test_seed.py (Track 4); docs/TEAM_WORKFLOW.md (Track 8). Coordinate with P03 before editing seed.
- **Must NOT touch:** existing databases, `.env`, shared schema/config, other feature tests; no reset command.
- **Expected outcome:** safe seed and beginner steps producing equivalent fixture versions on independent databases, preserving existing business work.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Document which app/checkpoint paths to use and how to avoid cloud-sync folders.
- [ ] Seed six fictional hires, users/scopes, reviewed policies and independent source records from P03; print only safe IDs/revision, never credentials/hash contents.
- [ ] Prove a second seed refuses before modifying data; invalid input rolls back completely.
- [ ] Test two fresh DBs have equivalent intended fixture content despite generated hashes/times/IDs; startup never resets either.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_seed.py -q` and `npm run check`; attach two-path/repeat-run evidence and teammate instructions.

**Prompt:**
```text
Read AGENTS.md, PHASES.md, CHANGES.md, API_SPEC, DATA_MODEL and P03 first.
Implement only P14's claimed files. Reuse P03 fixtures/seed instead of adding
a second loader. Demonstrate separate local application/checkpoint paths
per teammate, private DEMO_PASSWORD hashing and a transactionally safe seed
that permits app_info but refuses nonempty business tables. Validate all
fixtures before writes and leave an existing DB unchanged on any refusal.
Test two independent fresh DBs, invalid-fixture rollback and repeat refusal.
Document the real fixture revision, safe identities, commands and backup
limits in the owned docs. Do not commit a database, password or reset helper.
Run the listed tests/full check, attach sanitized proof and update P14/log.
```

## P15 — Reviewed provider, selector and persistence contracts

- **Problem:** discovery and switching need common server-owned types/authorization before separate agents build incompatible adapters/UI.
- **Owner track:** 1, with 6/7/2 review. **Depends on:** P01; auth operation tests wait for P02.
- **May touch:** backend/app/shared/contracts.py, backend/app/shared/config.py, backend/app/main.py (router mounting only), scripts/export_contracts.py, .env.example, docs/DATA_MODEL.md, docs/PROVIDERS.md, backend/tests/test_provider_contracts.py; generated API_SPEC/openapi/api-types only through `npm run contracts`. Schema changes belong to P26.
- **Must NOT touch:** provider adapters, feature UI internals, real keys, live DBs, dependencies without a separately approved need.
- **Expected outcome:** reviewed types/endpoint policy/config plus exact named file seams for discovery, synthetic testing and selection; no runtime-feature completion claim.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Approve exact catalog/test/selection request/response/error contracts and authorized operator policy without inventing an unchecked admin role.
- [ ] Approve provider-specific server key variables, fixed endpoint registry, local-only behavior and handling of original `hosted` configuration.
- [ ] Define price/access/compatibility confidence and source/time; catalog listing never proves free entitlement.
- [ ] Define installation-wide selection for new cases and immutable case model/config snapshot across waits; P26 handles necessary durable schema/migrations.
- [ ] Reserve exact P16 dispatcher/router, P17–P22 adapter/test and P23 eligibility-test paths; review all affected callers and generated outputs.
- [ ] Run contract tests, `npm run contracts`, `npm run contracts:check` and `npm run check`; log the revision and notify all owners.

**Prompt:**
```text
Implement P15 only as Track 1 within the listed boundaries. Read
docs/PROVIDERS.md and existing model_client/config/case seams. Agree exact
catalog, explicit synthetic model-test and model-selection contracts with
Tracks 2/6/7, including refresh/test rate limits, current operator authority,
missing/invalid key, timeout/quota, stale catalog and unavailable states.
Browser accepts no credentials/base URLs; keys remain server environment.
Do not weaken existing business scope or expose transcripts. Define small
registry/adapter interfaces returning existing NextStep and reserve files.
Record new-case-only selection semantics and provider/model/config snapshot
requirements; send durable changes to P26 before implementation. Define
free-tier versus trial/paid/unknown labels, default no-paid execution and
local-only no-network-to-hosted policy. Update canonical types/config and
exporter as needed, regenerate docs/types, test and log the reviewed revision.
Do not claim the future endpoints/adapters work from schema presence alone.
```

## P16 — Bounded live catalog and shared dispatcher

- **Problem:** a static model list becomes wrong; one bad provider must not break discovery or leak its key.
- **Owner track:** 6. **Depends on:** P15 and P26 if approved metadata needs schema changes; P02 for authorized route verification.
- **May touch:** backend/app/agent/model_client.py, backend/app/agent/providers/__init__.py, backend/app/agent/providers/registry.py, backend/app/agent/providers/catalog.py, backend/app/agent/providers/router.py, backend/tests/test_provider_catalog.py. These are proposed new paths reserved by P15, not existing implemented modules.
- **Must NOT touch:** provider-specific adapters/tests, shared contracts/config, root router wiring, cases/graph/worker logic, frontend.
- **Expected outcome:** one reusable catalog/test/selection/dispatch seam with per-provider results, timestamps and fail-closed eligibility, ready for adapters.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Validate registry provider IDs and fixed origins; never use browser/model-supplied URLs or follow untrusted redirects.
- [ ] Query only configured hosted providers; local-only mode never contacts them. Cache briefly, expose timestamp/refresh and retain valid partial results.
- [ ] Bound time, response size, page count/model count, concurrency and refresh/test requests; preserve exact model IDs, not three arbitrary choices.
- [ ] Separate catalog retrieval from explicit synthetic testing/inference. Normalize sanitized provider errors and unknown capabilities/entitlements.
- [ ] Implement authorized default-selection read/write using P15 contracts/P26 persistence, reject stale/unapproved choices and preserve existing case snapshots; selection itself never starts inference.
- [ ] Dispatch selected adapters to existing NextStep validation without hidden retries/fallbacks; coordinate caller changes with P04/P15.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_provider_catalog.py -q` and `npm run check`; prove missing keys/401/429/timeout/malformed pages/redirection/redaction/local-only cases.

**Prompt:**
```text
Implement only P16's reserved catalog/registry/router/dispatcher files and
test. Use P15's exact canonical contracts/config and installed HTTP client;
no plugin framework/new dependency. Adapters arrive in P17–P22; stub their
transport in unit tests, not in production results. Return complete bounded
text-candidate catalogs with independent per-provider states and discovery
timestamps. A public catalog is not key validation or permission to infer.
Handle paging safely on approved origins, cache/refresh limits and partial
failures. Local-only mode must make zero hosted calls. Never infer prices
or entitlements from missing fields, and never invoke inference while listing.
Add explicit authorized selection read/write and synthetic-test seams with
bounded attempts and secret-safe errors, not an arbitrary prompt/URL executor.
Use P26's approved storage; changes affect new cases only. Keep one dispatcher
returning validated NextStep. Request root mounting from Track 1. Run checks,
attach mock/negative evidence and update P16/log; live adapter status stays separate.
```

## P17 — Ollama installed local models, including Llama

- **Problem:** a privacy demo must use actual on-device inference, not merely a model named Llama running in the cloud.
- **Owner track:** 6 or explicitly assigned adapter owner. **Depends on:** P16; integrates with P04/P24.
- **May touch:** backend/app/agent/providers/ollama.py, backend/tests/test_provider_ollama.py. Document live evidence in PR/CHANGES; shared provider prose changes handed to P12.
- **Must NOT touch:** registry/dispatcher after P16 without explicit extension, keys/config/schema, model downloads, other adapters.
- **Expected outcome:** installed local eligible models automatically listed and explicitly selected; real local schema-validated inference when hardware/model is supplied.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Read `/api/tags` and needed local metadata; handle Ollama offline/empty/model removed states.
- [ ] Exclude cloud-backed models and verify local-only server setup; no auto pull or remote fallback.
- [ ] Generate with approved format/schema, enforce timeout/attempt budget and parse existing NextStep; sanitize refusal/malformed output.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_provider_ollama.py -q` and full checks.
- [ ] With operator-installed Llama or another suitable model, record `ollama list`, model tag/digest, hardware, synthetic smoke and actual network/privacy limits; otherwise live verification pending.

**Prompt:**
```text
Implement only P17's Ollama adapter/test using P15/P16 interfaces. Discover
installed models from server-approved loopback Ollama; expose all eligible
local text candidates, not a hard-coded qwen/Llama tag. Reject cloud-backed
models and do not download/start an account/service or silently change model.
Use supported format/schema generation with strict NextStep validation and
budgeted timeouts/attempts. Tests mock tags/show/generation and cover offline,
empty, malformed, removed/cloud models, timeout and no hosted fallback.
Ask the operator to install a licence-appropriate model if absent. Record a
real synthetic local run only if available; catalog presence is not quality.
Run tests/full check, attach sanitized evidence, update P17/log and disclose
hardware and privacy limits instead of claiming the whole system is private.
```

## P18 — Groq and the minimal compatible hosted transport

- **Problem:** Groq models should be discovered with a Groq key without forcing an OpenAI account or duplicating HTTP code per provider.
- **Owner track:** 6 or claimed adapter owner. **Depends on:** P16.
- **May touch:** backend/app/agent/providers/compatible.py, backend/app/agent/providers/groq.py, backend/tests/test_provider_groq.py.
- **Must NOT touch:** registry/contracts, auth, other adapters, locks, billing/account settings.
- **Expected outcome:** one small shared wire transport and Groq catalog/inference adapter with honest free-plan/unknown entitlement labels.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Discover active Groq models using its documented endpoint; filter non-chat models via reviewed capabilities, not size/name alone.
- [ ] Keep provider key/origin separate from model developer; `openai/…` IDs do not require OpenAI credentials.
- [ ] Implement only common bounded HTTP/request/response parsing in compatible.py; provider-specific schema options remain explicit.
- [ ] Fail safely on 401/429/deprecation/unsupported schema; no SDK hidden retries/built-in tools/cloud or paid fallback.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_provider_groq.py -q` and full checks; record actual selected-model synthetic smoke if the key is provided privately.

**Prompt:**
```text
Implement P18 only in its three paths. Use P15/P16 contracts and the Groq
official API. Discover the account's current models; no permanent free list
or exactly-three limit. Reuse the installed client, extracting only shared
OpenAI-compatible wire handling needed now. Keep capabilities, auth, origin
and schema option differences explicit; the Groq key is independent of model
developer and compatible wire format is not OpenAI billing. Count every attempt, cap output/timeout,
validate NextStep and strip raw reasoning/error bodies. Test missing/invalid
key, non-chat models, 429, timeout, malformed/refusal, unsupported format and
no paid fallback. Do not set up billing or expose a key. Run listed checks;
record real smoke separately or say not run, then update P18/log.
```

## P19 — Cerebras discovery and trial-aware inference

- **Problem:** Cerebras is useful to compare, but calling its current trial “unlimited free API” would mislead users.
- **Owner track:** claimed provider owner (coordinate with 6). **Depends on:** P18 shared transport/P16.
- **May touch:** backend/app/agent/providers/cerebras.py, backend/tests/test_provider_cerebras.py.
- **Must NOT touch:** common transport/registry/config without an extended boundary, provider accounts/payment methods, other adapters.
- **Expected outcome:** discovered Cerebras text models with correct trial/paid/unknown access, validated generation and safe expiry/quota errors.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Use authenticated model list; optionally merge official public capability/pricing metadata without equating it to account access.
- [ ] Clearly distinguish limited trial credits and renewable free tiers; verify current account terms without logging billing data.
- [ ] Handle trial expiry, unsupported schema, 401/429/timeout and malformed output without changing provider.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_provider_cerebras.py -q` and full checks.
- [ ] Record live synthetic smoke only with separately authorized access; lack of a card/key is a documented blocked live check, not failure to be hidden.

**Prompt:**
```text
Implement only the P19 adapter/test using the frozen P16/P18 seams. Read
current official Cerebras trial/limits and model API docs linked in PROVIDERS.
Discover actual supported text models; do not hard-code retired Llama tags.
Merge only validated metadata and preserve unknown entitlement. No account,
payment method or purchase may be created. Trial credits are not a permanent
free tier; fail closed when execution lacks approved cost entitlement. Test
public-catalog-versus-key access, expiry, unsupported format, malformed JSON,
timeouts, quota and redaction/no fallback. Return strict NextStep. Run checks,
record available real smoke honestly and update only P19/log.
```

## P20 — Mistral capabilities and schema-compatible generation

- **Problem:** Mistral's catalog includes specialized models that cannot run this text investigation.
- **Owner track:** claimed provider owner. **Depends on:** P16/P18.
- **May touch:** backend/app/agent/providers/mistral.py, backend/tests/test_provider_mistral.py.
- **Must NOT touch:** registry/config/shared transport, OCR/audio workflows, dependencies, other providers.
- **Expected outcome:** live account catalog with completion-chat/capability filtering and tested structured generation; no invented free entitlement.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Parse model cards, archived status and completion-chat capabilities; preserve exact IDs/aliases safely.
- [ ] Distinguish open weights/free chat from free API entitlement; show unknown when not published/account-verified.
- [ ] Select supported schema/JSON request options explicitly and fail safely when unsupported; do not silently downgrade validation.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_provider_mistral.py -q` and full checks; attach real synthetic smoke when authorized access exists.

**Prompt:**
```text
Implement P20 only in its adapter/test. Use Mistral's official models endpoint
and explicit capabilities.completion_chat to distinguish text candidates
from embeddings, OCR, audio, classifiers and archived models. Reuse P18's
bounded transport where it fits without making every provider look identical.
Preserve free-tier/paid/unknown distinctions from reviewed metadata/account
policy, not from 'open' in a model name. Test missing capability, aliases,
unsupported structured mode, 401/429/timeout/refusal/malformed output and
secret redaction. Validate existing NextStep; no tools or fallback upgrade.
Run tests/full checks, record live smoke or not-run reason, update P20/log.
```

## P21 — Gemini native discovery and structured-output adapter

- **Problem:** Gemini's model listing/paging/schema behavior differs from the compatible providers; forcing one payload can silently break validation.
- **Owner track:** claimed provider owner. **Depends on:** P16/P15; no need to duplicate the P18 compatible client.
- **May touch:** backend/app/agent/providers/gemini.py, backend/tests/test_provider_gemini.py.
- **Must NOT touch:** common registry/types, browser keys, Google project/billing, model tool execution.
- **Expected outcome:** paged eligible Gemini catalog and bounded native text generation translated to existing NextStep with explicit free-tier/data-use disclosure.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] List all bounded pages and filter `generateContent`; do not mistake embeddings/live/audio support for this agent's capabilities.
- [ ] Keep resource names and invocation model identifiers consistent; validate metadata and page tokens.
- [ ] Use server-held key header, supported response schema/MIME settings and explicit handling of refused/blocked/empty/truncated candidates.
- [ ] Handle native schema limitations without weakening server NextStep validation or leaking reasoning; no Search/Maps/code execution.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_provider_gemini.py -q` and full checks; separately record a real authorized free-tier synthetic smoke and applicable data-use terms.

**Prompt:**
```text
Implement only P21's native Gemini adapter/test against P15/P16 interfaces.
Use the official Gemini Developer API, bounded page tokens, server key header
and supportedGenerationMethods metadata. Distinguish discovery, schema
compatibility, free-tier eligibility and account quota; they are not the same.
Translate the canonical output schema only as necessary for supported Gemini
constraints, then always validate original NextStep in trusted code. Handle
safety blocks, no candidates, malformed/truncated output and unsupported
schema as explicit failure; never invoke built-in tools or expose reasoning.
Test paging, bad metadata, 401/403/429/timeout, blocked output, redaction and
no fallback. Review free-tier data-use disclosure, use synthetic data only.
Run checks, record real smoke if available and update P21/log.
```

## P22 — OpenRouter free catalog and no-paid-fallback routing

- **Problem:** free variants can disappear, and a fallback from `:free` to a paid model can create unintended charges or change evaluation identity.
- **Owner track:** claimed provider owner. **Depends on:** P16/P18.
- **May touch:** backend/app/agent/providers/openrouter.py, backend/tests/test_provider_openrouter.py.
- **Must NOT touch:** account billing/credits, common transport/config, random model router defaults, other providers.
- **Expected outcome:** current eligible free models automatically visible with exact IDs, price evidence, limitations and reproducible explicit selection.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Read bounded current catalog and exact free variant metadata; never append `:free` to models that do not list it.
- [ ] Check text/schema compatibility and every applicable pricing field/override; unknown prices are not zero.
- [ ] Request only explicit approved model with paid fallbacks disabled and reviewed data-policy routing; disclose intermediary/provider behavior.
- [ ] Preserve selected versus returned serving identity, quota/negative-balance failures and no paid substitution.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_provider_openrouter.py -q` and full checks; use a small explicit live test, not bulk inference over the catalog.

**Prompt:**
```text
Implement P22's adapter/test only, using current official OpenRouter catalog
and free-variant/pricing docs. Discover exact entries, modalities, supported
parameters and all applicable costs/overrides. Preserve :free IDs and fail
closed on stale/unknown/nonzero cost under default no-paid policy. Do not
auto-strip suffixes, append a nonexistent free suffix, use openrouter/free
random routing, or configure paid fallback arrays. Keep explicit model and
returned serving metadata for evaluation; disclose that OpenRouter is an
intermediary and enforce approved data routing. Test disappearing variants,
nonzero request/reasoning cost, missing prices, pagination, unsupported schema,
quota/401/timeout, redaction and no paid retry. Run checks, record authorized
live smoke or not-run reason and update P22/log.
```

## P23 — Shared free-tier eligibility, quota and no-paid execution gate

- **Problem:** a model visible in a catalog may be paid, incompatible, unavailable to that account or out of quota; “free key” must not become accidental paid inference.
- **Owner track:** 6 with Track 7 review. **Depends on:** P15/P16 and at least one P17–P22 adapter; verify remaining adapters as they land. Serialize catalog edits after P16.
- **May touch:** backend/app/agent/providers/catalog.py, backend/tests/test_provider_eligibility.py. Reuse the existing P16 decision path; no second eligibility framework or private contract.
- **Must NOT touch:** billing/accounts, provider-specific adapter files, root config/shared types, dispatcher signature, frontend; send adapter defects to their owner.
- **Expected outcome:** one tested, fail-closed eligibility decision for local compute, verified free-tier/zero-price, trial, paid and unknown states; no extra provider added.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Reuse P15 types and P16 account/capability/cost decisions; show complete eligible candidate lists rather than arbitrary three-model limits.
- [ ] Prove unknown/nonzero costs, expired trials, stale entitlement and incompatible models cannot bypass the default no-paid policy.
- [ ] Keep quota unknown when the provider does not report it; handle 429 without provider switching, paid retry or unbounded backoff.
- [ ] Prove local-only mode never queries hosted providers and catalog refresh never performs inference.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_provider_eligibility.py -q` and full checks; attach negative evidence for all six planned model paths, marking unavailable live checks separately.

**Prompt:**
```text
Implement P23 only in its catalog/test paths after P16's owner hands them off.
The requested paths are Ollama/local Llama, Groq, Cerebras, Mistral, Gemini
and OpenRouter. Add no other provider. Reuse P15's exact canonical states and
the existing P16 eligibility path; do not create a parallel policy engine.
Distinguish catalog presence, text/schema compatibility, account access,
free/trial/paid/unknown cost and live quota. Under default no-paid policy,
unknown/stale entitlement fails closed, zero-price metadata alone is not
account approval, and expired trials cannot execute. Never infer remaining
tokens, buy credits, probe every model, auto-retry a paid variant or switch
provider on 429. Test negative combinations, local-only no-hosted calls and
refresh-without-inference. Send adapter defects to owners, run listed checks,
attach real evidence or not-run reasons and update only P23/log.
```

## P24 — Authenticated provider/model selector and explicit test UX

- **Problem:** users want “choose and run,” but must see missing keys, cost uncertainty and local/hosted privacy before inference starts.
- **Owner track:** 2; Track 1 owns a separate wiring PR. **Depends on:** P02/P15/P16 plus at least one implemented adapter; persistence depends on P26 decision.
- **May touch:** frontend/src/features/model-settings/ (components, scoped CSS, co-located tests). Track 1 separately may touch App.tsx, frontend/src/shared/api.ts and backend integration tests solely for reviewed selector wiring; claim those files before editing.
- **Must NOT touch:** existing feature internals/global styles, generated types by hand, keys/.env, backend provider code, locks.
- **Expected outcome:** authorized operator can refresh catalog, inspect price/compatibility/locality, explicitly test a synthetic example and select a model for new runs; ordinary users cannot change global selection.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Build provider/model dropdowns from generated API types, not hard-coded model IDs or provider count limits.
- [ ] Show exact ID, local/hosted, cost/access confidence, discovery/test timestamp, current selection and why an entry cannot run.
- [ ] Separate refresh, synthetic test, selection and investigation actions; hosted consent is explicit and current case snapshots do not silently switch.
- [ ] Include key-missing/offline/401/403/429/empty/stale/partial/unavailable/501 states, keyboard focus and native labels.
- [ ] Test unauthorized selection and confirmation/error handling with mocked fetch; after wiring, check actual backend denies forbidden requests too.
- [ ] Run frontend tests, build and `npm run check`; attach 390px/1440px sanitized screenshots and one live selected-model journey.

**Prompt:**
```text
Implement P24 in its owned UI folder only; coordinate Track 1 wiring as a
separate claimed slice. Read PROVIDERS and P15 contracts. Export typed
ModelSettings component using shared authenticated API/session props. List
all discovered provider/model candidates with searchable/native selection
as needed, honest local/hosted/cost/access/compatibility states and timestamps.
Never accept API keys/base URLs in browser, assume 'listed' means 'free', or
fire inference on refresh. Explicit Test uses the backend synthetic-only
operation and warns about quota; no arbitrary prompt tester. Block paid or
unknown execution under server policy and show the reason. Confirm selection
for new cases only; active/resumed work keeps its model snapshot. Support
loading/empty/partial/denied/stale/error states and accessibility. Test all
branches with mock transport, then actual auth/model flow after wiring. Run
tests/build/full checks, attach sanitized screenshots and update P24/log.
```

## P25 — Same-scenario provider comparison and regression matrix

- **Problem:** more selectable models are not useful unless the team knows which actually work and whether changing model makes results worse.
- **Owner track:** 7; provider owners supply private live access on their machines. **Depends on:** P08; each adapter before its live row; P09 for end-to-end results.
- **May touch:** evals/ (runner/scenarios/answer keys/results), backend/tests/test_provider_acceptance.py, docs/EVALUATION.md.
- **Must NOT touch:** runtime prompts/fixtures/adapter logic, shared contracts, keys, another owner's tests. Send discovered bugs to their owner.
- **Expected outcome:** reproducible control and real-model matrix for all six paths with explicit pass/fail/not-run, quality/cost/latency limits and tested selected default.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Reuse P08 held-out scenarios and rules-only baseline; keep answer keys out of model/runtime input.
- [ ] Evaluate local, Groq, Cerebras, Mistral, Gemini and OpenRouter with actual selected IDs/config/fixture/prompt versions; unconfigured access is not run.
- [ ] Measure evidence support, safe abstention, useful clarification/proposals, unauthorized-write prevention, failures, calls and latency; report denominators.
- [ ] Prove controls remain safe on invalid model outputs; separate schema compatibility, semantic quality, deterministic harness tests and live model evidence.
- [ ] Record free/trial/paid/unknown cost confidence and budget; do not buy credits or bulk-test every catalog model.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_provider_acceptance.py -q`, documented real eval CLI and full checks; publish sanitized result paths and acceptance recommendation.

**Prompt:**
```text
Implement P25 only in independent eval/test/docs boundaries. Extend the
existing P08 runner, not a second model framework. Document its exact real
CLI after implementation; do not invent a passing run. Run the same held-out
semantic checks on selected candidates across every requested provider and
the rules-only baseline, with fixed budgets and recorded input revisions.
No exact text/tool-order tests where multiple safe paths exist. Count errors,
refusals, quota/timeouts and not-run rows honestly; include denominators and
hardware/network context. Model smoke is not business-quality evidence.
Never publish keys, chain-of-thought or private account info. Send runtime
failures to owners; do not weaken assertions to improve scores. Recommend a
tested default based on actual quality/safety/cost/latency trade-offs, not
brand/size. Run checks, attach genuine results and update P25/log.
```

## P26 — Non-destructive schema upgrades and durable model snapshots

- **Problem:** fresh schemas do not upgrade existing teammate databases, and model selection must survive restart without altering an admitted case.
- **Owner track:** 1 with 6/7 review. **Depends on:** P15 design decision; run before P16/P24 if persistence changes are necessary.
- **May touch:** backend/app/shared/schema.sql, backend/app/shared/db.py, reviewed numbered migrations under backend/app/shared/, backend/app/shared/contracts.py and scripts/export_contracts.py only if schema-version contract requires it, scripts/migrate_db.py if needed, backend/tests/test_migrations.py, docs/DATA_MODEL.md, docs/TEAM_WORKFLOW.md; generated files only via exporter. Scope does not authorize unrelated schema redesign.
- **Must NOT touch:** real DB files, business history/fixtures destructively, feature internals without separate boundary; no automatic delete/reset on version mismatch.
- **Expected outcome:** smallest reviewed persistence/version strategy, safe backup/upgrade/restore instructions and tested new-case provider snapshot. If existing storage is demonstrably sufficient, record no migration needed rather than inventing one.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Inventory actual persistence required by P15, including application-owned model/config snapshots and default selection; approve only necessary additions.
- [ ] If schema changes: version startup/health/contracts consistently, validate supported source versions and run transactional numbered migration with no destructive defaults.
- [ ] Test fresh DB, supported upgrade, repeated upgrade, interrupted/failed upgrade rollback and refusal of unknown/newer versions; preserve users/scopes/evidence/decisions/actions.
- [ ] Test selection changes affect new cases only, persisted waits keep original model identity, missing original model escalates instead of switching.
- [ ] Exercise a stopped app+checkpoint backup/restore with P04 owner; document non-atomic checkpoint/application limitations honestly.
- [ ] Run `node scripts/python.mjs -m pytest backend/tests/test_migrations.py -q`, contracts regeneration/check if required and full checks; publish real commands before teammates upgrade.

**Prompt:**
```text
Implement P26 as integrator only after reviewing P15 persistence needs and
current schema/data ownership. Choose the smallest durable design; use no
migration if existing canonical storage safely suffices, but prove why. For
any actual schema change add a numbered reviewed migration/version handling,
backup-first command and tests; CREATE IF NOT EXISTS is not an upgrade.
Preserve all existing business/history/session semantics. Never delete DBs,
silently reset on mismatch or hold a write transaction during inference.
Case provider/model/config identity must survive restart and remain fixed
when the global default changes. Coordinate feature adoption with P04/P16
owners instead of editing their files. Test unknown versions, repeat/failure
rollback, preserved records and stopped paired backup/restore. Regenerate
canonical contracts if affected. Run checks, document exact upgrade limits,
notify eight teammates and update P26/log.
```

## P27 — Evidence-based architecture improvement decision

- **Problem:** different coding agents may propose conflicting rewrites; confidence and model size do not demonstrate a safer or more efficient design.
- **Owner track:** proposer plus Track 1 and affected-owner review. **Depends on:** a concrete measured problem, not mandatory before building.
- **May touch:** a new dated decision note under docs/decisions/ and this phase's coordination entries. Implementation files must be named in a separately approved phase/boundary before editing.
- **Must NOT touch:** runtime code/contracts/config/database during this decision task; no repo-wide cleanup, history rewrite or safety regression.
- **Expected outcome:** accept/reject/defer decision with before/after criteria, exact approved implementation scope, risk/trade-offs and rollback plan, not an unverified “better architecture.”
- **Status:** [ ] not started; use when needed. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Explain concrete problem/current baseline, smallest alternative and why existing code cannot solve it directly.
- [ ] List callers/tests/fixtures/config/contracts/data changes and affected owners; set acceptance criteria before comparison.
- [ ] Record same-input before/after checks, security regressions, latency/cost/quality trade-offs, hardware and untested areas. Concept-only proposals stay unverified.
- [ ] Reject weakened hard safety/evidence/accessibility gates; require integrator/affected-owner approval for implementation scope.
- [ ] Link tested migration/rollback plan if applicable; append decision to CHANGES and amend only affected phase boundaries after review.

**Prompt:**
```text
Perform P27 decision work only. Read connected source/callers and current
tests before recommending an architecture change. Use the accepting-a-better-
design procedure in TEAM_WORKFLOW. Write a concise dated decision note:
problem, smallest candidate, files/owners/contracts/data impact, agreed
baseline and acceptance criteria, actual before/after evidence if available,
risks/trade-offs/untested areas and rollback. No implementation authorization
comes from a model claiming 100% certainty or a stronger coding assistant.
No regression of permissions, approvals, evidence truth, durable limits,
duplicate protection, secrets or accessibility is acceptable. Request review
and an exact implementation boundary; do not edit runtime during this task.
Record accept/reject/defer truthfully, link evidence and update P27/log.
```

## P28 — Eight-member setup replay and evidence handoff

- **Problem:** one successful install does not show that eight teammates can follow the instructions or demonstrate their individual work.
- **Owner track:** 8 coordinating; 7 observes; every member records their own replay. **Depends on:** P14/P11 for final replay; collect foundation feedback early.
- **May touch:** docs/TEAM_WORKFLOW.md, docs/VERIFICATION.md, docs/team-checks/ (sanitized Markdown records only); README.md only through a serialized P12 handoff.
- **Must NOT touch:** runtime/config/contracts, binary DBs, keys/account screens/private resumes; no fabricated teammate results.
- **Expected outcome:** actual per-member setup/evidence matrix and corrected simple instructions for verified environments; unsupported/unavailable machines are visible.
- **Status:** [ ] not started. **Owner name:** unclaimed.

**Tasks and done checklist:**
- [ ] Record each member's chosen name, OS, Node/Python, branch/commit, schema/fixture revisions, app/checkpoint path policy and chosen provider availability without secrets.
- [ ] Each independently follows README: install, check, dev+smoke, built start+smoke; seed/restart/model steps only when implemented.
- [ ] Verify independent DBs, same fixture starting story, repeated-seed refusal and backup instructions; no copying one teammate's working DB as setup.
- [ ] Attach sanitized UI screenshots to PRs and exact test output/negative/restart evidence where relevant; photos alone never prove backend safety.
- [ ] Log failed/not-run steps and assigned owners, fix docs within boundary, then replay the corrected steps.
- [ ] Run `npm run check`; final done requires all eight real records or an explicit team-reviewed release exception, never eight invented checkmarks.

**Prompt:**
```text
Coordinate P28 only in its prose boundaries. Ask each of eight actual team
members to replay the README on their own clone and local database; do not
invent identities/platform checks or upload their DB/env files. Collect
commit/runtime/fixture/schema/provider metadata, exact commands/results and
sanitized evidence links in docs/team-checks. Distinguish foundation install,
business seed, mocked checks, actual inference and end-to-end acceptance.
Record missing hardware/keys as not run, not success. Verify SQLite separation,
seed refusal, restart persistence, optional-model absence and loopback URLs.
Fix unclear commands only in owned prose, send runtime defects to owners and
request P12 README updates as a serialized handoff. Run full checks and
update P28/log with the real member matrix and unresolved limitations.
```
