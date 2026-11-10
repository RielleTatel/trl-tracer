"""Compare a run with the best run on the same case set: KEEP or REVERT.

    python harness/compare.py [runs/<run>]           # default: the latest run
    python harness/compare.py --accept [runs/<run>]  # record it as the new best (after you commit)

Runs are comparable only when they cover the same cases and the same hand labels. A run that
fails the gates is always REVERT. Otherwise KEEP when the dev score is at least the best's.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

BEST = common.RUNS / "best.json"


def latest_run() -> Path:
    runs = sorted(p for p in common.RUNS.iterdir() if (p / "score.json").exists())
    if not runs:
        raise SystemExit("no scored run in runs/")
    return runs[-1]


def best_for(case_set: str) -> dict[str, Any] | None:
    return common.read_json(BEST).get(case_set) if BEST.exists() else None


def verdict(run_dir: Path) -> tuple[str, str]:
    meta = common.read_json(run_dir / "meta.json")
    summary = common.read_json(run_dir / "score.json")
    best = best_for(meta["case_set"])
    if not summary["gates"]["pass"]:
        return "REVERT", "gates fail"
    if best is None:
        return "KEEP", "baseline (no best run yet for this case set)"
    best_summary = common.read_json(common.RUNS / best["run"] / "score.json")
    if best_summary["cases"] != summary["cases"] or best_summary["labels_hash"] != summary["labels_hash"]:
        return "RE-BASELINE", f"not comparable with {best['run']} (cases or labels changed); accept this run as the new baseline if intended"
    delta_a = summary["A"] - best_summary["A"]
    delta_b = (summary["B"] or 0) - (best_summary["B"] or 0)
    delta = summary["dev"] - best_summary["dev"]
    text = f"vs {best['run']}: dev {delta:+.4f} (A {delta_a:+.4f}, B {delta_b:+.4f})"
    return ("KEEP" if delta >= 0 else "REVERT"), text


def accept(run_dir: Path) -> None:
    meta = common.read_json(run_dir / "meta.json")
    best = common.read_json(BEST) if BEST.exists() else {}
    best[meta["case_set"]] = {"run": run_dir.name, "commit": meta["git"]["commit"]}
    common.write_json(BEST, best)
    print(f"best for {meta['case_set']}: {run_dir.name}")


if __name__ == "__main__":
    common.ensure_kit_python()
    args = sys.argv[1:]
    do_accept = "--accept" in args
    args = [a for a in args if a != "--accept"]
    run = Path(args[0]) if args else latest_run()
    if do_accept:
        accept(run)
    else:
        decision, why = verdict(run)
        print(f"{decision}: {run.name} — {why}")
