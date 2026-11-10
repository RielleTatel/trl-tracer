"""Safeguard for the AI-made (silver) labels: check them against the report and the organizer.

    python3 harness/check_labels.py               # every label file in brain/labels/
    python3 harness/check_labels.py USGS-SDG-012

The labels are made blind (without the organizer's estimate). This compares them with:
1. the contract: all 12 criteria, valid statuses, met criteria with in-range gold pages;
2. the report: every quote is verbatim on its first gold page (after whitespace normalisation);
3. the organizer's reference label (option 3): the label's TRL is within 1 of the organizer's
   estimated TRL, and the organizer's one-sentence reason overlaps a met criterion's quote/note.

Prints FLAG lines for a human spot-check; exit code 1 if any flag.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

STATUSES = {"met", "not met", "insufficient evidence"}
_WORD = re.compile(r"[a-z0-9]+")
_STOP = set("the a an and of to in for on with by was were is are this that from as at be it its used using".split())


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)).strip().lower()


def words(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 2}


def page_texts(case_id: str) -> list[str]:
    """Page text as the labellers saw it (runs/labelling/<case>.txt)."""
    text = (common.RUNS / "labelling" / f"{case_id}.txt").read_text(encoding="utf-8")
    parts = re.split(r"\n=== PAGE (\d+) ===\n", text)
    return [parts[i + 1] for i in range(1, len(parts) - 1, 2)]


def check(case_id: str) -> list[str]:
    flags: list[str] = []
    label = common.read_json(common.LABELS / f"{case_id}.json")
    entry = common.manifest_cases()[case_id]
    pages = page_texts(case_id)
    ids = [c["criterion_id"] for c in common.checklist()["criteria"]]
    levels = {c["criterion_id"]: int(m.group(1)) for c in common.checklist()["criteria"]
              if (m := re.search(r"\(TRL (\d)\)", c["description"]))}

    missing = [cid for cid in ids if cid not in label.get("criteria", {})]
    if missing:
        flags.append(f"missing criteria: {missing}")
    met_text = []
    for cid, item in label.get("criteria", {}).items():
        status = item.get("status")
        if status not in STATUSES:
            flags.append(f"{cid}: invalid status {status!r}")
            continue
        if status != "met":
            continue
        cited = [p.get("page") for p in item.get("pages", [])]
        if not cited or not all(isinstance(p, int) and 1 <= p <= len(pages) for p in cited):
            flags.append(f"{cid}: met without valid gold pages {cited}")
            continue
        quote = item.get("quote", "")
        if not quote or norm(quote) not in norm(pages[cited[0] - 1]):
            flags.append(f"{cid}: quote not found verbatim on page {cited[0]}: {quote[:90]!r}")
        met_text.append(f"{quote} {item.get('note', '')}")

    estimated = entry["reference_labels"]["estimated_trl"]
    reason = entry["reference_labels"]["rationale"]
    trl = label.get("trl")
    if not isinstance(trl, int):
        flags.append("no TRL estimate in the label")
    elif abs(trl - estimated) >= 2:
        flags.append(f"TRL {trl} vs organizer estimate {estimated} (gap {abs(trl - estimated)}): "
                     f"organizer's reason: \"{reason}\"")
    met_levels = sorted(levels[c] for c, i in label.get("criteria", {}).items() if i.get("status") == "met" and c in levels)
    if met_levels and abs(max(met_levels) - estimated) >= 2:
        flags.append(f"highest met level is TRL {max(met_levels)} vs organizer estimate {estimated}")
    overlap = words(reason) & words(" ".join(met_text))
    if len(overlap) < 2:
        flags.append(f"organizer's reason not reflected in any met criterion (shared words: {sorted(overlap)}): \"{reason}\"")
    return flags


if __name__ == "__main__":
    targets = sys.argv[1:] or sorted(p.stem for p in common.LABELS.glob("USGS-SDG-*.json"))
    flagged = 0
    for case_id in targets:
        label = common.read_json(common.LABELS / f"{case_id}.json")
        met = [c[-3:] for c, i in label["criteria"].items() if i.get("status") == "met"]
        estimated = common.manifest_cases()[case_id]["reference_labels"]["estimated_trl"]
        flags = check(case_id)
        flagged += bool(flags)
        print(f"{case_id}: label TRL {label.get('trl')} | organizer {estimated} | met {met} | "
              f"{'OK' if not flags else str(len(flags)) + ' flag(s)'}")
        for flag in flags:
            print(f"   FLAG {flag}")
    print(f"{len(targets)} label file(s), {flagged} with flags")
    sys.exit(1 if flagged else 0)
