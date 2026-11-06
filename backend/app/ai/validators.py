"""Deterministic checks on model output. A model's own confidence is never accepted as proof."""

import re

from app.shared.contracts import AssistantOutput, DocumentExtractionOutput, InsightOutput


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def quote_in(quote: str, source: str) -> bool:
    return normalize(quote) in normalize(source)


def check_assistant(output: AssistantOutput, passages: dict[str, str]) -> str | None:
    if output.status in ("ANSWERED", "PARTIAL") and not output.claims:
        return "ANSWER_WITHOUT_CLAIMS"
    if output.status in ("NOT_FOUND", "OUT_OF_SCOPE") and output.claims:
        return "ABSTENTION_WITH_CLAIMS"
    for claim in output.claims:
        for citation in claim.citations:
            if citation.chunk_id not in passages:
                return "CITATION_NOT_RETRIEVED"
            if not quote_in(citation.quote, passages[citation.chunk_id]):
                return "QUOTE_NOT_IN_PASSAGE"
    return None


def check_extraction(output: DocumentExtractionOutput, text: str) -> str | None:
    for field in output.fields:
        if not quote_in(field.quote, text):
            return "FIELD_QUOTE_NOT_IN_DOCUMENT"
    return None


def check_insight(output: InsightOutput, refs: set[str], values: set[int]) -> str | None:
    for recommendation in output.recommendations:
        if not set(recommendation.evidence_refs) <= refs:
            return "EVIDENCE_REF_NOT_SUPPLIED"
    text = " ".join([output.summary, *[r.text for r in output.recommendations]])
    for number in re.findall(r"\b\d+\b", text):
        if int(number) not in values:
            return "NUMBER_NOT_IN_METRICS"
    return None
