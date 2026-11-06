import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT / ".env"
_FILE_AT_START = dotenv_values(ENV_FILE)
load_dotenv(ENV_FILE)


def live_setting(name: str, default: str = "") -> str:
    """Reads .env each time, so a key pasted there works without restarting the app.

    A value set in the shell, or by a test, still wins over the file.
    """
    current = os.environ.get(name)
    if current is not None and current != _FILE_AT_START.get(name):
        return current.strip()
    fresh = dotenv_values(ENV_FILE).get(name)
    return (fresh if fresh is not None else current or default).strip()


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
    return live_setting("LLM_PROVIDER", "none").lower()


def llm_model() -> str:
    return live_setting("LLM_MODEL")


def worker_enabled() -> bool:
    return os.getenv("WORKER_ENABLED", "1") == "1"
