# Backend modules

Run from repository root with `npm run dev` after root README setup. Direct development command: `node scripts/python.mjs -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`.

`app/shared/` owns config/database/contracts/schema/errors. Separate auth, planning, evidence, cases, agent and actions folders are write boundaries, not microservices. Routers are already registered in app/main.py. Health/bootstrap are real; business endpoints/services are stubs. `tests/test_foundation.py` uses isolated temporary databases and makes no model calls.

Naming: service.py for domain operations, routes.py for HTTP boundary, test_<module>.py for owner tests. Prefer small direct functions. Track 1 owns requirements.in and exact requirements.txt lock; request dependencies rather than editing locks on eight branches.

Current environment support: only DATABASE_PATH is consumed by application code; .env.example marks checkpoint/model/auth/budget settings as future placeholders. P04 owns investigation/worker behavior; P15/P26 review new provider contracts/persistence, P16 owns shared discovery/dispatch, P17–P22 own separate adapters and P23 verifies shared eligibility. No provider catalog routes or migration/seed command are implemented yet. Follow PHASES.md dependencies and docs/TEAM_WORKFLOW.md rather than treating installed SDKs as completed features.

Database choice is confirmed: retain SQLite for the local demo and independent teammate environments. DATABASE_PATH accepts a file path, not a cloud connection URL; no PostgreSQL/MongoDB driver or cloud support has been implemented. Read [database decision](../docs/DATABASE_DECISION.md) for managed PostgreSQL trade-offs and the future reviewed migration/checkpointer work. Do not add a generic multi-database abstraction for an unrequested hosted deployment.
