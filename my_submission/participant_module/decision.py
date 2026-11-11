"""The decision step: case evidence + checklist + settings -> a complete, contract-valid result.

Pure and deterministic: no models, no files, no network. The harness's fast cycle replays it
over cached case evidence, and the tests drive it directly (spec: the decision step interface).

Case evidence record (plain JSON, may be partial or empty):

    {"version": "trl-tracer-evidence-v1",
     "documents": [{"document_id": "D001", "page_count": 44, "pages": ["text of page 1", ...]}],
     "criteria": {"<criterion_id>": {
         "candidates": [{"document_id", "page", "text", "retrieval", "rerank", "entail",
                         "sentences"?: ["ranked sentence", ...]}],
         "llm": "met" | "not met" | null,  "llm_p": P(yes) from the language model | absent}},
     "skipped": {"ocr": bool, "llm": bool, ...},
     "scope": "out"?}
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from participant_module import quotes, trl

DEFAULTS: dict[str, Any] = {
    "met_threshold": 0.85,  # best support score at or above this: met
    "borderline_low": 0.60,  # [borderline_low, met_threshold): met only if the language model says so
    "llm_yes": 0.5,  # language-model P(yes) needed to confirm a borderline criterion
    "max_pages": 3,  # distinct pages cited per met criterion (only the first 3 are scored)
    "page_min_score": 0.60,  # extra pages must reach this score
    "span_min_chars": 30,
    "span_max_chars": 300,
    "purpose_quote_ok": [],  # criterion IDs for which a purpose statement is good evidence (intended use)
    "met_threshold_by_criterion": {},  # criterion ID -> its own met threshold (extra pages use the lower bar too)
    "derived_any_met": [],  # criterion IDs met by another met criterion's evidence (if present in the checklist)
    "trl_prior": 6,
    "trl_prior_by_target": [],  # [{"any": [words], "trl": n}]: the first rule whose word is in the target description sets the prior; no "any" always matches
    "trl_band": [5, 7],
    "trl_strong": 0.90,
    "trl_extreme": 0.95,
    "trl_weak_moves": False,
    "trl_below_prior": "no_higher_met",  # strong level below the prior: "always" | "no_higher_met" (only if no level >= prior is met) | "never"  # spec: only strongly met levels move the TRL; True clamps weak ones to the band
}


def settings_with_defaults(settings: Mapping[str, Any]) -> dict[str, Any]:
    return {**DEFAULTS, **{k: v for k, v in settings.items() if k in DEFAULTS}}


def _page_texts(evidence: Mapping[str, Any]) -> dict[str, list[str]]:
    texts = {}
    for document in evidence.get("documents", []) or []:
        pages = list(document.get("pages", []) or [])
        count = int(document.get("page_count", len(pages)))
        texts[document["document_id"]] = pages[:count]
    return texts


def _judge(cid: str, entry: Mapping[str, Any], pages: Mapping[str, list[str]], s: Mapping[str, Any]
           ) -> tuple[str, list[dict[str, Any]], str, float]:
    """Returns (status, evidence items, explanation, best score)."""
    usable = []
    for c in entry.get("candidates", []) or []:
        doc_pages = pages.get(c.get("document_id"))
        page = c.get("page")
        if doc_pages is None or not isinstance(page, int) or not 1 <= page <= len(doc_pages):
            continue
        usable.append(c)
    if not usable:
        return "insufficient evidence", [], "No passage in the reports was found for this criterion.", 0.0

    own = (s.get("met_threshold_by_criterion") or {}).get(cid)
    if isinstance(own, (int, float)):
        s = {**s, "met_threshold": float(own), "page_min_score": min(float(s["page_min_score"]), float(own))}
    usable.sort(key=lambda c: (-float(c.get("entail", 0.0)), c["document_id"], c["page"]))
    best = float(usable[0].get("entail", 0.0))
    where = f"document {usable[0]['document_id']}, page {usable[0]['page']}"
    if best >= s["met_threshold"]:
        judged_met = True
    elif best >= s["borderline_low"] and (entry.get("llm") == "met" or (
            isinstance(entry.get("llm_p"), (int, float)) and entry["llm_p"] >= s["llm_yes"])):
        judged_met = True
    else:
        if best >= s["borderline_low"]:
            why = (f"The best passage ({where}) is borderline (score {best:.2f}) and the second "
                   "check did not confirm it.")
        else:
            why = f"The best passage ({where}) does not support this criterion strongly enough (score {best:.2f})."
        return "insufficient evidence", [], why, best

    items: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for c in usable:
        key = (c["document_id"], c["page"])
        score = float(c.get("entail", 0.0))
        if key in seen or (items and score < s["page_min_score"]):
            continue
        span = quotes.quotation(
            c.get("text", ""), pages[c["document_id"]][c["page"] - 1],
            min_chars=int(s["span_min_chars"]), max_chars=int(s["span_max_chars"]),
            ranked=c.get("sentences"), purpose_ok=cid in (s.get("purpose_quote_ok") or []),
        )
        if span is None:
            continue
        seen.add(key)
        items.append({"document_id": c["document_id"], "page": c["page"], "supporting_span": span})
        if len(items) >= int(s["max_pages"]):
            break
    if not items:
        return ("insufficient evidence", [],
                "Candidate pages were found, but none has a quotable sentence that describes the evidence.", best)
    return "met", items, f"Supported on {where} (score {best:.2f}).", best


def decide(meta: Mapping[str, Any], checklist: Mapping[str, Any], settings: Mapping[str, Any],
           evidence: Mapping[str, Any] | None) -> dict[str, Any]:
    s = settings_with_defaults(settings or {})
    evidence = evidence or {}
    pages = _page_texts(evidence)
    entries = evidence.get("criteria", {}) or {}
    ids = [c["criterion_id"] for c in checklist["criteria"]]

    status: dict[str, str] = {}
    references: dict[str, list[dict[str, Any]]] = {}
    missing: dict[str, str] = {}
    rationale: dict[str, str] = {}
    met_scores: dict[str, float] = {}
    for cid in ids:
        verdict, items, why, best = _judge(cid, entries.get(cid, {}) or {}, pages, s)
        status[cid], references[cid] = verdict, items
        if verdict == "met":
            met_scores[cid] = best
            rationale[cid] = why
        else:
            missing[cid] = why

    # Derived criteria (e.g. "the cited evidence concerns the assessed target itself"): when not
    # met on their own evidence, they are met by the strongest other met criterion's evidence.
    # Their status never feeds the TRL rule.
    for cid in [c for c in s["derived_any_met"] if c in status and status[c] != "met"]:
        donors = sorted((c for c in met_scores if c != cid and c not in s["derived_any_met"]),
                        key=lambda c: (-met_scores[c], ids.index(c)))
        if donors:
            status[cid], references[cid] = "met", [dict(item) for item in references[donors[0]]]
            missing.pop(cid, None)
            rationale[cid] = f"The evidence cited for {donors[0]} concerns the assessed target itself."

    result: dict[str, Any] = {
        "schema_version": meta["schema_version"],
        "checklist_version": checklist["version"],
        "case_id": meta["case_id"],
        "assessment_target": dict(meta["assessment_target"]),
        "criterion_status": status,
        "evidence_reference": references,
        "missing_evidence": missing,
        "error_code": None,
    }
    if rationale:
        result["criterion_rationale"] = rationale

    if evidence.get("scope") == "out":
        result.update(assessment_status="abstained", predicted_trl=None, abstention_reason="out of scope")
        return result

    levels = trl.criterion_levels(checklist)
    description = str((meta.get("assessment_target") or {}).get("description", ""))
    s = {**s, "trl_prior": trl.target_prior(description, s)}
    predicted, reason = trl.predict(met_scores, levels, s)
    quality_ids = [cid for cid in ids if cid not in levels]
    quality_met = sum(1 for cid in quality_ids if status[cid] == "met")
    quality_share = quality_met / len(quality_ids) if quality_ids else 0.0
    strong = any(score >= s["trl_strong"] for cid, score in met_scores.items() if cid in levels)
    confidence = round(min(1.0, 0.4 + 0.2 * quality_share + (0.2 if strong else 0.0)), 2)
    result.update(
        assessment_status="completed",
        predicted_trl=predicted,
        abstention_reason=None,
        trl_rationale=reason,
        confidence=confidence,
        uncertainty={"kind": "trl_interval", "lower": max(1, predicted - 1), "upper": min(9, predicted + 1)},
    )
    return result
