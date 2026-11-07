# Understand OnboardIQ: problem, people, workflow and what is left

**Updated: 7 November 2026.** This is a beginner's guide to the application we actually have, not a promise that every planned feature is finished.

> **The short answer:** we built a website that coordinates a new employee's joining work. Most of the dependable work uses ordinary rules. Four parts can ask an AI model for help. Without a working model connection, those parts are disabled or use clearly labelled practice rules. We have not built a production HR/payroll system.

Read sections 1–10 in order. The detailed file list is folded away at the bottom; you do not need it to understand the product.

## 1. What problem are we solving?

Imagine Priya is joining a company next Monday.

- HR needs her documents.
- IT needs to prepare a laptop and accounts.
- Payroll needs to prepare her payroll profile.
- The benefits team needs to record her benefits choice.
- Training needs to record required courses.
- Her manager needs a buddy and a first-week plan.

These teams may use separate messages and spreadsheets. Priya has to keep asking: **“Who is doing what? What is still missing? Am I ready to join?”**

There is a second problem: someone can tick a task as complete even though the real outcome is not established. “Laptop reserved” does not mean “Priya received the laptop.”

**Our problem is coordination plus trustworthy progress—not replacing the people who do the work.**

## 2. What solution did we build?

One website brings the joining work together:

1. HR adds the employee's details.
2. Approved company rules create the relevant checklist.
3. Every task gets an owner and due date. Some tasks must wait for earlier tasks.
4. Each team records its work.
5. The website separately checks the supporting records.
6. If something is confusing, an AI-assisted investigation can help explain it and suggest a fix.
7. The right person approves an important correction. Backend code performs the allowed change.

Two labels must stay separate:

| Label | Plain meaning | Laptop example |
|---|---|---|
| Task complete / claimed | Someone said they finished that task | IT clicked Complete |
| Evidence / proof | A separate recorded fact supports a specific outcome | The equipment record shows handover with a date |

A check can say **Verified**, **Blocked** (records disagree) or **Unknown** (not enough evidence). The result proves only the recorded check, not everything about the employee.

“Orchestrator” simply means **coordinator**. That is the main product we built.

## 3. Exactly how many roles are there?

There are **7 roles: HR, IT, Payroll, Benefits, Training, Manager and Employee.** A new employee uses the Employee role. These are user permissions, not seven AI agents. There is no separate super-admin or recruiter role in this application.

### 3.1 HR — manages the joining process

**Features built:**
- Create a new hire and link their employee login; edit permitted employee details.
- See the employee directory, onboarding plans, deadlines and progress dashboard.
- Review documents: verify, reject with a reason, or request another upload.
- Request optional AI document extraction; the final verification stays with HR.
- Open an investigation and answer clarification questions addressed to HR.
- Review and approve/reject a proposed work-location change.
- Manage approved policy/knowledge documents and reply to questions sent to HR.
- See insights, activity history, AI run records and reliability information.
- Run an overdue reminder check and issue requested temporary passwords from Settings.

**Why useful:** HR can see which team needs to act instead of chasing everyone separately.

**Limit:** HR can view several team screens, but Payroll, Benefits, Training and IT still control their own source updates. HR is not a universal bypass. Settings shows model status; it is not a model-selection dropdown.

### 3.2 IT — prepares equipment and access

**Features built:** see inventory and relevant hires/tasks; request a specific device; approve/reject equipment reservations; record device handover; record access requests and mark them provisioned in the simulated system.

**Why useful:** distinguishes “a laptop is set aside” from “the employee collected it.”

**Limit:** this does not really create Microsoft, VPN or email accounts, ship a laptop, or contact an enterprise IT system. These are demo records. A task completion is not an automatic reservation or handover.

### 3.3 Payroll — records payroll readiness

**Features built:** see relevant employees and tasks; record bank-form submission, tax-form submission, payroll-profile creation and setup confirmation.

**Why useful:** shows whether preparation is complete without making the employee ask repeatedly.

**Limit:** these are status flags. The app does not calculate salaries, send money or connect to a real payroll provider. The payroll status record does not contain account numbers; document uploads are a separate private-storage feature.

### 3.4 Benefits — records the benefits response

**Features built:** see relevant records/tasks and update benefits states: Not invited, Invited, Enrolled or Declined.

**Why useful:** makes “we invited the employee” different from “the employee's choice is recorded.”

**Limit:** no insurance-company connection or real benefits purchase. Applicability follows the approved fictional rules; AI does not decide eligibility.

### 3.5 Training — records course completion

**Features built:** see assigned course records and tasks; mark a course recorded complete.

**Why useful:** gives the coordinator a clear view of outstanding training.

**Limit:** the app does not teach the course, assess competence or connect to an external learning platform. Recorded completion is not proof of someone’s skill.

### 3.6 Manager — prepares the person's team

**Features built:** see assigned hires and their progress; select a buddy; record the first-week plan; work through manager-owned tasks; open an investigation from a hire workspace.

**Why useful:** makes the manager's joining responsibilities visible, not just HR's paperwork.

**Limit:** the dedicated IT request screen is currently in IT/HR navigation, not Manager navigation. Backend permissions also allow managers to request equipment/access, but do not mistake an allowed API operation for a fully exposed manager-screen feature. Managers do not approve IT reservations or HR location corrections.

### 3.7 Employee / new employee — follows their joining plan

**Features built:** see “My onboarding,” joining details, next action and checklist; upload documents; see review/resubmission outcomes; complete their assigned tasks; ask policy questions; read notifications; decline benefits through their own portal.

**Why useful:** one place to see what they owe the company and what they are waiting for.

**Limit:** the benefits team records enrolment; the employee portal currently offers decline, not a complete self-service enrolment form. A newly self-registered account sees no hire plan until HR links it. An employee cannot approve their own documents or equipment.

### Features shared across roles

All seven roles have their own Tasks, Knowledge assistant and Notifications pages. The allowed employees, records and policy passages differ by role and assigned access. Staff have a directory; the employee primarily uses their personal portal. The backend enforces access even if somebody manually changes a page URL.

Source checks: [navigation](../frontend/src/shared/routes.ts), [backend permissions](../backend/app/auth/permissions.py), and the corresponding screens in the optional file map.

## 4. Follow one complete example: Priya joins

