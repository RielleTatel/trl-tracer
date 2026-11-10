"""Seam 1: the module contract, exercised exactly as the server does.

Each test runs the real package in a fresh worker process (the base environment's Python, the
restricted environment, the time budget) through the harness, then checks the result with the
kit's contract validator. These tests load the real models, so they are marked `module`;
skip them in quick runs with `-m "not module"`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
import common  # noqa: E402
import run  # noqa: E402

pytestmark = pytest.mark.module

EXAMPLE = common.KIT / "docs" / "EXAMPLE_REQUEST.json"


def config(checklist: dict[str, Any], settings: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "run_id": "pytest",
        "deadline_ms": common.DEADLINE_MS,
        "checklist": checklist,
        "module": {"package_id": "trl-tracer", "settings": settings or {}},
        "compute": {"device": "cpu", "seed": common.SEED},
        "module_root": str(common.SUBMISSION),
        "asset_root": str(common.SUBMISSION / "assets"),
    }


def model_of(checklist: dict[str, Any]):
    from apctt_contracts.config import Checklist

    return Checklist.model_validate(checklist)


def example_case(tmp_path: Path, checklist_version: str) -> dict[str, Any]:
    from apctt_contracts.pdf import local_worker_case

    request = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    case = local_worker_case(request["case"], tmp_path / "documents")
    return {**case, "checklist_version": checklist_version}


def check(record: dict[str, Any]) -> dict[str, Any]:
    assert record["failure"] is None, (record["failure"], record.get("output_issues"), record.get("stderr_tail"))
    assert record["output_issues"] == []
    assert record["result"]["assessment_status"] in ("completed", "abstained")
    return record["result"]


def test_example_report_gives_a_valid_result(tmp_path, checklist):
    case = example_case(tmp_path, checklist["version"])
    result = check(run.run_case(case["case_id"], tmp_path / "run", config(checklist), model_of(checklist), case=case))
    assert set(result["criterion_status"]) == {c["criterion_id"] for c in checklist["criteria"]}


@pytest.mark.parametrize("case_id", common.smoke_case_ids())
def test_smoke_cases_give_valid_results(tmp_path, checklist, case_id):
    record = run.run_case(case_id, tmp_path / "run", config(checklist), model_of(checklist))
    check(record)
    assert record["wall_s"] < common.GATE_SLOWEST_S


def test_internal_error_still_gives_a_valid_result(tmp_path, checklist):
    case = example_case(tmp_path, checklist["version"])
    settings = {"debug_fault": "evidence"}  # test hook: the evidence stage raises
    result = check(run.run_case(case["case_id"], tmp_path / "run", config(checklist, settings), model_of(checklist), case=case))
    assert result["assessment_status"] == "completed"
    assert result["predicted_trl"] == 6


def test_nearly_exhausted_time_still_gives_a_valid_result(tmp_path, checklist):
    case = example_case(tmp_path, checklist["version"])
    settings = {"reserve_ms": common.DEADLINE_MS}  # always "too little time left" for new work
    record = run.run_case(case["case_id"], tmp_path / "run", config(checklist, settings), model_of(checklist), case=case)
    result = check(record)
    assert result["predicted_trl"] == 6
    assert record["evidence"]["skipped"]["evidence"] is True


def test_changed_checklist_gives_a_result_keyed_by_its_ids(tmp_path):
    changed = {"version": "TEST-CHECKLIST-2", "criteria": [
        {"criterion_id": "ZZ-01", "description": "The report states that a prototype was tested."},
        {"criterion_id": "ZZ-02", "description": "The report compares results with acceptance criteria."},
    ]}
    case = example_case(tmp_path, changed["version"])
    result = check(run.run_case(case["case_id"], tmp_path / "run", config(changed), model_of(changed), case=case))
    assert set(result["criterion_status"]) == {"ZZ-01", "ZZ-02"}
    assert result["checklist_version"] == "TEST-CHECKLIST-2"


def test_cleanup_never_raises(tmp_path, checklist):
    case = example_case(tmp_path, checklist["version"])
    settings = {"debug_fault": "cleanup"}  # test hook: per-case state is broken before cleanup
    record = run.run_case(case["case_id"], tmp_path / "run", config(checklist, settings), model_of(checklist), case=case)
    check(record)
