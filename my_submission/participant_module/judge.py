"""Judging: how strongly each candidate passage supports its criterion.

The entailment model (deberta-v3-base-zeroshot-v2.0-c, MIT) scores P(entailment) of each
criterion hypothesis given the passage; a candidate's `entail` is its best score over the
hypotheses used. Pairs are scored in length-sorted batches with a time check between batches,
so judging stops cleanly when time runs out (unscored candidates simply stay unmet).
Each candidate also gets its sentences ranked by word overlap with the criterion, so the
decision step quotes the most relevant sentence first.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from participant_module import quotes, retrieve

DEFAULTS: dict[str, Any] = {
    "hypotheses_per_criterion": 1,
    "judge_max_tokens": 256,
    "judge_batch": 16,
}


def load_entailer(path: Any) -> dict[str, Any]:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True, dtype=torch.float32).eval()
    labels = {v.lower(): int(k) for k, v in model.config.id2label.items()}
    return {"tokenizer": tokenizer, "model": model, "entailment": labels["entailment"]}


def rank_sentences(text: str, rules: Mapping[str, list[str]]) -> list[str]:
    wanted = set(retrieve.tokens(" ".join(rules["hypotheses"] + rules["queries"])))
    found = quotes.sentences(text)
    return sorted(found, key=lambda s: (-len(wanted & set(retrieve.tokens(s))), found.index(s)))


def judge(criteria: dict[str, dict[str, Any]], per_criterion: Mapping[str, Mapping[str, list[str]]],
          entailer: Mapping[str, Any] | None, settings: Mapping[str, Any], has_time: Callable[[], bool],
          skipped: dict[str, Any]) -> None:
    """Adds `entail` and `sentences` to every candidate it has time for (in place)."""
    s = {**DEFAULTS, **{k: v for k, v in settings.items() if k in DEFAULTS}}
    jobs: list[tuple[dict[str, Any], str]] = []
    for cid, entry in criteria.items():
        rules = per_criterion[cid]
        hypotheses = rules["hypotheses"][: max(1, int(s["hypotheses_per_criterion"]))]
        for candidate in entry["candidates"]:
            candidate["sentences"] = rank_sentences(candidate["text"], rules)
            jobs += [(candidate, h) for h in hypotheses]
    if entailer is None:
        skipped["judge"] = True
        return

    import torch

    tokenizer, model, label = entailer["tokenizer"], entailer["model"], entailer["entailment"]
    jobs.sort(key=lambda job: len(job[0]["text"]) + len(job[1]))  # similar lengths: less padding
    size = int(s["judge_batch"])
    for start in range(0, len(jobs), size):
        if not has_time():
            skipped["judge"] = True
            return
        batch = jobs[start:start + size]
        with torch.inference_mode():
            encoded = tokenizer([c["text"] for c, _ in batch], [h for _, h in batch], truncation="only_first",
                                max_length=int(s["judge_max_tokens"]), padding=True, return_tensors="pt")
            probs = torch.softmax(model(**encoded).logits, dim=-1)[:, label].tolist()
        for (candidate, _), p in zip(batch, probs):
            candidate["entail"] = round(max(float(p), float(candidate.get("entail", 0.0))), 4)
