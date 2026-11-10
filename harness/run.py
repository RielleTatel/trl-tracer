"""Slow cycle: run trl-tracer on a set of public cases, validate, score, compare and log.

    python harness/run.py --set tuning                 # tuning | heldout | smoke | all
    python harness/run.py --cases USGS-SDG-012,USGS-SDG-040
    python harness/run.py --set smoke --settings my_settings.json --note "met threshold 0.6"

Each case runs in a fresh worker process with the base environment's Python, a restricted
environment and the 3-minute budget (interpreter start included), as on the organizer's server.
Writes runs/<run_id>/ (meta.json, cases/<case_id>.json, score.json), prints the dev score and the
KEEP / REVERT verdict, and appends a summary line to brain/experiments.md.
"""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

GRACE_S = 2.0  # termination_grace_ms


def worker_env(scratch: Path) -> dict[str, str]:
    for sub in ("home", "tmp", "cache"):
        (scratch / sub).mkdir(parents=True, exist_ok=True)
    return {
        "PATH": f"{common.BASE_PYTHON.parent}:/usr/bin:/bin",
        "HOME": str(scratch / "home"),
        "TMPDIR": str(scratch / "tmp"),
        "TMP": str(scratch / "tmp"),
        "TEMP": str(scratch / "tmp"),
        "XDG_CACHE_HOME": str(scratch / "cache"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONUTF8": "1",
        "PYTHONHASHSEED": str(common.SEED),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "CUDA_VISIBLE_DEVICES": "",
        "APCTT_MODEL_STORE": str(common.MODELS),
    }


def run_case(case_id: str, run_dir: Path, config: dict[str, Any], checklist_model: Any) -> dict[str, Any]:
    from apctt_contracts.results import validate_result

    case = common.worker_case(case_id)
    scratch = run_dir / "scratch" / case_id
    scratch.mkdir(parents=True, exist_ok=True)
    case_path, config_path, record_path = scratch / "case.json", scratch / "config.json", scratch / "record.json"
    common.write_json(case_path, case)
    common.write_json(config_path, config)
    argv = [str(common.BASE_PYTHON), "-s", str(Path(__file__).parent / "worker_case.py"),
            str(case_path), str(config_path), str(record_path)]
    started = time.monotonic_ns()
    proc = subprocess.Popen([*argv, str(started)], cwd=scratch, env=worker_env(scratch),
                            stdout=open(scratch / "stdout.log", "w"), stderr=open(scratch / "stderr.log", "w"),
                            start_new_session=True)
    failure = None
    try:
        proc.wait(timeout=config["deadline_ms"] / 1000)
    except subprocess.TimeoutExpired:
        failure = "TIMEOUT"
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=GRACE_S)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
    wall_s = (time.monotonic_ns() - started) / 1e9

    record: dict[str, Any] = {"case_id": case_id, "result": None, "evidence": None, "error": None}
    if failure is None and record_path.exists():
        try:
            record = common.read_json(record_path)
        except ValueError:
            failure = "WORKER_PROTOCOL_ERROR"
    elif failure is None:
        failure = "WORKER_PROTOCOL_ERROR"  # crashed or wrote no record (for example NaN in the result)
    if failure is None and record.get("error"):
        failure = record["error"]["code"]
    issues: list[dict[str, str]] = []
    if failure is None:
        found = validate_result(record["result"], case=case, checklist=checklist_model)
        issues = [{"path": i.path, "rule": i.rule} for i in found]
        if issues:
            failure = "INVALID_OUTPUT"
        elif record["result"]["assessment_status"] == "failed":
            failure = f"MODULE_FAILED:{record['result'].get('error_code')}"
    record.update(failure=failure, ok=failure is None, output_issues=issues, wall_s=round(wall_s, 3))
    record["stderr_tail"] = (scratch / "stderr.log").read_text(errors="replace")[-4000:]
    common.write_json(run_dir / "cases" / f"{case_id}.json", record)
    shutil.rmtree(scratch, ignore_errors=True)
    return record


