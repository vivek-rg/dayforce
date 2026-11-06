"""Generate the shared reference from real request/response schemas, without starting the app."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app  # noqa: E402
from app.shared.contracts import (  # noqa: E402
    ActionResult,
    InvestigationContext,
    NextStep,
    ToolObservation,
)

ACCESS = {
    "create_session": "Public local login; verify seeded credentials. Rate-limit failed attempts.",
    "delete_session": "Authenticated token owner; revoke only current session.",
    "me": "Authenticated current user only.",
    "list_hires": "Authenticated; return only persisted hire scopes, including HR.",
    "create_hire": "HR only. Grant creating HR scope in the same transaction; validate manager.",
    "get_hire": "Authenticated hire scope. Filter fields by role.",
    "get_plan": "Authenticated hire scope. Field-filter evidence, not just the hire profile.",
    "my_work": "Authenticated owner; tasks must also belong to authorized hires.",
    "complete_task": "Current task owner + hire scope; compare expected_version and prerequisites.",
    "run_checks": "HR/IT/PAYROLL/BENEFITS/TRAINING/MANAGER in hire scope; category-filter checks.",
    "write_source": "Category authority + hire scope; never accept actor/time from client.",
    "create_case": "Hire scope; employee limited to own hire. Queue scoped investigation.",
    "get_case": "Case hire scope; sanitize questions, evidence, proposals and timeline.",
    "answer_question": "Exact active recipient user + case hire scope; no role-only override.",
    "get_work_item": "Authenticated linked case/hire scope.",
    "review_inbox": "HR/IT with matching proposal reviewer_role and hire scope.",
    "preview": "HR + hire scope; body case belongs to hire. No official profile mutation.",
    "decide": "Exact reviewer role + hire scope, current inputs, expiry and prerequisites.",
    "health": "Public minimal local health; no private records, keys, paths or model calls.",
    "bootstrap": "Public foundation message only; no hire or identity data.",
}


def resolve(schema, document):
    if "$ref" in schema:
        target = document
        for part in schema["$ref"][2:].split("/"):
            target = target[part]
        return target
    return schema


def example(schema, document):
    schema = resolve(schema, document)
    if "default" in schema:
        return schema["default"]
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][0]
    variants = schema.get("anyOf", schema.get("oneOf"))
    if variants:
        return example(variants[0], document)
    kind = schema.get("type")
    if kind == "object" or "properties" in schema:
        return {
            name: example(value, document) for name, value in schema.get("properties", {}).items()
        }
    if kind == "array":
        return [example(schema["items"], document)]
    if kind in ("number", "integer"):
        return schema.get("minimum", 1)
    if kind == "boolean":
        return True
    if kind == "null":
        return None
    if schema.get("format") == "date":
        return "2026-11-16"
    if schema.get("format") == "date-time":
        return "2026-11-06T10:00:00Z"
    return "sample_value" + "x" * max(0, schema.get("minLength", 0) - 12)


def ts_type(schema):
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    if "const" in schema:
        return json.dumps(schema["const"])
    if "enum" in schema:
        return " | ".join(json.dumps(value) for value in schema["enum"])
    variants = schema.get("anyOf", schema.get("oneOf"))
    if variants:
        return " | ".join(ts_type(value) for value in variants)
    kind = schema.get("type")
    if kind == "array":
        return f"Array<{ts_type(schema['items'])}>"
    if kind == "object" or "properties" in schema:
        if "properties" not in schema:
            additional = schema.get("additionalProperties", {})
            value_type = ts_type(additional) if isinstance(additional, dict) else "unknown"
            return f"Record<string, {value_type}>"
        required = schema.get("required", [])
        fields = [
            f"  {json.dumps(name)}{'' if name in required else '?'}: {ts_type(value)};"
            for name, value in schema["properties"].items()
        ]
        return "{\n" + "\n".join(fields) + "\n}"
    return {
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "null": "null",
    }.get(kind, "unknown")


def json_block(value):
    return "```json\n" + json.dumps(value, indent=2) + "\n```\n"


def generate():
    document = app.openapi()
    # Describe target security explicitly; a 501 stub does not authenticate requests yet.
    document.setdefault("components", {}).setdefault("securitySchemes", {})["DemoBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "description": "Target contract; business routes return 501 until implementation.",
    }
    for model in (NextStep, InvestigationContext, ToolObservation, ActionResult):
        schema = model.model_json_schema(ref_template="#/components/schemas/{model}")
        document["components"]["schemas"].update(schema.pop("$defs", {}))
        document["components"]["schemas"][model.__name__] = schema
    sections = [
        "# API specification v1\n",
        "<!-- Generated by npm run contracts. Edit schemas/routes/exporter, not this file. -->\n",
        "## Implementation status\n",
        "Only `GET /api/health` and `GET /api/bootstrap` work. Every business route is a typed "
        "**501 FEATURE_NOT_IMPLEMENTED** stub. Success examples below are the frozen target "
        "contract, not completed features. OpenAPI in `docs/openapi.json` is the handoff snapshot. "
        "Runtime `/openapi.json` exposes FastAPI contracts; this snapshot adds target security "
        "metadata and the internal agent protocol.\n",
        "## Global rules\n",
        "- All paths below include `/api`. JSON only; reject extra input fields. "
        "IDs are opaque strings, never array indexes. Never infer permission from a supplied ID.\n"
        "- After P02: `Authorization: Bearer <token>` for all business endpoints except login. "
        "No cookie sessions, browser role header, public registration, or arbitrary tool endpoint. "
        "Eight-hour server expiry; logout revokes token. Store hashes, not raw tokens/passwords.\n"
        "- ISO date-only joining/deadline dates; UTC timestamps. Lists are `{items: [...]}`; "
        "empty is `[]`. Local fixture size is at most six hires; pagination is deferred. "
        "A case response returns at most the 100 newest timeline items chronologically; "
        "history remains in storage. Never silently truncate decision evidence.\n"
        "- Unknown resource: 404. Existing out-of-scope resource: indistinguishable 404. "
        "Known in-scope record but wrong operation/role: 403. Missing/expired token: 401. "
        "Invalid shape: 422; stale version/state/policy or unsupported pack: 409. "
        "Unexpected server failures must be sanitized 500, never traceback/secret data.\n"
        "- Duplicate same question answer or decision returns its existing accepted result. "
        "Different answer after ANSWERED or different decision after recorded decision: 409. "
        "Approval queues work, not execution success. Recheck inputs at execution.\n"
        "- No endpoint may accept model credentials, model URLs, arbitrary SQL, actor IDs, "
        "source timestamps, or authoritative role claims from the browser.\n",
        "## Error contract\n",
        json_block(
            {
                "error": {
                    "code": "STALE_VERSION",
                    "message": "Inputs changed; request a new proposal.",
                    "details": [],
                }
            }
        ),
        "Stable codes: FEATURE_NOT_IMPLEMENTED (501), UNAUTHENTICATED (401), FORBIDDEN (403), "
        "NOT_FOUND (404), STALE_VERSION / INVALID_STATE / POLICY_REVIEW_REQUIRED (409), "
        "VALIDATION_ERROR (422), DATABASE_UNAVAILABLE (503), INTERNAL_ERROR (500). "
        "Token/credential input is never echoed in error details.\n",
        "## Source-record authority and semantics\n",
        "`PUT /hires/{hire_id}/sources/{source_id}`: expected_version=0 creates an absent record "
        "at v1; positive expected_version conditionally updates that exact record. Body category "
        "must match the existing record. Server sets source_system=demo, external_id=source_id, "
        "actor and time. Conflicting identity/category/version is 409. Atomically invalidate "
        "dependent current checks and create sanitized audit. This is a simulated-source control, "
        "not an unrestricted agent mutation. Unassigned inventory is seeded, "
        "not created through this endpoint.\n",
        "| Category | Permitted writer | Additional invariant |\n|---|---|---|\n"
        "| documents | Own EMPLOYEE submits, scoped HR reviews | Employee can set SUBMITTED only; "
        "REVIEWED requires HR. Review does not establish signature/legal authenticity. |\n"
        "| equipment | Scoped IT | HANDED_OVER requires matching hire assignee and handover_at; "
        "RESERVED requires assignee, no handover_at. AVAILABLE requires null assignee/handover. "
        "Prevent a source write from moving another hire's device. |\n"
        "| payroll | Scoped PAYROLL | setup_confirmed implies profile_created. |\n"
        "| benefits | Scoped BENEFITS; own EMPLOYEE may only record DECLINED | ENROLLED needs "
        "benefits-owner confirmation; decline satisfies only an explicitly permitting policy. |\n"
        "| training | Scoped TRAINING | Record completion, not competence. |\n"
        "| manager | Assigned MANAGER | Active supported buddy user; non-empty plan. |\n",
        "## Endpoint contracts\n",
    ]
    for path, methods in document["paths"].items():
        for method, operation in methods.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue
            name = operation["operationId"].split("_api_")[0]
            access = ACCESS.get(name, "See scoped ownership rules.")
            if name not in ("health", "bootstrap", "create_session"):
                operation["security"] = [{"DemoBearer": []}]
            sections += [
                f"### `{method.upper()} {path}`\n",
                operation["summary"] + "\n",
                f"**Authority:** {access}\n",
            ]
            parameters = operation.get("parameters", [])
            sections.append(
                "**Parameters:** "
                + (
                    ", ".join(
                        f"`{p['name']}` ({p['in']}, {ts_type(p['schema'])}, "
                        f"{'required' if p.get('required') else 'optional'})"
                        for p in parameters
                    )
                    if parameters
                    else "none"
                )
                + ".\n"
            )
            request = operation.get("requestBody", {}).get("content", {}).get("application/json")
            if request:
                sections += [
                    "**Request body:** " + ts_type(request["schema"]) + "\n",
                    json_block(example(request["schema"], document)),
                ]
            else:
                sections.append("**Request body:** none.\n")
            for status, response in operation["responses"].items():
                if not status.startswith("2"):
                    continue
                content = response.get("content", {}).get("application/json")
                sections.append(
                    f"**Success {status}:** "
                    + (ts_type(content["schema"]) if content else "no body")
                    + "\n"
                )
                if content:
                    sections.append(json_block(example(content["schema"], document)))
            codes = [status for status in operation["responses"] if not status.startswith("2")]
            sections.append("**Errors:** " + ", ".join(codes) + "; global meanings above.\n")
    sections += [
        "## Internal agent contract (not a public endpoint)\n",
        "`NextStep` has one `next_step` discriminated union: read, ask, propose, finish, escalate. "
        "No read arguments/hire ID exist; scope is supplied by the server. This is the final-guide "
        "illustration simplified into a provider-compatible object envelope. Ask recipient_role is "
        "a suggestion; the server resolves an authorized recipient. Proposal reviewer, versions, "
        "execution and verification are server-only.\n",
        json_block(
            {
                "next_step": {
                    "step": "read",
                    "tool": "get_equipment_status",
                    "reason_summary": "Check independent assignment evidence.",
                }
            }
        ),
        "## All shared JSON schemas\n",
        "Required keys, nullable fields, enums, bounds and discriminators below are normative. "
        "JSON examples use illustrative IDs, not guaranteed seeded records.\n",
    ]
    for name, schema in sorted(document["components"]["schemas"].items()):
        sections += [f"### {name}\n", json_block(schema)]
    types = (
        "// Generated by npm run contracts. Source: backend/app/shared/contracts.py. Do not edit.\n"
    )
    types += "\n".join(
        f"export type {name} = {ts_type(schema)};\n"
        for name, schema in sorted(document["components"]["schemas"].items())
    )
    return {
        ROOT / "docs/openapi.json": json.dumps(document, indent=2, sort_keys=True) + "\n",
        ROOT / "docs/API_SPEC.md": "\n".join(sections),
        ROOT / "frontend/src/shared/api-types.ts": types,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, contents in generate().items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != contents:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding="utf-8", newline="\n")
    if stale:
        raise SystemExit("Contract drift; run npm run contracts: " + ", ".join(stale))
    print(
        "Contracts checked."
        if args.check
        else "Contracts, OpenAPI snapshot and TypeScript types generated."
    )


if __name__ == "__main__":
    main()
