"""Fast cycle: re-run only the decision step over a slow run's cached evidence.

    python3 harness/replay.py                          # latest slow run, current settings
    python3 harness/replay.py runs/<run> --settings try.json --note "met 0.5"

Re-applies `decide()` with the current submission settings (plus --settings) and the current
decision code to the cached case evidence of every case of a slow run, validates each result
with the kit's contract validator, and writes a normal scored run (timings and memory are copied
from the slow run, so the gates still apply). Takes seconds. Changes to retrieval, judging,
models or the rules file need a slow run (harness/run.py) instead.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def latest_slow_run() -> Path:
    runs = sorted(p for p in common.RUNS.iterdir()
                  if (p / "meta.json").exists() and not common.read_json(p / "meta.json").get("replay_of"))
    if not runs:
        raise SystemExit("no slow run in runs/")
    return runs[-1]


def decide_all(source: Path, settings: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Replay every case of `source` in memory; returns case records like run.py writes."""
    sys.path.insert(0, str(common.SUBMISSION))
    from apctt_contracts.config import Checklist
    from apctt_contracts.results import validate_result
    from participant_module.decision import decide

    from score import load_records

    checklist = common.checklist()
    model = Checklist.model_validate(common.read_json(common.CHECKLIST))
    out = {}
    for case_id, old in load_records(source).items():
        record = {k: old.get(k) for k in ("case_id", "wall_s", "peak_rss_bytes", "timings_ms", "failure")}
        if old.get("failure") == "TIMEOUT" or not isinstance(old.get("evidence"), dict):
            record.update(ok=False, result=None, output_issues=[], failure=old.get("failure") or "NO_EVIDENCE")
            out[case_id] = record
            continue
        case = common.worker_case(case_id)
        meta = {k: case[k] for k in ("schema_version", "case_id", "assessment_target")}
        result = decide(meta, checklist, settings, old["evidence"])
        issues = [{"path": i.path, "rule": i.rule} for i in validate_result(result, case=case, checklist=model)]
        record.update(result=result, output_issues=issues, ok=not issues, failure="INVALID_OUTPUT" if issues else None)
        out[case_id] = record
    return out


def main() -> int:
    common.ensure_kit_python()
    sys.stdout.reconfigure(line_buffering=True)
    import compare
    from run import append_experiment
    from score import describe, score

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", nargs="?", type=Path, help="slow run to replay (default: latest)")
    parser.add_argument("--settings", type=Path, help="JSON object merged over submission.json settings")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    source = args.source or latest_slow_run()
    source_meta = common.read_json(source / "meta.json")
    settings = dict(common.submission().get("settings", {}))
    if args.settings:
        settings.update(common.read_json(args.settings))
    records = decide_all(source, settings)

    started = datetime.now()
    run_dir = common.RUNS / (started.strftime("%Y%m%d-%H%M%S") + "-replay")
    meta = {**source_meta, "run_id": run_dir.name, "replay_of": source.name, "started": started.isoformat(timespec="seconds"),
            "git": common.git_state(), "settings": settings, "note": args.note or f"replay of {source.name}"}
    common.write_json(run_dir / "meta.json", meta)
    for case_id, record in records.items():
        common.write_json(run_dir / "cases" / f"{case_id}.json", {k: v for k, v in record.items() if k != "evidence"})
    summary = score(records)
    common.write_json(run_dir / "score.json", summary)
    decision, why = compare.verdict(run_dir)
    print(describe(summary))
    print(f"{decision}: {why}")
    append_experiment(run_dir, meta, summary, decision, why)
    return 0 if summary["gates"]["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