| Step | What happens | Who/what does it? |
|---|---|---|
| 1 | HR creates Priya as an engineer joining in Hyderabad | HR enters details |
| 2 | Tasks, owners, dates and dependencies are created | Ordinary approved rules, not AI |
| 3 | Priya uploads her fictional offer letter, which says Bengaluru | Employee upload |
| 4 | The document/profile location disagreement becomes visible | Python text recognition/comparison can detect it without AI |
| 5 | HR can ask for suggested document fields and supporting quotes | Optional model call; HR still reviews the document |
| 6 | HR/Manager opens an investigation: “Which location is correct?” | Human starts it; configured model or labelled practice rules choose next steps |
| 7 | The investigation asks HR and waits; HR answers | Saved case/question records; the answer itself is not approval |
| 8 | A specific location change and its task changes are proposed | Suggested correction; backend prepares the review |
| 9 | HR reviews and approves/rejects it | Human decision; backend applies an approved change |
| 10 | A compatible Bengaluru laptop reservation is proposed for IT review | Investigation suggestion or a separate permitted manual request |
| 11 | IT approves; backend reserves that device | Human approval plus backend write/read-back |
| 12 | The outcome says “reserved; collection pending” until handover is recorded | Independent recorded equipment outcome |

Payroll, Benefits, Training and Manager work continue alongside this story. A resolved location/equipment investigation does **not** mean all onboarding is complete.

The investigation is narrow and its prompt guides this sequence. A real model is not guaranteed to choose the same successful path every time. In practice mode the steps are scripted. There is also a known approval-execution safety gap described in section 11; it is not fixed by this document.

## 5. Where, exactly, is AI used?

There are **four implemented places that can call a model**:

| Website feature | What we ask the model to do | What remains ordinary code / human work |
|---|---|---|
| HR: document extraction | Suggest fields such as name/location and quote the document | File checks, location matching, comparisons and the human verification decision |
| All roles: Knowledge assistant | Draft an answer using permitted approved passages and cite them | Search, access filtering, quote checks and escalation handling |
| HR/Manager: investigation | Choose a permitted read, phrase a question, suggest one supported correction, or stop/escalate | Permissions, saved progress, limits, reviewer assignment and action execution |
| HR: AI insights | Phrase a summary and suggestions from supplied metrics | SQL/Python calculates the numbers; no model-owned scoring of employees |

**AI does not create the joining rules, decide permissions, verify identity, confirm payroll, approve its own proposal or establish that a laptop was delivered.** Those should not depend on a model guessing correctly.

### “We have not configured keys. Is AI running?”

Taking your statement that no hosted key is configured: **the real hosted AI features will not work yet.** The code connection can exist without being configured to run.

| Setting | Actual behavior |
|---|---|
| LLM_PROVIDER=none | No model. Manual onboarding continues; AI features are unavailable or decline/escalate |
| LLM_PROVIDER=stub | Scripted offline rules imitate model replies so you can practice; **not real AI** |
| LLM_PROVIDER=hosted | Needs a valid backend endpoint, supported model and authorized provider key to make real calls |
| LLM_PROVIDER=ollama | Needs a separately running local Ollama installation and suitable installed model; no hosted API key needed |

No key by itself does not mean a secret AI runs in the background. Missing context can also make the assistant decline without calling a model at all. We have not opened your private .env or Render settings to certify their current contents.

### Groq, OpenAI and free models: three different ideas

- **Model:** the trained system that generates an answer.
- **Provider:** the service running that model, for example Groq.
- **API:** the way our backend asks that service a question.

The saved evaluation used the model **openai/gpt-oss-20b on Groq**. “openai/” here is part of the model identifier. **It does not require buying OpenAI's hosted API or supplying an OpenAI key.** “OpenAI-compatible” describes a request format used by several services; it is not a billing requirement.

**What already exists:** a configurable common hosted connection; Groq is the default example and has a saved historical live run. This does not mean your current local/Render installation has a working key.

**What is not built/verified:** an automatic free-model catalog, provider dropdown or account-entitlement gate; separately validated Cerebras/Mistral/OpenRouter integrations; a native Gemini adapter. A compatible endpoint might reuse the transport, but that is not proof it works correctly with every provider.

**Our budget position:** no paid OpenAI setup or other paid service is required or enabled by this review. A provider's free access depends on its account rules, quotas and current terms; the code cannot promise unlimited free use. Local Ollama avoids a hosted inference bill but still requires suitable hardware and a live test. Pick one genuinely available path later; do not attempt every provider now.

[AI connection code](../backend/app/ai/providers.py) · [clearly labelled practice implementation](../backend/app/ai/stub.py) · [saved evaluation and limitations](EVALUATION.md)

## 6. What is the harness we built?

Think of the AI as a helpful junior assistant. **The harness is the supervisor, checklist and locked doors around it.** It is application code—not another model, and not just a prompt saying “be safe.”

| Protection built | Simple example |
|---|---|
| Read only what the person may access | An employee's policy answer must not retrieve an HR-only passage |
| Allow only specific tasks/tools | The investigation cannot ask to run arbitrary SQL or visit a random URL |
| Require a fixed response shape | Reject an answer/proposal with unexpected fields |
| Check quoted sources | Reject a quotation that is not in the supplied passage |
| Bound work and save progress | Count model/read attempts and save a waiting human question |
| Require the right human approval | HR reviews location changes; IT reviews reservations |
| Check records before changing them | Reject certain stale profile/plan/device versions instead of overwriting blindly |
| Avoid repeating an effect | Repeating a completed reservation action does not reserve again |
| Read the result and keep a history | Say exactly what is stored, and record decisions/model-run metadata |
| Fail without blocking all onboarding | If a model is unavailable, keep manual tasks and review usable |

The model-call wrapper is [ai/harness.py](../backend/app/ai/harness.py). Permissions, evidence, approvals and the worker add the rest of the harness. It can be tested using practice replies without a real key—but **that tests controls, not model intelligence**.

**It is not perfect:** checking that a quote exists does not prove every sentence based on it is true. The current worker also misses some after-approval authority/expiry checks. Limits and saved state have additional qualifications in section 11. So say “we built harness controls,” not “AI output is guaranteed correct or safe.”

## 7. How are the pieces connected? Did the architecture change?

```text
Person uses the website (React)
             |
             v
One Python backend (FastAPI)
   |-- rules, permissions, documents and evidence checks
   |-- optional model calls through the AI harness
   |-- one background worker for investigations/approved actions
             |
             v
That backend's SQLite database and private uploaded files
```

The earlier guide proposed LangGraph to save the agent's progress. The implemented version uses ordinary Python and application database tables instead. The filename graph.py does not mean LangGraph runs it. LangGraph dependencies remain installed but are not used by this application path.

Other changes from the early plan include schema v2, richer document/knowledge screens, IT access, notifications/insights, employee self-sign-up, HR-mediated reset and sessionStorage so refresh stays signed in. Docker/Render delivery files now exist too.

**Recommendation: keep the current single-backend/single-worker architecture for the prototype.** We did not approve or perform a new architecture migration. Fix the demonstrated gaps before adding more frameworks/providers. A real shared production service needs a separate reviewed storage/security plan.

## 8. Would a real company find this useful? Does it meet the challenge?

**Potentially useful:** companies with several teams preparing each starter could benefit from clear ownership, fewer missing steps, earlier document/location conflicts and honest progress. The difference from a basic checklist is showing the claim and supporting record separately, with a controlled recovery path.

