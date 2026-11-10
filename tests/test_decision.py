"""Seam 2: the pure decision step. Case evidence + checklist + settings -> result.

Tests assert only on the returned result (spec: Testing Decisions).
"""

from __future__ import annotations

import json
import re
from typing import Any

from conftest import contract_issues
from participant_module.decision import decide

TARGET = {"target_id": "T1", "type": "technology", "description": "Flood model"}
META = {"schema_version": "apctt-pdf-example-v1", "case_id": "CASE-1", "assessment_target": TARGET}

FILLER = "This page describes the study area and the data sources used in the report."
PAGES = [
    FILLER,  # p1
    "The model was calibrated to 16 flood events and validated at three stream gages in the basin. " + FILLER,  # p2
    "Water levels were simulated for the 1-percent annual exceedance flood. " + FILLER,  # p3
    "The flood maps were demon-\nstrated to county planners during the pilot study. " + FILLER,  # p4
    "The system has reached TRL 6.",  # p5: a bare TRL assertion only
    "Field measurements agreed with the simulated water surface within 0.3 feet at all gages. " + FILLER,  # p6
]


def evidence(criteria: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {
        "version": "trl-tracer-evidence-v1",
        "documents": [{"document_id": "D001", "page_count": len(PAGES), "pages": PAGES}],
        "criteria": criteria,
        **extra,
    }


def cand(page: int, entail: float, text: str | None = None) -> dict[str, Any]:
    return {"document_id": "D001", "page": page, "text": text or PAGES[page - 1], "retrieval": 1.0, "rerank": 1.0, "entail": entail}


def case_for_validator(checklist: dict[str, Any]) -> dict[str, Any]:
    return {**META, "checklist_version": checklist["version"],
            "documents": [{"document_id": "D001", "page_count": len(PAGES), "path": "/dev/null"}]}


def run(checklist: dict[str, Any], criteria: dict[str, Any], settings: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    result = decide(META, checklist, settings or {}, evidence(criteria, **extra))
    assert contract_issues(result, case_for_validator(checklist), checklist) == []
    return result


def ids(checklist: dict[str, Any]) -> list[str]:
    return [c["criterion_id"] for c in checklist["criteria"]]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"-\s*\n\s*", "", text)).strip()


def level_id(checklist: dict[str, Any], level: int) -> str:
    return next(c["criterion_id"] for c in checklist["criteria"] if f"(TRL {level})" in c["description"])


# -- empty and partial evidence -------------------------------------------------------------


def test_empty_evidence_gives_valid_completed_result_with_trl_prior(checklist):
    result = decide(META, checklist, {}, {})
    assert contract_issues(result, case_for_validator(checklist), checklist) == []
    assert result["assessment_status"] == "completed"
    assert result["predicted_trl"] == 6
    assert set(result["criterion_status"].values()) == {"insufficient evidence"}
    assert set(result["missing_evidence"]) == set(ids(checklist))


def test_criteria_missing_from_evidence_are_insufficient_with_explanation(checklist):
    cid = level_id(checklist, 6)
    result = run(checklist, {cid: {"candidates": [cand(2, 0.97)]}})
    others = [c for c in ids(checklist) if c != cid]
    assert all(result["criterion_status"][c] == "insufficient evidence" for c in others)
    assert all(result["missing_evidence"][c].strip() for c in others)


# -- met judgement --------------------------------------------------------------------------


def test_strong_candidate_is_met_with_quoted_evidence_on_the_cited_page(checklist):
    cid = level_id(checklist, 6)
    result = run(checklist, {cid: {"candidates": [cand(2, 0.97)]}})
    assert result["criterion_status"][cid] == "met"
    item = result["evidence_reference"][cid][0]
    assert (item["document_id"], item["page"]) == ("D001", 2)
    assert item["supporting_span"].strip()
    assert norm(item["supporting_span"]) in norm(PAGES[1])


def test_weak_candidate_is_not_met(checklist):
    cid = level_id(checklist, 6)
    result = run(checklist, {cid: {"candidates": [cand(2, 0.2)]}})
    assert result["criterion_status"][cid] == "insufficient evidence"
    assert result["evidence_reference"][cid] == []


