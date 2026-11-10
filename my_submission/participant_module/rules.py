"""Criterion rules: hypotheses, search phrases and trap cues per criterion, from the rules file.

The rules file (assets/criteria_rules.json) is exported from the criterion cards. Placeholders
{target}, {application} and {environment} are filled from the case. A criterion whose ID is not
in the file falls back to its checklist description, so any checklist works.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

RULES_FILE = "criteria_rules.json"
_PREFIX = re.compile(r"^[^:]{1,80}\(TRL\s*[1-9]\)\s*:\s*|^[^:]{1,60}:\s*(?=the report)", re.IGNORECASE)


def load(asset_root: Path | None) -> dict[str, Any]:
    """The rules file, or empty rules when it is missing or unreadable."""
    try:
        data = json.loads((Path(asset_root) / RULES_FILE).read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("criteria"), dict):
            return data
    except (OSError, ValueError, TypeError):
        pass
    return {"version": None, "global": {}, "criteria": {}}


class _Blank(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _fill(text: str, values: Mapping[str, str]) -> str:
    return " ".join(text.format_map(_Blank(values)).split())


def description_hypothesis(description: str) -> str:
    """'Basic principles (TRL 1): the report states X' -> 'The report states X'."""
    text = _PREFIX.sub("", description.strip()).strip()
    return (text[:1].upper() + text[1:]) if text else description


def for_case(rules: Mapping[str, Any], checklist: Mapping[str, Any], case: Mapping[str, Any]) -> dict[str, dict[str, list[str]]]:
    """Per checklist criterion: filled hypotheses, queries and traps."""
    target = case.get("assessment_target", {}) or {}
    values = {
        "target": str(target.get("description", "the assessed technology")),
        "application": str(case.get("intended_application", "its intended application")),
        "environment": str(case.get("intended_environment", "its intended environment")),
    }
    out = {}
    known = rules.get("criteria", {}) or {}
    for criterion in checklist["criteria"]:
        cid, description = criterion["criterion_id"], criterion.get("description", "")
        entry = known.get(cid) or {}
        hypotheses = [_fill(h, values) for h in entry.get("hypotheses", []) if h.strip()]
        queries = [_fill(q, values) for q in entry.get("queries", []) if q.strip()]
        out[cid] = {
            "hypotheses": hypotheses or [description_hypothesis(description)],
            "queries": queries or [description_hypothesis(description)],
            "traps": [t for t in entry.get("traps", []) if t.strip()],
        }
    return out


def page_traps(rules: Mapping[str, Any]) -> list[str]:
    return [t for t in (rules.get("global", {}) or {}).get("page_traps", []) if t.strip()]
