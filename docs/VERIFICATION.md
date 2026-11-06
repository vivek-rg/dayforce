# Foundation verification record

## Scope

P01 only. These checks demonstrate repository setup, contracts and connectivity, **not** a working onboarding/AI/security product. Feature phases P02–P28 are not implemented (P27 is an optional design-review process). R01 expanded planning and R02 reviews the foundation handoff; neither implements business features. No real model/API call, paid plan, public deployment, presentation, recording or resume upload was performed.

## Environment

Windows; Python 3.13.9, Node 24.13.0, npm 11.17.0. CI configuration targets Ubuntu/Python 3.12/Node 22, but no remote GitHub Actions run has happened. macOS/Linux launch commands are documented but not manually exercised on those operating systems.

## Observed checks — 6 November 2026

- `npm run check`: Ruff + ESLint, formatting, **14 backend tests + 3 frontend tests**, strict TypeScript/Vite build, generated contracts: passed.
- `npm run dev` followed by `npm run smoke` in another terminal: passed actual frontend-origin → API proxy → SQLite-backed health/bootstrap and served HTML.
- Business GET routes return the documented 501 error, invalid login payload returns sanitized 422, unknown API route returns 404, unavailable database returns sanitized 503 in tests.
- Repeat schema initialization preserves an existing stored value; SQLite foreign keys enforced; shared model examples validate; generated OpenAPI/Markdown/TypeScript drift checks pass.

## Fresh Git clone and runtime evidence

- Created an isolated **temporary local Git snapshot and actual clone**, excluding .env, .venv, node_modules, databases and built output. No commit/remote/push was made in the user's working repository. Verification clone: `C:\Users\vinay\AppData\Local\Temp\opencode\dayone-foundation-y0_k13yq\clone`.
- In the clone: `python -m venv .venv`; `.venv\Scripts\python.exe -m pip install -r backend/requirements.txt`; `npm ci`; copy .env.example → .env; `npm run check`; `.venv\Scripts\python.exe -m pip check`: all passed. Python/npm caches supplied downloaded packages, but neither an existing environment nor node_modules was copied.
- `npm run build` + `npm start`, then `SMOKE_BASE_URL=http://127.0.0.1:8000 npm run smoke` (PowerShell environment assignment used): passed in both working source and the verification clone. Actual SQLite files were created on first startup; the stored project name was read through HTTP.
- `GET /.env` on the built server returned 404. Only frontend assets/index and explicit APIs are served.
- Desktop Edge headless rendered the actual loaded DB-backed success message; screenshot inspected. The diagnostic UI is intentionally not the onboarding feature UI. No full interactive/mobile/keyboard acceptance or feature E2E approval is claimed; P09/P10 own those checks.
- Impeccable's mechanical detector over App.tsx/styles.css returned no findings; this is not a substitute for browser acceptance/security tests.
- Final foundation after internal seam typing/regeneration: `npm run check` passed again (14 backend + 3 frontend tests, 20 HTTP contracts and 54 shared schemas). Subsequent handoff edits are documentation/status only.
- `pip check`: no broken requirements. `npm audit --omit=dev`: **0 reported production-dependency vulnerabilities**. Full `npm audit`: **10 moderate**, **0 high**, **0 critical**, in the development lint dependency tree via minimatch (GHSA-g3hv-75wg-m249). Audit results are time-dependent, not a security certification.

## Dependency advisory decision

Patched Vite/Vitest versions were selected after the initial install audit exposed high/critical findings. Remaining moderate minimatch findings are transitive development-tool issues, not a demonstrated application exploit; use only trusted source/globs and loopback dev servers. They remain an explicit limitation. Do not silently `npm audit fix --force`/downgrade the toolchain or override a dependency across a major version without compatibility testing. Track 1 should recheck upstream fixes before a broader/public deployment. Python dependencies were checked for compatibility with `pip check`, **not** comprehensively vulnerability-audited.

