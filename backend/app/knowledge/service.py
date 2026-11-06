"""Approved-knowledge ingestion, permission-filtered search and grounded answers."""

import hashlib
import json
import math
import re
import sqlite3
import time

from app.ai.harness import AiOutputRejected, AiUnavailable, record_run, run_operation
from app.ai.prompts import ASSISTANT_SYSTEM, assistant_user
from app.ai.providers import current_provider
from app.ai.validators import check_assistant
from app.auth.permissions import KNOWLEDGE_ACCESS
from app.shared.contracts import (
    AssistantAnswer,
    AssistantClaim,
    AssistantOutput,
    Citation,
    KnowledgeDocument,
    User,
)
from app.shared.db import connect
from app.shared.errors import not_found
from app.shared.util import new_id, now_iso

MAX_CHUNK_WORDS = 350
TOP_K = 6
MIN_COVERAGE = 0.6
STOPWORDS = frozenset(
    """a about after all also am an and any are as at back be been before bring but by can could
    company did different do does doing during each every fall few for from get getting give
    going got had hand has have how i if in into is it its just like long many may me month more
    much must my need needs new of off on or other our out over per please policies policy really
    rule rules should so some still tell than that the their them then there these they thing
    this to us use was we were what when where which who why will with within would year years
    you your""".split()
)
# A small reviewed list that closes common paraphrase gaps. Porter stemming handles the rest.
SYNONYMS = {
    "wfh": ("remote", "home"),
    "remotely": ("remote",),
    "laptop": ("laptop", "device", "equipment"),
    "computer": ("laptop", "device"),
    "vacation": ("leave",),
    "holiday": ("leave", "holiday"),
    "pto": ("leave",),
    "sick": ("sick", "leave"),
    "ill": ("sick",),
    "illness": ("sick",),
    "doctor": ("medical", "doctor"),
    "note": ("certificate", "note"),
    "parents": ("parental",),
    "parent": ("parental",),
    "maternity": ("parental",),
    "paternity": ("parental",),
    "expense": ("reimbursement", "expense"),
    "expenses": ("reimbursement", "expense"),
    "reimburse": ("reimbursement",),
    "claim": ("reimbursement", "claim"),
    "insurance": ("insurance", "benefits"),
    "medical": ("insurance", "medical"),
    "health": ("insurance", "medical"),
    "salary": ("payroll", "salary"),
    "paid": ("paid", "payroll", "pay"),
    "documents": ("documents", "document"),
    "paperwork": ("documents", "document"),
    "joiners": ("hire", "onboarding"),
    "joiner": ("hire", "onboarding"),
    "broke": ("lost", "damaged"),
    "broken": ("lost", "damaged"),
    "lost": ("lost", "damaged"),
    "stolen": ("lost", "damaged"),
}
ADVICE_PATTERN = re.compile(
    r"\b(should i (resign|quit|sue|negotiate)|legal advice|am i eligible|can i sue|"
    r"medical advice|how much does \w+ (earn|make)|fire \w+|terminate \w+)\b",
    re.I,
)
TERM_PATTERN = re.compile(r"[a-z0-9]+")


def chunk_text(body: str) -> list[tuple[str, str]]:
    """Split on Markdown headings, then cap long sections. Returns (section reference, text)."""
    sections: list[tuple[str, list[str]]] = []
    heading = "Introduction"
    lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("#"):
            if any(item.strip() for item in lines):
                sections.append((heading, lines))
            heading = line.lstrip("# ").strip() or heading
            lines = []
        else:
            lines.append(line)
    if any(item.strip() for item in lines):
        sections.append((heading, lines))
    chunks = []
    for reference, content in sections:
        words = " ".join(content).split()
        for start in range(0, len(words), MAX_CHUNK_WORDS):
            chunks.append((reference, " ".join(words[start : start + MAX_CHUNK_WORDS])))
    return chunks


def create_draft(
    connection: sqlite3.Connection, title: str, access_level: str, body: str, user_id: str
) -> KnowledgeDocument:
    existing = connection.execute(
        "SELECT id, MAX(version) AS version FROM knowledge_documents WHERE title=?", (title,)
    ).fetchone()
    document_id = existing["id"] if existing["id"] else new_id("KB")
    version = (existing["version"] or 0) + 1
    connection.execute(
        "INSERT INTO knowledge_documents (id, version, title, access_level, status, body, sha256, "
        "uploaded_by, created_at) VALUES (?,?,?,?,'DRAFT',?,?,?,?)",
        (
            document_id,
            version,
            title,
            access_level,
            body,
            hashlib.sha256(body.encode()).hexdigest(),
            user_id,
            now_iso(),
        ),
    )
    return get_document(connection, document_id, version)


