"""LLM_PROVIDER=stub: deterministic offline rules that speak the model protocol.

This is NOT artificial intelligence, and every response made with it is labelled as a stub in the
API and UI. It exists so the full journey and the harness can be exercised on a machine with no
model, and it doubles as the rules-only baseline in evaluation. Never present its output as a
model result.
"""

import json
import re


class StubProvider:
    name = "stub"
    model = "stub-rules-not-ai"
    is_stub = True
    is_local = True

    def generate(self, operation, messages, schema, timeout, max_tokens):
        from app.ai.providers import Reply

        text = messages[-1]["content"]
        handler = {
            "assistant.answer": _assistant,
            "document.extract": _extract,
            "insights.summarize": _insights,
            "agent.next_step": _next_step,
        }[operation]
        return Reply(text=json.dumps(handler(text)))


def _first_sentence(text: str) -> str:
    match = re.search(r"^(.{20,380}?[.!?])(\s|$)", text.strip(), flags=re.S)
    return (match.group(1) if match else text.strip()[:380]).strip()


def _assistant(text: str) -> dict:
    passages = re.findall(r'<passage id="([^"]+)">\s*(.*?)\s*</passage>', text, flags=re.S)
    if not passages:
        return {"status": "NOT_FOUND", "claims": [], "uncertainty": "", "suggest_escalation": True}
    chunk_id, body = passages[0]
    sentence = _first_sentence(body)
    return {
        "status": "ANSWERED",
        "claims": [{"text": sentence, "citations": [{"chunk_id": chunk_id, "quote": sentence}]}],
        "uncertainty": "Offline rules quoted the best matching passage without interpreting it.",
        "suggest_escalation": False,
    }


_LABELS = {
    "employee_name": r"(?:employee name|name)\s*[:\-]\s*(.+)",
    "work_location": r"(?:work location|place of posting|location)\s*[:\-]\s*(.+)",
    "joining_date": r"(?:joining date|date of joining|start date)\s*[:\-]\s*(.+)",
    "designation": r"(?:designation|position|role)\s*[:\-]\s*(.+)",
}


def _extract(text: str) -> dict:
    body = re.search(r"<document>\s*(.*?)\s*</document>", text, flags=re.S)
    document = body.group(1) if body else ""
    fields, missing = [], []
    for name, pattern in _LABELS.items():
        match = re.search(pattern, document, flags=re.I)
        if match:
            fields.append(
                {
                    "name": name,
                    "value": match.group(1).strip()[:200],
                    "quote": match.group(0).strip()[:300],
                }
            )
        else:
            missing.append(name)
    category = re.search(r"Uploaded category: (\w+)", text)
    return {
        "suggested_category": category.group(1) if category else "signed_employment",
        "fields": fields,
        "missing": missing,
        "summary": f"Offline rules found {len(fields)} labelled fields.",
    }


def _insights(text: str) -> dict:
    body = re.search(r"<metrics>\s*(.*?)\s*</metrics>", text, flags=re.S)
    metrics = json.loads(body.group(1)) if body else []
    active = [metric for metric in metrics if metric["value"] > 0]
    return {
        "summary": "; ".join(f"{m['label']}: {m['value']}" for m in active)[:800]
        or "No open bottlenecks were found.",
        "recommendations": [
            {
                "text": f"Review: {metric['label']}.",
                "evidence_refs": [item["ref"] for item in metric["evidence"]][:6],
            }
            for metric in active
            if metric["evidence"]
        ][:5],
    }


def _next_step(text: str) -> dict:
    body = re.search(r"<steps>\s*(.*?)\s*</steps>", text, flags=re.S)
    steps = json.loads(body.group(1)) if body else []
    reads = [step.get("tool") for step in steps if step["kind"] == "read"]
    decided_count = sum(1 for step in steps if step["kind"] == "proposal" and step["decision"])
    wanted = {"get_document_evidence": 1, "get_equipment_status": 1 + decided_count}
    for tool, count in wanted.items():
        if reads.count(tool) < count:
            return {
                "next_step": {
                    "step": "read",
                    "tool": tool,
                    "reason_summary": f"Offline rules read {tool}.",
                }
            }
    if any(step["kind"] == "rejected_proposal" for step in steps):
        return {
            "next_step": {
                "step": "escalate",
                "reason_summary": "The server rejected a proposal, so a person should look.",
                "evidence_ids": [],
            }
        }
    facts: dict = {}
    evidence: list[str] = []
    for step in steps:
        if step["kind"] == "read":
            facts.update(step.get("facts", {}))
            evidence += [item["id"] for item in step.get("evidence", [])]
    decided = [step for step in steps if step["kind"] == "proposal"]
    conflict = facts.get("document_location") and facts.get("document_location") != facts.get(
        "profile_location"
    )
    answers = [step for step in steps if step["kind"] == "answer"]
    if conflict and not any(step.get("action_type") == "CHANGE_WORK_LOCATION" for step in decided):
        if not answers:
            return {
                "next_step": {
                    "step": "ask",
                    "question": (
                        f"The profile says {facts['profile_location']} but the signed document "
                        f"says {facts['document_location']}. Which location is correct?"
                    ),
                    "recipient_role": "HR",
                    "evidence_ids": evidence[:4],
                }
            }
        return {
            "next_step": {
                "step": "propose",
                "payload": {
                    "action_type": "CHANGE_WORK_LOCATION",
                    "location_id": facts["document_location"],
                },
                "evidence_ids": evidence[:4] or ["none"],
                "reason_summary": "The reviewer confirmed the document location.",
            }
        }
    device = facts.get("available_device_record_id")
    if device and not any(step.get("action_type") == "RESERVE_EQUIPMENT" for step in decided):
        return {
            "next_step": {
                "step": "propose",
                "payload": {"action_type": "RESERVE_EQUIPMENT", "equipment_record_id": device},
                "evidence_ids": evidence[:4] or ["none"],
                "reason_summary": "A compatible device is free at the approved location.",
            }
        }
    return {
        "next_step": {
            "step": "finish",
            "reason_summary": "Offline rules found nothing further to do.",
            "evidence_ids": evidence[:4],
        }
    }
