"""Container entrypoint: seed demo data once on an empty database, then serve the built app.

Seeding is skipped whenever any user exists, so redeploys never touch existing data.
"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.shared.config import database_path  # noqa: E402


def has_users() -> bool:
    path = database_path()
    if not path.exists():
        return False
    connection = sqlite3.connect(path)
    try:
        return connection.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None
    except sqlite3.OperationalError:
        return False
    finally:
        connection.close()


if __name__ == "__main__":
    database_path().parent.mkdir(parents=True, exist_ok=True)
    if not has_users():
        subprocess.run([sys.executable, str(ROOT / "fixtures" / "seed.py")], cwd=ROOT, check=True)
    port = os.getenv("PORT", "8000")
    os.execv(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--app-dir",
            "backend",
            "--host",
            "0.0.0.0",
            "--port",
            port,
        ],
    )
