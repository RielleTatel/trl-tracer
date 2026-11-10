"""Second opinion: a small language model's P(yes) that a passage meets a criterion.

qwen3-0.6b (Apache-2.0) with thinking off reads the criterion, the assessed target and the best
candidate passage, and the probability of the next token "yes" versus "no" is read from one
forward pass: deterministic, about a second per criterion on a laptop CPU, and it never writes
text (so it can never invent a quotation). Loaded only after text extraction and judging, and
only while enough time remains; each criterion is asked at most once, best candidates first.
Only criteria in the borderline band [borderline_low, met_threshold) are asked, and the decision
step uses the answer only there (see decision.py).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

DEFAULTS: dict[str, Any] = {
    "llm_max_calls": 12,  # criteria asked per case
    "llm_min_remaining_ms": 60_000,  # load the model only if at least this much time is left
    "llm_max_passage_chars": 900,
}

SYSTEM = ("You check evidence in technical reports for a technology readiness assessment. "
          "For models, software and data products, read hardware words by analogy: a prototype is a "
          "working version of the product, a relevant environment is real data or sites like the "
          "intended ones. Answer yes only if the passage itself reports what was actually done, tested, "
          "found or used that satisfies the criterion. Answer no for purpose statements, plans, background, "
          "figure captions, lists, or anything that does not clearly satisfy this specific criterion. "
          "Answer with one word: yes or no.")

_EXAMPLE = ("Assessed technology: a groundwater flow model\nCriterion: Relevant-environment validation (TRL 5): the "
            "report states that the component was tested in a relevant environment and reports the results.\n"
            "Passage from the report: {p}\nDoes the passage show that the criterion is met for the assessed "
            "technology? Answer yes or no.")
EXAMPLES = [  # two worked examples: without them the model answers "yes" to everything (P(yes) about 0.99)
    {"role": "user", "content": _EXAMPLE.format(p="The model was calibrated to water levels measured in 42 wells "
                                                  "from 2010 to 2015; the mean absolute error was 1.8 ft.")},
    {"role": "assistant", "content": "yes"},
    {"role": "user", "content": _EXAMPLE.format(p="The purpose of this report is to describe the development and "
                                                  "calibration of a groundwater flow model for the basin.")},
    {"role": "assistant", "content": "no"},
]


def load(path: Any) -> dict[str, Any]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(path, local_files_only=True, dtype=torch.float32).eval()
    yes = tokenizer.encode("yes", add_special_tokens=False)[0]
    no = tokenizer.encode("no", add_special_tokens=False)[0]
    return {"tokenizer": tokenizer, "model": model, "yes": yes, "no": no}


def p_yes(llm: Mapping[str, Any], criterion: str, target: str, passage: str) -> float:
    import torch

    tokenizer, model = llm["tokenizer"], llm["model"]
    messages = [
        {"role": "system", "content": SYSTEM},
        *EXAMPLES,
        {"role": "user", "content": (f"Assessed technology: {target}\nCriterion: {criterion}\n"
                                     f"Passage from the report: {passage}\n"
                                     "Does the passage show that the criterion is met for the assessed technology? "
                                     "Answer yes or no.")},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    encoded = tokenizer(text, return_tensors="pt")
    with torch.inference_mode():
        logits = model(**encoded).logits[0, -1].float()
    pair = torch.softmax(logits[[llm["yes"], llm["no"]]], dim=-1)
    return round(float(pair[0]), 4)


def second_opinion(criteria: dict[str, dict[str, Any]], checklist: Mapping[str, Any], case: Mapping[str, Any],
                   load_llm: Callable[[], Any] | None, settings: Mapping[str, Any],
                   remaining_ms: Callable[[], float], has_time: Callable[[], bool], skipped: dict[str, Any]) -> None:
    """Adds `llm_p` (and `llm_page`) to criteria entries, in place."""
    s = {**DEFAULTS, **{k: v for k, v in settings.items() if k in DEFAULTS}}
    from participant_module.decision import settings_with_defaults

    band = settings_with_defaults(settings)
    low, high = float(band["borderline_low"]), float(band["met_threshold"])
    asked = [(best, cid) for cid, e in criteria.items() if e["candidates"]
             for best in [max(c.get("entail", 0.0) for c in e["candidates"])] if low <= best < high]
    if not asked or load_llm is None:
        skipped["llm"] = load_llm is None
        return
    if remaining_ms() < float(s["llm_min_remaining_ms"]):
        skipped["llm"] = True
        return
    llm = load_llm()
    if llm is None:
        skipped["llm"] = True
        return
    descriptions = {c["criterion_id"]: c.get("description", c["criterion_id"]) for c in checklist["criteria"]}
    target = str((case.get("assessment_target") or {}).get("description", "the assessed technology"))
    calls = 0
    for _, cid in sorted(asked, key=lambda x: (-x[0], x[1])):
        if calls >= int(s["llm_max_calls"]) or not has_time():
            skipped["llm"] = True
            break
        best = max(criteria[cid]["candidates"], key=lambda c: (c.get("entail", 0.0), -c["page"]))
        passage = best["text"][: int(s["llm_max_passage_chars"])]
        criteria[cid]["llm_p"] = p_yes(llm, descriptions.get(cid, cid), target, passage)
        criteria[cid]["llm_page"] = [best["document_id"], best["page"]]
        calls += 1
