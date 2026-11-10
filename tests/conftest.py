"""Test setup: the package under test and the kit's contract validator.

Run with the kit's Python, which has pytest and the kit's contract code:

    apctt-participant-kit-0.5.0-cpu/.venv/bin/python -m pytest tests
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "my_submission"))

OFFICIAL_CHECKLIST = ROOT / "apctt-participant-kit-0.5.0-cpu" / "contracts" / "checklist.official.json"


@pytest.fixture
def checklist() -> dict[str, Any]:
    data = json.loads(OFFICIAL_CHECKLIST.read_text(encoding="utf-8"))
    return {"version": data["version"], "criteria": data["criteria"]}


def contract_issues(result: dict[str, Any], case: dict[str, Any], checklist: dict[str, Any]) -> list[tuple[str, str]]:
    """The kit's own result validator (what the server applies)."""
    from apctt_contracts.config import Checklist
    from apctt_contracts.results import validate_result

    model = Checklist.model_validate({"version": checklist["version"], "criteria": checklist["criteria"]})
    return [(i.path, i.rule) for i in validate_result(result, case=case, checklist=model)]
