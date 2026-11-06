"""Shared test world: an isolated database with reviewed synthetic reference data."""

import json
from datetime import date, timedelta
from pathlib import Path

from app.agent.worker import process_pending_work
from app.ai.providers import ProviderError, Reply

PASSWORD = "synthetic-demo-pass"
DOCUMENTS = Path(__file__).resolve().parents[2] / "fixtures" / "documents"


class World:
    def __init__(self, client):
        self.client = client
        self._tokens: dict[str, str] = {}

    def headers(self, user_id: str) -> dict[str, str]:
        if user_id not in self._tokens:
            response = self.client.post(
                "/api/sessions", json={"user_id": user_id, "password": PASSWORD}
            )
            assert response.status_code == 200, response.text
            self._tokens[user_id] = response.json()["access_token"]
        return {"Authorization": f"Bearer {self._tokens[user_id]}"}

    def get(self, user_id: str, path: str, **kwargs):
        return self.client.get("/api" + path, headers=self.headers(user_id), **kwargs)

    def post(self, user_id: str, path: str, json_body=None, **kwargs):
        return self.client.post(
            "/api" + path, headers=self.headers(user_id), json=json_body, **kwargs
        )

    def put(self, user_id: str, path: str, json_body=None):
        return self.client.put("/api" + path, headers=self.headers(user_id), json=json_body)

    def create_hire(self, **overrides) -> dict:
        response = self.post("U_HR", "/hires", hire_body(**overrides))
        assert response.status_code == 201, response.text
        return response.json()

    def plan(self, user_id: str, hire_id: str) -> dict:
        response = self.get(user_id, f"/hires/{hire_id}/plan")
        assert response.status_code == 200, response.text
        return response.json()

    def task(self, hire_id: str, key_title: str, user_id: str = "U_HR") -> dict:
        return next(t for t in self.plan(user_id, hire_id)["tasks"] if key_title in t["title"])

    def complete(self, user_id: str, hire_id: str, title: str):
        task = self.task(hire_id, title)
        return self.post(
            user_id, f"/tasks/{task['id']}/complete", {"expected_version": task["version"]}
        )

    def upload(
        self,
        user_id: str,
        hire_id: str,
        category: str,
        filename: str,
        content: bytes,
    ):
        return self.client.post(
            f"/api/hires/{hire_id}/documents",
            headers=self.headers(user_id),
            data={"category": category},
            files={"file": (filename, content)},
        )

    def upload_fixture(self, user_id: str, hire_id: str, category: str, name: str):
        return self.upload(user_id, hire_id, category, name, (DOCUMENTS / name).read_bytes())

    def review(self, document: dict, decision: str = "VERIFY", reason: str = "", user="U_HR"):
        return self.post(
            user,
            f"/documents/{document['id']}/reviews",
            {"decision": decision, "reason": reason, "expected_version": document["version"]},
        )

    def source(self, user_id: str, category: str, source_id: str) -> dict:
        items = self.get(user_id, "/sources", params={"category": category}).json()["items"]
        return next(item for item in items if item["id"] == source_id)

    def work(self) -> int:
        return process_pending_work()


def hire_body(**overrides) -> dict:
    body = {
        "display_name": "Priya Sharma",
        "worker_type": "employee",
        "role": "engineer",
        "location_id": "HYD-DEMO",
        "work_mode": "office",
        "start_date": (date.today() + timedelta(days=14)).isoformat(),
        "manager_user_id": "U_MANAGER",
        "employee_user_id": "U_PRIYA",
        "department_id": "DEP_ENG",
        "designation": "Software Engineer",
        "work_email": "priya@northstar.example",
    }
    body.update(overrides)
    return body


class Scripted:
    """A provider that returns exactly what a test specifies. Stub transport, not model quality."""

    name = "scripted"
    model = "scripted-test"
    is_stub = False
    is_local = True

    def __init__(self, *replies, local: bool = True):
        self.replies = list(replies)
        self.calls: list[dict] = []
        self.is_local = local

    def generate(self, operation, messages, schema, timeout, max_tokens):
        self.calls.append({"operation": operation, "messages": messages})
        reply = self.replies.pop(0) if self.replies else ProviderError("NO_SCRIPT")
        if isinstance(reply, Exception):
            raise reply
        return Reply(text=reply if isinstance(reply, str) else json.dumps(reply), input_tokens=5)