def test_met_threshold_comes_from_settings(checklist):
    cid = level_id(checklist, 6)
    criteria = {cid: {"candidates": [cand(2, 0.7)]}}
    assert run(checklist, criteria, {"met_threshold": 0.65})["criterion_status"][cid] == "met"
    assert run(checklist, criteria, {"met_threshold": 0.75})["criterion_status"][cid] == "insufficient evidence"


def test_borderline_criterion_follows_the_language_model_answer(checklist):
    cid = level_id(checklist, 6)
    settings = {"met_threshold": 0.85, "borderline_low": 0.6}
    assert run(checklist, {cid: {"candidates": [cand(2, 0.7)], "llm": "met"}}, settings)["criterion_status"][cid] == "met"
    assert run(checklist, {cid: {"candidates": [cand(2, 0.7)], "llm": "not met"}}, settings)["criterion_status"][cid] == "insufficient evidence"


def test_language_model_cannot_rescue_a_score_below_the_borderline_band(checklist):
    cid = level_id(checklist, 6)
    settings = {"met_threshold": 0.85, "borderline_low": 0.6}
    result = run(checklist, {cid: {"candidates": [cand(2, 0.3)], "llm": "met"}}, settings)
    assert result["criterion_status"][cid] == "insufficient evidence"


# -- evidence pages -------------------------------------------------------------------------


def test_at_most_three_distinct_pages_strongest_first(checklist):
    cid = level_id(checklist, 6)
    cands = [cand(3, 0.90), cand(2, 0.97), cand(2, 0.95), cand(6, 0.92), cand(4, 0.91), cand(1, 0.88)]
    items = run(checklist, {cid: {"candidates": cands}})["evidence_reference"][cid]
    pages = [i["page"] for i in items]
    assert pages == [2, 6, 4]
    assert all(norm(i["supporting_span"]) in norm(PAGES[i["page"] - 1]) for i in items)


def test_max_pages_comes_from_settings(checklist):
    cid = level_id(checklist, 6)
    cands = [cand(2, 0.97), cand(6, 0.96), cand(3, 0.95)]
    items = run(checklist, {cid: {"candidates": cands}}, {"max_pages": 1})["evidence_reference"][cid]
    assert [i["page"] for i in items] == [2]


def test_candidate_on_a_page_outside_the_document_is_ignored(checklist):
    cid = level_id(checklist, 6)
    bad = {**cand(2, 0.99), "page": 99}
    result = run(checklist, {cid: {"candidates": [bad, cand(6, 0.95)]}})
    assert [i["page"] for i in result["evidence_reference"][cid]] == [6]


# -- quotations -----------------------------------------------------------------------------


def test_quotation_survives_hyphenated_line_breaks(checklist):
    cid = level_id(checklist, 6)
    result = run(checklist, {cid: {"candidates": [cand(4, 0.97, "The flood maps were demonstrated to county planners during the pilot study.")]}})
    item = result["evidence_reference"][cid][0]
    assert item["page"] == 4
    assert norm(item["supporting_span"]) in norm(PAGES[3])


def test_text_not_on_the_cited_page_is_never_quoted(checklist):
    cid = level_id(checklist, 6)
    invented = cand(1, 0.99, "The prototype was demonstrated in the operational environment for two years.")
    result = run(checklist, {cid: {"candidates": [invented]}})
    assert result["criterion_status"][cid] == "insufficient evidence"
    assert result["evidence_reference"][cid] == []


def test_bare_trl_assertion_is_never_used_as_evidence(checklist):
    cid = level_id(checklist, 6)
    result = run(checklist, {cid: {"candidates": [cand(5, 0.99)]}})
    assert result["criterion_status"][cid] == "insufficient evidence"
    assert "quot" in result["missing_evidence"][cid].lower()


