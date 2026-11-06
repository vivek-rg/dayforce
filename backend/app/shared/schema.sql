-- Schema v2: Track 1 owns migrations. Never delete/reseed an existing user database.
CREATE TABLE IF NOT EXISTS app_info (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    project_name TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version = 2)
);
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    email TEXT,
    role TEXT NOT NULL CHECK (role IN ('HR','IT','PAYROLL','BENEFITS','TRAINING','MANAGER','EMPLOYEE')),
    password_hash TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1))
);
CREATE INDEX IF NOT EXISTS users_by_role ON users(role);
CREATE TABLE IF NOT EXISTS login_attempts (
    user_id TEXT PRIMARY KEY,
    failures INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT
);
CREATE TABLE IF NOT EXISTS departments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS hires (
    id TEXT PRIMARY KEY,
    employee_code TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    worker_type TEXT NOT NULL CHECK (worker_type IN ('employee','contractor')),
    role TEXT NOT NULL CHECK (role IN ('engineer','operations_associate','sales_associate')),
    location_id TEXT NOT NULL CHECK (location_id IN ('HYD-DEMO','BLR-DEMO')),
    work_mode TEXT NOT NULL CHECK (work_mode IN ('office','remote')),
    start_date TEXT NOT NULL,
    manager_user_id TEXT NOT NULL REFERENCES users(id),
    employee_user_id TEXT UNIQUE REFERENCES users(id),
    department_id TEXT NOT NULL REFERENCES departments(id),
    designation TEXT NOT NULL,
    work_email TEXT NOT NULL,
    personal_email TEXT,
    phone TEXT,
    employment_status TEXT NOT NULL DEFAULT 'PRE_JOINING' CHECK (employment_status IN ('PRE_JOINING','ACTIVE','WITHDRAWN')),
    created_at TEXT NOT NULL,
    completed_at TEXT,
    profile_version INTEGER NOT NULL DEFAULT 1 CHECK (profile_version > 0),
    plan_version INTEGER NOT NULL DEFAULT 1 CHECK (plan_version > 0)
);
CREATE INDEX IF NOT EXISTS hires_by_start ON hires(start_date);
CREATE INDEX IF NOT EXISTS hires_by_manager ON hires(manager_user_id);
CREATE TABLE IF NOT EXISTS user_scopes (
    user_id TEXT NOT NULL REFERENCES users(id),
    hire_id TEXT NOT NULL REFERENCES hires(id),
    PRIMARY KEY (user_id, hire_id)
);
CREATE INDEX IF NOT EXISTS scopes_by_hire ON user_scopes(hire_id);
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
    category TEXT NOT NULL CHECK (category IN ('documents','equipment','it_access','payroll','benefits','training','manager')),
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    owner_user_id TEXT NOT NULL REFERENCES users(id),
    policy_id TEXT NOT NULL,
    policy_version INTEGER NOT NULL,
    rule_id TEXT NOT NULL,
    check_type TEXT,
    due_date TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'MEDIUM' CHECK (priority IN ('LOW','MEDIUM','HIGH')),
    critical INTEGER NOT NULL CHECK (critical IN (0,1)),
    work_state TEXT NOT NULL CHECK (work_state IN ('PENDING','WAITING_DEPENDENCY','IN_PROGRESS','COMPLETED','CANCELLED')),
    completed_at TEXT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    UNIQUE (hire_id, logical_key),
    FOREIGN KEY (policy_id, policy_version) REFERENCES policies(id, version)
);
CREATE INDEX IF NOT EXISTS tasks_by_owner ON tasks(owner_user_id, work_state);
CREATE INDEX IF NOT EXISTS tasks_by_state_due ON tasks(work_state, due_date);
CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id TEXT NOT NULL REFERENCES tasks(id),
    prerequisite_task_id TEXT NOT NULL REFERENCES tasks(id),
    PRIMARY KEY (task_id, prerequisite_task_id),
    CHECK (task_id != prerequisite_task_id)
);
CREATE TABLE IF NOT EXISTS source_records (
    id TEXT PRIMARY KEY,
    hire_id TEXT REFERENCES hires(id),
    category TEXT NOT NULL CHECK (category IN ('documents','equipment','it_access','payroll','benefits','training','manager')),
    source_system TEXT NOT NULL,
    external_id TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    payload_json TEXT NOT NULL CHECK (json_valid(payload_json)),
    observed_at TEXT NOT NULL,
    updated_by TEXT NOT NULL REFERENCES users(id),
    UNIQUE (source_system, external_id)
);
CREATE INDEX IF NOT EXISTS sources_by_hire ON source_records(hire_id, category);
CREATE TABLE IF NOT EXISTS cases (
    id TEXT PRIMARY KEY,
    hire_id TEXT NOT NULL REFERENCES hires(id),
    opened_by TEXT NOT NULL REFERENCES users(id),
    message TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('OPEN','INVESTIGATING','WAITING_HUMAN','WAITING_APPROVAL','EXECUTING','RESOLVED','ESCALATED')),
    kind TEXT NOT NULL DEFAULT 'INVESTIGATION' CHECK (kind IN ('INVESTIGATION','MANUAL')),
    thread_id TEXT NOT NULL UNIQUE,
    model_calls INTEGER NOT NULL DEFAULT 0 CHECK (model_calls >= 0),
    tool_calls INTEGER NOT NULL DEFAULT 0 CHECK (tool_calls >= 0),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_case_per_hire ON cases(hire_id)
    WHERE state NOT IN ('RESOLVED','ESCALATED');
