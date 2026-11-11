"""The rules file and its loader: cards and rules file agree; any checklist gets hypotheses."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from participant_module import rules

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "my_submission" / "assets"
CASE = {
    "assessment_target": {"target_id": "T", "type": "technology", "description": "the Richland County flood model"},
    "intended_application": "flood mapping",
    "intended_environment": "Ohio streams",
}


def test_rules_file_matches_the_cards():
    done = subprocess.run([sys.executable, str(ROOT / "harness" / "export_rules.py"), "--check"], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr


def test_every_official_criterion_has_drafted_rules(checklist):
    loaded = rules.load(ASSETS)
    for criterion in checklist["criteria"]:
        entry = loaded["criteria"][criterion["criterion_id"]]
        assert entry["hypotheses"] and entry["queries"]


def test_placeholders_are_filled_from_the_case(checklist):
    per = rules.for_case(rules.load(ASSETS), checklist, CASE)
    text = " ".join(h for entry in per.values() for h in entry["hypotheses"])
    assert "{" not in text
    assert "the Richland County flood model" in text


def test_unknown_criterion_falls_back_to_its_description():
    changed = {"version": "X", "criteria": [{"criterion_id": "NEW-1", "description": "Field trial (TRL 6): the report states that a field trial was run."}]}
    per = rules.for_case(rules.load(ASSETS), changed, CASE)
    assert per["NEW-1"]["hypotheses"] == ["The report states that a field trial was run."]
    assert per["NEW-1"]["queries"] == ["The report states that a field trial was run."]


def test_missing_rules_file_falls_back_for_every_criterion(tmp_path, checklist):
    per = rules.for_case(rules.load(tmp_path), checklist, CASE)
    assert all(entry["hypotheses"] and entry["queries"] for entry in per.values())


def test_contents_pages_are_page_traps():
    from participant_module import retrieve

    contents = "iv\nContents\n" + "".join(f"Section {n}{'.' * 40}{n}\n" for n in range(1, 6))
    body = "The model was calibrated to 16 flood events.\nIt was validated at three streamgages."
    documents = [{"document_id": "D001", "pages": [contents, body]}]
    assert retrieve.trap_pages(documents, []) == {("D001", 1)}