def append_experiment(run_dir: Path, meta: dict[str, Any], summary: dict[str, Any], decision: str, why: str) -> None:
    from score import describe

    git = meta["git"]
    line = (
        f"- {meta['started'][:16].replace('T', ' ')} | `{run_dir.name}` | {meta['case_set']}({summary['cases']}) | "
        f"{git['commit']}{'+dirty' if git['dirty'] else ''} | {describe(summary)} | {decision}: {why}"
        + (f" | {meta['note']}" if meta.get("note") else "")
    )
    if not common.EXPERIMENTS.exists():
        common.EXPERIMENTS.write_text("# Experiments\n\n", encoding="utf-8")
    with common.EXPERIMENTS.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def main() -> int:
    common.ensure_kit_python()
    from apctt_contracts.config import Checklist

    import compare
    from score import describe, load_records, score

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--set", dest="case_set", help="tuning | heldout | smoke | all")
    group.add_argument("--cases", help="comma-separated case IDs")
    parser.add_argument("--settings", type=Path, help="JSON object merged over submission.json settings")
    parser.add_argument("--note", default="", help="what changed, for brain/experiments.md")
    args = parser.parse_args()

    case_ids = args.cases.split(",") if args.cases else common.case_set(args.case_set)
    case_set = args.case_set or "cases:" + ",".join(case_ids)
    settings = dict(common.submission().get("settings", {}))
    if args.settings:
        settings.update(common.read_json(args.settings))

    started = datetime.now()
    run_id = started.strftime("%Y%m%d-%H%M%S") + f"-{args.case_set or 'cases'}"
    run_dir = common.RUNS / run_id
    meta = {
        "run_id": run_id,
        "case_set": case_set,
        "cases": case_ids,
        "started": started.isoformat(timespec="seconds"),
        "git": common.git_state(),
        "settings": settings,
        "package_hash": common.tree_hash(common.SUBMISSION / "participant_module"),
        "rules_hash": common.tree_hash(common.SUBMISSION / "assets"),
        "note": args.note,
    }
    common.write_json(run_dir / "meta.json", meta)
    config = {
        "run_id": run_id,
        "deadline_ms": common.DEADLINE_MS,
        "checklist": common.checklist(),
        "module": {"package_id": "trl-tracer", "settings": settings},
        "compute": {"device": "cpu", "require_cuda": False, "allow_cpu_fallback": False,
                    "precision": "float32", "loading_policy": "cold_per_case", "seed": common.SEED,
                    "visible_devices": None},
        "module_root": str(common.SUBMISSION),
        "asset_root": str(common.SUBMISSION / "assets"),
    }
    checklist_model = Checklist.model_validate(common.read_json(common.CHECKLIST))

    print(f"run {run_id}: {len(case_ids)} case(s)")
    for index, case_id in enumerate(case_ids, 1):
        record = run_case(case_id, run_dir, config, checklist_model)
        status = record["result"]["assessment_status"] if record["ok"] else record["failure"]
        trl = record["result"]["predicted_trl"] if record["ok"] else None
        print(f"  [{index:>3}/{len(case_ids)}] {case_id}  {status:<10} trl={trl}  "
              f"est={common.estimated_trl(case_id)}  {record['wall_s']:.1f} s")
    shutil.rmtree(run_dir / "scratch", ignore_errors=True)

    meta["finished"] = datetime.now().isoformat(timespec="seconds")
    common.write_json(run_dir / "meta.json", meta)
    summary = score(load_records(run_dir))
    common.write_json(run_dir / "score.json", summary)
    decision, why = compare.verdict(run_dir)
    print(describe(summary))
    print(f"{decision}: {why}")
    if decision == "KEEP" and why.startswith("baseline"):
        compare.accept(run_dir)
    append_experiment(run_dir, meta, summary, decision, why)
    return 0 if summary["gates"]["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
