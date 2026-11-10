"""The evidence stage: everything that reads PDFs or runs a model.

It builds the case evidence record that the decision step consumes (see decision.py). Each
step checks the time budget first and records in `skipped` what it did not do, and the record
is filled in place, so partial work survives an exception. Judging is added in ticket 08.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from typing import Any

from participant_module import judge, pdf_text, retrieve, rules

EVIDENCE_VERSION = "trl-tracer-evidence-v1"


def empty_record() -> dict[str, Any]:
    return {"version": EVIDENCE_VERSION, "documents": [], "criteria": {}, "skipped": {}, "timings_ms": {}}


def _timed(record: dict[str, Any], name: str, started: float) -> None:
    record["timings_ms"][name] = round((time.monotonic() - started) * 1000, 1)


def collect(case: Mapping[str, Any], checklist: Mapping[str, Any], settings: Mapping[str, Any],
            models: Mapping[str, Any], has_time: Callable[[str], bool], record: dict[str, Any]) -> dict[str, Any]:
    """Fill `record` in place and return it."""
    if settings.get("debug_fault") == "evidence":
        raise RuntimeError("debug_fault: evidence stage failure (test hook)")
    if not has_time("evidence"):
        record["skipped"]["evidence"] = True
        return record
    record["skipped"]["evidence"] = False

    started = time.monotonic()
    for document in case["documents"]:
        record["documents"].append(pdf_text.extract_document(document, lambda: has_time("text")))
    _timed(record, "text", started)
    record["skipped"]["text"] = not all(d["complete"] for d in record["documents"])

    started = time.monotonic()
    loaded = models.get("rules") or rules.load(None)
    per_criterion = rules.for_case(loaded, checklist, case)
    trapped = retrieve.trap_pages(record["documents"], rules.page_traps(loaded))
    max_chars = int(settings.get("passage_max_chars", retrieve.DEFAULTS["passage_max_chars"]))
    passages = [p for p in pdf_text.passages(record["documents"], max_chars=max_chars)
                if (p["document_id"], p["page"]) not in trapped]
    record["trap_pages"] = sorted([d, p] for d, p in trapped)
    record["criteria"] = retrieve.retrieve(passages, per_criterion, models, settings,
                                           lambda: has_time("retrieve"), record["skipped"])
    _timed(record, "retrieve", started)

    started = time.monotonic()
    judge.judge(record["criteria"], per_criterion, models.get("entailer"), settings,
                lambda: has_time("judge"), record["skipped"])
    _timed(record, "judge", started)
    return record
