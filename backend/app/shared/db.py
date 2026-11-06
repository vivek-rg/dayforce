import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.shared.config import database_path


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


def initialize(path: Path | None = None) -> None:
    target = path or database_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with connect(target) as connection:
        connection.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))
        connection.execute(
            "INSERT OR IGNORE INTO app_info (id, project_name, schema_version) VALUES (1, ?, 1)",
            ("DayOne Proof",),
        )