CREATE TABLE IF NOT EXISTS case_steps (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES cases(id),
    position INTEGER NOT NULL,
    kind TEXT NOT NULL,
    summary TEXT NOT NULL,
    observed_json TEXT NOT NULL CHECK (json_valid(observed_json)),
    created_at TEXT NOT NULL,
    UNIQUE (case_id, position)
);
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
CREATE INDEX IF NOT EXISTS evidence_by_hire ON evidence(hire_id, check_type, checked_at);
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
CREATE INDEX IF NOT EXISTS proposals_by_reviewer ON proposals(reviewer_role, expires_at);
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
    action_id TEXT REFERENCES actions(id),
    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    retry_at TEXT,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS work_by_state ON work_items(state, updated_at);
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
CREATE INDEX IF NOT EXISTS audit_by_hire ON audit_events(hire_id, created_at);
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    hire_id TEXT NOT NULL REFERENCES hires(id),
    category TEXT NOT NULL CHECK (category IN ('government_id','address_proof','education','previous_employment','bank_details','tax','signed_employment')),
    state TEXT NOT NULL CHECK (state IN ('SUBMITTED','UNDER_REVIEW','VERIFIED','REJECTED','RESUBMISSION_REQUESTED','SUPERSEDED')),
    storage_key TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK (size_bytes > 0),
    original_name TEXT NOT NULL,
    text_available INTEGER NOT NULL CHECK (text_available IN (0,1)),
    declared_location_id TEXT,
    uploaded_by TEXT NOT NULL REFERENCES users(id),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TEXT NOT NULL,
    UNIQUE (hire_id, category, sha256)
);
CREATE INDEX IF NOT EXISTS documents_by_hire ON documents(hire_id, category);
CREATE INDEX IF NOT EXISTS documents_by_state ON documents(state, created_at);
CREATE TABLE IF NOT EXISTS document_reviews (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id),
    reviewer_user_id TEXT NOT NULL REFERENCES users(id),
    decision TEXT NOT NULL CHECK (decision IN ('VERIFY','REJECT','REQUEST_RESUBMISSION')),
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS reviews_by_document ON document_reviews(document_id, created_at);
CREATE TABLE IF NOT EXISTS ai_runs (
    id TEXT PRIMARY KEY,
    operation TEXT NOT NULL,
    prompt_version INTEGER NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    user_id TEXT REFERENCES users(id),
    hire_id TEXT REFERENCES hires(id),
    case_id TEXT REFERENCES cases(id),
    chunk_ids_json TEXT NOT NULL CHECK (json_valid(chunk_ids_json)),
    status TEXT NOT NULL CHECK (status IN ('VALIDATED','ABSTAINED','REJECTED_OUTPUT','UNAVAILABLE')),
    validation_result TEXT NOT NULL,
    failure_reason TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    input_tokens INTEGER,
    output_tokens INTEGER,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    retrieval_ms INTEGER,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ai_runs_by_operation ON ai_runs(operation, created_at);
CREATE INDEX IF NOT EXISTS ai_runs_by_status ON ai_runs(status, created_at);
CREATE TABLE IF NOT EXISTS document_extractions (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id),
    ai_run_id TEXT NOT NULL REFERENCES ai_runs(id),
    suggested_category TEXT NOT NULL,
    fields_json TEXT NOT NULL CHECK (json_valid(fields_json)),
    missing_json TEXT NOT NULL CHECK (json_valid(missing_json)),
    mismatches_json TEXT NOT NULL CHECK (json_valid(mismatches_json)),
    summary TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS extractions_by_document ON document_extractions(document_id, created_at);
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    title TEXT NOT NULL,
    access_level TEXT NOT NULL CHECK (access_level IN ('GENERAL','MANAGER','IT','PAYROLL','BENEFITS','HR')),
    status TEXT NOT NULL CHECK (status IN ('DRAFT','APPROVED','RETIRED')),
    body TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    uploaded_by TEXT NOT NULL REFERENCES users(id),
    approved_by TEXT REFERENCES users(id),
    effective_from TEXT,
    created_at TEXT NOT NULL,
    PRIMARY KEY (id, version)
);
CREATE INDEX IF NOT EXISTS knowledge_by_status ON knowledge_documents(status, access_level);
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    document_version INTEGER NOT NULL,
    position INTEGER NOT NULL,
    section_ref TEXT NOT NULL,
    text TEXT NOT NULL,
    access_level TEXT NOT NULL,
    FOREIGN KEY (document_id, document_version) REFERENCES knowledge_documents(id, version)
);
CREATE INDEX IF NOT EXISTS chunks_by_document ON knowledge_chunks(document_id, document_version);
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_chunks_fts USING fts5(
    chunk_id UNINDEXED, section_ref, text, tokenize = 'porter unicode61'
);
CREATE TABLE IF NOT EXISTS hr_escalations (
    id TEXT PRIMARY KEY,
    raised_by TEXT NOT NULL REFERENCES users(id),
    ai_run_id TEXT REFERENCES ai_runs(id),
    question_text TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('OPEN','ANSWERED')),
    resolution TEXT,
    resolved_by TEXT REFERENCES users(id),
    created_at TEXT NOT NULL,
    resolved_at TEXT
);
CREATE INDEX IF NOT EXISTS escalations_by_state ON hr_escalations(state, created_at);
CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    hire_id TEXT REFERENCES hires(id),
    task_id TEXT REFERENCES tasks(id),
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    dedupe_key TEXT NOT NULL,
    read_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (user_id, dedupe_key)
);
CREATE INDEX IF NOT EXISTS notifications_by_user ON notifications(user_id, read_at, created_at);

