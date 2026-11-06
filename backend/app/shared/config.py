import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")


def database_path() -> Path:
    value = Path(os.getenv("DATABASE_PATH", ".runtime/dayone.db"))
    return value if value.is_absolute() else ROOT / value