## Local Git state and manual publication

The working directory is initialized as a Git repository on `feature/p01-foundation`. All source remains uncommitted for team review; no remote URL/account, remote branch protection or GitHub Actions result exists yet. The integration lead must review/stage safe source, create the first foundation commit, publish it as the team's initial main branch and configure PR reviews/CI. After that, every feature phase follows own-branch/small-PR workflow. Temporary verification commits exist only in the isolated snapshot, not the user's working tree.

## Known boundaries

- Initial schema only: no business seed, sessions, task planner, agent, approvals or executor exists.
- No CI result, model latency/quality, hosted schema/key compatibility, real integration, production security/compliance or enterprise user outcome is claimed.
- Smoke checks are real HTTP, not a browser interaction test. A future P09/P10 browser journey must be tested separately.
- npm development-tool advisories above remain open. Never expose development servers to untrusted networks.
- GitHub repository/remote, personal data publication consent and final assets require human/team action.

## R02 foundation/handoff recheck — 6 November 2026, 12:02:56 UTC

- Reviewed root/module setup docs, environment consumption, launch/smoke scripts, tests, contracts/schema handoff, CI configuration, phase ownership and submission privacy instructions. Preserved the original guide/PDF and canonical/generated contracts; this review changes ignore rules and explanatory prose only.
- Corrected `.env.example`: DATABASE_PATH is the only setting currently read by application code. Checkpoint/auth/model/budget values remain explicitly future placeholders, not active safety controls or working provider settings. No secret/private `.env` was read or edited.
- Fixed a privacy mismatch: resume PDFs and common recording formats were described as ignored but lacked Git rules. Added those targeted rules and custom-location SQLite journal/checkpoint sidecar protection. `git check-ignore -q` assertions pass for `.env`, resume/video samples and SQLite companions; `.env.example` remains visible for commit. No actual private asset was staged.
- `npm run check`: passed Ruff/ESLint/formatting, 14 backend tests, 3 frontend tests, TypeScript/Vite build and generated-contract drift. An initial frontend README formatting failure was corrected with Prettier on that single owned file, then the whole check passed.
- `.venv\Scripts\python.exe -m pip check`: passed. `npm audit --omit=dev`: zero findings. Full `npm audit`: **10 moderate** development-tool findings, exit 1 as expected; these remain open under the documented advisory decision. No force-fix/dependency change was made.
- Temporary external assert-based review script: all current handoff Markdown relative file links/code fences, unique P01–P28 definitions/required sections, blank key/password placeholders and effective Git privacy exclusions passed. Original researched guide was preserved, not rewritten/revalidated as implementation instructions. Relative file existence is checked, not every external URL or Markdown heading fragment.
- Real HTTP: ran `node scripts/dev.mjs` and `node scripts/dev.mjs --built` (the root npm launch scripts), each followed by `node scripts/smoke.mjs` with the matching SMOKE_BASE_URL. Both passed proxy/same-origin health/bootstrap/HTML with an isolated temporary application DB; hire route remained honest 501. Built `/.env` and `/backend/app/main.py` returned 404. SQLite integrity passed and restart preserved app_info with all business tables empty. Only test-owned processes were terminated; the user's runtime database was untouched.
- The external test helper initially left its own SQLite connection open at temporary-directory cleanup. Explicitly closing that test-only connection fixed cleanup; the complete rerun passed. No application connection/lifecycle defect was demonstrated by that helper failure.
- Still not checked here: another fresh dependency install/clone, macOS/Linux execution, remote GitHub CI, live model/key/quota/semantic quality, full browser accessibility journey, eight real teammate machines, business seed/migrations or backup restore. These are future release/feature gates, not implied by P01 completion. No commit or push was performed.

## R03 current policy and database decision — 6 November 2026, 12:13:00 UTC

