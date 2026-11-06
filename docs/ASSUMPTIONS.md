# Assumptions and 30-hour scope

## Confirmed inputs

- `../Topic_3_Final_Guide.md` is the agreed product/architecture input and remains in the repository unchanged.
- `../AI_Innovation_Challenge_University_Brief 1.pdf` is the official brief. Topic 3 coordinates documents, equipment, payroll setup, benefits enrolment, training and manager tasks by worker profile/location.
- Eight teammates, about 30 hours remaining, one local recorded ten-minute demo, five slides, GitHub submission. No additional organizer constraints reported by the user.
- React/TypeScript/Vite, FastAPI/Pydantic, SQLite, LangGraph investigation. Local Ollama plus requested hosted adapters: **Groq**, Cerebras, Mistral, Gemini and OpenRouter, with explicit selection and the same safety harness. No paid plan/payment-method setup is authorized; keys/credits/free eligibility must be verified separately.
- The user reconfirmed a **local demo** and prioritizes easy setup for all eight teammates. Keep SQLite and identical commands/fixture revisions; do not require cloud configuration or sync live database files. Neon/Supabase managed PostgreSQL are conditional shared-hosting options, not implemented backends. MongoDB offers no established time advantage for this relational workflow. All engines still need migration discipline; see DATABASE_DECISION.md.

## Decisions made to avoid blocking the foundation

1. Foundation means health + database-backed bootstrap only, not a finished onboarding product. Typed business routes deliberately return 501 until their owner implements and tests them.
2. One fictional organization, one backend process, one worker, local disk. Bind to loopback only. No public deployment, multi-tenancy, production SSO, live enterprise integration, payments or real personal data.
3. Use Python 3.12 or 3.13 and Node 22.14+ (22.x) or 24.x, matching package.json. The development runner uses `.venv` without shell activation on Windows/macOS/Linux. Node 24 / Python 3.13 are the verified local environment; CI is configured for Ubuntu/Python 3.12/Node 22, not evidence of a remote run.
4. No inference/key/download is needed for foundation startup. Model modules are stubs. Every adapter needs separate mock control tests and an actual live selected-model smoke before being advertised as live-validated. Automatic catalog/selector is planned in P15–P25, not working now.
5. Track 1 is the integration lead until the team assigns a real name in PHASES.md. Track numbers denote people, not services or agents. Nobody is assigned an invented personal name.
6. The remote GitHub URL does not exist here yet. README clone commands accept it as an interactive input; the team must create/push the remote manually. No remote/account/license is invented.
7. Eight-person participation follows the user's confirmation. The brief lists 3–5 with actual size variable; this is not independent eligibility approval.
8. The source text, inventory and payroll systems are simulated. All observations retain source, version and time. A task completion never constitutes proof of an outcome.
9. Use opaque bearer demo sessions (no browser-local role claims), expiring after eight hours, for the 30-hour implementation. This avoids cookie/CSRF infrastructure; frontend keeps the bearer token in memory. Login credentials come from local environment, stored only as salted password hashes. Authentication is NOT implemented by the foundation.
10. Calendar-day deadlines; joining dates are ISO dates, timestamps are UTC. Location IDs HYD-DEMO and BLR-DEMO are fictional, not law.
11. This 30-hour contract accepts only the two configured location IDs. An unknown location is rejected with 422 and sent to manual HR review outside automatic hire creation; a supported profile with no applicable approved pack returns 409 POLICY_REVIEW_REQUIRED. This deliberately narrows the guide's broader unsupported-profile intake scenario rather than inventing default rules.

## Core demo and scope cuts

Create Priya's hire and six-category plan. Approved profile says Hyderabad; supplied offer text says Bengaluru. Equipment task claims completion but separate source has reservation only. Agent reads permitted evidence, asks HR, pauses durably, and resumes after an authorized answer. HR reviews location impact; IT separately approves reservation. Version-checked execution reads back equipment state and says **reserved; collection pending**.

Must keep: normal plan, useful model interpretation, human question, persisted wait, exact reviewed action, authorization, stale/duplicate protection, independent read-back, honest uncertainty.

First cut if needed: executable location change. Keep its read-only preview and fully implement one IT reservation. Never cut permission checks to make the demo work. No policy editor, generic workflow builder, extra agents, OCR, email, Slack, vector database, cloud hosting or CSS redesign.

## Dependency map

Foundation/contracts (P01) → auth (P02), plan/data/checks (P03), investigation (P04), actions (P05), overview UI (P06), work/review UI (P07), evaluation scaffolding (P08), submission work (P13).

P02 + P03 + P04 + P05 + P06 + P07 + P08 plus one live validated adapter → integrated end-to-end journey (P09) → demo polish (P10) → local release rehearsal (P11) → README finalization (P12) → submission check (P13). Submission drafting starts early; its final gate follows P12.

The board now has **28 phases** while preserving legacy P01–P13 IDs. P14 covers local DB reproducibility; P15 contracts → P26 necessary durable schema/migrations → P16 discovery/dispatcher → P17–P22 adapters → P23 shared eligibility gate → P24 selector → P25 common live comparison. P27 is the improvement decision process; P28 collects real teammate setup evidence. See PHASES for exact parallelism and file boundaries. Additional providers increase work: the original 30-hour schedule is not a promise that the expanded scope fits. Re-estimate with the team, integrate one model path early, and explicitly record approved deferrals before the final freeze.

## Remaining real inputs

- Team names, repository URL, model-machine RAM/GPU/disk and actual provider access.
- Teammates' strongest tools; retain these contracts if implementation tools change.
- Whether a paid inference experiment is justified by measured failures. Start at $0; optional US$5 ceiling requires explicit team approval and provider spend controls.
- Resumes require each person's consent. Public repositories expose personal contact details; do not publish them without consent.
- Submission assets are deliberately **not ignored**: consented resumes, size-reviewed recordings, PPTX and presentation PDFs can be versioned normally. Secrets, local DB/checkpoint files and generated dependency/build/cache folders remain ignored. Large video still needs an approved delivery method within platform limits.

## Authority and change control

The original final guide is product rationale, not evidence of implementation or an immutable architecture. `API_SPEC.md`, `openapi.json`, `DATA_MODEL.md`, `backend/app/shared/contracts.py`, and `backend/app/shared/schema.sql` define the current executable handoff. P15 explicitly plans a reviewed extension, not a private adapter/UI contract. Conflicts are resolved by Track 1 with a logged canonical revision and generated outputs, never by silently changing a field on one branch.

Any teammate/coding agent may propose a better solution via P27. Accept only after concrete criteria, before/after evidence, affected-owner review and migration/rollback planning; retain safety gates and disclose untested areas. Branch names are user choice. Each clone uses independent SQLite/application/checkpoint files; shared fixture/schema/migration revisions, not raw database synchronization, establish a common baseline. See TEAM_WORKFLOW and PROVIDERS for commands, cost/privacy caveats and handoffs.