We have **not measured real customer time savings**, compared against existing HR products, or proven market novelty. This is a prototype of that workflow. The current “independent” evidence comes from separate controlled demo records/human review, not live enterprise systems.

The official Topic 3 asks for documents, equipment, payroll setup, benefits enrolment, training and manager tasks based on worker profile/location. All six areas exist; IT access is an extra category. The [official brief](../AI_Innovation_Challenge_University_Brief%201.pdf) permits this kind of mixed rules/AI design. LangGraph and a vector database are not mandatory. AI should help with interpretation—not replace trustworthy controls.

**Before real-company use:** fix the safety gap; confirm persistent storage/backups and safe upgrades; add reviewed production identity/privacy controls; connect real systems only with permission; test accessibility, concurrency and recovery; and independently assess model quality. Multi-company isolation, SSO, OCR, malware scanning and real payroll/insurance/account provisioning are not built.

**Better next experiment:** have someone unfamiliar with the code try several different joining scenarios and policy questions. Measure missing steps, correct answers and human review effort. That is more useful now than adding five more providers or claiming AI saves an invented number of hours.

## 9. How do databases work locally, in GitHub and on Render?

### GitHub stores the recipe—not your working notebook

| File / location | Meaning | Shared through Git? |
|---|---|---|
| backend/app/shared/schema.sql | Instructions for the database tables | Yes |
| fixtures/seed.py and fixture inputs | Instructions/sample data for initial demo accounts and records | Yes |
| .env.example | Blank public settings template | Yes |
| .env | Your private settings and keys | No |
| .runtime/dayone.db | Your installation's actual users, tasks and decisions | No |
| .runtime/documents/ | That installation's private uploaded files | No |

The dot matters: the default folder is **.runtime**, not /runtime. A matching filename on two machines still means two different files. [The ignore rules](../.gitignore) deliberately keep local data out of Git.

### What Render does with the checked-in deployment files

If your teammate deployed the current Docker/Render setup:

1. Render obtains the committed source from GitHub.
2. Docker builds the website and installs the backend dependencies. It does **not** copy your local .runtime database; the build ignores it.
3. The server starts scripts/serve.py, which looks for users in the configured database file.
4. If there are no users, it runs the safe seed script. That initializes tables and inserts synthetic users/records using Render's own DEMO_PASSWORD setting.
5. If users already exist, it skips seeding and keeps those accounts/passwords.
6. The backend serves the built website and API on Render's supplied port.

**So Render creates/uses its own database. It does not download your local database from GitHub.** The real dashboard configuration still needs confirmation by the teammate who deployed it.

For a no-hosted-AI demo, the operator can choose LLM_PROVIDER=none or stub; no hosted key is needed for those modes. DEMO_PASSWORD still needs a private 12+-character value for a fresh seed. A Groq key is only for explicitly enabling actual hosted inference. Do not paste either secret into Git or chat. We have not changed these settings.

### Why Render login may differ

Your local password was used when you created your local demo accounts. Render's accounts were created separately. An account may be missing/inactive, have an old missing email, or have a different stored password.

**Changing DEMO_PASSWORD after seeding does not reset existing passwords.** Two failure modes were reproduced in earlier isolated tests: changed setting versus old stored password; and an old account without an email. Neither has been confirmed as Render's actual cause. Ask the deployment owner for sanitized existence/activity/email/password-match results, not the secret values. Do not delete/reseed the database as a guess.

### Will Render keep the data?

The checked-in render.yaml uses a free instance with no persistent disk. Its local files can be lost on instance replacement/redeploy, so do not promise that accounts/progress/uploads survive. Actual dashboard settings may differ.

Reliable retention needs an explicitly approved persistent-storage/backup arrangement, or a reviewed move to a shared database service. We have not configured either and will not purchase one automatically. Changing to PostgreSQL is not just changing the filename. For now, keep local development data separate from any hosted demo data.

## 10. How do I run and test it?

### Local: you have already seeded and logged in

From the project root in PowerShell:

```powershell
npm.cmd run dev
```

Open http://127.0.0.1:5173 yourself. Leave the terminal running. Do not seed on every launch; existing accounts keep their stored passwords. Ctrl+C stops the launcher.

In a second terminal:

```powershell
npm.cmd run smoke
npm.cmd run check
```

Smoke checks basic HTTP/database connectivity. Check runs automated code/contract tests and a build. Neither means a browser tested every button or that a real model answered correctly.

To run the built local website, stop dev first:

```powershell
npm.cmd run build
npm.cmd start
```

Open http://127.0.0.1:8000. These local start commands do not automatically seed users. The separate container startup has the empty-installation seed behavior explained above.

### Render: there is no npm render command

Our package.json has **no npm render or npm run render script**. Your deployment owner uses Render's dashboard/GitHub deployment process with the checked-in deployment files. Running the local commands does not publish changes or copy accounts to Render.

To test the existing hosted app, open its URL yourself and use its separately seeded credentials. Confirm login and storage first; test real AI only after an authorized free/local provider is explicitly configured. No key, account, deployment or purchase was configured by this documentation edit.

## 11. What works, what is missing, and what needs verification?

### Implemented in code

- Seven-role login/access checks and employee-only self-sign-up.
- Profile/location-based plans, task owners, dates and dependencies.
- Documents with human review; separate evidence checks.
- Equipment requests/approvals/reservation and handover records.
- Payroll/benefits/training/manager demo records.
- Notifications, dashboards, audit history and metrics.
- Four optional AI operation paths and a labelled rules-only practice mode.
- Saved investigation questions/progress and background work.

**“Implemented” means code exists and has test coverage—not that every production guarantee holds.**

### Fix before claiming the safety path is complete

| Issue found | Simple meaning | Status |
|---|---|---|
| Worker misses current approver/expiry rechecks | Approval can still execute after the approver loses access/is deactivated, or the proposal expires | Reproduced earlier in temporary databases; backend not fixed, as requested |
| Hosted files may disappear | A restart with preserved disk is not recovery after the disk's contents are lost | Check Render storage before promising durable progress |
| Older account/database upgrades are limited | Missing emails are not filled automatically; populated schema-v1 databases are not generally migrated | Needs owner-reviewed upgrade/repair, not deleting data |

### Built, but not fully verified or reliable yet

- **Hosted login:** exact cause still needs private deployment evidence.
- **Real model on your installation:** no working hosted inference if no valid key/configuration; we have not inspected your private configuration.
- **Model quality:** saved Groq tests exist, but a small untuned question set found the expected source for only 5 of 11 questions. Free-plan limits interrupted some calls. The questions had one author; they are not independent validation.
- **Answer correctness:** quote membership/response shape are checked, not the meaning of every answer. Human document review remains necessary.
- **Investigation lifecycle:** call/read counters persist, but there is no fixed case-level model snapshot and no fully persisted cumulative active-time budget across resumes. Transport retries can add time too.
- **UI/release:** full role-by-role browser/accessibility acceptance, container build, hosted authenticated journey, current CI/clean-clone evidence and eight-machine setup replay still need confirmation. Earlier dated checks do not prove these all happened now.