-- Read models over source_records: one truth, the entity names people expect.
CREATE VIEW IF NOT EXISTS equipment_assets_v AS
    SELECT id, version, hire_id AS assigned_hire_id, observed_at,
           json_extract(payload_json, '$.asset_tag') AS asset_id,
           json_extract(payload_json, '$.asset_name') AS asset_name,
           json_extract(payload_json, '$.asset_type') AS asset_type,
           json_extract(payload_json, '$.serial_number') AS serial_number,
           json_extract(payload_json, '$.location_id') AS location_id,
           json_extract(payload_json, '$.state') AS state,
           json_extract(payload_json, '$.handover_at') AS handover_at
    FROM source_records WHERE category = 'equipment';
CREATE VIEW IF NOT EXISTS payroll_status_v AS
    SELECT id, version, hire_id, observed_at,
           json_extract(payload_json, '$.bank_submitted') AS bank_submitted,
           json_extract(payload_json, '$.tax_submitted') AS tax_submitted,
           json_extract(payload_json, '$.profile_created') AS profile_created,
           json_extract(payload_json, '$.setup_confirmed') AS setup_confirmed
    FROM source_records WHERE category = 'payroll';
CREATE VIEW IF NOT EXISTS benefits_enrolments_v AS
    SELECT id, version, hire_id, observed_at, json_extract(payload_json, '$.state') AS state
    FROM source_records WHERE category = 'benefits';
CREATE VIEW IF NOT EXISTS training_assignments_v AS
    SELECT id, version, hire_id, observed_at,
           json_extract(payload_json, '$.course_id') AS course_id,
           json_extract(payload_json, '$.state') AS state
    FROM source_records WHERE category = 'training';
