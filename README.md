# OnboardIQ

An evidence-first employee onboarding platform, built on the DayOne Proof foundation. **A task marked complete is a claim; a separate check establishes what actually happened.** It coordinates documents, equipment, IT access, payroll, benefits, training and manager work from approved rules based on each person's profile and location.

AI reads permitted records and approved policies, then explains, cites and proposes. Trusted code validates and executes. People approve anything important.

**What works now:** sign-in and role permissions, rule-based plans, human document review, equipment approval with read-back, a cited knowledge assistant, a bounded investigation agent, notifications and escalation, dashboards, and audit records. All of it is covered by automated tests.

**Known limits:**
- **Tested on one real model:** `openai/gpt-oss-20b` on Groq's free plan, whose rate limit can interrupt AI features under heavy use. Automated tests use scripted replies, or a labelled offline-rules mode (`LLM_PROVIDER=stub`) that is not AI. See [evaluation results](docs/EVALUATION.md).
- **The assistant misses many reworded questions.** It offers HR instead of guessing.
- All data is synthetic, and IT, payroll and equipment systems are simulated.
- No OCR, encryption at rest, single sign-on or production hardening. SQLite on one machine, for a local demo.

## Demo in one go

After the install steps below, set a private `DEMO_PASSWORD` of at least 12 characters in `.env`. To use offline rules, also set `LLM_PROVIDER=stub`. Then seed once and start:

```sh
node scripts/python.mjs fixtures/seed.py
npm run dev
```

Open http://127.0.0.1:5173 and sign in with `hema@northstar.example` (HR), or open **Demo accounts** on the sign-in page for the other roles. All accounts use your `DEMO_PASSWORD`. The story is in [the demo plan](docs/DEMO_PLAN.md).

Google and Microsoft sign-in, password reset and self sign-up are not connected. Those buttons say so when clicked.

## Deploying

This has been run locally, not on a server. For a hosted demo:

1. Use one instance with persistent disk, because SQLite and uploaded files live in `.runtime/`. Back up both together.
2. Put HTTPS in front of it. The app binds to `127.0.0.1` by default, so a reverse proxy must run on the same machine. The optional `docker-compose.yml` publishes on loopback too.
3. Set a strong private `DEMO_PASSWORD` before seeding, and set `LLM_API_KEY` only on the server.
4. Use synthetic data only. There is no encryption at rest, single sign-on, malware scanning or backup in this build.

## First things to read

1. [AGENTS.md](AGENTS.md): rules for every teammate/AI tool.
2. [PHASES.md](PHASES.md): 28 scoped phases, eight tracks, dependencies, copy-paste prompts and completion checklists.
3. [CHANGES.md](CHANGES.md): latest handoffs.
4. [API contracts](docs/API_SPEC.md) and [data model](docs/DATA_MODEL.md): build these exact shapes.
5. [Agreed final guide](Topic_3_Final_Guide.md) and [official problem statement](AI_Innovation_Challenge_University_Brief%201.pdf).

New teammate? Start with the install commands below, then [the eight-person setup and SQLite guide](docs/TEAM_WORKFLOW.md). For planned automatic model discovery and free-tier limits, read [providers](docs/PROVIDERS.md).

## Architecture

```text
Browser (React/TypeScript)
  → same-origin /api (Vite proxy in dev, FastAPI static frontend in built demo)
  → FastAPI/Pydantic → SQLite application data on local disk

Approved rules -> tasks and independent checks
Question or case -> permission-filtered context -> registered AI operation
  -> schema and citation validation -> advisory answer or typed proposal
  -> the correct person approves -> version-checked action -> read-back
```

One backend, one local worker and one company; not microservices or a replacement HR/payroll suite. SQLite simplifies a small local recorded demo; it is not a multi-company hosting recommendation. The model cannot approve/execute its own proposal. [Assumptions and scope](docs/ASSUMPTIONS.md) explain the thirty-hour cuts.

## Database choice — simplest setup for this deadline

