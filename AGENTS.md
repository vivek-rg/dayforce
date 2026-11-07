# OnboardIQ — shared contributor and AI-agent rules

## Start here

1. Read this file, [the active implementation plan](docs/decisions/2026-11-07-improvement-plan.md), [CHANGES.md](CHANGES.md), relevant [API](docs/API_SPEC.md)/[data](docs/DATA_MODEL.md) contracts and affected source/callers/tests before work. README.md owns the complete setup/architecture guide. The old PHASES.md board is retired by explicit user request; do not recreate it or duplicate its backlog.
2. Agree a small task, owner and exact file boundary in the active plan before editing. One writer per file, including agents on one laptop. If scope expands, record the integrator/affected-owner decision there first. Historical audits/unchecked old phases are not automatically open defects.
3. Preserve unrelated changes and working data. Use your own valid branch name, small clear commits and reviewed PRs; never push feature work directly to main, force-push shared branches, reset/discard other people’s work or buy/deploy services without authorization. Current user-requested work stays uncommitted/unpushed/undeployed unless separately approved.
4. After a task run relevant verification and npm run check; append actual results/limitations to CHANGES.md and docs/VERIFICATION.md, and update only that task in the active plan. Preserve independent log entries on conflicts. Tests using stubs prove controls, not real-model quality.

## Product truth

OnboardIQ coordinates documents, equipment, payroll, benefits, training and manager work using approved worker/location rules. Seven roles retain their existing scope. Task completion is a claim; independent evidence establishes only the exact checked outcome. Missing/stale/unavailable evidence is UNKNOWN; a real mismatch is BLOCKED; NOT_APPLICABLE needs an approved rule. Never call a laptop delivered because it was reserved. Preserve evidence/audit history.

Demo: Priya’s Hyderabad profile/Bengaluru offer conflict -> responsible HR clarification and persisted wait -> reviewed location/plan diff -> separate IT-approved reservation -> fresh receipt showing collection pending. Fictional company/policies/data and simulated external systems. One company, one backend, one local worker and one bounded investigation loop—not eight agents or a real enterprise HR integration.

The end-to-end build includes auth/plans/evidence/documents/knowledge/cases/actions/notifications/analytics and UI. Current dated proof lives in verification/evaluation, not generic completion claims. One Groq-hosted openai/gpt-oss-20b model has historical live evaluation; Ollama has mock transport tests, not live hardware acceptance. Gemini/Mistral hosted-compatible settings are unverified candidates, not live-tested native adapters. Integrator review and release/submission gates remain in the active plan.

## Architecture and ownership

- React + TypeScript + Vite; relative /api browser calls only. Backend FastAPI + Pydantic, standard-library SQLite, parameterized SQL and per-operation connections/short transactions. No write transaction across network/model/human waits.
- Agent state/questions/counters/work live in application tables; no separate LangGraph checkpointer. Explicit none/stub/hosted/ollama modes through backend/app/ai/. Stub is labelled Offline rules, not AI. No silent provider/paid/cloud fallback.
- Local demo remains the accepted database choice. Each teammate uses independent local files with matching code/schema/fixture revision. Do not share SQLite over Git/sync/network drives. Cloud PostgreSQL, general migrations, model catalogs/selector and simultaneous credential expansion are deferred, not completed features.

| Area                                                                                                           | Owner / boundary                                                            |
| -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Shared contracts/schema, main.py, frontend root shell/styles/API helper, scripts, config/CI/dependencies/locks | Integrator (Track 1); coordinate all shared edits                           |
| backend/app/auth/                                                                                              | Auth owner (Track 1)                                                        |
| backend/app/planning/, evidence/, fixtures/                                                                    | Rules/data owner (Track 4)                                                  |
| backend/app/cases/, agent/ and ai/                                                                             | Investigation/transport owner (Track 6)                                     |
| backend/app/actions/                                                                                           | Approval/execution owner (Track 5)                                          |
| frontend/src/features/overview/, workspace/                                                                    | Overview/workspace owner (Track 2)                                          |
| frontend/src/features/my-work/, review/                                                                        | Task/review owner (Track 3)                                                 |
| evals/, backend/tests/test_acceptance.py                                                                       | Independent evaluation owner (Track 7)                                      |
| Submission prose/assets                                                                                        | Documentation/submission owner (Track 8); contracts remain integrator-owned |

