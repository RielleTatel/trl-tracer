"""Sweep fast-cycle settings over a slow run's cached evidence; propose, never commit.

    python3 harness/sweep.py                       # latest slow run, default grid
    python3 harness/sweep.py runs/<run> --grid grid.json --top 10

The grid is a JSON object of setting -> list of values; every combination is replayed in
memory (no files written per combination) and scored. Prints the best combinations with their
dev score, A, B, the share of criteria judged met and the number of completed TRLs that move
off the prior, and saves everything to runs/sweeps/<timestamp>.json. Nothing under git changes:
copy a proposal into submission.json settings yourself, then confirm with harness/replay.py.
"""

from __future__ import annotations

import argparse
import itertools
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

DEFAULT_GRID: dict[str, list[Any]] = {
    "met_threshold": [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7],
    "trl_strong": [0.3, 0.4, 0.5, 0.6, 0.7],
    "trl_extreme": [0.5, 0.6, 0.7, 0.8, 0.9],
}


def met_share(records: dict[str, dict[str, Any]]) -> float:
    statuses = [s for r in records.values() if r.get("ok") for s in r["result"]["criterion_status"].values()]
    return sum(1 for s in statuses if s == "met") / len(statuses) if statuses else 0.0


def main() -> int:
    common.ensure_kit_python()
    sys.stdout.reconfigure(line_buffering=True)
    from replay import decide_all, latest_slow_run
    from score import score

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", nargs="?", type=Path)
    parser.add_argument("--grid", type=Path, help="JSON object: setting -> list of values")
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    source = args.source or latest_slow_run()
    grid = common.read_json(args.grid) if args.grid else DEFAULT_GRID
    base = dict(common.submission().get("settings", {}))
    keys = list(grid)
    rows = []
    for values in itertools.product(*(grid[k] for k in keys)):
        trial = dict(zip(keys, values))
        if trial.get("trl_extreme", 1) < trial.get("trl_strong", 0):
            continue
        settings = {**base, **trial}
        records = decide_all(source, settings)
        summary = score(records)
        prior = int(settings.get("trl_prior", 6))
        moved = sum(1 for r in records.values() if r.get("ok") and r["result"]["predicted_trl"] not in (None, prior))
        rows.append({"settings": trial, "dev": summary["dev"], "A": summary["A"], "B": summary["B"],
                     "met_share": round(met_share(records), 3), "moved_off_prior": moved,
                     "gates": summary["gates"]["pass"], "trl": summary["trl"]})
    rows.sort(key=lambda r: (-r["dev"], r["met_share"]))
    out = common.RUNS / "sweeps" / (datetime.now().strftime("%Y%m%d-%H%M%S") + ".json")
    common.write_json(out, {"source": source.name, "base_settings": base, "grid": grid, "results": rows})
    print(f"{len(rows)} combinations over {source.name}; saved {out.relative_to(common.ROOT)}")
    for r in rows[: args.top]:
        b = "–" if r["B"] is None else f"{r['B']:.3f}"
        print(f"dev {r['dev']:.4f}  A {r['A']:.4f}  B {b}  met {r['met_share']:.1%}  moved {r['moved_off_prior']:>2}  "
              f"exact/±1/2+ {r['trl']['exact']}/{r['trl']['off_by_1']}/{r['trl']['off_by_2_plus']}  {r['settings']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