**Decision confirmed with the user: keep SQLite for the local demo.** Each teammate follows the same install/run commands; the backend creates their own database automatically. No database server, cloud account or shared password is needed. P03/P14 will supply the same reviewed synthetic fixture baseline; they are not implemented yet.

SQLite is fastest **for this existing code and local-demo requirement**, not universally best. Neon and Supabase both offer managed PostgreSQL and are better candidates if we later need shared online state. Neon is a focused database option; Supabase is useful when its extra auth/storage services are actually needed. MongoDB would require more relational-workflow redesign here. **All choices still need schema/version migrations**; cloud hosting does not remove them. See [database comparison and future migration checklist](docs/DATABASE_DECISION.md).

Pitch accurately: “The local prototype uses SQLite for reproducible setup. A shared hosted deployment would be evaluated on managed PostgreSQL with reviewed migrations and concurrency/security tests.” Do not claim cloud support, a completed migration or production readiness.

## Prerequisites

- Git; access to the team GitHub repository once the integration lead creates it.
- Node.js **22.14+ (22.x) or 24.x**, including npm. Node 24 was tested locally.
- Python **3.12 or 3.13**, including pip/venv. Use the matching interpreter below; Windows `py -3.13` can replace `python` if needed.
- Internet for initial dependency install. **No Docker, database service, model/API key or paid account is required to run/test this foundation.**
- Local persistent disk. Do not run the database on a network/OneDrive-synced folder; if your Desktop syncs to OneDrive, clone elsewhere.

## Clone and install — Windows PowerShell

The repository URL is a manual input because no GitHub remote exists in this folder yet. Ask Track 1 for its real clone URL; no invented URL is supplied.

**If you already have this prepared folder, skip the clone/cd lines and start at the version/install commands in place.** The local Git repository is on `feature/p01-foundation`, with uncommitted source for review. Track 1 must review/stage the safe files, make the initial foundation commit, publish the initial main branch to the real team remote and then enable PR checks. This one-time initial publication is the integrator's responsibility; feature work must use small PRs afterward. No account/remote/push was created automatically.

```powershell
$RepoUrl = Read-Host "Paste the team's real Git clone URL"
git clone $RepoUrl dayone-proof
cd dayone-proof
python --version
node --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm ci
Copy-Item .env.example .env
npm run check
npm run dev
```

If `npm.ps1` is blocked by a restrictive PowerShell policy, use `npm.cmd` for the same commands rather than weakening machine-wide execution policy. Do not overwrite an existing `.env`; copying is a first-clone step. No shell activation is necessary: npm scripts find the root `.venv` themselves.

## Clone and install — macOS/Linux (Bash)

```bash
read -r -p "Paste the team's real Git clone URL: " REPO_URL
git clone "$REPO_URL" dayone-proof
cd dayone-proof
python3 --version
node --version
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
npm ci
cp .env.example .env
npm run check
npm run dev
```

Use Python 3.12/3.13 rather than a system Python older than 3.12. CI is configured for Ubuntu/Python 3.12/Node 22; actual remote CI results require a push. See [verification record](docs/VERIFICATION.md) for platforms actually exercised here.

## Open and verify

- Website: **http://127.0.0.1:5173**. It should say the frontend/backend/SQLite are connected, with an explicit foundation-only notice.
- API docs: **http://127.0.0.1:8000/docs**; runtime OpenAPI: `/openapi.json`.
- Health: **http://127.0.0.1:8000/api/health** returns `{"status":"ok","database":"ok","schema_version":1}`.
- SQLite is initialized at `.runtime/dayone.db`, with one stored project-name row. No destructive reset/seed runs on startup.
- **Ctrl+C** stops the frontend and backend together. Ports 5173/8000 must be free; the runner refuses occupied ports rather than testing an unrelated app.

In a second terminal at the repository root:

```sh
npm run smoke
npm test
npm run lint
npm run build
npm run contracts:check
# All reproducible checks together:
npm run check
```

`smoke` tests HTTP through the frontend origin, database health and served HTML; it is **not** a browser interaction/E2E workflow test. Unit tests use temporary isolated databases. No API calls to a model occur in CI/foundation tests. `npm run check` includes formatting, strict TypeScript build and generated-contract drift checks.