### Not built / deferred

Automatic provider discovery/model picker, tested native Gemini support and independently validated additional hosted providers; a free-tier entitlement/billing gate; embeddings/vector search; OCR; real external systems and external email/chat notifications; general safe migration tooling; production hardening/multi-company support.

A model picker or another framework is not needed just to explain or demonstrate the existing prototype. Agree deferrals with the team rather than secretly treating the whole roadmap as done.

### Submission still needs real assets

The indexed submission folders contain instructions, not the final accessible ten-minute video and five-slide PPTX/PDF. The final README/CI/evaluation evidence must match the demonstrated build. Resumes require consent if the team collects them; they are not a deliverable listed in the official PDF. Model licence/terms and organizer eligibility still need team sign-off.

### What has actually been checked?

The earlier full check passed **136 backend tests + 37 frontend tests**, lint, formatting, build and generated-contract drift. Local login was confirmed by you. Earlier read-only hosted health/OpenAPI checks passed; that was not hosted login acceptance. Saved Groq results are dated 6 November, not a newly configured key or new live-model run.

A fresh npm.cmd run check also passed for this revision: 136 backend tests, 37 frontend tests, lint, formatting, build and contract drift. Tests use isolated data and scripted/offline replies. No browser, private database/settings inspection or live inference was performed for this rewrite.

## 12. Are all the other documents and code up to date?

**No—not all Markdown files describe the latest application consistently.** You correctly noticed a mixture of the first foundation version and the later R06 build.

| Document | What is confusing/outdated |
|---|---|
| README.md | Good new overview, but later text still says the seed does not exist, schema v1/foundation-only UI and unfinished fixture work |
| backend/README.md | Still calls business services stubs and describes implemented settings/seed/model behavior as future work |
| fixtures/README.md | Old no-seed/six-hire plan conflicts with the implemented seed; actual seed has 3 hires and 11 accounts |
| evals/README.md | Says the evaluation runner is not implemented even though runner/results exist |
| docs/PROVIDERS.md | Discovery/selector plan is still future work, but its “only health/bootstrap and stubs” description of the whole app is outdated |
| docs/TEAM_WORKFLOW.md, docs/DATABASE_DECISION.md, docs/README.md | Some setup and current-capability sentences still describe the foundation |
| AGENTS.md, docs/DATA_MODEL.md, docs/ASSUMPTIONS.md | Newer status/overrides sit beside obsolete stub/checkpointer/session assumptions |
| PHASES.md | Some done statuses sit beside unchecked tasks; some deferrals still require team agreement; the new safety gap needs follow-up |
| docs/VERIFICATION.md and CHANGES.md | Contain dated history. Old results/events must stay historical, not be rewritten as if they occurred today |

The generated API files and types passed the previous drift check. That is useful code/contract evidence, **not proof that every code file is bug-free or every instruction is current**.

**What this revision updates:** this explanation, its P12 coordination note, and an appended change-log entry. It does not claim to repair every other Markdown file. That needs a small agreed documentation cleanup with the relevant owners. Generated specs must be regenerated from code, never hand-edited. Keep the original guide/PDF and past log entries as history.

For the actual implementation, use current source plus canonical contracts and dated test evidence. For a beginner's explanation, start here rather than the older foundation paragraphs.

## 13. What were the changes made before this review? Were they needed?

There are two different groups; do not mix them up.

### A. The teammate's earlier R06 application build

CHANGES.md records the broad feature build, application-table agent state instead of LangGraph, schema v2, document/knowledge/insight screens, employee self-sign-up/reset and sessionStorage. These are earlier team changes—not features added by the recent explanatory review. They need integrator/affected-owner review because they changed shared contracts and earlier assumptions.

### B. The small changes made during our recent investigation

| Change | Why it was made | Was it needed? |
|---|---|---|
| frontend/vite.config.ts: removed demo-password injection | The development server previously embedded the configured demo password in browser JavaScript | Yes, a security fix. Production builds had used an empty value; we did not establish a production-password leak |
| Login.tsx: demo buttons fill email only, with a short instruction | Removing the password injection needs the login screen to stop relying on it | Yes, the matching behavior/clarity change; you enter your password yourself |
| frontend/vite.config.test.ts: two regression cases | Check both development/build configuration so password injection does not return | Yes, protects the security fix; no new dependency |
| Installed missing already-pinned pypdf and python-multipart in .venv | The local test/startup environment was missing packages the existing code requires | Needed for local verification; dependency manifests were not changed |
| docs/PROJECT_REVIEW.md | You requested an explanation/review | Documentation only; first version was too technical, so this version simplifies it |
| PHASES.md and appended CHANGES.md entries | Record scope, real verification and remaining limits for the team | Required coordination; not new product features |
| fix/demo-login-audit branch | Keeps the work separate for review | A Git working branch, not a deployment or architecture change |

Test/build commands also regenerate ignored build/cache files. Those are not new authored features. Your .env creation and demo seeding were setup steps **you performed** after the instructions; the reviewer did not reset your database.

**Not changed by those fixes:** backend behavior, canonical contracts, passwords, private keys, Render settings/deployment or database engine. They do not fix Render login. No commit/push/deployment or purchase was performed by this agent.

## 14. What should we do next, in a sensible order?

1. **Understand the existing manual product:** try each role using the same local demo installation and note who can do what. Do not assume every screen uses AI.
2. **Resolve hosted setup:** ask the deployment owner to check its accounts/settings privately and explain its storage. Do not copy a database into Git or wipe progress.
3. **Agree and repair the demonstrated safety gap:** small backend/test change after approval; no architecture rewrite required.
4. **Choose one genuine free/local inference route:** verify entitlement/hardware, configure privately, and test the four model features. Do not buy OpenAI or silently enable paid usage.
5. **Check real behavior:** independent wording/scenarios, failures, human review, restart and role access; record failures honestly.
6. **Reconcile the active instructions and finish delivery:** current setup docs, team-approved deferrals, reviewed build/CI, ten-minute demonstration and five slides.

**One sentence you can use:** “We built an onboarding coordinator where rules handle routine work, separate records establish progress, and an optional bounded AI assistant helps with questions and exceptions while people retain approval.”

---

<details>
<summary>Optional technical appendix — open only if you want the 182-file map</summary>

## Optional appendix: technical file map

This map inventories indexed first-party project files plus explicitly checked safe root configuration files. It separates file presence from feature completion. All listed code is application/demo/test infrastructure, not evidence that it ran live on every platform. Dependency installations, Git internals, caches, built assets, private configuration and runtime data are excluded; they are explained as categories below rather than read as project source. No personal asset content was opened.

### Excluded generated/private/local categories

