"""Score a harness run: the dev score and the hard gates.

    python harness/score.py runs/<run>      # re-score a run (for example after adding labels)

- A, TRL score: the official table (PROBLEM_DESCRIPTION §13.2) against the organizer's estimated
  TRL of each public case. A proxy: those are rough estimates, not expert labels.
- B, evidence score: the official formula (§13.3) against the hand labels in brain/labels/, over
  the labelled cases of the run only. None while no case of the run is labelled.
- dev score: (0.45 A + 0.40 B) / 0.85 when B exists, else A. Runs are only comparable when they
  cover the same cases and the same labels (see `labels_hash`).
- gates: no invalid or failed result, no timeout, slowest case and peak memory within limits.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def trl_points(record: dict[str, Any], gold: int) -> float:
    result = record.get("result")
    if not record.get("ok"):
        return 0.0  # failed for any reason: invalid output, timeout, crash
    status = result["assessment_status"]
    if status == "abstained":
        return 0.25  # the public estimates always give a TRL, so it counts as determinable
    if status != "completed":
        return 0.0
    gap = abs(int(result["predicted_trl"]) - gold)
    return 1.0 if gap == 0 else 0.5 if gap == 1 else 0.0


def evidence_hits(record: dict[str, Any], label: dict[str, Any]) -> tuple[list[float], list[float]]:
    """Per labelled criterion: hits in the met part and in the not-established part."""
    met_part: list[float] = []
    other_part: list[float] = []
    result = record.get("result") if record.get("ok") else None
    for cid, gold in label["criteria"].items():
        said = result["criterion_status"].get(cid) if result else None
        if gold["status"] == "met":
            gold_pages = {(p["document_id"], int(p["page"])) for p in gold.get("pages", [])}
            first: list[tuple[str, int]] = []
            for item in (result["evidence_reference"].get(cid, []) if result else []):
                key = (item["document_id"], int(item["page"]))
                if key not in first:
                    first.append(key)
            hit = said == "met" and any(key in gold_pages for key in first[:3])
            met_part.append(1.0 if hit else 0.0)
        else:
            other_part.append(1.0 if result and said != "met" else 0.0)
    return met_part, other_part


def labels_for(case_ids: list[str]) -> dict[str, dict[str, Any]]:
    labels = {}
    for case_id in case_ids:
        path = common.LABELS / f"{case_id}.json"
        if path.exists():
            labels[case_id] = common.read_json(path)
    return labels


def score(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    case_ids = sorted(records)
    a_points = {cid: trl_points(records[cid], common.estimated_trl(cid)) for cid in case_ids}
    labels = labels_for(case_ids)
    met_all: list[float] = []
    other_all: list[float] = []
    for cid, label in labels.items():
        met, other = evidence_hits(records[cid], label)
        met_all += met
        other_all += other
    if met_all and other_all:
        b = (2 * sum(met_all) / len(met_all) + sum(other_all) / len(other_all)) / 3
    elif met_all or other_all:
        part = met_all or other_all
        b = sum(part) / len(part)
    else:
        b = None
    a = sum(a_points.values()) / len(a_points) if a_points else 0.0
    dev = (0.45 * a + 0.40 * b) / 0.85 if b is not None else a

    completed = [r for r in records.values() if r.get("ok") and r["result"]["assessment_status"] == "completed"]
    gaps = [abs(r["result"]["predicted_trl"] - common.estimated_trl(r["case_id"])) for r in completed]
    invalid = sorted(cid for cid, r in records.items() if not r.get("ok") and r.get("failure") != "TIMEOUT")
    timeouts = sorted(cid for cid, r in records.items() if r.get("failure") == "TIMEOUT")
    slowest = max(records.values(), key=lambda r: r.get("wall_s", 0.0), default={})
    peak = max((r.get("peak_rss_bytes") or 0 for r in records.values()), default=0) / 1e9
    gates = {
        "invalid_or_failed": invalid,
        "timeouts": timeouts,
        "slowest_s": round(slowest.get("wall_s", 0.0), 2),
        "slowest_case": slowest.get("case_id"),
        "peak_rss_gb": round(peak, 2),
    }
    gates["pass"] = (
        not invalid and not timeouts
        and gates["slowest_s"] <= common.GATE_SLOWEST_S
        and gates["peak_rss_gb"] <= common.GATE_PEAK_RSS_GB
    )
    return {
        "cases": len(case_ids),
        "A": round(a, 4),
        "B": None if b is None else round(b, 4),
        "dev": round(dev, 4),
        "labelled_cases": sorted(labels),
        "labels_hash": hashlib.sha256(repr(sorted(labels.items())).encode()).hexdigest()[:12],
        "trl": {
            "completed": len(completed),
            "abstained": sum(1 for r in records.values() if r.get("ok") and r["result"]["assessment_status"] == "abstained"),
            "exact": sum(1 for g in gaps if g == 0),
            "off_by_1": sum(1 for g in gaps if g == 1),
            "off_by_2_plus": sum(1 for g in gaps if g >= 2),
        },
        "gates": gates,
        "per_case_A": a_points,
    }


def load_records(run_dir: Path) -> dict[str, dict[str, Any]]:
    return {p.stem: common.read_json(p) for p in sorted((run_dir / "cases").glob("*.json"))}


def describe(summary: dict[str, Any]) -> str:
    g, t = summary["gates"], summary["trl"]
    b = "–" if summary["B"] is None else f"{summary['B']:.3f}"
    return (
        f"A {summary['A']:.3f} (exact {t['exact']}, ±1 {t['off_by_1']}, abstain {t['abstained']}) | "
        f"B {b} | dev {summary['dev']:.3f} | gates {'PASS' if g['pass'] else 'FAIL'} "
        f"(invalid {len(g['invalid_or_failed'])}, timeouts {len(g['timeouts'])}, "
        f"slowest {g['slowest_s']} s, peak {g['peak_rss_gb']} GB)"
    )


if __name__ == "__main__":
    common.ensure_kit_python()
    run_dir = Path(sys.argv[1])
    summary = score(load_records(run_dir))
    common.write_json(run_dir / "score.json", summary)
    print(describe(summary))
