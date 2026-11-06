-- Schema v1: Track 1 owns migrations. Never delete/reseed an existing user database.
CREATE TABLE IF NOT EXISTS app_info (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    project_name TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version = 1)
);
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('HR','IT','PAYROLL','BENEFITS','TRAINING','MANAGER','EMPLOYEE')),
    password_hash TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1))
);
CREATE TABLE IF NOT EXISTS hires (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    worker_type TEXT NOT NULL CHECK (worker_type IN ('employee','contractor')),
    role TEXT NOT NULL CHECK (role IN ('engineer','operations_associate')),
    location_id TEXT NOT NULL CHECK (location_id IN ('HYD-DEMO','BLR-DEMO')),
    work_mode TEXT NOT NULL CHECK (work_mode IN ('office','remote')),
    start_date TEXT NOT NULL,
    manager_user_id TEXT NOT NULL REFERENCES users(id),
    employee_user_id TEXT UNIQUE REFERENCES users(id),
    profile_version INTEGER NOT NULL DEFAULT 1 CHECK (profile_version > 0),
    plan_version INTEGER NOT NULL DEFAULT 1 CHECK (plan_version > 0)
);
CREATE TABLE IF NOT EXISTS user_scopes (
    user_id TEXT NOT NULL REFERENCES users(id),
    hire_id TEXT NOT NULL REFERENCES hires(id),
    PRIMARY KEY (user_id, hire_id)
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS policies (
    id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    approved_by TEXT NOT NULL REFERENCES users(id),
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    scope_json TEXT NOT NULL CHECK (json_valid(scope_json)),
    sections_json TEXT NOT NULL CHECK (json_valid(sections_json)),
    rules_json TEXT NOT NULL CHECK (json_valid(rules_json)),
    PRIMARY KEY (id, version)
);
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    hire_id TEXT NOT NULL REFERENCES hires(id),
    logical_key TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('documents','equipment','payroll','benefits','training','manager')),
    title TEXT NOT NULL,
    owner_user_id TEXT NOT NULL REFERENCES users(id),
    policy_id TEXT NOT NULL,
    policy_version INTEGER NOT NULL,
    rule_id TEXT NOT NULL,
    due_date TEXT NOT NULL,
    critical INTEGER NOT NULL CHECK (critical IN (0,1)),
    work_state TEXT NOT NULL CHECK (work_state IN ('PENDING','WAITING_DEPENDENCY','IN_PROGRESS','COMPLETED','CANCELLED')),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    UNIQUE (hire_id, logical_key),
    FOREIGN KEY (policy_id, policy_version) REFERENCES policies(id, version)
);
CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id TEXT NOT NULL REFERENCES tasks(id),
    prerequisite_task_id TEXT NOT NULL REFERENCES tasks(id),
    PRIMARY KEY (task_id, prerequisite_task_id),
    CHECK (task_id != prerequisite_task_id)
);
CREATE TABLE IF NOT EXISTS source_records (
    id TEXT PRIMARY KEY,
    hire_id TEXT REFERENCES hires(id),
    category TEXT NOT NULL CHECK (category IN ('documents','equipment','payroll','benefits','training','manager')),
    source_system TEXT NOT NULL,
    external_id TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    payload_json TEXT NOT NULL CHECK (json_valid(payload_json)),
    observed_at TEXT NOT NULL,
    updated_by TEXT NOT NULL REFERENCES users(id),
    UNIQUE (source_system, external_id)
);
CREATE TABLE IF NOT EXISTS cases (
    id TEXT PRIMARY KEY,
    hire_id TEXT NOT NULL REFERENCES hires(id),
    opened_by TEXT NOT NULL REFERENCES users(id),
    message TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('OPEN','INVESTIGATING','WAITING_HUMAN','WAITING_APPROVAL','EXECUTING','RESOLVED','ESCALATED')),
    thread_id TEXT NOT NULL UNIQUE,
    model_calls INTEGER NOT NULL DEFAULT 0 CHECK (model_calls >= 0),
    tool_calls INTEGER NOT NULL DEFAULT 0 CHECK (tool_calls >= 0),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_case_per_hire ON cases(hire_id)
    WHERE state NOT IN ('RESOLVED','ESCALATED');
CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    hire_id TEXT NOT NULL REFERENCES hires(id),
    case_id TEXT REFERENCES cases(id),
    check_type TEXT NOT NULL,
    source_record_id TEXT REFERENCES source_records(id),
    source_version INTEGER,
    profile_version INTEGER NOT NULL,
    policy_id TEXT NOT NULL,
    policy_version INTEGER NOT NULL,
    result TEXT NOT NULL CHECK (result IN ('VERIFIED','BLOCKED','UNKNOWN','NOT_APPLICABLE')),
    reason_code TEXT NOT NULL,
    observed_json TEXT NOT NULL CHECK (json_valid(observed_json)),
    checked_at TEXT NOT NULL,
    expires_at TEXT,
    FOREIGN KEY (policy_id, policy_version) REFERENCES policies(id, version)
);
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES cases(id),
    dedupe_key TEXT NOT NULL,
    recipient_user_id TEXT NOT NULL REFERENCES users(id),
    text TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('PENDING','ANSWERED','CANCELLED')),
    answer TEXT,
    answered_by TEXT REFERENCES users(id),
    answered_at TEXT,
    UNIQUE (case_id, dedupe_key)
);
CREATE TABLE IF NOT EXISTS proposals (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES cases(id),
    action_type TEXT NOT NULL CHECK (action_type IN ('CHANGE_WORK_LOCATION','RESERVE_EQUIPMENT')),
    payload_json TEXT NOT NULL CHECK (json_valid(payload_json)),
    evidence_ids_json TEXT NOT NULL CHECK (json_valid(evidence_ids_json)),
    expected_versions_json TEXT NOT NULL CHECK (json_valid(expected_versions_json)),
    plan_diff_json TEXT CHECK (plan_diff_json IS NULL OR json_valid(plan_diff_json)),
    reviewer_role TEXT NOT NULL CHECK (reviewer_role IN ('HR','IT')),
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decisions (
    proposal_id TEXT PRIMARY KEY REFERENCES proposals(id),
    reviewer_user_id TEXT NOT NULL REFERENCES users(id),
    decision TEXT NOT NULL CHECK (decision IN ('APPROVE','REJECT')),
    note TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS actions (
    id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL UNIQUE REFERENCES proposals(id),
    state TEXT NOT NULL CHECK (state IN ('PENDING','RUNNING','SUCCEEDED','FAILED','UNKNOWN')),
    observed_json TEXT NOT NULL CHECK (json_valid(observed_json)),
    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS work_items (
    id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    case_id TEXT NOT NULL REFERENCES cases(id),
    kind TEXT NOT NULL CHECK (kind IN ('INVESTIGATE','RESUME','EXECUTE')),
    state TEXT NOT NULL CHECK (state IN ('PENDING','RUNNING','DONE','FAILED')),
    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    retry_at TEXT,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    hire_id TEXT NOT NULL REFERENCES hires(id),
    case_id TEXT REFERENCES cases(id),
    actor_user_id TEXT REFERENCES users(id),
    action_id TEXT REFERENCES actions(id),
    event_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TEXT NOT NULL
);
