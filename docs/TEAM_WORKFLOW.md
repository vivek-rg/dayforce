# Eight teammates: setup, SQLite and safe changes

## What each person needs

Git, Node 22.14+ (22.x) or 24.x, Python 3.12/3.13 and a local folder outside OneDrive/network sync. No SQLite server, Docker, API key or model is needed for the current foundation.

Follow [README installation](../README.md#clone-and-install--windows-powershell) once per clone. Keep your own `.venv`, `node_modules` and `.env`. Do not copy another member's tokens or private configuration. Only copy `.env.example` to `.env` on a fresh clone; do not overwrite an existing file.

### Daily commands (repository root, either shell)

```sh
git status --short --branch
git switch main
git pull --ff-only origin main
git switch -c any-name-you-choose
npm run check
npm run dev
```

The remote and main branch must exist first; Track 1 performs the initial publication. If you have uncommitted work, stop before switching/pulling and save it deliberately; never reset/clean to make a command pass. The branch name is your choice. Open http://127.0.0.1:5173; leave that terminal running. In a second terminal:

```sh
npm run smoke
```

Ctrl+C stops your development servers. `npm run check` checks code/tests/types/contracts, not live model quality. After pulling a changed npm lockfile, run `npm ci`; after changed Python requirements, run your `.venv` Python's `-m pip install -r backend/requirements.txt` again. Do not upgrade dependency versions yourself just to fix an install error.

## How SQLite works for eight people

**One database per clone/machine.** The backend creates `.runtime/dayone.db` on first startup with the schema and one project-name row. Business tables are empty. Each connection enables foreign keys and has a five-second lock timeout. Do not share the live file over Git, Drive, OneDrive or a network drive. Different teammates' work-in-progress data does not automatically sync.

The user confirmed a **local demo and easiest team setup**, so keep this existing SQLite path. Everyone runs the same commands against the same schema/fixture revision; nobody needs to create a cloud database account. One shared online database is a different requirement, not necessary for eight people to develop together. All engines still need migrations. See [SQLite versus Neon/Supabase/MongoDB](DATABASE_DECISION.md) before proposing a backend switch.

What Git shares: SQL schema, reviewed migration scripts, synthetic fixture files and tests. What Git does not share: `.db`, checkpoints, sessions, API keys, `.env`, installed models, virtual environments or dependencies. Eight copies generated from the same reviewed fixture revision give a reproducible starting story, **not identical mutable database state**. Tests get isolated temporary databases.

Agent state lives in the application database, so one database file is a complete backup. Uploaded documents sit beside it in `.runtime/documents`; back up both together.

### Use a separate demo database without deleting your current work

Existing environment variables override `.env`. Stop the app first. Choose a new path that does not already contain your business data:

PowerShell:

```powershell
$env:DATABASE_PATH = ".runtime/demo-practice.db"
npm run dev
```

Bash:

```bash
DATABASE_PATH=.runtime/demo-practice.db npm run dev
```

The app creates the folder/schema, not the demo hires. Set the same paths in **every** future seed/eval command and app terminal; otherwise you may seed one DB and view another. For repeat work, privately set these values in `.env` instead. In PowerShell remove session overrides after stopping the app:

```powershell
Remove-Item Env:DATABASE_PATH
```

### Demo seed — not implemented yet

Wait until P03 is merged and verified. Its required command is `node scripts/python.mjs fixtures/seed.py`, using a private `DEMO_PASSWORD` of at least 12 characters from `.env`. Do not paste passwords into PRs/screenshots/shell history. The command must seed only an empty business database, hash passwords, use one transaction and refuse a second run without overwriting anything. Health's existing app_info row is allowed. Fixture revision/date and printed non-secret user IDs should be documented by P03/P14.

There is no reset command. For a new practice run, choose a new database/checkpoint pair; keep existing files until their owner decides what to do. Never run SQL deletes or replace somebody else's DB to resolve a Git conflict.

### Back up before a migration or risky rehearsal

1. Stop backend and worker fully. No active writes, seed, tests against that DB or model run.
2. Choose a new backup folder under ignored `.runtime/`. Copy the whole stopped runtime directory, including any SQLite journal/WAL/SHM and checkpoint companions. Do not copy a live SQLite file with ordinary file-copy commands.
3. Keep the backup private/local. It can contain sessions, prompts and personal data if someone broke the synthetic-only rule. Do not attach it to a PR.

PowerShell (app stopped):

```powershell
$Backup = ".runtime/backups/$(Get-Date -Format yyyyMMdd-HHmmss)"
New-Item -ItemType Directory -Path $Backup
Get-ChildItem .runtime -File | Copy-Item -Destination $Backup
```

Bash (app stopped):

```bash
backup=".runtime/backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"
find .runtime -maxdepth 1 -type f -exec cp -p {} "$backup/" \;
```

These commands cover files directly under the **default** runtime folder. For custom/nested DB paths, copy the exact application and checkpoint files **and their companion files** from both locations into a private backup outside the source folders, recording their original paths. P26 must test restore; do not advertise these stopped-file copies as an online backup service. Restore only after stopping the app and preserving the current files too; coordinate with the data owner rather than overwriting an uncertain version.

### Schema updates

`CREATE TABLE IF NOT EXISTS` initializes empty databases; it does not upgrade old tables. Track 1 owns P26 migrations and publishes exact upgrade/backup commands and supported source versions. Pull the matching code, stop the app, back up, run that reviewed command, then test health and preserved data. **No migration runner exists yet**; there is intentionally no invented command here. If a new branch needs one, stop and ask Track 1. Never delete `.runtime` as the normal fix.

## Eight tracks without eight conflicting rewrites

| Track | Primary job | Where to start |
|---|---|---|
| 1 | Integration, authentication, contracts, DB upgrades, release | P02, P15, P26, P09/P11; approve P27 changes |
| 2 | Hire overview/workspace, later selector | P06, then P24 after provider contracts; P10 |
| 3 | My work, clarification, reviews | P07; scoped part of P10 |
| 4 | Synthetic seed, rules, plans, evidence | P03; P14 with Track 8 |
| 5 | Immutable proposals, approval, safe execution | P05 |
| 6 | Cases/agent/worker and provider transport | P04, P16–P23 in order or explicitly split subfiles |
| 7 | Independent controls/security/model evaluation | P08, P25; observe P28 |
| 8 | Setup guide, fixture prose review, evidence/assets | P14/P28 docs, P12/P13; assist reviewed provider research |

Tracks describe ownership, not mandatory personal identities. Reassign a phase when the team agrees and records its exact file boundary; do not parallelize writers inside `model_client.py`. Track 1 is a reviewer/integrator, not permission to bypass feature owners. P16 must reserve provider-specific files before delegating parallel adapter work. Do not edit another track's tests/helpers to hide a failure.

### Copy-paste wrapper for any coding agent

```text
Read AGENTS.md, PHASES.md and CHANGES.md first, then the selected phase,
docs/API_SPEC.md, docs/DATA_MODEL.md and the affected source/callers/tests.
Implement only phase <ID>, within its allowed files. Check dependencies and
claim its owner/status before editing. Branch naming is my choice.
Preserve other work, secrets, contracts and all security/evidence gates.
If blocked or a better design needs other files, explain it and request a
reviewed boundary/change decision; do not silently redesign or fake success.
Run the phase checks and npm run check. Report exact results and what was
not tested. Attach sanitized evidence, append CHANGES.md and update only
this phase checklist/status. Do not claim live-model success from stubs.
```

Replace `<ID>` with one phase and append that phase's prompt. Do not paste `.env`, a private resume or full database into an external assistant. Two assistants must not write the same working tree/files simultaneously without an explicit coordinator.

### Finishing a task

- Run its tests and `npm run check`. If unrelated concurrent work fails, report the exact failing command/owner; do not mark a failing release green.
- Capture a UI screenshot for visible changes, or terminal/test output for backend tasks. Use only synthetic names; hide keys/tokens/passwords, account dashboards and private tabs. Prefer PR attachments; do not create binary screenshot churn in source unless the phase explicitly owns an evidence folder.
- Attach phase ID, commit, fixture/schema/config revisions, OS/runtime, commands/results and remaining limits. A picture of green text is not a substitute for runnable tests.
- Update your checklist/status; append CHANGES. Use `blocked` with owner/reason or `implemented; live test not run`, not a false completed box.
- Review `git diff` and staged files (initial untracked files do not appear in ordinary `git diff`). Stage only intended paths, commit and `git push -u origin HEAD`. Ask an affected teammate to review the small PR. Keep both handoff entries when resolving shared Markdown conflicts.

### Putting submission assets in GitHub

`resume/`, `video/` and `ppt/` assets are **not ignored**. Use normal `git add` on the specific reviewed files; no `-f` is required. Resume owners must consent to public personal information, recordings/slides must not contain keys or private tabs, and large video must follow GitHub/LFS/Release/link limits in video/README.md. This policy does not make `.env`, DB/checkpoint files, dependency folders, build output or caches safe to commit. Review before staging; removing an accidentally published secret in a later commit does not revoke it.

## Accepting a better design

No architecture is sacred, but “my model is smarter” is not evidence. Before changing a shared interface or foundation:

1. Explain the concrete problem and the smallest solution. List callers, affected owners/files, fixture/config/schema/API changes and user/data/privacy risks.
2. Agree measurable acceptance criteria **before** running the comparison: same scenarios, commit/input versions, hardware and budgets. Record old-version results, then new-version results. For model quality use held-out cases and actual inference, not only stub tests.
3. Preserve hard gates: authorization, no secret leaks, evidence semantics, exact human approval, stale/duplicate protection, durable waits, accessibility and manual operation during outage. A faster path that weakens these fails.
4. Integrator plus affected owner reviews. Decide explicitly whether a measured latency/cost/quality trade-off is worth it; no blanket “100% verified” claim. Include uncertainty, failed cases and untested platforms.
5. Land a small PR with migration/rollback steps if needed, canonical contract regeneration, tests and docs. Log decision/evidence in CHANGES, update affected phase boundaries, notify owners and rerun the integrated journey.
6. If it regresses, stop rollout and undo only that reviewed change through a normal reviewed follow-up. Do not reset shared history or overwrite unrelated work. Data rollback needs a tested restoration plan; reversing code alone may not reverse a migration.

## Quick troubleshooting

| Symptom | First safe check |
|---|---|
| `npm.ps1` blocked | Use `npm.cmd`; do not weaken global execution policy. |
| `.venv` or dependency missing | Re-run README install using Python 3.12/3.13 and the matching `.venv` interpreter. |
| Port 5173/8000 occupied | Stop your old app with Ctrl+C; do not kill an unknown teammate's process. |
| `501 FEATURE_NOT_IMPLEMENTED` | Expected for foundation business routes; check phase status, not a missing database download. |
| Hire list is 501, or empty after feature implementation | Foundation hire routes are 501 and have no business seed; after P03, confirm app/seed use the same DB path. |
| SQLite locked | Stop duplicate app/seed writers; wait for short transactions. Never delete lock/journal files. |
| DB differs from teammate | Expected local state; compare code/schema/fixture revisions, not raw DB files. |
| Model missing | Check provider key on backend or `ollama list`; discovery/inference is not implemented yet. |
| Model 401/429/timeout | Check access/quota privately; no repeated unbounded retries, paid upgrade or cloud fallback. |
| Contract drift | Request Track 1 canonical fix/regeneration; never hand-edit generated API types. |
