# Database decision — easy setup first, honest cloud roadmap

## Confirmed choice

The user selected **a local recorded demo**, not one shared online application, and wants the easiest setup for eight teammates. **Keep the existing SQLite foundation for this submission.** A cloud database can be configured later if requirements change; no cloud account or driver switch is needed now.

This is the fastest choice for **this codebase and deadline**, not a claim that SQLite is best for every company. The current repository already uses Python's standard-library `sqlite3`, SQLite SQL constraints and isolated SQLite tests. Business implementation is still pending. Replacing the database now would add work before the onboarding journey exists.

## Quick comparison for this project

| Choice | What teammates must set up | Fit for our current local demo | When it becomes useful |
|---|---|---|---|
| SQLite | Nothing beyond the existing app install; a private local file is created automatically | **Recommended now.** No credentials, service provisioning or network dependency; existing code/tests already work | One local backend/worker, small synthetic data, reproducible individual development |
| Neon PostgreSQL | Cloud project, private connection URL, database driver, SSL/pool configuration, reviewed SQL/test changes | More setup/change than retaining the current foundation. A focused managed-PostgreSQL option if only a shared SQL database is needed | Shared online state or hosted pilot after scope/security/concurrency review |
| Supabase PostgreSQL | Cloud project and DB connection plus the same PostgreSQL application changes; extra auth/storage setup only if intentionally adopted | Useful platform, but its extra services are not currently required. A project/key does not automatically replace our FastAPI permissions or sessions | Shared PostgreSQL plus an actual requirement for the platform's other services |
| MongoDB | Managed/local deployment, credentials/driver and document-model/query/transaction/test redesign | **Not recommended for this deadline.** Hires, scopes, tasks, evidence, decisions and actions are strongly related | Only if a later measured requirement justifies document-first storage and the redesign |

Neon and Supabase are service options for PostgreSQL, not engines that remove migration work. PostgreSQL and MongoDB also need controlled data/schema evolution, access management, backups and tests. No free-plan size/availability/backup guarantee is promised here; check the actual provider account and current terms before adopting cloud infrastructure.

## The same easy setup for eight people

1. Everyone clones the reviewed commit and follows the same root README install commands.
2. Everyone makes their own `.env` from `.env.example` once. Keep `DATABASE_PATH=.runtime/dayone.db` unless they need a separate practice path.
3. `npm run dev` creates that clone's folder/schema plus one project-name row. No database server/account/key is required.
4. Everyone runs `npm run check`, then the HTTP smoke in a second terminal. Tests use isolated temporary databases.
5. After P03/P14 is implemented, everyone uses the **same reviewed synthetic fixtures and safe seed command** on an empty business DB. That gives the same starting story, not permanently synchronized mutable records.
6. Track 1 owns canonical schema/migrations. Feature owners must not each add incompatible columns; P26 tests upgrades and preservation before anyone applies a schema change.
7. Keep a single backend/worker per local application DB, transactions short and files on local disk. Do not share a live SQLite file through Git, Drive, OneDrive or a network mount.

**Working today:** initialization, health/bootstrap and the connectivity screen. **Not working yet:** business seed, login, agent/checkpoint behavior, approvals, a migration runner or provider selector. Do not confuse an existing table or future `.env` placeholder with an implemented feature.

Commands, independent paths and stopped backup instructions are in [TEAM_WORKFLOW.md](TEAM_WORKFLOW.md). Current exact tables/invariants are in [DATA_MODEL.md](DATA_MODEL.md). Cloud selection is not needed to make these commands the same on all eight laptops.

## What SQLite does and does not solve

- It avoids a cloud service dependency for this local submission; it does **not** remove schema migration requirements.
- It allows multiple readers and serializes writes. Eight developers with eight independent databases are different from eight deployed app instances sharing one database.
- Lock contention still needs short transactions, bounded waits and conditional writes. No transaction may stay open across model/network/human waits.
- Current `CREATE TABLE IF NOT EXISTS` creates missing tables, not upgrades existing columns. P26 must add a reviewed migration/version strategy when the schema changes. Never delete a working DB as the normal “migration.”
- SQLite is not inherently unprofessional, and a cloud brand is not proof of correctness. Choose based on workload, operating model and measured results.

## If shared online state becomes necessary

Use P27 to approve the changed requirement and exact implementation boundary. A sensible first candidate is **managed PostgreSQL**, with Neon if the need is only a focused hosted DB, or Supabase if its additional services are genuinely required/team-familiar. Do not require both or introduce a second database just for a pitch.

Before claiming a working migration:

- Agree one owner-controlled integration/demo environment and isolated per-developer/test databases or branches. Do not let all developers experiment destructively against one shared schema/data set.
- Choose an installed/approved PostgreSQL driver and server-only connection configuration. Never expose privileged DB URLs/service keys in React, Git, logs or screenshots; validate TLS and least-privilege roles.
- Port SQLite-specific SQL, JSON/boolean/date handling, placeholders, connection/transaction behavior, constraints and schema version checks. Python `sqlite3.Connection` seams and SQLite tests do not become PostgreSQL-compatible by changing a URL.
- Preserve current API contracts or review/regenerate intentional revisions. Seed only synthetic environments; verify foreign keys, unique events and conditional updates under real concurrent requests.
- Decide graph checkpoint storage separately. The current SQLite checkpointer plan cannot be silently treated as a cloud PostgreSQL checkpointer; approve dependency/config changes if moving it too.
- Apply reviewed numbered migrations; back up and test restoration/data transfer, version preservation, counts/relationships and rollback before switching the demo. “No business rows yet” may simplify the transfer but does not erase the SQL/driver work.
- Run authorization/scope, exact approval, stale/inventory race, duplicate/restart and real end-to-end checks on the selected engine. Test timeouts/outages, connection limits and selected service behavior. A local model plus a cloud DB is not a fully on-device system.

No cloud account, migration, connection URL, benchmark or production guarantee is created by this document.

## Accurate pitch wording

> “Our local prototype uses SQLite so each teammate can reproduce it without a database service. Approved rules, independent evidence and conditional transactions form the safety design. For a shared hosted deployment we would evaluate managed PostgreSQL, with reviewed migrations and concurrency/security checks. That cloud migration has not been implemented.”

Only describe planned controls as implemented once their phases and tests actually pass. Do not claim “industry standard,” “optimized,” “100% verified” or “production ready” as a substitute for measured evidence.