- **Supersedes R02's artifact ignore policy:** the user wants approved resumes, recordings, PPTX and presentation PDFs eligible for ordinary Git staging. Removed resume/video exclusions; kept `.env`, local database/checkpoint/companion files, dependencies, build output and caches ignored. No actual resume/recording/presentation was created, staged or uploaded; consent, secret review and ordinary Git file-size limits still apply. R02's earlier test results above remain historical, not the current asset policy.
- Corrected active provider scope to Groq, Cerebras, Mistral, Gemini and OpenRouter plus local Ollama/Llama. Six paths remain, with P23 reassigned to the shared free-tier/eligibility/quota gate. No unrelated provider URL, key instruction or adapter task remains in active handoff docs. Historical CHANGES entries are append-only records and are superseded by the current R03 scope.
- Asked the user about shared online state versus a local demo and existing cloud setup. The user chose the local demo and prioritized easy setup for all teammates; retained working SQLite and documented identical commands/schema/fixture revisions on independent files. Added DATABASE_DECISION.md comparing Neon/Supabase managed PostgreSQL and MongoDB, genuine migration work on every engine, checkpoint implications and accurate pitch wording. No engine, connection helper, schema, wire contract or runtime feature changed.
- `npm run check`: passed Ruff/ESLint/formatting, **14 backend tests + 3 frontend tests**, TypeScript/Vite build and generated-contract drift.
- Temporary external assert-based policy check passed for all current handoff Markdown relative file links/code fences, exactly 28 phase definitions and their required sections, six-provider scope, normal Git eligibility of resume/video/PPT samples plus `.env.example`, and continued exclusion of secrets, DB files/companions, dependencies/builds/caches. SQLite file-path default is unchanged. The temporary helper was removed after verification; no private `.env` or actual personal asset was read.
- Not rerun in this policy-only revision: HTTP/browser smoke, fresh-clone install, eight-member replay, dependency audit, live model/account/quota checks or cloud migration/performance tests. Prior R02 runtime smoke/audit evidence remains as dated above, not a new guarantee. All feature phases remain pending; no commit/push was performed.

## R04 Python-version-independent contract snapshot — 6 November 2026, 12:26:59 UTC

- Investigated the user's hosted CI report (1 failed, 13 passed). Local Python 3.13 contract tests passed; tested export stability across hash seeds 0/1/2/42/99/random with no difference. GitHub CLI was unavailable and public Actions API access returned 404, so no hosted job log or new CI outcome is claimed.
- Reproduced the failure using a temporary official Windows Python **3.12.10** embeddable interpreter and matching pinned **pydantic_core 2.50.4 cp312** wheel, reusing the existing pinned pure-Python dependency directory with pytest plugin autoload disabled. The mismatch was the generated JSON response description for HTTP 422: Python 3.12's `http.client.responses` says `Unprocessable Entity`, while local Python 3.13 says `Unprocessable Content`. FastAPI uses that standard-library text when no explicit description is supplied. This was metadata drift, not a changed response schema or a working-business-route failure.
- Added a parameterized regression that changes the stdlib 422 phrase and clears the OpenAPI cache before exporting. Before the fix: `node scripts/python.mjs -m pytest backend/tests/test_contracts.py -k python_422_reason -q --tb=short` failed for the Python 3.12 phrase and passed for 3.13, confirming the same difference without skipping drift checks.
- Fixed the shared route response definition in backend/app/main.py to explicitly use the existing snapshot's `Unprocessable Content` description. No status codes, response models, runtime error payloads, business behavior or dependencies changed.
- `npm run contracts`: passed and produced **no generated file changes**. `npm run check`: passed Ruff/ESLint/formatting, **16 backend + 3 frontend tests**, strict TypeScript/Vite build and contract drift. Temporary Python 3.12 run of `-m pytest backend/tests -q --tb=short`: **16 passed**. `git diff --check`: passed. Temporary interpreter/package directories and reproduction scripts were removed after use; the main virtual environment was not modified.
- Remaining: actual Ubuntu/GitHub Actions rerun, live-model/business features and prior documented boundaries. This Windows Python 3.12 reproduction is not a claim of a hosted Ubuntu run. No commit/push was performed; patch is on fix/portable-openapi-snapshot.

