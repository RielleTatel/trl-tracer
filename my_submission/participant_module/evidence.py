"""The evidence stage: everything that reads PDFs or runs a model.

It builds the case evidence record that the decision step consumes (see decision.py). Each
step checks the time budget first and records in `skipped` what it did not do.
Stub for now: text extraction, retrieval and judging are added by tickets 05, 07 and 08.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from typing import Any

from participant_module import pdf_text

EVIDENCE_VERSION = "trl-tracer-evidence-v1"


def empty_record() -> dict[str, Any]:
    return {"version": EVIDENCE_VERSION, "documents": [], "criteria": {}, "skipped": {}, "timings_ms": {}}


def collect(case: Mapping[str, Any], checklist: Mapping[str, Any], settings: Mapping[str, Any],
            models: Mapping[str, Any], has_time: Callable[[str], bool], record: dict[str, Any]) -> dict[str, Any]:
    """Fill `record` in place (so partial work survives an exception) and return it."""
    if settings.get("debug_fault") == "evidence":
        raise RuntimeError("debug_fault: evidence stage failure (test hook)")
    if not has_time("evidence"):
        record["skipped"]["evidence"] = True
        return record
    record["skipped"]["evidence"] = False

    started = time.monotonic()
    for document in case["documents"]:
        record["documents"].append(pdf_text.extract_document(document, lambda: has_time("text")))
    record["timings_ms"]["text"] = round((time.monotonic() - started) * 1000, 1)
    record["skipped"]["text"] = not all(d["complete"] for d in record["documents"])
    return record
