import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")


def database_path() -> Path:
    value = Path(os.getenv("DATABASE_PATH", ".runtime/dayone.db"))
    return value if value.is_absolute() else ROOT / value


def documents_path() -> Path:
    """Private files sit beside the database, never under a served static folder."""
    return database_path().parent / "documents"


def int_setting(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def llm_provider() -> str:
    """none (AI off), stub (labelled offline rules), ollama (local) or hosted."""
    return os.getenv("LLM_PROVIDER", "none").strip().lower()


def llm_model() -> str:
    return os.getenv("LLM_MODEL", "").strip()


def worker_enabled() -> bool:
    return os.getenv("WORKER_ENABLED", "1") == "1"
