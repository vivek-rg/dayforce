# DayOne Proof — shared instructions for every human and AI agent

## Mandatory rules

1. **Always read AGENTS.md, PHASES.md, and CHANGES.md before starting any task.** Then read the phase, `docs/API_SPEC.md`, `docs/DATA_MODEL.md` and affected source. The long rationale is `Topic_3_Final_Guide.md`.
2. **Agree a small task and its files before editing.** Stay in that boundary so eight people do not overwrite each other. If more files are needed, ask the integrator to record the expanded boundary in PHASES.md before editing them. Better designs are welcome through the change process below; this is not a ban on improvements.
3. **Follow docs/API_SPEC.md and docs/DATA_MODEL.md exactly.** Contract changes need Track 1 review, updated canonical schemas/specification and an entry in CHANGES.md. Never hand-edit generated files or invent fields to unblock one UI.
4. **After every task:** run its verification, append an entry to CHANGES.md, and update only that phase/task status in PHASES.md. Report failures honestly. Tests using model stubs do not validate a real model.
5. **Never commit secrets or `.env`.** No model keys in frontend, logs, screenshots, prompts, resume examples, fixtures or recording. Use synthetic employee data only.
6. **Use your own branch with any valid name you choose**, small commits with clear messages, and a small PR into main. There is no required branch-name pattern. Do not push feature work directly to main, force-push shared branches, reset or discard another person's changes.

## Product and demo

We coordinate six onboarding categories by approved worker/location rules. Task completion is a claim; independent evidence establishes only the exact checked outcome. AI reads permitted evidence, asks a responsible person, and proposes narrow recovery. Trusted code validates, authorizes, records approval, executes a conditional local action and reads back the result. Never say a laptop was delivered because it was reserved.

Demo: Priya's offer/profile location conflict + completed equipment task without handover evidence → HR clarification/persisted pause → reviewed location diff → IT-approved reservation → fresh receipt showing collection pending. All systems/policies are fictional. One company, one backend, one bounded investigation agent, one local worker; not eight agents.

## Foundation status

Only `/api/health`, `/api/bootstrap`, the connectivity screen and initial SQLite schema work. Other routes return **501**, and service functions raise `NotImplementedError`. Do not assume authentication, AI, approvals, business seed data or security are complete. No feature phase was implemented during setup.

## Stack and structure

- Frontend: React + TypeScript + Vite; browser calls relative `/api` only.
- Backend: Python + FastAPI + Pydantic; standard-library SQLite, parameterized SQL, per-operation connections, short transactions. The user confirmed a local demo: keep the working database, give all eight teammates the same setup/fixture revision and use independent local files. Cloud PostgreSQL is conditional future work, not a completed migration; see docs/DATABASE_DECISION.md.
- Agent phase: LangGraph + SQLite checkpointer; explicitly selected local Ollama or approved hosted provider/model. P15–P25 plan discovery/selection for **Groq**, Cerebras, Mistral, Gemini and OpenRouter. P17–P22 implement six paths including local; P23 verifies shared free-tier/cost eligibility. All use the same validated `NextStep` and safety controls; this is planned, not implemented.
- Tests: pytest/FastAPI TestClient, Vitest, manual browser acceptance, CI; no external keys needed for foundation checks.

| Folder | Owner / role |
|---|---|
| `backend/app/auth/` | Track 1/P02; sessions, access checks |
| `backend/app/planning/`, `backend/app/evidence/`, `fixtures/` | Track 4/P03; approved rules, tasks, source records, deterministic checks |
| `backend/app/cases/`, `backend/app/agent/` | Track 6/P04; scoped cases, questions, graph, adapters, worker |
| `backend/app/actions/` | Track 5/P05; proposals, reviews, executor, read-back |
| `frontend/src/features/overview/`, `workspace/` | Track 2/P06 |
| `frontend/src/features/my-work/`, `review/` | Track 3/P07 |
| `frontend/src/features/model-settings/` (planned) | Track 2/P24; Track 1 wires root navigation |
| `backend/app/agent/providers/` (planned) | P16 dispatcher/catalog, P17–P22 claimed adapters, P23 eligibility gate; one writer per shared file |
| `evals/`, `backend/tests/test_acceptance.py` | Track 7/P08; independent evaluation/security/integration evidence |
| `docs/`, `resume/`, `video/`, `ppt/` | Track 8 for submission prose/assets; contracts reserved to Track 1 |
| `backend/app/shared/`, `frontend/src/shared/`, `scripts/`, root config, CI, locks, migrations | Track 1 integration ownership; no concurrent edits |

Each feature track owns its own `backend/tests/test_<module>.py` or co-located frontend `*.test.ts(x)`. Tests can read shared contracts; they do not rewrite another track's helpers.

## Contracts and conventions

