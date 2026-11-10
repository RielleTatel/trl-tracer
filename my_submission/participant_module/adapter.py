"""trl-tracer AssessmentModule: the four protocol methods and the never-fail guard.

assess() runs the evidence stage (PDF text, retrieval, judging) and then the pure decision step.
Whatever goes wrong (an exception, too little time), it returns a contract-valid result built
from the evidence gathered so far, with the TRL prior: a failed case scores 0, a prior TRL keeps
most of the TRL score.
"""

from __future__ import annotations

import random
import sys
import time
import traceback
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from participant_module import decision, evidence, models, rules

ADAPTER_DEFAULTS: dict[str, Any] = {
    "reserve_ms": 15_000,  # stop starting new work when less than this is left
    "threads": 4,  # CPU threads for torch (the event laptop has 4 cores)
    "use_dense": True,  # bge-base-en-v1.5 dense retrieval
    "use_rerank": True,  # granite-embedding-reranker-english-r2
}


class AssessmentModule:
    def __init__(self) -> None:
        self.checklist: Mapping[str, Any] = {}
        self.settings: dict[str, Any] = {}
        self.asset_root: Path | None = None
        self.models: dict[str, Any] = {}
        self.last_evidence: dict[str, Any] | None = None  # read by the harness (fast-cycle cache)

    def load(self, config: Mapping[str, Any], asset_root: Path) -> None:
        self.checklist = config["checklist"]
        self.settings = {**ADAPTER_DEFAULTS, **dict(config["module"].get("settings") or {})}
        self.asset_root = Path(asset_root)
        seed = int(config.get("compute", {}).get("seed", 42))
        random.seed(seed)
        try:
            import numpy

            numpy.random.seed(seed)
        except ImportError:
            pass
        self.models["rules"] = rules.load(self.asset_root)
        self.load_ms: dict[str, float] = {}
        loaders = [("embedder", "use_dense", models.embedder), ("reranker", "use_rerank", models.reranker)]
        if any(self.settings.get(flag) for _, flag, _ in loaders):
            try:
                models.offline()
                import torch

                torch.manual_seed(seed)
                models.set_threads(self.settings["threads"])
            except Exception:
                print(traceback.format_exc(limit=3), file=sys.stderr)
        for name, flag, loader in loaders:
            if not self.settings.get(flag):
                continue
            started = time.monotonic()
            try:  # a model that fails to load is skipped; retrieval degrades instead of failing
                self.models[name] = loader()
            except Exception:
                print(traceback.format_exc(limit=3), file=sys.stderr)
            self.load_ms[name] = round((time.monotonic() - started) * 1000, 1)

    def assess(self, case: Mapping[str, Any], context: Any) -> dict[str, Any]:
        record = evidence.empty_record()
        record["timings_ms"]["load"] = dict(getattr(self, "load_ms", {}))
        self.last_evidence = record
        reserve = float(self.settings["reserve_ms"])

        def has_time(stage: str) -> bool:
            return context.remaining_ms() > reserve

        started = time.monotonic()
        try:
            evidence.collect(case, self.checklist, self.settings, self.models, has_time, record)
        except Exception:
            record["error"] = traceback.format_exc(limit=5)
            print(record["error"], file=sys.stderr)
        record["timings_ms"]["evidence"] = round((time.monotonic() - started) * 1000, 1)
        return self._decide(case, record)

    def _decide(self, case: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
        meta = {k: case[k] for k in ("schema_version", "case_id", "assessment_target")}
        for attempt in (record, None):  # with the evidence, then with none at all
            try:
                return decision.decide(meta, self.checklist, self.settings, attempt)
            except Exception:
                print(traceback.format_exc(limit=5), file=sys.stderr)
        return self._prior_only(meta)

    def _prior_only(self, meta: Mapping[str, Any]) -> dict[str, Any]:
        """Last resort, independent of the decision step: every criterion unassessed, TRL prior."""
        ids = [c["criterion_id"] for c in self.checklist["criteria"]]
        prior = int(self.settings.get("trl_prior", decision.DEFAULTS["trl_prior"]))
        return {
            "schema_version": meta["schema_version"],
            "checklist_version": self.checklist["version"],
            "case_id": meta["case_id"],
            "assessment_target": dict(meta["assessment_target"]),
            "assessment_status": "completed",
            "predicted_trl": prior,
            "criterion_status": {cid: "insufficient evidence" for cid in ids},
            "evidence_reference": {cid: [] for cid in ids},
            "missing_evidence": {cid: "The criterion could not be assessed." for cid in ids},
            "abstention_reason": None,
            "error_code": None,
        }

    def reset_case(self) -> None:
        try:
            if self.settings.get("debug_fault") == "cleanup":
                self.last_evidence = object()  # test hook: broken per-case state
            self.last_evidence = self.last_evidence if isinstance(self.last_evidence, dict) else None
        except Exception:
            pass

    def close(self) -> None:
        try:
            self.models.clear()
        except Exception:
            pass
