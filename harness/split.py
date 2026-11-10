"""Make the fixed tuning / held-out split of the 99 public cases (once).

    python harness/split.py            # writes brain/split.json; refuses to overwrite
    python harness/split.py --force

70 tuning and 29 held-out cases, stratified by the organizer's estimated TRL and spread over
the SDGs, with a fixed seed. The smoke cases and the only TRL-4 and TRL-8 cases stay in the
tuning set, so they can be hand-labelled.
"""

from __future__ import annotations

import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

HELDOUT = 29
SEED = 2026


def make_split() -> dict[str, list[str]]:
    cases = common.manifest_cases()
    keep = set(common.smoke_case_ids())
    by_trl: dict[int, list[str]] = defaultdict(list)
    for case_id, entry in sorted(cases.items()):
        by_trl[entry["reference_labels"]["estimated_trl"]].append(case_id)

    rng = random.Random(SEED)
    targets = {trl: (round(len(ids) * HELDOUT / len(cases)) if len(ids) > 1 else 0) for trl, ids in by_trl.items()}
    largest = max(by_trl, key=lambda trl: len(by_trl[trl]))
    targets[largest] += HELDOUT - sum(targets.values())

    heldout: list[str] = []
    for trl, ids in sorted(by_trl.items()):
        # Round-robin over SDGs after a seeded shuffle, so each band's held-out cases span SDGs.
        by_sdg: dict[int, list[str]] = defaultdict(list)
        for case_id in ids:
            if case_id not in keep:
                by_sdg[cases[case_id]["sdg"]].append(case_id)
        for group in by_sdg.values():
            rng.shuffle(group)
        order: list[str] = []
        while any(by_sdg.values()):
            for sdg in sorted(by_sdg):
                if by_sdg[sdg]:
                    order.append(by_sdg[sdg].pop())
        heldout += order[: targets[trl]]
    tuning = sorted(set(cases) - set(heldout))
    return {"seed": SEED, "tuning": tuning, "heldout": sorted(heldout)}


if __name__ == "__main__":
    if common.SPLIT.exists() and "--force" not in sys.argv:
        sys.exit("brain/split.json exists; use --force to replace it (this changes every comparison)")
    split = make_split()
    common.write_json(common.SPLIT, split)
    cases = common.manifest_cases()
    for name in ("tuning", "heldout"):
        trls: dict[int, int] = defaultdict(int)
        for case_id in split[name]:
            trls[cases[case_id]["reference_labels"]["estimated_trl"]] += 1
        print(f"{name:<8} {len(split[name]):>3} cases  TRL counts {dict(sorted(trls.items()))}")
