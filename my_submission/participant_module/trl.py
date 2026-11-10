"""The TRL rule: from met criteria to a predicted TRL.

Not a strict ladder (reports often skip early stages). Start from the prior; move to the
highest level criterion met with a strong score; leave the band only on very strong evidence;
go below the band only when the evidence is clearly early-stage. Levels come from the
checklist text "(TRL n)", so no criterion ID is hard-coded.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

_LEVEL = re.compile(r"\(TRL\s*([1-9])\)")


def criterion_levels(checklist: Mapping[str, Any]) -> dict[str, int]:
    levels = {}
    for criterion in checklist["criteria"]:
        match = _LEVEL.search(criterion.get("description", ""))
        if match:
            levels[criterion["criterion_id"]] = int(match.group(1))
    return levels


def predict(met_scores: Mapping[str, float], levels: Mapping[str, int], settings: Mapping[str, Any]) -> tuple[int, str]:
    """`met_scores`: criterion ID -> best support score, for met criteria. Returns (TRL, reason)."""
    prior = int(settings["trl_prior"])
    low, high = (int(v) for v in settings["trl_band"])
    strong, extreme = float(settings["trl_strong"]), float(settings["trl_extreme"])

    met_levels = {levels[c]: max(s, 0.0) for c, s in met_scores.items() if c in levels}
    by_level: dict[int, float] = {}
    for cid, score in met_scores.items():
        if cid in levels:
            by_level[levels[cid]] = max(by_level.get(levels[cid], 0.0), score)
    if not by_level:
        return prior, f"No level criterion is met; the prior TRL {prior} is used."

    strong_levels = {lvl: s for lvl, s in by_level.items() if s >= strong}
    if strong_levels:
        top = max(strong_levels)
        score = strong_levels[top]
        if low <= top <= high:
            return top, f"TRL {top} is the highest level criterion met with strong support ({score:.2f})."
        if top > high:
            if score >= extreme:
                return top, f"TRL {top} is met with very strong support ({score:.2f})."
            return high, f"TRL {top} is met ({score:.2f}) but not very strongly; capped at TRL {high}."
        early = all(lvl < low for lvl in met_levels)
        if early and score >= extreme:
            return top, f"All met level criteria are early-stage; TRL {top} is met with very strong support ({score:.2f})."
        return low, f"The strongest met level is TRL {top} ({score:.2f}); raised to TRL {low}."

    weak_top = max(by_level)
    if not settings.get("trl_weak_moves", False):
        return prior, f"Level criteria are met only weakly (highest TRL {weak_top}); the prior TRL {prior} is kept."
    clamped = min(max(weak_top, low), high)
    return clamped, f"Level criteria are met only weakly (highest TRL {weak_top}); kept within TRL {low}-{high}."