def approve(
    connection: sqlite3.Connection, document_id: str, version: int, user_id: str
) -> KnowledgeDocument:
    """Only now is the text searchable. The previous version is retired in the same transaction."""
    row = connection.execute(
        "SELECT * FROM knowledge_documents WHERE id=? AND version=?", (document_id, version)
    ).fetchone()
    if row is None:
        not_found()
    if row["status"] == "APPROVED":
        return get_document(connection, document_id, version)
    for old in connection.execute(
        "SELECT id FROM knowledge_chunks WHERE document_id=?", (document_id,)
    ).fetchall():
        connection.execute("DELETE FROM knowledge_chunks_fts WHERE chunk_id=?", (old["id"],))
    connection.execute("DELETE FROM knowledge_chunks WHERE document_id=?", (document_id,))
    connection.execute(
        "UPDATE knowledge_documents SET status='RETIRED' WHERE id=? AND status='APPROVED'",
        (document_id,),
    )
    connection.execute(
        "UPDATE knowledge_documents SET status='APPROVED', approved_by=?, effective_from=? "
        "WHERE id=? AND version=?",
        (user_id, now_iso()[:10], document_id, version),
    )
    for position, (reference, text) in enumerate(chunk_text(row["body"])):
        chunk_id = new_id("CHUNK")
        connection.execute(
            "INSERT INTO knowledge_chunks (id, document_id, document_version, position, "
            "section_ref, text, access_level) VALUES (?,?,?,?,?,?,?)",
            (chunk_id, document_id, version, position, reference, text, row["access_level"]),
        )
        connection.execute(
            "INSERT INTO knowledge_chunks_fts (chunk_id, section_ref, text) VALUES (?,?,?)",
            (chunk_id, reference, text),
        )
    return get_document(connection, document_id, version)


def get_document(connection, document_id: str, version: int) -> KnowledgeDocument:
    row = connection.execute(
        "SELECT d.*, (SELECT COUNT(*) FROM knowledge_chunks c WHERE c.document_id=d.id "
        "AND c.document_version=d.version) AS chunk_count FROM knowledge_documents d "
        "WHERE d.id=? AND d.version=?",
        (document_id, version),
    ).fetchone()
    return _to_document(row)


def _to_document(row) -> KnowledgeDocument:
    return KnowledgeDocument(
        id=row["id"],
        version=row["version"],
        title=row["title"],
        access_level=row["access_level"],
        status=row["status"],
        chunk_count=row["chunk_count"],
        created_at=row["created_at"],
    )


def list_documents(connection, user: User) -> list[KnowledgeDocument]:
    allowed = KNOWLEDGE_ACCESS[user.role]
    marks = ",".join("?" * len(allowed))
    status = "" if user.role.value == "HR" else "AND d.status='APPROVED'"
    rows = connection.execute(
        "SELECT d.*, (SELECT COUNT(*) FROM knowledge_chunks c WHERE c.document_id=d.id "
        "AND c.document_version=d.version) AS chunk_count FROM knowledge_documents d "
        f"WHERE d.access_level IN ({marks}) {status} ORDER BY d.title, d.version DESC",
        allowed,
    ).fetchall()
    return [_to_document(row) for row in rows]


def query_terms(question: str) -> list[tuple[str, ...]]:
    """Each meaningful word becomes one group of alternatives. FTS operators cannot survive this."""
    groups: list[tuple[str, ...]] = []
    for word in TERM_PATTERN.findall(question.lower()):
        if word in STOPWORDS or len(word) < 2:
            continue
        group = SYNONYMS.get(word, (word,))
        if group not in groups:
            groups.append(group)
    return groups[:12]


def search(connection: sqlite3.Connection, question: str, access_levels: tuple[str, ...]):
    """Filter by access in SQL first, then rank. Restricted text never reaches later steps."""
    groups = query_terms(question)
    if not groups:
        return []
    marks = ",".join("?" * len(access_levels))
    matched: dict[str, int] = {}
    ranks: dict[str, float] = {}
    rows_by_id: dict[str, sqlite3.Row] = {}
    for group in groups:
        match = " OR ".join(f'"{term}"' for term in group)
        rows = connection.execute(
            "SELECT c.id AS chunk_id, c.text, c.section_ref, c.access_level, c.document_id, "
            "c.document_version, d.title, bm25(knowledge_chunks_fts) AS rank "
            "FROM knowledge_chunks_fts f JOIN knowledge_chunks c ON c.id=f.chunk_id "
            "JOIN knowledge_documents d ON d.id=c.document_id AND d.version=c.document_version "
            f"WHERE knowledge_chunks_fts MATCH ? AND d.status='APPROVED' "
            f"AND c.access_level IN ({marks})",
            (match, *access_levels),
        ).fetchall()
        for row in rows:
            matched[row["chunk_id"]] = matched.get(row["chunk_id"], 0) + 1
            ranks[row["chunk_id"]] = ranks.get(row["chunk_id"], 0.0) + row["rank"]
            rows_by_id[row["chunk_id"]] = row
    # The reliability gate: most of the question's meaningful words must appear in the passage.
    needed = max(1, math.ceil(MIN_COVERAGE * len(groups)))
    reliable = [chunk_id for chunk_id, count in matched.items() if count >= needed]
    reliable.sort(key=lambda chunk_id: (-matched[chunk_id], ranks[chunk_id]))
    return [dict(rows_by_id[chunk_id]) for chunk_id in reliable[:TOP_K]]