Tracks describe ownership, not mandatory identities; claim actual people and remaining tasks in the plan. Feature owners use their module tests/co-located frontend tests; do not rewrite another owner’s helpers to hide failures. Cross-module service seams and shared boundaries require affected-owner review. Do not invent a new framework, dependency, repository layer or generic workflow designer without an actual requirement and approval.

## Contracts and hard safety rules

- Canonical wire models: backend/app/shared/contracts.py. SQL authority: backend/app/shared/schema.sql. Generated docs/API_SPEC.md, docs/openapi.json and frontend/src/shared/api-types.ts come from npm run contracts after reviewed canonical changes—never hand-edit them. Health compatibility alias /health intentionally stays outside business OpenAPI; /api/health is canonical.
- JSON uses snake_case, exact enums, opaque IDs, ISO dates/UTC timestamps; Pydantic forbids extra fields. TypeScript strict types, import type for generated types; never hide errors with any or type-check suppression. Python snake_case functions/modules, PascalCase models and typed new public functions. Ruff/ESLint/Prettier follow repository patterns.
- Permissions are never model-owned. No arbitrary SQL/URLs, browser/model-supplied actor authority, unapproved source writes, public tool executor or privileged transcript in lower-role views. Revalidate current identity/scope on resume and execution.
- Immutable proposal + input versions + correct reviewer + expiry + atomic conditional write + stable action/event identity + read-back form one safety path. Approval is not execution. Reconcile uncertain external outcomes before retry; do not claim exactly-once distributed effects.
- Preserve loading/empty/denied/stale/error/unavailable states, manual fallbacks, native labels/buttons, keyboard focus, escaped text and non-colour status labels. Current black/white/red UI/public guides (white navigation, restrained red action/selection accents) and finite reduced-motion-safe illustration are approved; polish must not obstruct working features or invent outcomes.
- No secret/private .env, model key, session, bank/identity/medical details, DB, upload, personal resume or private document in prompts/logs/screenshots/fixtures/external indexing. Synthetic evidence only. Model keys belong only in the backend’s private environment, never VITE variables. Do not inspect private configuration to answer setup questions.

## Run and verify

Follow root README for supported Python/Node, root .env, .venv/npm ci, safe seed and dev/built run. From root:

```sh
npm run dev
# Second terminal with the owned server running:
npm run smoke
npm run check
```

Check covers lockfile guard, lint/format, backend/frontend tests, strict build and generated-contract drift. Use npm.cmd on PowerShell when needed. Integrator only after canonical changes: npm run contracts. Format only allowed paths; global npm run format is integration-owner-only. Startup initializes schema/app_info without deleting data or seeding business hires. Seed refuses existing users. Never reseed/reset/delete a working DB as repair. Back up the stopped DB+companions+uploads before reviewed upgrades; no general migration command exists.

For architectural changes use the active plan’s change gate: concrete problem/smallest alternative, callers/owners/data risks, same-input before/after evidence and explicit latency/cost/quality trade-offs. Integrator+affected-owner review, migrations/restore/rollback when needed. Reject weaker safety/evidence/accessibility even if faster. Undo only the team’s reviewed change, never somebody else’s work.

## Submission and handoff

- One remaining-work list lives in docs/decisions/2026-11-07-improvement-plan.md; root README is the human setup/architecture guide; video/script.md owns the under-ten-minute eight-person rehearsal. Do not add another temporary report unless needed; answer general opinion questions in chat/README. Original PDF is authoritative; historical rationale/reviews are not current runtime claims.
- Resume PDFs, recordings, PPTX/presentation PDFs are Git-eligible only after each relevant owner’s consent, secret and size review. No fabricated assets/metrics. Large video needs an accessible approved LFS/Release/hosted link; do not buy/publish automatically. Keep .env/keys/DB/checkpoints/dependencies/builds/caches ignored.
- Shared docs may be consolidated only after checking readers/links and moving unique guidance; runtime knowledge fixtures and canonical/generated contracts are not disposable documentation. Preserve append-only evidence.
- Other coding tools read this same file; CLAUDE.md/GEMINI.md redirect here. Optional local plugins are not teammate prerequisites; do not index/upload private material.
- Confirm actual deadline and organizer approval for eight members. Freeze new features three hours before submission. Prioritize working product + testable harness (50% of official rubric), genuine model evidence and actual deliverables—not extra architecture boxes or decoration. Report failures and untested platforms honestly, never “100% verified.”
