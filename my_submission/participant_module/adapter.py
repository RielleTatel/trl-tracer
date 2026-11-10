"""trl-tracer AssessmentModule: always-abstain fallback (ticket 01).

Returns a contract-valid abstention for every case. It is the emergency fallback package and
the baseline the harness compares every later version against.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any


class AssessmentModule:
    def __init__(self) -> None:
        self.checklist: Mapping[str, Any] = {}
        self.settings: Mapping[str, Any] = {}

    def load(self, config: Mapping[str, Any], asset_root: Path) -> None:
        self.checklist = config["checklist"]
        self.settings = config["module"]["settings"]

    def assess(self, case: Mapping[str, Any], context: Any) -> dict[str, Any]:
        ids = [criterion["criterion_id"] for criterion in self.checklist["criteria"]]
        return {
            "schema_version": case["schema_version"],
            "checklist_version": self.checklist["version"],
            "case_id": case["case_id"],
            "assessment_target": dict(case["assessment_target"]),
            "assessment_status": "abstained",
            "predicted_trl": None,
            "criterion_status": {cid: "insufficient evidence" for cid in ids},
            "evidence_reference": {cid: [] for cid in ids},
            "missing_evidence": {cid: "No evidence was assessed for this criterion." for cid in ids},
            "abstention_reason": "insufficient evidence",
            "error_code": None,
        }

    def reset_case(self) -> None:
        pass

    def close(self) -> None:
        pass
