"""Deterministic test environment: no worker thread, no model, isolated files."""

import os

os.environ["WORKER_ENABLED"] = "0"
os.environ["LLM_PROVIDER"] = "none"
os.environ["LLM_API_KEY"] = ""

import pytest  # noqa: E402
from app.ai.providers import set_provider_for_tests  # noqa: E402
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from fixtures.seed import seed  # noqa: E402

from .helpers import PASSWORD, World  # noqa: E402


@pytest.fixture
def world(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    with TestClient(app, raise_server_exceptions=False) as client:
        seed(PASSWORD, demo_hires=False)
        yield World(client)
    set_provider_for_tests(None)