## R05 cross-platform npm lockfile repair — 6 November 2026, 12:39:03 UTC

- User's next CI log confirms the 16 backend tests pass, then Vitest fails to load `@rollup/rollup-linux-x64-gnu`. The committed lockfile lists Rollup's platform dependencies but has records for only its Windows binaries; esbuild similarly has only its Windows native package recorded. This is incomplete cross-platform dependency metadata, not a failed frontend assertion.
- Added scripts/check-lockfile.mjs and `npm run lockfile:check`, run first by `npm run check`. It asserts each declared Rollup/esbuild native platform package has the exact required locked version. It failed against the old lockfile before repair and passes afterward, catching omitted macOS/Linux variants without requiring those operating systems to run the guard.
- Regenerated package-lock.json with npm **11.17.0** in a temporary independent manifest-only directory with neither lockfile nor node_modules. Existing-lockfile-only refreshes did not restore missing records; a full isolated resolution was required. Compared all original package-name/version identities with the regenerated tree: none removed/upgraded, with new identities limited to missing native optional variants and the existing declared optional fsevents dependency. npm also restored resolved/integrity metadata and changed some dependency hoisting; manifests gained no dependencies. The user's node_modules was not deleted or reinstalled.
- Linux-targeted clean install: `npm ci --include=optional --ignore-scripts --os=linux --cpu=x64 --libc=glibc --no-audit --no-fund` in an isolated directory passed. Asserted actual `@rollup/rollup-linux-x64-gnu/rollup.linux-x64-gnu.node` and `@esbuild/linux-x64/bin/esbuild` files exist. These Linux binaries were **not executed on Windows**; this is install/artifact evidence, not an Ubuntu runtime claim.
- Independent clean Windows install: `npm ci --include=optional --no-audit --no-fund`, `npm run lint --workspace frontend`, `npm run test --workspace frontend` (**3 passed**) and `npm run build` all passed with fresh dependencies and copied safe frontend source/config. No virtual environment, private .env, database or personal asset was copied. npm warned that esbuild's install script lacked allowScripts approval; the tested binaries and build worked without changing global approval policy.
- Working-source `npm run check`: passed lockfile guard, Ruff/ESLint/formatting, **16 backend + 3 frontend tests**, TypeScript/Vite build and contract drift. `npm audit --omit=dev`: zero findings. `git diff --check`: passed. Temporary reproduction/install directories and helper were removed after use.
- Scope/limits: all edits remain on the user's existing fix/portable-openapi-snapshot branch; the empty extra branch created before the user's correction was removed. No further branch, commit, push, dependency upgrade, runtime/schema/API change or CI-specific install workaround was made. Actual GitHub Actions/Ubuntu/Node 22 execution and non-Windows native execution still require the hosted rerun. Prior documented development-tool advisories are not claimed resolved by lockfile metadata repair.

## End-to-end build R06 (2026-11-06)

Run on macOS with Python 3.12, Node 26 for the browser driver, and Chrome. Not rerun on Windows or Linux.

| Check | Result |
|---|---|
| `npm run check` (lint, format, tests, build, contract drift) | Passed |
| Backend tests | 130 passed, using scripted model replies and labelled offline rules |
| Frontend tests | 35 passed |
| Scripted real-Chrome run against the production build, offline rules | 48 of 48 checks passed, no page errors, no server errors, on a fresh clone |
| Live model | One evaluation run on Groq; see docs/EVALUATION.md |

The browser script is not in the repository, because it would add a dependency. It signs in as each role, drives every screen with real clicks including uploads and downloads, and walks every sidebar link at 1440 px and 390 px.

**Not verified:** hosting on a real server, a full keyboard or screen-reader pass, other browsers, Windows or Linux, and live-model answers through the browser UI.