| Location/category | What it is | Why it is not a source-review target |
|---|---|---|
| .env | Private settings and secrets | Never publish or copy into the report |
| .runtime/ and SQLite companion files | This installation's data and uploaded documents | Private/mutable; not shared source or fixtures |
| .venv/ | Installed Python packages | Third-party dependencies; requirements is reviewed instead |
| node_modules/ | Installed JavaScript packages | Third-party dependencies; manifests/lock guard/build are checked instead |
| frontend/dist/ | Compiled frontend | Regenerated by the checked build; do not edit by hand |
| .git/ | Repository history/index | Not application code; do not alter someone else's history |
| Python/test/lint/Vite caches and local tooling state | Regenerable local artifacts | Not product features; no private plugin/IDE state inspection |
| Personal PDFs, recordings and presentation binaries | Submission material | Require consent and separate size/secret/playback review |

### Root and CI

| File | Purpose / review note |
|---|---|
| [.dockerignore](../.dockerignore) | Keeps secrets, local data, dependencies and submission assets out of the container build context. |
| [.env.example](../.env.example) | Public settings template; provider, database and budget settings. It is not a populated private configuration. |
| [.gitattributes](../.gitattributes) | Line-ending rules and binary-file handling. |
| [.github/workflows/ci.yml](../.github/workflows/ci.yml) | GitHub Actions Ubuntu/Python 3.12/Node 22 check workflow; file presence is not a verified hosted run. |
| [.gitignore](../.gitignore) | Excludes secrets, local data, dependencies, builds and caches; submission assets need explicit privacy review. |
| [.prettierignore](../.prettierignore) | Formatting exclusions for generated/dependency/runtime files. |
| [AGENTS.md](../AGENTS.md) | Shared ownership/safety instructions; contains some obsolete foundation-only wording. |
| [AI_Innovation_Challenge_University_Brief 1.pdf](../AI_Innovation_Challenge_University_Brief%201.pdf) | Official three-page requirements and judging rubric, read for this review. |
| [CHANGES.md](../CHANGES.md) | Append-only history; earlier entries are historical, not current implementation truth. |
| [CLAUDE.md](../CLAUDE.md) | Points that coding assistant to AGENTS.md. |
| [Dockerfile](../Dockerfile) | Builds the frontend, installs Python dependencies and runs the container entrypoint. |
| [GEMINI.md](../GEMINI.md) | Points that coding assistant to AGENTS.md. |
| [PHASES.md](decisions/2026-11-07-improvement-plan.md) | 28-phase ownership/status board; mixed completed/pending/deferred work. |
| [README.md](../README.md) | Main setup/product overview; currently contains contradictory old foundation instructions. |
| [Topic_3_Final_Guide.md](../Topic_3_Final_Guide.md) | Preserved original researched design recommendation, not proof of the current implementation. |
| [package-lock.json](../package-lock.json) | Generated pinned JavaScript dependency resolution; checked by lockfile guard/install/build, not manually rewritten. |
| [package.json](../package.json) | Root workspaces and dev/test/lint/build/contracts verification commands. |
| [pyproject.toml](../pyproject.toml) | Pytest paths and Ruff lint/style settings. |
| [render.yaml](../render.yaml) | Render deployment blueprint; free ephemeral-storage configuration, with private secret inputs. |

### Backend application

| File | Purpose / review note |
|---|---|
| [backend/app/__init__.py](../backend/app/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/actions/__init__.py](../backend/app/actions/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/actions/adapters.py](../backend/app/actions/adapters.py) | Simulated IT access request adapter; no external IT system contacted. |
| [backend/app/actions/routes.py](../backend/app/actions/routes.py) | HTTP endpoints, input/output contracts and role/scope checks for actions. |
| [backend/app/actions/service.py](../backend/app/actions/service.py) | Proposal/reviewer/version/decision/local execution and read-back logic; see the known safety gap. |
| [backend/app/agent/__init__.py](../backend/app/agent/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/agent/graph.py](../backend/app/agent/graph.py) | Single bounded investigation loop with database steps, waits, counters and narrow proposals. |
| [backend/app/agent/model_client.py](../backend/app/agent/model_client.py) | Delegates the agent next-step operation to the shared AI harness. |
| [backend/app/agent/tools.py](../backend/app/agent/tools.py) | Seven allowlisted scoped reads; refreshes current user/hire access. |
| [backend/app/agent/worker.py](../backend/app/agent/worker.py) | One local worker thread, durable queue claims and restart reconciliation. |
| [backend/app/ai/__init__.py](../backend/app/ai/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/ai/harness.py](../backend/app/ai/harness.py) | Four registered model operations; schema/semantic checks, single repair and run metadata. |
| [backend/app/ai/prompts.py](../backend/app/ai/prompts.py) | Versioned prompts and controlled context formatting. |
| [backend/app/ai/providers.py](../backend/app/ai/providers.py) | Configured hosted/Ollama/disabled transports and explicit test override; no automatic provider fallback. |
| [backend/app/ai/stub.py](../backend/app/ai/stub.py) | Deterministic model-protocol implementation; explicitly not AI. |
| [backend/app/ai/validators.py](../backend/app/ai/validators.py) | Checks source-quote/citation references and supplied insight values. |
| [backend/app/analytics/__init__.py](../backend/app/analytics/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/analytics/routes.py](../backend/app/analytics/routes.py) | HTTP endpoints, input/output contracts and role/scope checks for analytics. |
| [backend/app/analytics/service.py](../backend/app/analytics/service.py) | SQL/Python dashboard/reliability counts and optional validated model summaries. |
| [backend/app/auth/__init__.py](../backend/app/auth/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/auth/permissions.py](../backend/app/auth/permissions.py) | Backend operation/source/category/knowledge permission matrices. |
| [backend/app/auth/routes.py](../backend/app/auth/routes.py) | HTTP endpoints, input/output contracts and role/scope checks for auth. |
| [backend/app/auth/service.py](../backend/app/auth/service.py) | Password/session/account/reset and object-level authorization logic. |
| [backend/app/cases/__init__.py](../backend/app/cases/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/cases/routes.py](../backend/app/cases/routes.py) | HTTP endpoints, input/output contracts and role/scope checks for cases. |
| [backend/app/documents/__init__.py](../backend/app/documents/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/documents/routes.py](../backend/app/documents/routes.py) | HTTP endpoints, input/output contracts and role/scope checks for documents. |
| [backend/app/documents/service.py](../backend/app/documents/service.py) | Safe upload/private storage, text/location extraction, advisory model extraction and human review. |
| [backend/app/evidence/__init__.py](../backend/app/evidence/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/evidence/routes.py](../backend/app/evidence/routes.py) | HTTP endpoints, input/output contracts and role/scope checks for evidence. |
| [backend/app/evidence/service.py](../backend/app/evidence/service.py) | Deterministic independent outcome predicates, source handling and historical receipts. |
| [backend/app/knowledge/__init__.py](../backend/app/knowledge/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/knowledge/routes.py](../backend/app/knowledge/routes.py) | HTTP endpoints, input/output contracts and role/scope checks for knowledge. |
| [backend/app/knowledge/service.py](../backend/app/knowledge/service.py) | Approved document chunking/versioning, permission-filtered FTS5 and grounded answers. |
| [backend/app/main.py](../backend/app/main.py) | Creates FastAPI app, mounts routes, runs worker lifecycle, sanitizes HTTP errors, logs requests and serves built assets. |
| [backend/app/notifications/__init__.py](../backend/app/notifications/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/notifications/routes.py](../backend/app/notifications/routes.py) | HTTP endpoints, input/output contracts and role/scope checks for notifications. |
| [backend/app/notifications/service.py](../backend/app/notifications/service.py) | In-app notification delivery, deduplication and deterministic escalation. |
| [backend/app/planning/__init__.py](../backend/app/planning/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/planning/routes.py](../backend/app/planning/routes.py) | HTTP endpoints, input/output contracts and role/scope checks for planning. |
| [backend/app/planning/service.py](../backend/app/planning/service.py) | Approved rule selection, ownership/dates/dependencies, task claims, completion and location-plan impact. |
| [backend/app/shared/__init__.py](../backend/app/shared/__init__.py) | Python package marker; no standalone feature. |
| [backend/app/shared/config.py](../backend/app/shared/config.py) | Backend environment loading, live model settings and local storage paths. |
| [backend/app/shared/contracts.py](../backend/app/shared/contracts.py) | Canonical Pydantic wire/internal models and enums. |
| [backend/app/shared/db.py](../backend/app/shared/db.py) | SQLite connections/schema initialization; limited upgrade and email-column handling. |
| [backend/app/shared/errors.py](../backend/app/shared/errors.py) | Sanitized API error helpers and leftover stub helper. |
| [backend/app/shared/schema.sql](../backend/app/shared/schema.sql) | Canonical SQLite tables, constraints, FTS and simulated-source views. |
| [backend/app/shared/util.py](../backend/app/shared/util.py) | IDs, UTC timestamps, dates, audit records and JSON helper. |

