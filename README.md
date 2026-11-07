[Video](video/VIDEO_LINK.md) | [PPT](ppt/README.md) | [Resume](resume/)

# OnboardIQ

**The next step. The right person. The proof behind it.**

OnboardIQ is a working, evidence-first **employee onboarding prototype for Topic 3** of the AI Innovation Challenge. It coordinates HR, IT, Payroll, Benefits, Training, Managers and Employees around one new hire. A task marked complete is a claim—not proof that the employee received the intended result. **A reserved laptop is not a delivered laptop.**

**Demo recording: not recorded/published yet.** The final playable recording/link belongs in [video/VIDEO_LINK.md](video/VIDEO_LINK.md); do not mistake the [rehearsal script](video/script.md) for a submitted video.

- [Problem and solution](#problem-and-solution) · [User journey and roles](#user-journey-and-roles)
- [Architecture](#architecture) · [Folder guide](#folder-guide)
- [Install and run](#install-and-run) · [Environment settings](#environment-settings)
- [AI keys and providers](#ai-keys-and-providers) · [Data and backups](#data-and-backups)
- [Verification](#verification) · [Troubleshooting](#troubleshooting)
- [Honest Topic 3 assessment](#honest-topic-3-assessment) · [Submission](#submission)

## Problem and solution

A new employee’s first day depends on several teams: documents may be uploaded but not reviewed; equipment may be reserved but not collected; a profile may disagree with an offer letter about the work location. A checklist alone can hide those gaps. People need to know **what must happen next, who owns it, and what the evidence actually establishes**.

OnboardIQ creates an approved profile/location-based plan, assigns owners/dependencies/deadlines, and keeps **task progress separate from outcome evidence**. When records disagree, an optional bounded AI investigation reads permitted context, asks the responsible person and proposes a narrow correction. Trusted code validates it; the correct person reviews it; conditional execution reads back the actual result. Manual workflows still work when AI is disabled, unavailable or quota-limited.

This is one fictional company and simulated source systems—not a live Dayforce integration, production payroll engine or autonomous HR department. All supplied employee documents/policies are synthetic. No customer adoption, time savings or production-readiness claim is established. The [official brief](AI_Innovation_Challenge_University_Brief%201.pdf) permits structured retrieval/mock data and equivalent technology; its exact deliverables and weights are summarized below.

## User journey and roles

### One example: Priya’s joining-day handoff

1. HR creates Priya’s engineering profile in Hyderabad; approved rules build the six-category plan.
2. Priya uploads a synthetic offer showing Bengaluru. Human document review and optional AI extraction reveal the mismatch.
3. The investigation reads scoped evidence and asks HR which location is authoritative. Its wait is saved; a model guess is not approval.
4. HR answers and reviews an exact proposed location change and plan diff.
5. IT separately approves a specific Bengaluru equipment reservation. Current identity, versions and expiry are checked again before the local write.
6. The fresh receipt says **reserved; collection pending**. Payroll, benefits, training and manager work remain independently owned. Resolving an investigation does not make every onboarding task complete.

The public `#/how-it-works` and `#/role-guide` pages explain this before sign-in and inside Help. Selecting a role in a guide changes explanatory text, not account permissions.

| Role     | Implemented work                                                                                                                            | Synthetic demo email                               |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| HR       | Create/link hires, review documents, answer clarification, review location proposals, maintain approved knowledge and oversee scoped status | hema@northstar.example                             |
| IT       | Provision simulated access, review equipment reservations and record equipment outcomes                                                     | imran@northstar.example                            |
| Payroll  | Record sanitized payroll profile/setup flags; no real bank/salary processing                                                                | padma@northstar.example                            |
| Benefits | Record invitation/enrolment/decline states; no insurer integration                                                                          | ben@northstar.example                              |
| Training | Record assigned course completion; no external LMS integration                                                                              | tara@northstar.example                             |
| Manager  | Record buddy and first-week plan for authorized hires                                                                                       | manoj@northstar.example                            |
| Employee | See own onboarding/tasks, upload documents and answer own questions                                                                         | priya@northstar.example or arjun@northstar.example |

Emails are not passwords. Set the private demo password before seeding. The seed creates three in-progress hires (Arjun, Leela, Ravi); **Priya’s account is deliberately unlinked so HR can create her hire during the demo**. New employee sign-up similarly requires HR to link a hire. Forgot password requests an HR-issued temporary password; no email is sent. Authorization is enforced on the server even when a screen/link is hidden.

## Architecture

```text
React + TypeScript + Vite
  Hash routes, labelled forms, sessionStorage bearer token
                 | relative /api only
                 v
FastAPI HTTP boundary + Pydantic contracts
  Authenticate -> current hire scope -> operation/field authority
                 |
    +------------+----------------------+------------------+
    |                                   |                  |
Approved rules / tasks / evidence    Documents /       Cases / questions
Department records / notifications  approved knowledge  persisted work queue
    |                                   |                  |
    |                               SQLite FTS5       One local worker
    |                                   |                  |
    |                       Shared governed AI harness <---+
    |                       prompt -> chosen transport -> JSON validation
    |                       -> semantic checks -> bounded repair / fallback
    |                                                   |
    +---- Human-reviewed immutable proposal <-----------+
                | correct reviewer + versions + expiry
                v
       Conditional local action + audit + read-back
                |
       SQLite application tables + private sibling uploads
```

### What each layer is responsible for

- **Frontend:** presents existing authorized work; no model keys, direct provider calls or authoritative role claims. Tokens are in sessionStorage, so refresh retains a session but closing its tab ends that browser storage. Server expiry/revocation remains authoritative. Source Sans 3 is bundled under its licence; no remote font request.
- **API/services:** routes validate inputs, authenticate and call named domain services. IDs are opaque. Out-of-scope records return an indistinguishable 404; wrong operations return 403; stale states return 409; invalid shapes return 422 without echoing secret input.
- **Planning/evidence:** approved executable rules select applicable tasks. Completing a task does not write independent source evidence. Results are VERIFIED, BLOCKED, UNKNOWN or approved NOT_APPLICABLE. Missing, unavailable or stale evidence is UNKNOWN—not success. Fictional prose uploads do not change executable rules.
- **Knowledge:** approved Markdown/TXT is chunked and searched with SQLite FTS5 plus access filtering. The assistant cites checked passage quotes or abstains/escalates. There is no vector/embedding store; matching a quote does not prove the answer’s entire meaning is correct.
- **AI harness:** four registered operations—policy answer, advisory document extraction, investigation next step and insight summary. Prompts live in source with versions. Responses undergo JSON/Pydantic and relevant semantic checks, with at most one repair attempt. Invalid output/outage produces an explicit manual path. Provider JSON mode is not a substitute for server validation.
- **Investigation/worker:** one bounded loop chooses allowlisted reads, asks a person, proposes or finishes/escalates. Work, steps, questions and counters live in application tables, so a separate LangGraph checkpointer was unnecessary. Saved waits resume against fresh authority; no write transaction stays open across model/network/human waits. Default investigation budgets:12 model attempts,16 reads,30-second model transport timeout and90-second active run segment. Transport quota waits and synchronous calls can extend observed wall-clock time; this is not a strict whole-case90-second SLA.
- **Actions:** immutable proposal/evidence/version bundle, correct HR/IT reviewer, expiry, stable action/event IDs, conditional local write, audit and read-back. Approval queues work; it is not execution success. Local transaction/replay controls are not an exactly-once guarantee for future distributed enterprise services.
- **Persistence:** standard-library SQLite, parameterized SQL, per-operation connections, foreign keys and short transactions. Uploaded files are private siblings of the DB, never a served repository folder. No general migration runner or production backup service is implemented.
- **Observability:** sanitized request IDs/status/timing, AI run references/model/prompt version/attempts/validation/latency and domain audit events. Operational logging avoids credentials and full prompts/documents. Case context can still contain permitted synthetic source text; treat the entire DB/backup as private.

### Why these technical choices

React/Vite keeps the existing role interface simple; FastAPI/Pydantic gives typed HTTP boundaries and generated OpenAPI. SQLite/FTS5 makes a local prototype reproducible without a database service or vector infrastructure. One worker and application-owned wait state fit the bounded recovery workflow. The harness is the **trusted controls around AI**, not a particular orchestration framework. A shared hosted service may justify PostgreSQL, SSO and stronger operations later; those are not completed migrations/integrations today.

## Folder guide

| Path                                                           | Purpose                                                                                                    |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `backend/app/main.py`                                          | App lifecycle, middleware/errors, mounted API routes, readiness and built-site serving                     |
| `backend/app/auth/`                                            | Password/session handling, account scope and role/field permissions                                        |
| `backend/app/planning/`                                        | Hires, approved-rule plans, tasks/dependencies and profile/location changes                                |
| `backend/app/evidence/`                                        | Scoped source records, independent checks and exact evidence receipts                                      |
| `backend/app/documents/`                                       | Private uploads, human reviews and advisory extraction                                                     |
| `backend/app/knowledge/`                                       | Approved policy documents, FTS5 retrieval, citations and HR escalation                                     |
| `backend/app/cases/`                                           | Scoped investigations, timelines, questions and human answers                                              |
| `backend/app/agent/`                                           | Bounded investigation state machine, allowlisted read tools and local work queue                           |
| `backend/app/ai/`                                              | Shared prompt/operation harness, transports and explicitly labelled offline stub                           |
| `backend/app/actions/`                                         | Immutable proposals, reviewer decisions, conditional execution and read-back                               |
| `backend/app/notifications/`                                   | In-app notifications, follow-up/escalation sweep                                                           |
| `backend/app/analytics/`                                       | Scoped dashboards, AI runs/insights and reliability measurements                                           |
| `backend/app/shared/`                                          | Canonical contracts/schema, SQLite/config/error/utilities                                                  |
| `backend/tests/`                                               | pytest unit/API/integration/security tests with isolated synthetic databases                               |
| `frontend/src/App.tsx`                                         | Session-aware root shell and route rendering                                                               |
| `frontend/src/features/auth/`, `guide/`                        | Sign-in/reset/sign-up and static public/in-app explanations                                                |
| `frontend/src/features/overview/`, `workspace/`                | Dashboard, directory/create/edit hire and plan/evidence/document/investigation/history tabs                |
| `frontend/src/features/my-work/`, `review/`                    | Owned tasks and exact HR/IT review/diffs                                                                   |
| `frontend/src/features/it/`, `payroll/`, `manager/`, `portal/` | Department screens; payroll folder also houses Benefits and Training; employee portal                      |
| `frontend/src/features/assistant/`, `knowledge/`, `insights/`  | Grounded answers, approved knowledge administration and advisory insights                                  |
| `frontend/src/features/notifications/`, `audit/`, `settings/`  | Answers/notifications, audit/reliability and existing settings—not a model selector                        |
| `frontend/src/shared/`                                         | API helper/generated types, session/routes/hooks, accessible primitives/icons and illustration             |
| `frontend/src/styles.css`, `fonts.css`                         | Shared black/white/red responsive design, reduced-motion and bundled font                                  |
| `frontend/PRODUCT.md`, `DESIGN.md`                             | Product truth and implemented visual-system rules; font licence stays alongside                            |
| `fixtures/`                                                    | Safe seed, executable fictional policy pack, sample documents and nine runtime knowledge Markdown files    |
| `evals/`                                                       | Evaluation runner, separate scenarios/answer keys and dated JSON results; see its focused README           |
| `scripts/`                                                     | Python launcher, dev/built startup, smoke, portable lockfile guard, deployment serve and contract exporter |
| `docs/`                                                        | API/data contracts, dated evaluation/verification and retained explanatory review—not another setup guide  |
| `docs/decisions/2026-11-07-improvement-plan.md`                | The one active backlog, decisions and change/acceptance gate                                               |
| `.github/workflows/`                                           | CI definition; configuration alone is not evidence of a remote passing run                                 |
| `video/`, `ppt/`, `resume/`                                    | Script/real video link, final five slides and individually consented team resumes                          |
| `.env.example`, `render.yaml`, `Dockerfile`                    | Safe config template and disposable synthetic container/hosting instructions                               |
| `.runtime/`, `.venv/`, `node_modules/`, `frontend/dist/`       | Private runtime/generated local artifacts, ignored—not submission source                                   |
| `frontend/.impeccable/`                                        | Ignored local design/reference/browser evidence artifacts, not a teammate prerequisite                     |
| `AGENTS.md`, `CHANGES.md`                                      | Shared contributor rules and append-only historical change evidence                                        |
| `CLAUDE.md`, `GEMINI.md`                                       | Small redirects to the same shared agent rules, not independent instructions                               |
| Original challenge PDF / `Topic_3_Final_Guide.md`              | Official authority and historical pre-build rationale; old framework plans are not current runtime facts   |

Canonical wire types are `backend/app/shared/contracts.py`; SQL authority is `backend/app/shared/schema.sql`. Generate `docs/API_SPEC.md`, `docs/openapi.json` and `frontend/src/shared/api-types.ts` with `npm run contracts` **only after an approved canonical change**. Never patch generated types to unblock one screen. [DATA_MODEL](docs/DATA_MODEL.md) explains storage; it does not override SQL.

## Install and run

### Prerequisites

Git, Node **22.14+ in 22.x or 24.x**, Python **3.12 or3.13**, pip/venv and a local folder outside OneDrive/network sync. No Docker, cloud database, API key or paid account is required for manual workflows or automated checks. Model inference is optional.

The configured team repository is https://github.com/vivek-rg/dayforce.git. Local changes on feat/onboardiq-demo-experience are not reproduced by cloning until the team reviews and publishes them. Do not assume CI or a deployed service contains an uncommitted fix.

### Windows PowerShell

Skip clone/cd if already in the prepared folder. `py -3.13` may replace `python` if that is how the supported interpreter is installed.

```powershell
git clone https://github.com/vivek-rg/dayforce.git dayone-proof
cd dayone-proof
python --version
node --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm ci
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
npm run check
```

Use `npm.cmd` if PowerShell blocks npm.ps1; do not weaken global execution policy. npm scripts find the root .venv, so activating it is optional.

### macOS / Linux Bash

```bash
git clone https://github.com/vivek-rg/dayforce.git dayone-proof
cd dayone-proof
python3 --version
node --version
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
npm ci
[ -f .env ] || cp .env.example .env
npm run check
```

Choose Python 3.12/3.13, not an older system Python. Latest local replay is Windows; clean-clone Linux/macOS/eight-member reproduction and remote CI remain explicit release checks.

### Configure, seed once and start

In the **root `.env` beside package.json**, privately set DEMO_PASSWORD to at least 12 characters. For deterministic rehearsal use `LLM_PROVIDER=stub` (**Offline rules—not AI**); for manual-only use `none`. No frontend .env or second backend .env is needed.

```sh
node scripts/python.mjs fixtures/seed.py
npm run dev
```

Open **http://127.0.0.1:5173** and choose a demo email. Enter the password privately, never during screen recording. The seed refuses existing users rather than resetting progress. Changing DEMO_PASSWORD later does not change stored password hashes. Startup alone creates schema/app_info, not business users/hires. An empty unseeded sign-in page is expected.

In a second terminal at repository root:

```sh
npm run smoke
npm run check
```

Keep the first terminal running; Ctrl+C stops only launcher-owned services. The launcher refuses occupied 5173/8000 ports. Never kill unknown processes.

### Built same-origin demonstration

Stop dev first:

```sh
npm run build
npm start
```

Open **http://127.0.0.1:8000**. PowerShell smoke:

```powershell
$env:SMOKE_BASE_URL = "http://127.0.0.1:8000"
npm run smoke
Remove-Item Env:SMOKE_BASE_URL
```

Bash: `SMOKE_BASE_URL=http://127.0.0.1:8000 npm run smoke`. API-only local start, when needed: `node scripts/python.mjs -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`.

- API docs: http://127.0.0.1:8000/docs
- Canonical readiness: http://127.0.0.1:8000/api/health
- Compatibility readiness: http://127.0.0.1:8000/health (same database-backed check; hidden from business OpenAPI)

Healthy response: `{"status":"ok","database":"ok","schema_version":2}`. A DB/schema failure returns a sanitized 503, not a fake 200. This readiness check is not a model inference test or certification of every business table/workflow.

## Environment settings

Only **one private root `.env`** is required locally. Copy `.env.example` once; never overwrite an existing private file. Real keys/passwords/DB files must not enter Git, React, VITE variables, screenshots, prompts or recordings. Process/shell overrides can win over file values. AI settings are reread from the root file; DB/worker/budget settings require restarting the backend. Do not switch models during a waiting case; immutable model snapshots are deferred.

| Setting                         | Meaning / safe use                                                                                                          |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_PATH`                 | Local SQLite file, default `.runtime/dayone.db`; relative paths resolve from repository root. Not a PostgreSQL URL.         |
| `DEMO_PASSWORD`                 | Private password of at least 12 characters for initial synthetic seed. No built-in credential.                              |
| `LLM_PROVIDER`                  | `none`, `stub`, `hosted` or `ollama`. Stub is scripted practice, not a real model.                                          |
| `LLM_MODEL`                     | Exact model/tag offered by your selected provider, not a guessed display name.                                              |
| `LLM_API_KEY`                   | The **one active hosted provider’s** key; unused for none/stub/local Ollama.                                                |
| `LLM_BASE_URL`                  | Trusted operator-selected hosted OpenAI-compatible API base, without `/chat/completions`. Never supplied by browser/model.  |
| `OLLAMA_BASE_URL`               | Local Ollama endpoint, default `http://127.0.0.1:11434`; keep loopback.                                                     |
| `WORKER_ENABLED`                | `1` runs the app’s local worker; tests use 0. Case processing needs the worker.                                             |
| `MAX_MODEL_CALLS`               | Investigation attempted-call budget, default 12. Validation repair also consumes attempts.                                  |
| `MAX_TOOL_CALLS`                | Persisted investigation read budget, default 16.                                                                            |
| `MODEL_TIMEOUT_SECONDS`         | Agent model-call transport timeout, default 30; other registered operations have their own limits.                          |
| `INVESTIGATION_TIMEOUT_SECONDS` | Active loop-segment deadline, default 90; human waits excluded, not a hard overall request/case SLA.                        |
| `SMOKE_BASE_URL`                | Optional smoke-script origin, default development origin; use 8000 for built start.                                         |
| `PORT`                          | Container `scripts/serve.py` bind port, default 8000; not a frontend key or a way to change the dev launcher’s fixed ports. |

There is no CHECKPOINT_PATH configuration in the current runtime. The coding assistant/editor’s MCP/provider settings are separate from this product’s backend inference settings.

## AI keys and providers

**Hosted inference needs a key for the selected provider; manual workflows and local Ollama do not. Never send your actual key in chat.** Paste the selected key only after `LLM_API_KEY=` in your private root .env. The current application does not read separate GEMINI_API_KEY or MISTRAL_API_KEY variables or pool/switch multiple keys automatically. You can keep unused keys in your private password manager, not the repository.

### App health is not a model endpoint

OnboardIQ runs on `http://127.0.0.1:8000` during local development. `/api/health` (and its `/health` alias) checks application/database readiness. This backend is **not an OpenAI-compatible inference server** and does not implement `/v1/models`. Repeated incoming `GET /v1/models` requests returning 404 mean a caller is asking the wrong service for that route; **they do not establish whether your private API key exists or is valid**. No in-repository caller for that path was found. The supplied access logs do not identify the caller; check the model-client/discovery tool or health-probe configuration privately. Do not add a fake models endpoint to silence it.

Keep three destinations distinct:

| Destination                                                        | Correct purpose                                           |
| ------------------------------------------------------------------ | --------------------------------------------------------- |
| OnboardIQ `/api/*` on port 8000                                    | Browser business API; browser uses relative `/api` calls  |
| `LLM_BASE_URL` (for example Groq `https://api.groq.com/openai/v1`) | Backend hosted inference; app appends `/chat/completions` |
| `OLLAMA_BASE_URL` (normally `http://127.0.0.1:11434`)              | Local Ollama service; app appends `/api/chat`             |

In an authorized signed-in session, `/api/health/ai` shows configuration plus the last recorded availability problem, without a provider call or key exposure. `available=true` means configured, **not** reachable, authenticated or quality-tested. `available=false` can mean intentionally off or incomplete provider/model/endpoint/key settings, not necessarily a missing key. A provider 401 may indicate rejected credentials/access; a provider 404 may indicate a wrong endpoint or unavailable model ID; 429 is quota/rate limiting. These outgoing model failures are different from the incoming `/v1/models` probe above. Verify inference only with an explicitly authorized synthetic operation, then inspect its actual result/run. No key inspection or live inference was performed for this troubleshooting update.

### Groq — historical live-tested path

```dotenv
LLM_PROVIDER=hosted
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
LLM_API_KEY=
```

Fill the blank locally with **your Groq key**, from https://console.groq.com/keys. The `openai/` model prefix names the model developer; it does not mean use an OpenAI key. This exact model has historical live evidence here, but current availability/quota must be checked in your account. A successful old run is not a guarantee it will work today.

### Mistral or Gemini — configuration candidates, not live-validated integrations

Keep `LLM_PROVIDER=hosted`; replace **all three** of base URL, model and key together:

| Provider             | `LLM_BASE_URL`                                            | `LLM_MODEL` and key                                                                     | Evidence here                                                                   |
| -------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Mistral              | `https://api.mistral.ai/v1`                               | Exact chat/JSON-capable model available in your Mistral account; its key in LLM_API_KEY | Official chat/JSON wire format reviewed; no live project run                    |
| Gemini Developer API | `https://generativelanguage.googleapis.com/v1beta/openai` | Exact compatible Gemini model in your AI Studio project; its key in LLM_API_KEY         | Official OpenAI-compatibility path reviewed; no live project run/native adapter |

Do not leave the Groq model ID while changing to Mistral/Gemini. The generic hosted transport sends bearer auth, chat messages, temperature0, max_tokens and JSON-object mode, then validates server-side. Provider/model capabilities vary: a config example is **not** proof this entire workflow is compatible. A native adapter, automatic catalogs, selector and per-case immutable model config remain deferred. No code change or key installation was made for Gemini/Mistral in this documentation task.

First obtain permission for a small synthetic compatibility/quality run and check account billing, quota, data-use and model licence/acceptable-use terms. A key, free website chat or open weights does not mean unlimited free API inference. Gemini is a different model/licensing choice, not automatically the open-weight model preferred by the challenge. No automatic paid/provider fallback or paid upgrade is authorized.

Official sources checked for this guide:
[Groq compatibility](https://console.groq.com/docs/openai), [limits](https://console.groq.com/docs/rate-limits), [Mistral chat](https://docs.mistral.ai/api/endpoint/chat), [Mistral JSON mode](https://docs.mistral.ai/inference/conversations/structured-output/json_mode), [Gemini compatibility](https://ai.google.dev/gemini-api/docs/openai), [Gemini pricing/data-use](https://ai.google.dev/gemini-api/docs/pricing). Terms/models change; check your account before recording.

### Ollama / no-model alternatives

For an already-installed local model, select `LLM_PROVIDER=ollama`, its exact installed tag in LLM_MODEL and loopback OLLAMA_BASE_URL. Install/start/select the model yourself; no download is automatic. `ollama list` shows installed tags. Transport is mock-tested, **not live-validated on this hardware**. Configure Ollama’s own service for local-only operation before making privacy claims; the app’s .env does not reconfigure an existing Ollama process. See [Ollama FAQ](https://docs.ollama.com/faq).

For manual-only use `LLM_PROVIDER=none`; for a scripted rehearsal use `stub` and keep its Offline rules label visible. The banner/config-status screen can identify configuration/failure, but does not itself prove a live inference worked. After authorized inference, inspect the actual AI run/model/validation and visible outcome. [Evaluation instructions](evals/README.md) use isolated DBs; do not run every provider just to test your keys.

## Data and backups

**Development:** each teammate uses the same reviewed commit/schema/fixture revision on an independent local SQLite file. Those copies provide the same starting story, not synchronized progress. Git shares code/schema/synthetic inputs—not DBs, sessions, uploads or keys.

**Recording:** use one demo laptop/backend/DB with prepared role sessions and one screen controller; everyone can narrate virtually. Separate laptops’ localhost addresses do not point at the same data. Sharing one live hosted application is a different deployment requirement; do not expose the local dev server or shared SQLite file to solve it. [Recording plan](video/script.md).

For a fresh practice without touching working data, stop the app and set a **new DATABASE_PATH** consistently for seed and app. Example PowerShell:

```powershell
$env:DATABASE_PATH = ".runtime/practice-2026-11-07/dayone.db"
node scripts/python.mjs fixtures/seed.py
npm run dev
# After stopping the app:
Remove-Item Env:DATABASE_PATH
```

Bash: set/export the same DATABASE_PATH for both commands. Prefer a separate practice **directory**, since uploads share the documents folder beside the DB. Never reset/reseed/delete a working DB to fix a screen or prepare a recording.

**Stopped backup:** stop backend/worker and all writers. Copy the DB, any SQLite journal/WAL/SHM companion files and its sibling `documents/` directory into a new private backup. For the default layout you may copy the complete stopped `.runtime/` directory to a new private location outside the source tree; do not recursively copy a backup into itself. Record original paths/code/schema/fixture versions. Never ordinary-copy a live SQLite file or delete journal files. Restore only on disposable copies until verified; preserve the current state before any owner-approved restore. An interrupted upload may leave orphan files—retain/reconcile them, do not delete blindly.

Initialization accepts v2 and can rebuild **empty** v1; it refuses v1 business data. `CREATE TABLE IF NOT EXISTS` is not a general migration system. Unsupported/newer schemas need owner-reviewed migration instructions and backups, not data deletion.

Docker/Render is an optional **disposable synthetic** deployment: the free blueprint has no persistent disk and AI is off by default. Instance replacement/redeploy may lose DB/uploads; automatic empty seeding is not restoration. Editing render.yaml does not alter an existing service’s dashboard settings. Durable hosting/authenticated hosted acceptance/restore remain unverified; no paid disk or cloud DB is purchased/configured by this guide.

## Verification

```sh
npm run check
npm run smoke
```

`check` runs lockfile validation, Ruff/ESLint, formatting, pytest/Vitest, strict TypeScript/Vite build and generated-contract drift. Smoke requires a running server and checks HTML plus database-backed readiness—not all browser workflows. Tests use isolated synthetic DBs and scripted provider replies, no paid keys.

Useful focused commands:

```sh
node scripts/python.mjs -m pytest backend/tests/test_foundation.py backend/tests/test_contracts.py -q
npm run test --workspace frontend
node scripts/python.mjs evals/run.py --provider stub --no-write
```

The last command is **not a real AI evaluation**. Model-quality evidence is separate: [EVALUATION.md](docs/EVALUATION.md) records a historical Groq run, untuned retrieval **5/11**, quota failures and non-independent scenarios. [VERIFICATION.md](docs/VERIFICATION.md) records dated tests/browser evidence and limitations; read its newest task entry rather than treating old counts as a fresh run.

No production SSO, multi-tenancy, encryption at rest, malware scanning, OCR, real payroll/insurer/Dayforce connector or full production/security certification. Current accepted development-tool advisories and upload-crash orphan limit remain documented. Do not run `npm audit fix --force` or upgrade frameworks blindly.

## Troubleshooting

| Symptom                                               | Safe next step                                                                                                                                                                                                                                                                                                   |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /health returns 404` in an older running service | Canonical path is `/api/health`; checked-in Render already uses it. This source adds the compatible `/health` alias. Restart local app or publish/deploy reviewed code yourself; local edits do not fix an old deployment. Verify the service dashboard’s actual health path—its setting was not inspected here. |
| `/health` or `/api/health` returns503                 | Check the chosen local DB path/schema and stopped backups. Do not hide database failure with a constant200 or delete data.                                                                                                                                                                                       |
| npm.ps1 blocked / missing .venv                       | Use npm.cmd; install the documented pinned dependencies with the matching Python interpreter.                                                                                                                                                                                                                    |
| Ports 5173/8000 occupied                              | Stop your own old app with Ctrl+C; identify, do not kill unknown services.                                                                                                                                                                                                                                       |
| Empty hires / Priya has no plan                       | Verify current role/scope and matching seed/app DB. A fresh empty DB has no business hires; HR must link/create Priya.                                                                                                                                                                                           |
| Password changed in.env but sign-in still fails       | Stored password hashes are unchanged. Use the existing HR reset flow; do not reseed working data.                                                                                                                                                                                                                |
| SQLite locked                                         | Stop duplicate writers and let short transactions finish; never delete locks/journals or use a synced/network drive.                                                                                                                                                                                             |
| `/v1/models` returns 404 on port 8000                 | Wrong service for model discovery; this is the onboarding app, not a model server. Check the requesting client/probe and point it at its real provider/model API. This does not diagnose a missing key.                                                                                                          |
| AI off after adding a key                             | Check selected provider/model/base URL and root .env privately; inspect process overrides. Only LLM_API_KEY is consumed for hosted inference. Never print the key for debugging.                                                                                                                                 |
| 401/429/timeout from provider                         | Check account/model access/quota privately; use manual fallback. No unbounded retries, automatic key rotation or paid upgrade.                                                                                                                                                                                   |
| Contract drift                                        | Correct canonical source through integrator review, regenerate once and rerun checks; never hand-edit generated types.                                                                                                                                                                                           |

## Honest Topic 3 assessment

**Yes: this is a credible Topic 3 submission, not merely a chatbot. No: winning/selection cannot be promised or assigned an honest percentage without the judges and competing entries.** The official rubric rewards a useful workflow and governed harness, not the number of API keys or animation effects.

| Official criterion      | What is credible now                                                                                                                  | What most needs evidence before submission                                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Product value 25%       | All six onboarding areas, profile/location rules, accountable handoffs and separate Claim/Proof                                       | Demonstrate one person’s end-to-end outcome; no measured user/time-saving study yet                                                        |
| Harness engineering 25% | Typed validation, scoped reads, persisted waits, budgets, correct human review, version/duplicate controls, read-back/manual fallback | Show controls working in the recorded build, including an actual safe refusal or restart                                                   |
| LLM implementation 20%  | Four grounded/advisory operations and one historical real-model investigation                                                         | Weakest evidence: untuned retrieval 5/11, quota interruptions, no independently held-out semantic scoring; no new live browser/model proof |
| Engineering quality 15% | Layered code, parameterized SQLite, generated API, automated tests and CI configuration                                               | Reviewed published commit, real CI and independent clean setup/restore; not all platforms exercised                                        |
| Demo recording 15%      | Rehearsal script and coherent Priya storyline can showcase the mechanism                                                              | Actual clear under-ten-minute recording and exactly five slides are still missing                                                          |

My recommendation: **stop expanding the product; prioritize one genuine model journey, honest safety proof and a polished recording**. More untested providers or cosmetic pages will not repair weak model evidence. The distinguishing pitch is trustworthy coordination and controlled recovery—not globally novel onboarding automation, guaranteed compliance or a production-ready enterprise suite.

Use [the active implementation plan](docs/decisions/2026-11-07-improvement-plan.md) for all unfinished work; there is no second phase board or separate temporary opinion document to maintain.

## Submission

The official PDF requires a GitHub repository with CI/setup guide, a 10-minute working-prototype recording linked here, and **exactly five slides**: problem/value; workflow/demo; architecture/harness; safety/testing/evaluation; future improvements/expected impact. Aim for 9:30, leaving a 30-second margin.

- [Recording script, eight speaking parts and researched tool options](video/script.md)
- [Actual video status/link](video/VIDEO_LINK.md) — pending, not fabricated
- [Five-slide deliverables](ppt/README.md) — real PPTX/PDF still required
- [Team resume consent/naming](resume/README.md) — team-requested assets, not a stated official PDF deliverable
- [One remaining-work plan](docs/decisions/2026-11-07-improvement-plan.md)

Your eight-person team size needs organizer confirmation: the brief says 3–5, with actual size variable. Confirm the actual deadline. Freeze new features three hours before it. Recordings/slides/resumes are Git-eligible after consent/secret/file-size checks; never invent files/links or publish someone’s personal details automatically. Oversized video needs a real accessible approved hosted/LFS/Release link; Git LFS is not preconfigured. Test playback without the owner’s login.

## Contributing and documentation policy

Read [AGENTS.md](AGENTS.md), the [active plan](docs/decisions/2026-11-07-improvement-plan.md) and [CHANGES.md](CHANGES.md) before edits. Agree a small task/file boundary; keep one writer per file. Integrator owns shared contracts/root wiring/dependencies. Use your own valid branch name and small reviewed PRs; never force-push shared history, reset someone else’s changes or directly push feature work to main. No automatic commit/push/deployment is authorized.

Only necessary distinct Markdown remains: this root guide, contributor rules/redirects, one current plan, canonical API/data explanation, dated evaluation/verification/change evidence, the preserved explanatory/original-rationale snapshots, frontend product/design truth, evaluation CLI guidance, actual submission status/script/consent instructions, and **nine runtime policy inputs**. Removing policy Markdown would break seed/retrieval/evaluation; it is data, not clutter. Completed history is evidence, not an active backlog.