def _citation(row: dict, quote: str) -> Citation:
    return Citation(
        chunk_id=row["chunk_id"],
        document_id=row["document_id"],
        title=row["title"],
        version=row["document_version"],
        section_ref=row["section_ref"],
        access_level=row["access_level"],
        quote=quote,
    )


def _abstain(user: User, status: str, message: str, reason: str, retrieval_ms=None):
    provider = current_provider()
    run_id = record_run(
        "assistant.answer",
        1,
        provider,
        "ABSTAINED",
        "NO_MODEL_CALL",
        user_id=user.id,
        failure_reason=reason,
        retrieval_ms=retrieval_ms,
    )
    return AssistantAnswer(
        status=status,
        message=message,
        claims=[],
        uncertainty="",
        suggest_escalation=True,
        sources=[],
        ai_run_id=run_id,
        model=provider.model,
        is_stub=provider.is_stub,
    )


def answer(question: str, user: User) -> AssistantAnswer:
    not_available = (
        "This is not in the approved knowledge base. You can send the question to HR instead."
    )
    if ADVICE_PATTERN.search(question):
        return _abstain(
            user,
            "OUT_OF_SCOPE",
            "This needs a person. I can only explain approved policy, so please ask HR.",
            "ADVICE_REQUEST",
        )
    started = time.monotonic()
    with connect() as connection:
        rows = search(connection, question, KNOWLEDGE_ACCESS[user.role])
    retrieval_ms = int((time.monotonic() - started) * 1000)
    if not rows:
        # No reliable context means the model is not called at all, so it cannot improvise.
        return _abstain(user, "NOT_FOUND", not_available, "NO_RELIABLE_CONTEXT", retrieval_ms)
    passages = {row["chunk_id"]: row["text"] for row in rows}
    by_id = {row["chunk_id"]: row for row in rows}
    sources = [_citation(row, row["text"][:200]) for row in rows[:3]]
    provider = current_provider()
    fallback = {"sources": sources, "model": provider.model, "is_stub": provider.is_stub}
    try:
        result = run_operation(
            "assistant.answer",
            [
                {"role": "system", "content": ASSISTANT_SYSTEM},
                {
                    "role": "user",
                    "content": assistant_user(
                        question, [{"chunk_id": k, "text": v} for k, v in passages.items()]
                    ),
                },
            ],
            user_id=user.id,
            chunk_ids=list(passages),
            retrieval_ms=retrieval_ms,
            semantic_check=lambda output: check_assistant(output, passages),
        )
    except AiUnavailable as exc:
        return AssistantAnswer(
            status="UNAVAILABLE",
            message="The AI service is unavailable. These approved sources look relevant.",
            claims=[],
            uncertainty="",
            suggest_escalation=True,
            ai_run_id=exc.run_id,
            **fallback,
        )
    except AiOutputRejected as exc:
        return AssistantAnswer(
            status="UNAVAILABLE",
            message="I could not produce a verified answer. These approved sources look relevant.",
            claims=[],
            uncertainty="",
            suggest_escalation=True,
            ai_run_id=exc.run_id,
            **fallback,
        )
    output: AssistantOutput = result.output
    claims = [
        AssistantClaim(
            text=claim.text,
            citations=[_citation(by_id[item.chunk_id], item.quote) for item in claim.citations],
        )
        for claim in output.claims
    ]
    message = {
        "ANSWERED": "Here is what the approved sources say.",
        "PARTIAL": "The approved sources answer part of this.",
        "NOT_FOUND": not_available,
        "OUT_OF_SCOPE": "This needs a person, so please ask HR.",
    }[output.status]
    return AssistantAnswer(
        status=output.status,
        message=message,
        claims=claims,
        uncertainty=output.uncertainty,
        suggest_escalation=output.suggest_escalation or output.status != "ANSWERED",
        sources=sources if not claims else [],
        ai_run_id=result.run_id,
        model=result.model,
        is_stub=result.is_stub,
    )


def dumps_passages(rows: list[dict]) -> str:
    return json.dumps([{"chunk_id": row["chunk_id"], "title": row["title"]} for row in rows])