def test_quotation_length_is_limited(checklist):
    cid = level_id(checklist, 6)
    long_sentence = "The model was evaluated " + "and checked again " * 40 + "at every gage."
    pages = [long_sentence]
    ev = {"version": "trl-tracer-evidence-v1",
          "documents": [{"document_id": "D001", "page_count": 1, "pages": pages}],
          "criteria": {cid: {"candidates": [{"document_id": "D001", "page": 1, "text": long_sentence, "entail": 0.97}]}}}
    result = decide(META, checklist, {"span_max_chars": 120}, ev)
    span = result["evidence_reference"][cid][0]["supporting_span"]
    assert 0 < len(span) <= 120
    assert norm(span) in norm(long_sentence)


# -- TRL rule -------------------------------------------------------------------------------


def trl_of(checklist, met_levels: dict[int, float], settings: dict[str, Any] | None = None) -> int | None:
    criteria = {level_id(checklist, level): {"candidates": [cand(2, score)]} for level, score in met_levels.items()}
    return run(checklist, criteria, settings)["predicted_trl"]


def test_no_level_met_gives_the_prior(checklist):
    assert trl_of(checklist, {}) == 6
    assert trl_of(checklist, {}, {"trl_prior": 7}) == 7


def test_highest_strongly_met_level_inside_the_band(checklist):
    assert trl_of(checklist, {5: 0.97}) == 5
    assert trl_of(checklist, {4: 0.97, 5: 0.96, 7: 0.95}) == 7
    assert trl_of(checklist, {6: 0.97, 7: 0.93}) == 7


def test_levels_above_the_band_need_very_strong_evidence(checklist):
    assert trl_of(checklist, {6: 0.97, 9: 0.99}) == 9
    assert trl_of(checklist, {6: 0.97, 9: 0.92}) == 7


def test_weakly_met_levels_are_clamped_to_the_band(checklist):
    settings = {"met_threshold": 0.8, "trl_strong": 0.9}
    assert trl_of(checklist, {8: 0.85}, settings) == 7
    assert trl_of(checklist, {4: 0.85}, settings) == 5


def test_clearly_early_stage_evidence_moves_below_the_band(checklist):
    assert trl_of(checklist, {3: 0.99}) == 3
    assert trl_of(checklist, {4: 0.92}) == 5  # strong but not very strong: stay in the band


def test_completed_result_has_rationale_and_interval_containing_the_trl(checklist):
    result = run(checklist, {level_id(checklist, 6): {"candidates": [cand(2, 0.97)]}})
    assert result["trl_rationale"].strip()
    interval = result["uncertainty"]
    assert interval["lower"] <= result["predicted_trl"] <= interval["upper"]
    assert 0 <= result["confidence"] <= 1


# -- abstention, checklist, determinism -----------------------------------------------------


def test_out_of_scope_flag_abstains_with_that_reason(checklist):
    result = run(checklist, {}, scope="out")
    assert result["assessment_status"] == "abstained"
    assert result["abstention_reason"] == "out of scope"
    assert result["predicted_trl"] is None


def test_changed_checklist_uses_its_ids_and_falls_back_to_the_prior():
    changed = {"version": "TEST-CHECKLIST", "criteria": [
        {"criterion_id": "X-1", "description": "The report states a field test."},
        {"criterion_id": "X-2", "description": "The report compares results with requirements."},
    ]}
    result = run(changed, {"X-1": {"candidates": [cand(2, 0.97)]}})
    assert set(result["criterion_status"]) == {"X-1", "X-2"}
    assert result["criterion_status"]["X-1"] == "met"
    assert result["predicted_trl"] == 6


def test_same_input_gives_identical_output(checklist):
    criteria = {level_id(checklist, 6): {"candidates": [cand(3, 0.9), cand(2, 0.97), cand(6, 0.9)]}}
    first = json.dumps(run(checklist, criteria), sort_keys=True)
    second = json.dumps(run(checklist, criteria), sort_keys=True)
    assert first == second


def test_ties_are_broken_by_page_order(checklist):
    cid = level_id(checklist, 6)
    items = run(checklist, {cid: {"candidates": [cand(6, 0.95), cand(2, 0.95)]}})["evidence_reference"][cid]
    assert [i["page"] for i in items] == [2, 6]
