[Video](#demo-video) | [PPT](#presentation) | [Resumes](#team-resumes)

# OnboardIQ

**The next step. The right person. The proof behind it.**

OnboardIQ is an employee onboarding prototype built for **Topic 3: Employee Onboarding** of the AI Innovation Challenge. It brings HR, IT, Payroll, Benefits, Training, Managers and Employees into one workflow, with clear responsibilities and evidence for each outcome.

[Overview](#project-at-a-glance) · [The problem](#problem-and-solution) · [User journey](#user-journey-and-roles) · [Architecture](#architecture) · [Setup](#install-and-run) · [Quality checks](#verification)

## Submission materials

### Demo video

**Watch the demo:** `DEMO_VIDEO_LINK`

Recording location: `video/`.

### Presentation

**Open the five-slide presentation:** `PRESENTATION_FILE_LINK`

Presentation location: `ppt/`.

<!-- Replace the two link placeholders above with the final accessible video and presentation links. The folder paths are upload locations, not links to files that already exist. -->

### Team resumes

All eight uploaded resumes are in [resume/](resume/):

| Team member | Resume |
| --- | --- |
| Danyal Ibrahim | [PDF](resume/danyal_ibrahim_resume.pdf) |
| Kavana Vijay Hegde | [PDF](resume/KAVANA_VIJAY_HEGDE_.pdf) |
| Koushik A | [PDF](resume/koushik_a_resume.pdf) |
| Lakshmi M | [PDF](resume/Lakshmi_M_1DT23CS103.pdf) |
| Ruhinaaz | [PDF](resume/Ruhinaaz_resume.pdf) |
| Swet Anshu | [PDF](resume/Swet_Anshu_resume.pdf) |
| Vinay | [PDF](resume/vinay_resume.pdf) |
| Vivek R Gowda | [PDF](resume/Vivek_R_Gowda_resume.pdf) |

Challenge rules: [AI Innovation Challenge brief](AI_Innovation_Challenge_University_Brief%201.pdf).

## Project at a glance

> **A checklist tells you what someone marked done. OnboardIQ also shows what the evidence supports.**

One hire gets one coordinated plan. Each team sees its own work, knows what is blocking the next step and records the actual outcome. AI helps investigate disagreements; it does not replace the person responsible for the decision.

```text
New-hire profile -> Approved plan -> Owned team tasks -> Checked evidence
                                                              |
                                                     Something disagrees?
                                                              |
                                Read facts -> Ask a person -> Propose a change
                                                              |
                                          Human approval -> Execute -> Verify
```

| What we coordinate | What people record |
| --- | --- |
| Documents | Employee submissions and HR review decisions |
| Equipment and IT access | Device reservation, handover and simulated account provisioning |
| Payroll setup | Profile/setup confirmation flags, not real banking information |
| Benefits enrolment | Invitation, enrolment or permitted decline |
| Training | Assigned courses and recorded completion |
| Manager tasks | Buddy assignment and a first-week plan |

**Built with:** React, TypeScript and Vite · FastAPI and Pydantic · SQLite with FTS5 search · optional hosted or local model inference.

## Problem and solution

A new hire depends on several teams before they can start work. Documents need review, equipment needs delivery, payroll needs setup, and training and manager tasks need coordination. A checklist can look complete even when the employee is still blocked.

OnboardIQ separates **task progress** from **proof of the result**. A reserved laptop is not a delivered laptop. Uploading a document does not mean HR has verified it. Each task has an owner, due date and dependencies; separate checks show whether the expected outcome is supported by current evidence.

Plans come from approved rules based on the worker profile and location. When records disagree, an optional AI investigation reads permitted evidence, asks the responsible person for clarification and proposes a limited correction. Application code validates the proposal, a person approves it, and the system checks the actual result after execution. Manual workflows continue when AI is disabled or unavailable.

### Progress is not the same as proof

| What happened | What it does not prove | What still needs checking |
| --- | --- | --- |
| An employee uploaded an offer letter | HR has verified it | A permitted human review |
| IT reserved a laptop | The employee received it | The handover record and matching assignee |
| Someone completed a task | Its intended outcome happened | Current independent evidence |
| HR approved a change | The change executed successfully | Execution and a fresh result read-back |
| An investigation was resolved | Every onboarding task is complete | The remaining teams' tasks and outcome checks |

This prototype uses one fictional company, synthetic employee documents and simulated source systems. It is not a live Dayforce integration or a production payroll system.

## User journey and roles

### Example: Priya joins the company

1. **HR creates the hire.** Priya is initially listed as an engineer joining in Hyderabad. Approved rules create her onboarding plan across all six challenge areas.
2. **Priya submits documents.** Her synthetic offer letter says Bengaluru. Document review and optional extraction help identify the disagreement. Only a human reviewer can verify the document.
3. **The investigation checks evidence.** It reads permitted records and asks HR which location is correct. It saves the question and waits rather than treating a model guess as approval.
4. **HR reviews the correction.** The proposed location change shows the exact change and its effect on the plan. Approval does not silently complete unrelated work.
5. **IT reviews the equipment action.** A separate proposal reserves a specific Bengaluru laptop. The server rechecks permissions, record versions and expiry before execution.
6. **The system reads back the result.** It reports “reserved; collection pending,” not “delivered.” Payroll, benefits, training and manager work keep their own owners and evidence.

| Role | Main responsibility | Synthetic demo email |
| --- | --- | --- |
| HR | Create hires, review documents, answer clarifications and review location changes | `hema@northstar.example` |
| IT | Record access provisioning, review reservations and record equipment handover | `imran@northstar.example` |
| Payroll | Record sanitized payroll setup status, without real bank or salary processing | `padma@northstar.example` |
| Benefits | Record invitation, enrolment or decline status | `ben@northstar.example` |
| Training | Record assigned course completion | `tara@northstar.example` |
| Manager | Assign a buddy and record the first-week plan for authorized hires | `manoj@northstar.example` |
| Employee | View own plan, upload documents and answer own questions | `priya@northstar.example` or `arjun@northstar.example` |

The seed includes three hires already in progress: Arjun, Leela and Ravi. Priya has an account but no linked hire, so HR can create her during the demonstration. New employee sign-up also needs HR to link a hire before onboarding records become available.

The public `#/how-it-works` and `#/role-guide` pages explain the workflow before sign-in and are available through Help. Selecting a role in a guide does not change account permissions. Forgot password sends an in-app request for HR to issue a temporary password; it does not send email.

## Architecture

```text
React + TypeScript + Vite
             | relative /api requests
             v
FastAPI + Pydantic contracts
             | authentication, role and hire-scope checks
             v
Planning / Documents / Evidence / Department records
Knowledge search / Investigations / Notifications / Audit
             |
             +--> Shared AI harness --> Hosted model or local Ollama
             |       | typed validation, bounded repair, manual fallback
             |       v
             |   Human-reviewed proposal
             |       | permission, version and expiry checks
             |       v
             |   Conditional action + audit + result read-back
             v
SQLite application state + private uploaded files
             ^
             |
One local worker resumes saved investigations and actions
```

### How the important parts work

- **Planning:** approved executable rules select tasks for the worker profile and location. The plan tracks owners, dependencies and deadlines. Uploading policy prose does not change these rules.
- **Evidence:** checks compare the intended result with source records. Results are `VERIFIED`, `BLOCKED`, `UNKNOWN` or approved `NOT_APPLICABLE`. Missing, unavailable or stale evidence is not success. Marking a task complete does not create proof.
- **Documents:** uploads are limited to 5 MB and supported PDF, PNG, JPEG or TXT content, stored privately and reviewed by a person. Extraction is advisory. Text PDFs and plain text can be read; scanned images need manual review because OCR is not implemented.
- **Knowledge assistant:** approved Markdown/TXT policies are searched using SQLite FTS5 with access filtering. Answers must cite checked passage quotes, or the assistant abstains and offers HR escalation. Quote matching does not prove that every answer is semantically correct.
- **AI harness:** four operations share prompt versions, typed outputs, validation and run records: policy answers, document extraction, investigation next steps and insight summaries. Invalid output can receive at most one repair attempt, then falls back safely.
- **Investigations:** the model can choose only allowlisted reads, ask a person, propose an action or finish/escalate. Questions, steps, budgets and waiting state are saved in SQLite. No database transaction stays open across a model call or human wait. Default limits are 12 model attempts, 16 reads and a 90-second active run segment; this is not a hard whole-case time guarantee.
- **Actions:** proposals preserve the exact change, evidence, expected record versions, reviewer role and expiry. HR reviews location changes; IT reviews equipment reservations. Approval queues work rather than claiming execution succeeded. Execution rechecks authority and current versions, writes conditionally, records an audit event and reads back the result.
- **Access and observability:** the server checks the current user, role and hire scope. Passwords and session tokens are stored as hashes; browser tokens use tab-scoped sessionStorage. Request IDs, timings, AI run references and audit events help trace behavior without logging full prompts or credentials. The database and case history must still be treated as private.

### Key technical decisions

The **AI harness** is the set of trusted controls around the model: what it may read, what shape it must return, who must approve a change, how much work it may attempt and how the result is checked. It is not just a chat prompt.

React and Vite provide a typed role-based interface. FastAPI and Pydantic provide request validation and OpenAPI contracts. Standard-library SQLite and FTS5 make the prototype easy to run without a separate database or vector service. One worker and application-owned saved state support the bounded investigation flow; a separate orchestration framework is not required by the runtime.

Canonical API types are defined in [contracts.py](backend/app/shared/contracts.py), and storage is defined in [schema.sql](backend/app/shared/schema.sql). `npm run contracts` generates the API documentation, OpenAPI JSON and frontend wire types. Change the canonical source first, not the generated files.

## Folder guide

| Path | Contents |
| --- | --- |
| `backend/app/` | FastAPI routes, authentication and domain services |
| `backend/app/planning/`, `backend/app/evidence/` | Rule-based plans, task progress and independent outcome checks |
| `backend/app/documents/`, `backend/app/knowledge/` | Private document review and approved policy search |
| `backend/app/agent/`, `backend/app/cases/` | Saved investigations, local worker and human questions |
| `backend/app/actions/`, `backend/app/ai/` | Reviewed proposals, controlled execution, prompts, providers and validation |
| `backend/app/auth/` | Accounts, sessions, roles and hire-scope permissions |
| `backend/app/analytics/`, `backend/app/notifications/` | Database-backed metrics, audit/AI run views, notifications and follow-up |
| `backend/app/shared/` | Canonical contracts, SQL schema, configuration and shared utilities |
| `backend/tests/` | Backend unit, API, integration, security and resilience tests |
| `frontend/src/features/` | Role screens, onboarding workspace, guides and employee portal |
| `frontend/src/shared/` | API client, generated types, session handling and shared UI |
| `fixtures/` | Synthetic seed, executable policy rules and sample documents |
| `fixtures/knowledge/` | Nine Markdown policies used by seeding, retrieval and evaluation; these are application data |
| `evals/` | Evaluation runner, scenarios, separate answer keys and historical results |
| `scripts/` | Startup, smoke checks, contract generation and tooling |
| `docs/` | [API specification](docs/API_SPEC.md), [OpenAPI JSON](docs/openapi.json), [data model](docs/DATA_MODEL.md) and [evaluation results](docs/EVALUATION.md) |
| `.github/workflows/ci.yml` | Automated repository checks on push and pull request |
| `frontend/DESIGN.md`, `frontend/PRODUCT.md` | Interface design rules and product behavior notes |
| `frontend/OFL-Source-Sans-3.txt` | Licence for the bundled Source Sans 3 font |
| `resume/` | Uploaded team resumes |
| `ppt/`, `video/` | Presentation and recording upload locations |
| `.env.example`, `Dockerfile`, `render.yaml` | Safe environment template and optional container hosting configuration |

Local `.env`, `.runtime/`, `.venv/`, `node_modules/` and `frontend/dist/` are private or generated artifacts, not submission source.

### What `docs/` and `evals/` are for

These folders have different jobs. **The website does not load saved evaluation reports to answer questions or populate dashboards.** It uses its own database, approved knowledge and current workflow records.

| Files | Purpose | Where they are used |
| --- | --- | --- |
| `docs/API_SPEC.md`, `docs/openapi.json` | Generated descriptions of the API | Contract tests and `npm run contracts:check`; deleting them breaks current checks |
| `docs/DATA_MODEL.md` | Human-readable explanation of database tables and state | Developer/reviewer reference, not runtime input |
| `docs/EVALUATION.md` | Explanation of measured model/retrieval results and limits | Submission evidence, not runtime input |
| `evals/run.py`, `evals/scenarios.json`, `evals/answer_keys.json` | Reproducible evaluation program, questions and expected sources | Explicit evaluation commands; `evals/` is also included in linting |
| `evals/results/*.json` | Saved outputs from past evaluation runs | Raw evidence behind the evaluation report; not loaded by the app or by subsequent evaluation runs |
| `evals/README.md` | Instructions for rerunning and interpreting evaluations | Developer/reviewer reference |

Runtime knowledge comes from a separate place: `fixtures/seed.py` loads the nine `fixtures/knowledge/*.md` policies and `fixtures/policy_pack.json` into a new synthetic database. Policy search then uses approved database content, not evaluation questions or answer keys. The evaluation runner seeds its own temporary database and writes reports only when `--no-write` is omitted.

FastAPI also generates the running app's `/docs` and `/openapi.json` from Python routes and models. Those URLs are not a static website backed by the repository's `docs/` folder. The checked-in snapshot includes additional security metadata and internal agent schemas for review.

## Install and run

### Requirements

- Git
- Node.js **22.14+ in 22.x, or 24.x**
- Python **3.12 or 3.13**, with pip and venv
- A local folder outside network drives or cloud-sync folders

No model key, Docker installation or cloud database is required for manual workflows or automated checks.

### Windows PowerShell

Skip clone and cd if you already have the repository.

```powershell
git clone https://github.com/vivek-rg/dayforce.git
cd dayforce
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm ci
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Use `py -3.13` instead of `python` if needed. If PowerShell blocks `npm.ps1`, use `npm.cmd`; do not change the global execution policy.

### macOS / Linux

Use a Python 3.12 or 3.13 interpreter.

```bash
git clone https://github.com/vivek-rg/dayforce.git
cd dayforce
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
npm ci
[ -f .env ] || cp .env.example .env
```

### Configure, seed and start

Edit the single private root `.env` file:

- Set `DEMO_PASSWORD` to a private password of at least 12 characters. There is no built-in password.
- For manual workflows, use `LLM_PROVIDER=none`. For scripted rehearsal, use `LLM_PROVIDER=stub`, visibly labelled **Offline rules—not AI**. Real model configuration is described below.

```sh
node scripts/python.mjs fixtures/seed.py
npm run dev
```

Open **http://127.0.0.1:5173**, choose a demo email and enter the private password. Scripts automatically use the root `.venv`; activation is optional. Startup initializes the schema but does not create business users. Seed only an empty database: the seed refuses existing users and never resets their progress. Changing `DEMO_PASSWORD` later does not change stored passwords.

In a second terminal at the repository root:

```sh
npm run smoke
npm run check
```

Keep the first terminal running. Ctrl+C stops the services started by the launcher. If ports 5173 or 8000 are occupied, stop your own old application rather than killing unknown processes.

### Run the built application

Stop development mode first, then:

```sh
npm run build
npm start
```

Open **http://127.0.0.1:8000**. For the built-server smoke check in PowerShell:

```powershell
$env:SMOKE_BASE_URL = "http://127.0.0.1:8000"
npm run smoke
Remove-Item Env:SMOKE_BASE_URL
```

On Bash: `SMOKE_BASE_URL=http://127.0.0.1:8000 npm run smoke`. API documentation is at `http://127.0.0.1:8000/docs`. Database-backed readiness is at `/api/health`, with `/health` as a compatibility alias.

## Environment settings

Keep credentials only in the private root `.env`, never in Git, frontend `VITE_*` variables, screenshots or recordings. Shell/process overrides can take precedence. AI settings are reread from the root file; restart the backend after changing database, worker or budget settings.

| Setting | Purpose |
| --- | --- |
| `DATABASE_PATH` | SQLite file path; default `.runtime/dayone.db`, relative to the repository root |
| `DEMO_PASSWORD` | Private initial seed password, at least 12 characters |
| `LLM_PROVIDER` | `none`, `stub`, `hosted` or `ollama` |
| `LLM_MODEL` | Exact model ID or installed local model tag |
| `LLM_API_KEY` | Server-only key for the selected hosted provider |
| `LLM_BASE_URL` | Trusted hosted model API base; do not append `/chat/completions` |
| `OLLAMA_BASE_URL` | Local Ollama service, normally `http://127.0.0.1:11434` |
| `WORKER_ENABLED` | `1` enables saved investigation/action processing; tests use `0` |
| `MAX_MODEL_CALLS`, `MAX_TOOL_CALLS` | Investigation budgets; defaults 12 and 16 |
| `MODEL_TIMEOUT_SECONDS` | Investigation model transport timeout; default 30 seconds |
| `INVESTIGATION_TIMEOUT_SECONDS` | Active run-segment deadline; default 90 seconds, excluding human waits |
| `SMOKE_BASE_URL` | Optional smoke target; defaults to the development origin on port 5173 |
| `PORT` | Container server port used by `scripts/serve.py`; default 8000 |

## AI keys and providers

Only one provider is active at a time. The hosted transport uses an OpenAI-compatible chat endpoint; the local transport uses Ollama. Provider/model support must be verified rather than assumed.

The historical real-model evaluation used this Groq configuration:

```dotenv
LLM_PROVIDER=hosted
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
LLM_API_KEY=
```

Fill the key privately. The `openai/` model prefix does not mean an OpenAI key: this endpoint requires a Groq key. Review the chosen model licence, acceptable-use terms, provider privacy, account quota and any cost before use. Historical success is not a guarantee of current availability.

For a different compatible host, change the base URL, model and key together. The app reads `LLM_API_KEY`, not separate `GEMINI_API_KEY` or `MISTRAL_API_KEY` variables. Gemini/Mistral compatibility and local Ollama operation are not established by the historical Groq run. For Ollama, select `LLM_PROVIDER=ollama` and an already installed `LLM_MODEL` tag; keep the service local. No model is downloaded automatically.

### App health is not a model endpoint

Port 8000 serves OnboardIQ, not a model API. `/api/health` checks the application database, and `/v1/models` is not implemented. A 404 there does not prove a key is missing. Point model discovery at the actual provider, not this application.

Authenticated `/api/health/ai` reports configuration and recorded availability problems, not a live authentication or inference test. Provider 401, 404 and 429 errors can mean credentials/access, endpoint/model availability and quota problems respectively. Manual workflows remain available when model calls fail.

## Data and backups

Each teammate has an independent local SQLite database. Git shares code, schema and synthetic fixtures, not live progress, sessions, uploads or credentials. For a shared recording, use one prepared backend/database and role sessions on the recording machine. Different laptops' localhost addresses are not the same application.

Uploaded files live in a private `documents/` directory beside the database. For a fresh rehearsal, choose a new database **directory** with `DATABASE_PATH` before seeding and use the same value when starting the app. Do not delete or reseed a working database.

To back up, stop the backend, worker and all writers. Copy the database, any SQLite journal/WAL/SHM companions and the sibling documents directory to a private location outside the repository. Copying only the database misses uploads; ordinary-copying a live SQLite database is unsafe. Test restoration on disposable copies, preserving the current data.

The optional free Render configuration has no persistent disk. Replacement or redeployment can lose its database and uploads. It is intended only for disposable synthetic demonstrations, not durable employee storage. No general production migration or backup service is implemented.

## Verification

```sh
npm run check
npm run smoke
node scripts/python.mjs evals/run.py --provider stub --no-write
```

- `check` runs the portable lockfile guard, Ruff/ESLint, formatting, backend and frontend tests, strict TypeScript/Vite build and generated-contract drift checks.
- `smoke` needs a running application and checks served HTML plus database-backed readiness and bootstrap. It is not a complete browser acceptance test.
- The evaluation command uses an isolated temporary database and scripted offline rules, without paid model calls or saved result files. It measures retrieval and harness behavior, not model quality. See [evaluation instructions](evals/README.md).

[Historical evaluation results](docs/EVALUATION.md) include one live Groq investigation, quota failures and **5/11 retrieval recall on untuned questions**. The scenarios were not independently authored, and quote validation is not semantic answer scoring. Automated control tests must not be presented as a real-model accuracy rate or measured customer savings.

CI is configured in [.github/workflows/ci.yml](.github/workflows/ci.yml). A local passing check is not proof that a remote GitHub Actions run or deployed service is passing.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Missing dependencies | Install the pinned requirements and run `npm ci` using the supported Python/Node versions |
| Empty installation or Priya has no plan | Seed an empty database once; HR must create/link Priya before her plan exists |
| Password change in `.env` does not change sign-in | Existing hashes are unchanged; use the HR-mediated reset flow, not reseeding |
| SQLite is locked | Stop duplicate writers, avoid synced/network folders and never delete journals to clear a lock |
| Readiness returns 503 | Check the selected database and schema; preserve data and backups rather than hiding the failure |
| AI is unavailable | Check provider/model/base URL privately, quota and shell overrides; use the manual workflow |
| Generated contracts differ | Update canonical source, regenerate with `npm run contracts` and rerun checks |

## Challenge alignment and limits

The [official brief](AI_Innovation_Challenge_University_Brief%201.pdf) requires a repository with clear setup, user journey, architecture and technical decisions; a **10-minute working-prototype demo linked in this README**; and **exactly five slides** covering:

1. Problem and user value.
2. Product workflow and demo.
3. Architecture and harness design.
4. Safety, testing and evaluation evidence.
5. Future improvements and expected business impact.

The evaluation weights are product value **25%**, harness engineering **25%**, LLM implementation **20%**, engineering quality **15%** and demo recording **15%**. The brief permits AI-assisted coding, structured retrieval/mock data and equivalent technology choices. It lists 3–5 members with actual size variable; confirm any team-size variation with the organizers. Resumes are team submission materials, not a stated deliverable in this brief; publish them only with each person's consent.

OnboardIQ demonstrates the six onboarding areas with guarded model assistance and human accountability. It does not claim production SSO, multi-tenancy, encryption at rest, malware scanning, OCR, real payroll/insurer/LMS/Dayforce connections, distributed exactly-once execution or production security certification. Search quality, independent evaluation and durable hosted operations remain improvement areas. Development-tool dependency advisories also need review; do not force-upgrade the stack just before submission.

Keep the policy Markdown under `fixtures/knowledge/`: it is used by the application. Keep the bundled font licence with its font files. Never include private keys, working databases or unconsented personal information in the submitted repository.