Dependency audit caveat: the current full npm audit reports **10 moderate development-tool advisories, no high/critical**; `npm audit --omit=dev` reports zero. See [verification and advisory record](docs/VERIFICATION.md). Do not run force-upgrades or expose dev servers publicly. Python dependencies passed compatibility checks, not a comprehensive security audit.

## One-command development and built local demo

After install, **`npm run dev`** starts everything needed for foundation development. Ollama remains a separately installed prerequisite only when P17 implements the local adapter and P04 connects the investigation; the launcher does not download models or start paid services.

For the same-origin built demo, stop `dev` first:

```sh
npm run build
npm start
```

Open **http://127.0.0.1:8000**. In PowerShell use:

```powershell
$env:SMOKE_BASE_URL = "http://127.0.0.1:8000"
npm run smoke
Remove-Item Env:SMOKE_BASE_URL
```

In Bash: `SMOKE_BASE_URL=http://127.0.0.1:8000 npm run smoke`. No Vite preview/public server needed. Built mode serves only the frontend assets/index and API, never repository files/.env. Local deployment only; no production identity/HTTPS/tenant isolation is claimed.

## Environment and optional model setup

All settings are explained in [.env.example](.env.example). With the defaults, AI is off and every manual workflow still works. Set `LLM_PROVIDER` to turn it on. Seeding needs a private `DEMO_PASSWORD`, and no empty-password login exists.

After P02/P03, privately set a demo password of at least 12 characters before the safe seed command is implemented/used. `fixtures/README.md` specifies the planned `node scripts/python.mjs fixtures/seed.py`; **that command does not exist yet**. Do not destroy or reseed someone else's working database.

The current `.env.example` describes the original single-provider stub. **Automatic provider discovery, model dropdowns and switching do not work yet.** P15–P25 add them through reviewed contracts, backend adapters and a selector. Do not put proposed new variable names in `.env` and assume they are supported.

After the relevant provider phase, choose **one** model path and run a real smoke set:

- Local: install Ollama separately; `ollama list` shows downloaded models. If you choose a Llama model, download a suitable size yourself, for example `ollama pull llama3.2:3b`, after checking its current licence and your RAM/disk. The guide's alternative is `qwen3:8b`. P17 must list installed **local** models, not silently use Ollama cloud models or download anything. Model presence does not prove acceptable speed/quality.
- Hosted: planned providers are **Groq**, Cerebras, Mistral, Gemini and OpenRouter. Groq provides free-plan model access with account/model limits; use its current discovered catalog rather than a fixed list of three models. Each provider needs its own key/access; an OpenAI-compatible API does not require an OpenAI account. Free-tier eligibility, trials, quotas and billing differ; not every provider/model is permanently free. See [official sources and discovery design](docs/PROVIDERS.md).

Both paths are currently stubs. The planned screen will show configured providers, discovered text models, pricing/access confidence, refresh status and a synthetic test button; select a validated model before running an investigation. Keys stay on the backend; no silent provider/model fallback or paid activation. Only local inference with no cloud tools keeps inference data on the machine; it is not a claim that the whole computer is automatically private. No real model compatibility, quota or task quality has been tested. Use synthetic data only.

## Team workflow — eight people, one main branch

1. Assign **Track 1 as integrator** (real name claimed in PHASES.md). Only integrator owns shared contracts/schema, root wiring, dependencies/locks and CI. Other tracks own named folders.
2. Once the team remote/main exists: `git switch main`, `git pull --ff-only origin main`, read AGENTS/PHASES/CHANGES and claim your phase. Create a branch with **any valid name you choose**: `git switch -c my-branch` is only an example, not a naming rule.
3. Copy your phase's complete prompt into Codex/Claude/Gemini/Antigravity; explicitly tell it to read AGENTS.md. No optional plugin is required. Do not ask it to implement the whole project.
4. Change only allowed files; add small focused tests. Submit contract change requests to Track 1 before changing JSON fields or function seams.
5. Run phase checks and `npm run check`. Format only owned paths, not the whole repository. Append CHANGES and update only your PHASES block. Commit small, e.g. `feat(p03): generate approved onboarding tasks`.
6. Push the current branch with `git push -u origin HEAD`; open a small PR. One owner/reviewer per interface; merge often, integrate a thin journey early. Merge current main into long-lived branches rather than rewriting shared history.
7. Integrator reviews checks/contracts and merges. Preserve both append-only log entries and independent phase statuses on conflicts; never take a whole PHASES/CHANGES file from one branch.
8. Stop feature work three hours before the actual submission deadline (hour 27 in the original 30-hour schedule). Re-estimate the expanded plan with the team; final hours are verified fixes/recording/submission, not new architecture or paid tools just to increase stack size.

