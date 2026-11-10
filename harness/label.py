"""Hand-label a public case: per criterion, its status and gold pages, plus your own TRL.

    python3 harness/label.py USGS-SDG-012            # uses the latest run that has this case
    python3 harness/label.py USGS-SDG-012 --run runs/<run>

Writes brain/labels/<case_id>.json after every decision (stop any time with `quit`, run again to
resume) and appends one capture per decision to brain/captures.jsonl for the criterion cards.

Read before you look: for each criterion, skim the report (`toc`, `page N`, `find word`) and
form your own view first; `cands` then shows the pipeline's candidate pages. Looking at the
candidates first biases you towards agreeing with the pipeline, which inflates the evidence score.

Commands at each criterion:
    toc                 first lines of every page          page N        full text of page N
    find WORDS          pages containing all the words     cands         the pipeline's candidates
    met P[,P...]        criterion met; gold pages P        not           criterion not met
    ins                 insufficient evidence              note TEXT     note for this criterion
    trap N              candidate N looks like evidence but is not (a capture for the card)
    back                previous criterion                 skip          next, unlabelled
    quit                save and stop
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

STATUSES = {"met": "met", "not": "not met", "ins": "insufficient evidence"}


def latest_run_with(case_id: str) -> Path:
    runs = sorted((p for p in common.RUNS.iterdir() if (p / "cases" / f"{case_id}.json").exists()), reverse=True)
    for run in runs:
        record = common.read_json(run / "cases" / f"{case_id}.json")
        if isinstance(record.get("evidence"), dict) and record["evidence"].get("documents"):
            return run
    raise SystemExit(f"no run with cached evidence for {case_id}: run python3 harness/run.py --cases {case_id}")


def capture(entry: dict[str, Any]) -> None:
    common.CAPTURES.parent.mkdir(parents=True, exist_ok=True)
    with common.CAPTURES.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"date": date.today().isoformat(), **entry}, ensure_ascii=False) + "\n")


class Session:
    def __init__(self, case_id: str, run: Path) -> None:
        self.case_id = case_id
        self.entry = common.manifest_cases()[case_id]
        record = common.read_json(run / "cases" / f"{case_id}.json")
        self.evidence = record["evidence"]
        self.pages = {d["document_id"]: d["pages"] for d in self.evidence["documents"]}
        self.doc = self.evidence["documents"][0]["document_id"]
        self.criteria = common.checklist()["criteria"]
        self.path = common.LABELS / f"{case_id}.json"
        self.label = (common.read_json(self.path) if self.path.exists()
                      else {"case_id": case_id, "trl": None, "criteria": {}, "source_run": run.name})

    def save(self) -> None:
        common.write_json(self.path, self.label)

    def show_page(self, number: int) -> None:
        pages = self.pages[self.doc]
        if not 1 <= number <= len(pages):
            print(f"  pages are 1-{len(pages)}")
            return
        print(f"--- {self.doc} page {number} ---\n{pages[number - 1].strip() or '(no text on this page)'}\n---")

    def toc(self) -> None:
        for number, text in enumerate(self.pages[self.doc], start=1):
            first = " ".join(text.split())[:100]
            print(f"  p{number:>3}: {first}")

    def find(self, words: list[str]) -> None:
        wanted = [w.lower() for w in words]
        hits = [n for n, t in enumerate(self.pages[self.doc], start=1) if all(w in t.lower() for w in wanted)]
        print(f"  pages with {' '.join(words)!r}: {hits or 'none'}")

    def candidates(self, cid: str) -> list[dict[str, Any]]:
        found = self.evidence["criteria"].get(cid, {}).get("candidates", [])
        return sorted(found, key=lambda c: -c.get("entail", 0.0))

    def show_candidates(self, cid: str) -> None:
        for n, c in enumerate(self.candidates(cid), start=1):
            sentence = (c.get("sentences") or [c["text"]])[0]
            print(f"  [{n}] p{c['page']} entail={c.get('entail', 0):.2f}: {sentence[:220]}")

    def label_criterion(self, index: int) -> int | None:
        """Returns the next criterion index, or None to quit."""
        criterion = self.criteria[index]
        cid = criterion["criterion_id"]
        current = self.label["criteria"].get(cid, {})
        print(f"\n[{index + 1}/{len(self.criteria)}] {cid}: {criterion['description']}")
        if current:
            print(f"  current: {current.get('status')} pages {[p['page'] for p in current.get('pages', [])]}")
        note = current.get("note", "")
        while True:
            try:
                line = input(f"{cid}> ").strip()
            except EOFError:
                return None
            command, _, rest = line.partition(" ")
            if command == "quit":
                return None
            if command == "back":
                return max(0, index - 1)
            if command == "skip":
                return index + 1
            if command == "toc":
                self.toc()
            elif command == "page" and rest.strip().isdigit():
                self.show_page(int(rest))
            elif command == "find" and rest.strip():
                self.find(rest.split())
            elif command == "cands":
                self.show_candidates(cid)
            elif command == "note":
                note = rest.strip()
                print("  note kept")
            elif command == "trap" and rest.strip().isdigit():
                found = self.candidates(cid)
                n = int(rest)
                if 1 <= n <= len(found):
                    c = found[n - 1]
                    capture({"case_id": self.case_id, "criterion": cid, "page": c["page"], "verdict": "trap",
                             "quote": (c.get("sentences") or [c["text"]])[0], "why": note})
                    print(f"  trap captured: candidate {n} (p{c['page']})")
            elif command in STATUSES:
                pages: list[int] = []
                if command == "met":
                    try:
                        pages = [int(p) for p in rest.replace(",", " ").split()]
                    except ValueError:
                        pages = []
                    count = len(self.pages[self.doc])
                    if not pages or not all(1 <= p <= count for p in pages):
                        print(f"  give the gold pages, e.g. 'met 7,12' (pages 1-{count})")
                        continue
                self.label["criteria"][cid] = {
                    "status": STATUSES[command],
                    "pages": [{"document_id": self.doc, "page": p} for p in pages],
                    "note": note,
                }
                self.save()
                if command == "met":
                    capture({"case_id": self.case_id, "criterion": cid, "page": pages[0], "verdict": "met",
                             "quote": " ".join(self.pages[self.doc][pages[0] - 1].split())[:300], "why": note})
                return index + 1
            else:
                print("  commands: toc | page N | find WORDS | cands | met P,P | not | ins | note TEXT | trap N | back | skip | quit")

    def run(self) -> None:
        e = self.entry
        print(f"{self.case_id}: {e['title']}\n  target: {e['assessment_target']['description']} "
              f"({e['assessment_target']['type']})\n  application: {e['intended_application']}\n"
              f"  environment: {e['intended_environment']}\n  pdf: {common.PDF_DIR / (self.case_id + '.pdf')}\n"
              "Read before you look: skim the report (toc / page N / find) before `cands`.")
        index = next((i for i, c in enumerate(self.criteria) if c["criterion_id"] not in self.label["criteria"]),
                     len(self.criteria))
        while index is not None and index < len(self.criteria):
            index = self.label_criterion(index)
        if index is None:
            print(f"saved {self.path} ({len(self.label['criteria'])}/{len(self.criteria)} criteria); run again to resume")
            return
        if self.label.get("trl") is None:
            try:
                answer = input("Your own TRL estimate for this case (1-9, blank to skip): ").strip()
            except EOFError:
                answer = ""
            if answer.isdigit() and 1 <= int(answer) <= 9:
                self.label["trl"] = int(answer)
        self.save()
        print(f"done: {self.path}. Organizer's estimate was TRL {e['reference_labels']['estimated_trl']} "
              f"(\"{e['reference_labels']['rationale']}\"). Captures appended to {common.CAPTURES}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("case_id")
    parser.add_argument("--run", type=Path)
    args = parser.parse_args()
    Session(args.case_id, args.run or latest_run_with(args.case_id)).run()
