# Synthetic runtime fixtures — Track 4/P03, reviewed by Track 8

No business seed is implemented yet. Create `company.json`, `hires.json`, `sources.json` and `seed.py` only in P03. Name records with stable IDs, not scenario-name hints. Runtime input must never include expected_action/is_broken/should_escalate or evaluation answers.

Required fixture story: Northstar Demo; HYD-DEMO and BLR-DEMO; employee/contractor; engineer/operations_associate; six fictional hires; HR/IT/payroll/benefits/training/manager/employee identities; 10–12 reviewed task rules spanning all six categories. Policies are invented company process, not law. See docs/DATA_MODEL.md for pack/source shapes and docs/API_SPEC.md for enums and authority.

Priya's approved profile is Hyderabad, offer text says Bengaluru, task claims equipment complete, separate source only says reserved. Include one available compatible Bengaluru device and a normal operations hire. Preserve ambiguity: absence of handover is UNKNOWN, not automatic proof of non-delivery.

`node scripts/python.mjs fixtures/seed.py` must read DEMO_PASSWORD privately, hash it, populate a dedicated empty demo business database transactionally and refuse to overwrite existing data. Do not supply a destructive default reset. Seed inventory can have null hire_id; API writes cannot claim another hire's asset.

## Same starting story on eight laptops

Each member runs their own local database; do not commit or distribute `.runtime/dayone.db` or checkpoints. Git shares the reviewed fixture/schema version, not mutable data. P14 verifies equivalent fixture content on independent databases, repeat-seed refusal and rollback. The backend currently initializes an empty schema only; `seed.py` is still future P03 work, so do not run a nonexistent command expecting business data. See [team database commands and backups](../docs/TEAM_WORKFLOW.md#how-sqlite-works-for-eight-people). Use the same DATABASE_PATH in the app and seed terminal. New practice runs use a new DB/checkpoint path pair, never an automatic delete/reset.

This remains the chosen setup after the user's database review: same seed revision/commands on eight local SQLite files, no shared live database or cloud account. See [database decision](../docs/DATABASE_DECISION.md). Unlike the intentionally versioned synthetic fixture inputs or reviewed submission assets, database files remain ignored.

## What is here now

- `policy_pack.json`: the fictional approved rule pack that generates every plan.
- `knowledge/`: fictional policies, approved at seed time, with access levels set in `seed.py`.
- `documents/`: synthetic sample uploads, including one prompt-injection sample.
- `seed.py`: creates users, inventory, knowledge and three in-progress hires. It refuses a database that already has data. Priya's account stays free so that HR can create her in the demo.
