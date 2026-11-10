"""Export the criterion cards' distilled sections into the package's rules file.

    python3 harness/export_rules.py           # write my_submission/assets/criteria_rules.json
    python3 harness/export_rules.py --check   # exit 1 if the rules file is out of date

The cards in brain/criteria/ are the source you edit (Capture -> Organize -> Distill); this is
the Express step. Each card's title line names its criterion ID (`# APCTT-C06 — ...`); its
`## Distilled` section has `- Hypotheses:`, `- Search phrases:` and `- Trap cues:` lists.
`00-global.md` holds `- Page traps:`. Placeholder items in parentheses are skipped.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "brain" / "criteria"
RULES = ROOT / "my_submission" / "assets" / "criteria_rules.json"
VERSION = "trl-tracer-rules-v1"

FIELDS = {"hypotheses": "hypotheses", "search phrases": "queries", "trap cues": "traps", "page traps": "page_traps"}


def distilled(text: str) -> dict[str, list[str]]:
    match = re.search(r"^## Distilled.*?$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    out: dict[str, list[str]] = {}
    current = None
    for line in (match.group(1) if match else "").splitlines():
        head = re.match(r"^- ([A-Za-z ]+):\s*$", line)
        item = re.match(r"^\s+- (.+?)\s*$", line)
        if head:
            current = FIELDS.get(head.group(1).strip().lower())
            if current:
                out.setdefault(current, [])
        elif item and current and not item.group(1).startswith("("):
            out[current].append(item.group(1))
    return out


def build() -> dict[str, Any]:
    rules: dict[str, Any] = {"version": VERSION, "global": {}, "criteria": {}}
    for card in sorted(CARDS.glob("*.md")):
        text = card.read_text(encoding="utf-8")
        fields = distilled(text)
        if card.name.startswith("00-"):
            rules["global"].update(fields)
            continue
        title = re.match(r"^# (\S+)", text)
        if not title:
            raise SystemExit(f"{card.name}: the first line must be '# <criterion ID> — <name>'")
        rules["criteria"][title.group(1)] = {k: fields.get(k, []) for k in ("hypotheses", "queries", "traps")}
    return rules


def render(rules: dict[str, Any]) -> str:
    return json.dumps(rules, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    text = render(build())
    if "--check" in sys.argv:
        current = RULES.read_text(encoding="utf-8") if RULES.exists() else ""
        if current != text:
            sys.exit("criteria_rules.json is out of date: run python3 harness/export_rules.py")
        print("criteria_rules.json matches the cards")
    else:
        RULES.write_text(text, encoding="utf-8")
        rules = json.loads(text)
        print(f"wrote {RULES.relative_to(ROOT)}: {len(rules['criteria'])} criteria, "
              f"{sum(len(c['hypotheses']) for c in rules['criteria'].values())} hypotheses")