Never share `.venv`, `node_modules`, database/checkpoint files, tokens or `.env` in Git. **Resumes, videos, PPTX and presentation PDFs are not ignored** and may be committed after consent, secret and size review. Do not automatically commit all files with a broad `git add .` without reviewing staged content. Videos beyond GitHub's ordinary Git size limit need LFS or an accessible hosted/Release link, not an attempted oversized commit.

**SQLite for eight teammates:** each clone starts its own `.runtime/dayone.db` when the backend starts. You do not install a database server or connect to another person's laptop. Git shares the schema and, once P03 exists, reviewed synthetic fixtures; it does not sync database contents. Different progress on different laptops is expected. Tests use separate temporary databases. Pulling a schema change does not migrate an existing database: wait for the P26 reviewed migration, back up first, and never delete a teammate's data. Full commands, safe backups and troubleshooting are in [TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md).

**Architecture is adjustable:** propose an improvement with evidence, affected-owner review, regression tests and a rollback plan (P27). Different coding agents are welcome; none may lower safety gates or merge solely because it claims a stronger model. “Tests passed on this commit” is useful; “100% guaranteed” is not.

## Folder map

```text
AGENTS.md / CLAUDE.md / PHASES.md / CHANGES.md
Topic_3_Final_Guide.md                 agreed rationale (preserved)
AI_Innovation_Challenge_University_Brief 1.pdf
backend/app/shared/                   contracts, schema, DB, errors (Track 1)
backend/app/auth/                     identity (Track 1)
backend/app/planning/ + evidence/      plans and checks (Track 4)
backend/app/cases/ + agent/            investigation/worker/providers (Track 6)
backend/app/actions/                  approvals/execution (Track 5)
backend/tests/                        isolated module and integration tests
frontend/src/features/overview/ + workspace/  Track 2
frontend/src/features/my-work/ + review/      Track 3
frontend/src/features/model-settings/        planned P24, Track 2
frontend/src/shared/                  shared client/generated types (Track 1)
fixtures/                            synthetic runtime inputs (Track 4/8)
evals/                               independent scenarios/answers (Track 7)
scripts/                             portable launch, smoke, contract export
docs/                                specs, assumptions, verification, demo
resume/                              eight consented PDFs; naming in README
video/                               final recording or VIDEO_LINK.md
ppt/                                 five slides, PPTX and PDF
.github/workflows/                    CI checks
```

## Submission status

- [Demo video status/link](video/VIDEO_LINK.md): not recorded yet.
- [Presentation instructions](ppt/README.md): final five slides not created yet.
- [Resume instructions and privacy](resume/README.md): eight real consented PDFs still needed.
- [Demo/rubric checklist](docs/DEMO_PLAN.md) and [verified setup evidence](docs/VERIFICATION.md).

Official weighting: product value 25%, harness 25%, LLM implementation 20%, engineering quality 15%, demo 15%. Working controls and measured outcomes matter more than a plan, model size or framework count.

## Manual steps still needed

Create/push the team GitHub remote and enable PR reviews/CI; assign eight real names; implement P02–P28 as applicable (P27 only for proposed improvements), including the provider selector; supply consented resumes, final recording and presentation; measure recording-machine model feasibility; optionally obtain a hosted key without committing it. No external account/key is needed to run this foundation. Original source-document distribution rights, competition eligibility and personal-data publication consent remain the team's responsibility.