- Canonical wire types: `backend/app/shared/contracts.py`. SQL authority: `backend/app/shared/schema.sql`. Generated: `docs/API_SPEC.md`, `docs/openapi.json`, `frontend/src/shared/api-types.ts` via `npm run contracts`.
- OpenAPI snapshot adds future bearer security and internal NextStep; runtime endpoints are still honest 501 stubs. Read success schemas as target contracts, not implemented capability.
- Python: snake_case functions/modules, PascalCase models, Ruff format/check, type new public functions. TypeScript: PascalCase components, camelCase functions, strict types, ESLint + Prettier. Import generated types with `import type`.
- JSON API: snake_case, ISO date strings, UTC timestamps, opaque string IDs. Enum spelling is exact. Pydantic forbids extra fields. Never cast away errors with `any` or suppress type checking to merge.
- No model-owned permissions, arbitrary SQL/URLs, unapproved source writes or public tool executor. Revalidate current identity/scope on resume. Never leak a privileged transcript to lower-role views.
- Input versions + immutable proposal + correct reviewer + expiry + atomic conditional write + stable action/event IDs + read-back are one safety path, not optional parts.
- Preserve old evidence/audit history. Missing/stale/unavailable evidence is UNKNOWN. A real mismatch is BLOCKED. NOT_APPLICABLE needs an approved rule.
- No write transaction held across network/model/human waits. On uncertain external outcomes reconcile before retry; don't claim exactly-once distributed effects.
- Small files and direct functions; no new dependency/framework, repository abstraction or generic workflow designer without an actual requirement and Track 1 approval.
- UI: native labels/buttons, keyboard focus, escaped text, non-color status labels, loading/empty/denied/stale/unavailable states. Do not implement decorative polish before the end-to-end path.

## Run and verify (from root)

Follow README for `.venv`, `npm ci`, pinned Python install and copying `.env.example`. Then:

```sh
npm run dev
# In a second terminal:
npm run smoke
npm run check
# Integrator only after changing canonical contracts:
npm run contracts
```

`npm run check` = Ruff, ESLint, formatting check, backend/frontend tests, frontend typecheck/build, generated-contract drift check. `npm run format` is for the integration owner only; feature tracks format **only their allowed paths** with the same tools. `npm start` serves the built frontend/API on loopback port 8000 after `npm run build`. Foundation startup initializes an empty schema + one non-private app_info row without deleting existing data; it never seeds business hires.

## Parallel work and shared-file collision policy

Track 1 owns root wiring (`main.py`, `App.tsx`, styles/API helper), dependencies/lockfiles, shared schema/types, and release gates. UI tracks export their module components; integrator wires navigation. Backend routers are already mounted, so route owners can implement inside their folder. A cross-module call uses the existing named service seam; changing that seam is a contract review, not a local shortcut.

Claim the owner field/status for your phase in a tiny PR or ask the integrator to do it. Only edit your own PHASES block and append CHANGES entries; do not reflow either file. Those two files are deliberately shared coordination exceptions to each phase's code boundary. On a merge conflict, Track 1 preserves **both** log entries and all independent phase updates. Never resolve by taking one whole file.

Other AI tools: tell Codex/Gemini/Antigravity explicitly to read this file. `CLAUDE.md` points here. Optional local plugins are not prerequisites and may not run on teammates' machines. Gortex is not tracked here; standard Git/search/test commands are sufficient. Do not index/upload personal resumes or private documents to external tools.

## Simple team handoff

1. Read the three root handoff files, your phase and affected contracts/source. Claim the phase with your name; one writer per file at a time, including multiple agents on one laptop.
2. Use any branch name. Give your coding agent only that phase's prompt, not permission to rewrite the project.
3. Use your own `.env`, `.venv` and local SQLite files. Share schema, reviewed migrations and synthetic fixture inputs in Git, **not database files or keys**. See [team setup](docs/TEAM_WORKFLOW.md).
4. Test, attach sanitized proof to the PR, append CHANGES and update your phase checklist. A screenshot supplements tests; it does not prove authorization or restart safety.
5. The integrator merges small reviewed changes. When blocked, record the missing seam/owner instead of making a fake success or permissive fallback.

Submission policy: resume PDFs, recordings, PPTX and presentation PDFs are **not ignored**; they can be included in GitHub after the relevant owner's consent, secret review and file-size checks. This is permission to version approved assets, not permission to publish everyone's personal details automatically. Keep `.env`, keys, local DB/checkpoint files, dependencies, builds and caches ignored. Use a real accessible link/LFS/Release for video beyond ordinary Git limits; do not buy or publish services automatically.

## Improving the architecture without moving backwards

The architecture, phase plan and these instructions can change. A higher-capacity model or confident agent is not proof that a change is better. Use P27: state the problem, smallest alternative, affected files/contracts/owners, data/privacy risks, before/after measurements and rollback plan. Get integrator plus affected-owner review before changing shared boundaries. Regenerate contracts only from canonical source; use a reviewed migration for existing data.

Run existing regression/security checks and the same held-out scenarios on the old and new versions; use real-model results for model-quality claims. Reject changes that weaken authorization, approval, evidence truth, durability, accessibility or secret protection. Discuss measured cost/latency/quality trade-offs rather than claiming “100% verified.” Record what was tested, failures, untested platforms and the accepted decision in CHANGES. Revert only the team's own reviewed change if it fails, never somebody else's work. See [change gate](docs/TEAM_WORKFLOW.md#accepting-a-better-design).

## Stop line

Use PHASES.md's dependency order. Stop adding features three hours before submission. A paid model, extra architecture boxes or fabricated metrics do not earn marks. Product usefulness + working, testable harness controls are the first 50% of the official rubric.
