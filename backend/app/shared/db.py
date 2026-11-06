import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.shared.config import database_path

SCHEMA_VERSION = 2
PROJECT_NAME = "OnboardIQ"
V1_TABLES = (
    "audit_events",
    "work_items",
    "actions",
    "decisions",
    "proposals",
    "questions",
    "evidence",
    "cases",
    "source_records",
    "task_dependencies",
    "tasks",
    "policies",
    "sessions",
    "user_scopes",
    "hires",
    "users",
    "app_info",
)
BUSINESS_TABLES = ("users", "hires", "policies", "tasks", "source_records", "cases")


@contextmanager
def connect(path: Path | None = None):
    connection = sqlite3.connect(path or database_path(), timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def _migrate_v1(connection: sqlite3.Connection) -> None:
    """v1 only ever held the foundation row, so an empty v1 file can be rebuilt safely."""
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='app_info'"
    ).fetchone()
    if row is None:
        return
    version = connection.execute("SELECT schema_version FROM app_info WHERE id=1").fetchone()
    if version is None or version["schema_version"] != 1:
        return
    for table in BUSINESS_TABLES:
        if connection.execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone():
            raise sqlite3.DatabaseError(
                "This schema v1 database holds business rows; refusing an automatic rebuild."
            )
    for table in V1_TABLES:
        connection.execute(f"DROP TABLE IF EXISTS {table}")


def initialize(path: Path | None = None) -> None:
    target = path or database_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with connect(target) as connection:
        _migrate_v1(connection)
        connection.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(users)")}
        if "email" not in columns:
            connection.execute("ALTER TABLE users ADD COLUMN email TEXT")
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS users_by_email ON users(email COLLATE NOCASE)"
        )
        connection.execute(
            "INSERT OR IGNORE INTO app_info (id, project_name, schema_version) VALUES (1, ?, ?)",
            (PROJECT_NAME, SCHEMA_VERSION),
        )