### Backend tests and setup

| File | Purpose / review note |
|---|---|
| [backend/README.md](../README.md#architecture) | Backend handoff guide; several business/model-stub statements are obsolete. |
| [backend/requirements.txt](../backend/requirements.txt) | Pinned Python dependencies, including unused LangGraph packages and active PDF/multipart packages. |
| [backend/tests/__init__.py](../backend/tests/__init__.py) | Python package marker; no standalone feature. |
| [backend/tests/conftest.py](../backend/tests/conftest.py) | Creates isolated temporary test worlds; disables worker/live-model calls. |
| [backend/tests/helpers.py](../backend/tests/helpers.py) | Synthetic API test helpers and scripted provider replies. |
| [backend/tests/test_acceptance.py](../backend/tests/test_acceptance.py) | Route authentication, role/scope denial, error privacy, limited upgrade and seed refusal. |
| [backend/tests/test_actions.py](../backend/tests/test_actions.py) | Approval, stale/duplicate/race behavior, source authority and read-back; execution-time revocation/expiry cases are missing. |
| [backend/tests/test_agent.py](../backend/tests/test_agent.py) | Agent waits/restart/counters/scope/provider failure and transport/status controls. |
| [backend/tests/test_auth.py](../backend/tests/test_auth.py) | Sessions, case-insensitive email, lockout, scope, employee sign-up and HR reset. |
| [backend/tests/test_contracts.py](../backend/tests/test_contracts.py) | Generated drift/examples/paths and cross-Python 422 description stability. |
| [backend/tests/test_documents.py](../backend/tests/test_documents.py) | Upload/access attacks, extraction citations/injection/privacy and human-only review. |
| [backend/tests/test_foundation.py](../backend/tests/test_foundation.py) | Health/database/validation safety and remaining stub-detection test; not proof that business routes are still stubs. |
| [backend/tests/test_integration.py](../backend/tests/test_integration.py) | Full onboarding journey and manual workflow with AI disabled. |
| [backend/tests/test_knowledge.py](../backend/tests/test_knowledge.py) | Retrieval access, citations, abstention, invalid output, drafts, escalation and logs. |
| [backend/tests/test_planning.py](../backend/tests/test_planning.py) | Profile-dependent plans, dates/dependencies/ownership, evidence states and escalation. |

### Frontend application, shared code and setup

| File | Purpose / review note |
|---|---|
| [frontend/README.md](../README.md#folder-guide) | Frontend setup and hash-routing/session description. |
| [frontend/eslint.config.js](../frontend/eslint.config.js) | TypeScript/React lint rules. |
| [frontend/index.html](../frontend/index.html) | HTML application entry and font links. |
| [frontend/package.json](../frontend/package.json) | Pinned React/TypeScript/Vite/Vitest dependencies and frontend scripts. |
| [frontend/src/App.tsx](../frontend/src/App.tsx) | Authenticated shell, role-based navigation, AI-status banner and feature-page wiring. |
| [frontend/src/features/assistant/Assistant.tsx](../frontend/src/features/assistant/Assistant.tsx) | Question form, cited answers, uncertainty and user-to-HR escalation. |
| [frontend/src/features/audit/Audit.tsx](../frontend/src/features/audit/Audit.tsx) | Audit events, model-run records and reliability metrics. |
| [frontend/src/features/auth/Login.tsx](../frontend/src/features/auth/Login.tsx) | Sign-in, employee sign-up and HR-mediated reset request forms; selects demo emails only. |
| [frontend/src/features/auth/LoginArt.tsx](../frontend/src/features/auth/LoginArt.tsx) | Decorative login illustration; no backend/AI behavior. |
| [frontend/src/features/documents/DocumentQueue.tsx](../frontend/src/features/documents/DocumentQueue.tsx) | HR document queue, advisory extraction and human verification/rejection. |
| [frontend/src/features/insights/Insights.tsx](../frontend/src/features/insights/Insights.tsx) | Computed metrics and optional advisory AI narrative. |
| [frontend/src/features/it/ItEquipment.tsx](../frontend/src/features/it/ItEquipment.tsx) | Inventory, specific-device requests, handover and simulated access provisioning. |
| [frontend/src/features/knowledge/KnowledgeBase.tsx](../frontend/src/features/knowledge/KnowledgeBase.tsx) | HR knowledge draft/upload/approval and escalated question answers. |
| [frontend/src/features/manager/ManagerDashboard.tsx](../frontend/src/features/manager/ManagerDashboard.tsx) | Assigned hires, owned tasks, buddy and first-week plan. |
| [frontend/src/features/my-work/MyWork.tsx](../frontend/src/features/my-work/MyWork.tsx) | Current user-owned work list and filters. |
| [frontend/src/features/my-work/TaskRow.tsx](../frontend/src/features/my-work/TaskRow.tsx) | Task claim/proof display with permitted start/complete/reassign controls. |
| [frontend/src/features/notifications/AnswerForm.tsx](../frontend/src/features/notifications/AnswerForm.tsx) | Sends a human answer to a pending investigation question. |
| [frontend/src/features/notifications/Notifications.tsx](../frontend/src/features/notifications/Notifications.tsx) | Personal in-app notifications and clarification questions. |
| [frontend/src/features/overview/Overview.tsx](../frontend/src/features/overview/Overview.tsx) | HR computed dashboard, exceptions and manual escalation sweep. |
| [frontend/src/features/payroll/Benefits.tsx](../frontend/src/features/payroll/Benefits.tsx) | Scoped benefits-state recording. |
| [frontend/src/features/payroll/Payroll.tsx](../frontend/src/features/payroll/Payroll.tsx) | Scoped sanitized payroll preparation/confirmation flags. |
| [frontend/src/features/payroll/Training.tsx](../frontend/src/features/payroll/Training.tsx) | Scoped training source-state recording. |
| [frontend/src/features/portal/Portal.tsx](../frontend/src/features/portal/Portal.tsx) | Employee onboarding checklist, document upload, next action and benefits choice. |
| [frontend/src/features/review/PlanDiffView.tsx](../frontend/src/features/review/PlanDiffView.tsx) | Displays exact task creation/cancellation/preservation/check impact. |
| [frontend/src/features/review/ProposalCard.tsx](../frontend/src/features/review/ProposalCard.tsx) | Review/decision and pending/succeeded/failed/unknown outcome display. |
| [frontend/src/features/review/ReviewInbox.tsx](../frontend/src/features/review/ReviewInbox.tsx) | Lists role-appropriate proposals awaiting/recently receiving decisions. |
| [frontend/src/features/settings/Settings.tsx](../frontend/src/features/settings/Settings.tsx) | Model configuration/status and HR password resets; no provider/model selector. |
| [frontend/src/features/workspace/CreateHire.tsx](../frontend/src/features/workspace/CreateHire.tsx) | HR multi-step new-hire form using reference data and canonical API shapes. |
| [frontend/src/features/workspace/Directory.tsx](../frontend/src/features/workspace/Directory.tsx) | Authorized employee directory with filters and task-claim counts. |
| [frontend/src/features/workspace/DocumentsTab.tsx](../frontend/src/features/workspace/DocumentsTab.tsx) | Hire-scoped document list. |
| [frontend/src/features/workspace/EditHire.tsx](../frontend/src/features/workspace/EditHire.tsx) | HR editable profile/contact fields with expected version. |
| [frontend/src/features/workspace/EvidenceTab.tsx](../frontend/src/features/workspace/EvidenceTab.tsx) | Independent check receipts and manual run-check action. |
| [frontend/src/features/workspace/HireWorkspace.tsx](../frontend/src/features/workspace/HireWorkspace.tsx) | Hire profile summary and plan/evidence/documents/investigation/history tabs. |
| [frontend/src/features/workspace/HistoryTab.tsx](../frontend/src/features/workspace/HistoryTab.tsx) | Hire-scoped audit history. |
| [frontend/src/features/workspace/InvestigationTab.tsx](../frontend/src/features/workspace/InvestigationTab.tsx) | Open/poll cases; show questions, proposals, receipts and sanitized timeline. |
| [frontend/src/features/workspace/LocationChange.tsx](../frontend/src/features/workspace/LocationChange.tsx) | Request a reviewed location-change proposal, not an immediate mutation. |
| [frontend/src/features/workspace/PlanTab.tsx](../frontend/src/features/workspace/PlanTab.tsx) | Categorized tasks, dependencies and separate claim/proof views. |
| [frontend/src/features/workspace/TimelineTab.tsx](../frontend/src/features/workspace/TimelineTab.tsx) | Task/start-date timeline derived from plan data. |
| [frontend/src/main.tsx](../frontend/src/main.tsx) | Mounts the React application and global styles. |
| [frontend/src/shared/api-client.test.ts](../frontend/src/shared/api-client.test.ts) | Tests auth headers, uploads, structured failures and client helpers. |
| [frontend/src/shared/api-types.ts](../frontend/src/shared/api-types.ts) | Generated wire types; checked for drift, never hand-edit. |
| [frontend/src/shared/api.test.ts](../frontend/src/shared/api.test.ts) | Tests relative HTTP prefix and error propagation. |
| [frontend/src/shared/api.ts](../frontend/src/shared/api.ts) | Relative API methods, bearer/sessionStorage handling, uploads/downloads and structured errors. |
| [frontend/src/shared/format.ts](../frontend/src/shared/format.ts) | Readable names, dates, status tones and reason labels. |
| [frontend/src/shared/hooks.ts](../frontend/src/shared/hooks.ts) | Resource loading/actions, routing and 15-second/focus refresh. |
| [frontend/src/shared/icons.tsx](../frontend/src/shared/icons.tsx) | Navigation icons. |
| [frontend/src/shared/logic.test.ts](../frontend/src/shared/logic.test.ts) | Tests claim/proof, task/proposal/timeline/portal/format/navigation logic. |
| [frontend/src/shared/logic.ts](../frontend/src/shared/logic.ts) | Pure display/filter/timeline/task/portal calculations, not server authority. |
| [frontend/src/shared/routes.ts](../frontend/src/shared/routes.ts) | Hash routes, frontend role-page visibility and navigation groups. |
| [frontend/src/shared/session-context.ts](../frontend/src/shared/session-context.ts) | Shared authenticated-user/shell context definitions. |
| [frontend/src/shared/session.tsx](../frontend/src/shared/session.tsx) | Session restoration, login/signup/logout and unauthorized-state handling. |
| [frontend/src/shared/ui.tsx](../frontend/src/shared/ui.tsx) | Reusable labels, forms, states, tables, evidence cards and advisory/offline badges. |
| [frontend/src/styles.css](../frontend/src/styles.css) | Shared design/responsive/focus/reduced-motion styles; not business or AI logic. |
| [frontend/tsconfig.json](../frontend/tsconfig.json) | Strict TypeScript checking settings. |
| [frontend/vite.config.test.ts](../frontend/vite.config.test.ts) | Serve/build regression checks preventing demo-password injection into browser code. |
| [frontend/vite.config.ts](../frontend/vite.config.ts) | React development/build configuration and relative API proxy; no password injection. |

### Fixtures

| File | Purpose / review note |
|---|---|
| [fixtures/README.md](../README.md#data-and-backups) | Fixture handoff and safety policy; earlier no-seed/six-hire text is obsolete. |
| [fixtures/documents/government_id_priya.txt](../fixtures/documents/government_id_priya.txt) | Explicitly synthetic identity-text fixture; not a real identity document. |
| [fixtures/documents/injected_letter.txt](../fixtures/documents/injected_letter.txt) | Synthetic malicious-instruction fixture for injection/control tests. |
| [fixtures/documents/offer_letter_priya.txt](../fixtures/documents/offer_letter_priya.txt) | Fictional Priya offer text with Bengaluru location for the conflict demonstration. |
| [fixtures/knowledge/benefits_overview.md](../fixtures/knowledge/benefits_overview.md) | Fictional benefits overview knowledge input; approved/access-filtered during seeding. |
| [fixtures/knowledge/equipment_guide.md](../fixtures/knowledge/equipment_guide.md) | Fictional equipment guide knowledge input; approved/access-filtered during seeding. |
| [fixtures/knowledge/hr_compensation.md](../fixtures/knowledge/hr_compensation.md) | Fictional hr compensation knowledge input; approved/access-filtered during seeding. |
| [fixtures/knowledge/it_runbook.md](../fixtures/knowledge/it_runbook.md) | Fictional it runbook knowledge input; approved/access-filtered during seeding. |
| [fixtures/knowledge/leave_policy.md](../fixtures/knowledge/leave_policy.md) | Fictional leave policy knowledge input; approved/access-filtered during seeding. |
| [fixtures/knowledge/manager_handbook.md](../fixtures/knowledge/manager_handbook.md) | Fictional manager handbook knowledge input; approved/access-filtered during seeding. |
| [fixtures/knowledge/onboarding_documents.md](../fixtures/knowledge/onboarding_documents.md) | Fictional onboarding documents knowledge input; approved/access-filtered during seeding. |
| [fixtures/knowledge/reimbursement_policy.md](../fixtures/knowledge/reimbursement_policy.md) | Fictional reimbursement policy knowledge input; approved/access-filtered during seeding. |
| [fixtures/knowledge/remote_work_policy.md](../fixtures/knowledge/remote_work_policy.md) | Fictional remote work policy knowledge input; approved/access-filtered during seeding. |
| [fixtures/policy_pack.json](../fixtures/policy_pack.json) | 17 fictional approved profile/location task rules across seven categories. |
| [fixtures/seed.py](../fixtures/seed.py) | Safe one-time synthetic seed; 11 accounts, 3 departments, 5 inventory records, 9 knowledge documents and 3 hires. |

### Evaluation

| File | Purpose / review note |
|---|---|
| [evals/README.md](../evals/README.md) | Evaluation handoff; obsolete statements still say the implemented runner does not exist. |
| [evals/answer_keys.json](../evals/answer_keys.json) | Expected evaluation sources; not runtime policies or model context. |
| [evals/results/hosted_openai_gpt-oss-20b_2026-11-06T165624Z.json](../evals/results/hosted_openai_gpt-oss-20b_2026-11-06T165624Z.json) | Saved 6 November Groq live-model evaluation: historical evidence, not a current rerun. |
| [evals/results/stub_stub-rules-not-ai_2026-11-06T160636Z.json](../evals/results/stub_stub-rules-not-ai_2026-11-06T160636Z.json) | Saved 6 November offline-rules baseline: not model-quality evidence. |
| [evals/run.py](../evals/run.py) | Runs synthetic assistant/retrieval/control checks and optional live workflow against an isolated evaluation database. |
| [evals/scenarios.json](../evals/scenarios.json) | 82 synthetic evaluation questions grouped by intent/access/injection/untuned variants. |

### Documentation and submission instructions

| File | Purpose / review note |
|---|---|
| [docs/API_SPEC.md](../docs/API_SPEC.md) | Generated endpoint/type specification; regenerate from canonical code, do not hand-edit. |
| [docs/ASSUMPTIONS.md](../README.md#problem-and-solution) | Original scope/assumptions plus R06 override; not all older cuts still apply. |
| [docs/DATABASE_DECISION.md](../README.md#data-and-backups) | Local SQLite rationale and future hosted-database options; implementation-status sentences are outdated. |
| [docs/DATA_MODEL.md](../docs/DATA_MODEL.md) | Schema/lifecycle explanation with an R06 override and obsolete details below it. |
| [docs/DEMO_PLAN.md](../video/script.md) | Role-by-role onboarding/investigation demonstration and official-rubric mapping. |
| [docs/EVALUATION.md](../docs/EVALUATION.md) | Human-readable measured results, failures and limitations of saved live/stub runs. |
| [docs/PROJECT_REVIEW.md](../docs/PROJECT_REVIEW.md) | This plain-language explanation, evidence-grounded readiness review and file map. |
| [docs/PROVIDERS.md](../README.md#ai-keys-and-providers) | Planned discovery/eligibility/selection design, not an implemented model picker. |
| [docs/README.md](decisions/2026-11-07-improvement-plan.md) | Documentation index; some current-foundation wording is stale. |
| [docs/SUBMISSION_CHECKLIST.md](../README.md#submission) | Final release/delivery checklist, not evidence the items were submitted. |
| [docs/TEAM_WORKFLOW.md](../README.md#contributing-and-documentation-policy) | Team setup, independent databases, backup and ownership guidance; some seed/model instructions are stale. |
| [docs/VERIFICATION.md](../docs/VERIFICATION.md) | Dated test/platform evidence; read the R06 section rather than only the older foundation header. |
| [docs/openapi.json](../docs/openapi.json) | Generated OpenAPI snapshot; checked for drift rather than manually reviewed as independent business logic. |
| [ppt/README.md](../ppt/README.md) | Instructions for five final slides; no final PPTX/PDF found in the indexed folder. |
| [resume/README.md](../resume/README.md) | Team resume naming/consent instructions; not an official PDF deliverable or consent evidence. |
| [video/README.md](../video/script.md) | Recording length, size, privacy and publication instructions. |
| [video/VIDEO_LINK.md](../video/VIDEO_LINK.md) | Currently states not recorded; no actual accessible video link. |

### Scripts

| File | Purpose / review note |
|---|---|
| [scripts/check-lockfile.mjs](../scripts/check-lockfile.mjs) | Asserts Rollup/esbuild optional native-package versions are represented in the lockfile. |
| [scripts/dev.mjs](../scripts/dev.mjs) | Starts local API and Vite or built UI; refuses occupied ports and stops its own child processes. |
| [scripts/export_contracts.py](../scripts/export_contracts.py) | Generates OpenAPI, API Markdown and frontend types from canonical schemas/routes. |
| [scripts/python.mjs](../scripts/python.mjs) | Runs the repository virtual-environment Python without manual activation. |
| [scripts/serve.py](../scripts/serve.py) | Container launcher: seed only if no users, then bind Uvicorn to PORT on 0.0.0.0. |
| [scripts/smoke.mjs](../scripts/smoke.mjs) | Read-only HTTP health/bootstrap/HTML smoke; not browser end-to-end acceptance. |


</details>
