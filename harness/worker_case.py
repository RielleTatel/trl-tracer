"""Run one case in this process, the way the server's worker does, and write a JSON record.

Started by harness/run.py with the base environment's Python and a restricted environment:

    python -s worker_case.py <case.json> <config.json> <record.json> <started_ns>

`started_ns` is the parent's clock when it launched this process, so interpreter start counts
towards the time budget, as on the server. Uses only the standard library and the module.
"""

from __future__ import annotations

import json
import resource
import sys
import time
import traceback
from pathlib import Path


class Context:
    def __init__(self, run_id: str, seed: int, budget_ms: int, scratch: Path, started_ns: int) -> None:
        self.run_id = run_id
        self.seed = seed
        self.scratch_dir = scratch
        self._deadline_ns = started_ns + budget_ms * 1_000_000
        self.time_budget_ms = int(self.remaining_ms())

    def remaining_ms(self) -> float:
        return max(0.0, (self._deadline_ns - time.monotonic_ns()) / 1_000_000)


def peak_rss_bytes() -> int:
    scale = 1 if sys.platform == "darwin" else 1024  # ru_maxrss: bytes on macOS, KiB on Linux
    own = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    children = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return int(max(own, children) * scale)


def main(case_path: str, config_path: str, record_path: str, started_ns: str) -> int:
    case = json.loads(Path(case_path).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    record: dict = {"case_id": case["case_id"], "timings_ms": {}, "error": None, "result": None, "evidence": None}
    context = Context(config["run_id"], config["compute"]["seed"], config["deadline_ms"], Path.cwd(), int(started_ns))
    record["timings_ms"]["start"] = config["deadline_ms"] - context.remaining_ms()
    module = None
    try:
        sys.path.insert(0, config["module_root"])
        from participant_module.adapter import AssessmentModule

        module = AssessmentModule()
        t0 = time.monotonic()
        module.load(config, Path(config["asset_root"]))
        t1 = time.monotonic()
        record["timings_ms"]["load"] = (t1 - t0) * 1000
        record["result"] = module.assess(case, context)
        t2 = time.monotonic()
        record["timings_ms"]["assess"] = (t2 - t1) * 1000
        # Cached evidence for the fast cycle (spec: case evidence record), if the module exposes it.
        record["evidence"] = getattr(module, "last_evidence", None)
    except BaseException as exc:  # the server records any exception as MODULE_ERROR
        record["error"] = {"code": "MODULE_ERROR", "type": type(exc).__name__, "traceback": traceback.format_exc()}
    finally:
        t3 = time.monotonic()
        try:
            if module is not None:
                module.reset_case()
                module.close()
        except BaseException as exc:
            record["error"] = record["error"] or {"code": "CLEANUP_ERROR", "type": type(exc).__name__, "traceback": traceback.format_exc()}
        record["timings_ms"]["cleanup"] = (time.monotonic() - t3) * 1000
        record["peak_rss_bytes"] = peak_rss_bytes()
        try:
            json.dumps(record["result"], allow_nan=False)
        except (TypeError, ValueError) as exc:  # NaN, Infinity or non-JSON types: the server says INVALID_OUTPUT
            record["result"] = None
            record["error"] = record["error"] or {"code": "INVALID_OUTPUT", "type": type(exc).__name__, "traceback": str(exc)}
        try:
            json.dumps(record["evidence"], allow_nan=False)
        except (TypeError, ValueError) as exc:  # a harness-only cache: drop it, keep the result
            record["evidence"] = None
            record["evidence_error"] = f"{type(exc).__name__}: {exc}"
        Path(record_path).write_text(json.dumps(record, allow_nan=False, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
