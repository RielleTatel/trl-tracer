"""Retrieval: candidate passages per criterion.

1. BM25 (in-package) over all passages with the criterion's search phrases and hypotheses;
   it also pre-filters, so only the union of each criterion's BM25 top passages is embedded.
2. Dense retrieval with bge-base-en-v1.5 (query instruction per the model card).
3. Reciprocal-rank fusion of both rankings, then the cross-encoder reranker on the fused top.
Pages whose heading is a page trap (reference lists, front matter) are never candidates.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Callable, Mapping
from typing import Any

from participant_module import quotes

DEFAULTS: dict[str, Any] = {
    "bm25_k": 40,  # BM25 top passages per criterion (also the embedding pre-filter)
    "fused_k": 12,  # fused passages per criterion sent to the reranker
    "candidates_k": 8,  # reranked passages kept per criterion
    "rrf_k": 60,
    "passage_max_chars": 700,
}

QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "
_WORD = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")
_STOP = frozenset(
    "a an and are as at be been by for from has have in into is it its of on or that the their this to was were "
    "which with report states assessed technology".split()
)


def tokens(text: str) -> list[str]:
    return [w for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 1]


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75) -> None:
        self.docs, self.k1, self.b = docs, k1, b
        self.lengths = [len(d) for d in docs]
        self.avg = (sum(self.lengths) / len(docs)) if docs else 0.0
        self.freqs = [Counter(d) for d in docs]
        df = Counter(w for d in docs for w in set(d))
        n = len(docs)
        self.idf = {w: math.log(1 + (n - f + 0.5) / (f + 0.5)) for w, f in df.items()}

    def scores(self, query: list[str]) -> list[float]:
        out = []
        terms = [w for w in set(query) if w in self.idf]
        for freq, length in zip(self.freqs, self.lengths):
            s = 0.0
            for w in terms:
                f = freq.get(w, 0)
                if f:
                    s += self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / (self.avg or 1)))
            out.append(s)
        return out


def trap_pages(documents: list[Mapping[str, Any]], page_traps: list[str]) -> set[tuple[str, int]]:
    """Pages whose first lines start with a page-trap heading (e.g. 'References Cited'), and contents pages."""
    traps = [t.lower() for t in page_traps]
    found = set()
    for document in documents:
        for number, text in enumerate(document["pages"], start=1):
            lines = [line.strip().lower() for line in text.splitlines() if line.strip()][:12]
            leaders = sum(1 for line in text.splitlines() if quotes.dot_leaders(line))
            if leaders >= 3 or any(line.startswith(t) for line in lines for t in traps):
                found.add((document["document_id"], number))
    return found


def rank(values: list[float]) -> dict[int, int]:
    order = sorted(range(len(values)), key=lambda i: (-values[i], i))
    return {index: position for position, index in enumerate(order)}


def retrieve(passages: list[dict[str, Any]], per_criterion: Mapping[str, Mapping[str, list[str]]],
             models: Mapping[str, Any], settings: Mapping[str, Any], has_time: Callable[[], bool],
             skipped: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """criterion ID -> {"candidates": [...]}; degrades to BM25 only, then to nothing, when time runs out."""
    s = {**DEFAULTS, **{k: v for k, v in settings.items() if k in DEFAULTS}}
    out: dict[str, dict[str, Any]] = {cid: {"candidates": []} for cid in per_criterion}
    if not passages:
        return out
    bm25 = BM25([tokens(p["text"]) for p in passages])
    bm25_scores: dict[str, list[float]] = {}
    shortlist: dict[str, list[int]] = {}
    for cid, rules in per_criterion.items():
        query = tokens(" ".join(rules["queries"] + rules["hypotheses"]))
        scores = bm25.scores(query)
        bm25_scores[cid] = scores
        shortlist[cid] = sorted(range(len(passages)), key=lambda i: (-scores[i], i))[: int(s["bm25_k"])]

    dense: dict[str, dict[int, float]] = {}
    embedder = models.get("embedder")
    if embedder is not None and has_time():
        pool = sorted({i for ids in shortlist.values() for i in ids})
        vectors = embedder.encode([passages[i]["text"] for i in pool], batch_size=32,
                                  normalize_embeddings=True, convert_to_numpy=True)
        position = {i: n for n, i in enumerate(pool)}
        cids = list(per_criterion)
        queries = embedder.encode([QUERY_INSTRUCTION + " ".join(per_criterion[c]["hypotheses"]) for c in cids],
                                  normalize_embeddings=True, convert_to_numpy=True)
        for cid, q in zip(cids, queries):
            dense[cid] = {i: float(vectors[position[i]] @ q) for i in shortlist[cid]}
    else:
        skipped["dense"] = True

    reranker = models.get("reranker")
    for cid, rules in per_criterion.items():
        ids = shortlist[cid]
        b_rank = {i: r for r, i in enumerate(ids)}
        d_values = dense.get(cid)
        if d_values:
            d_order = sorted(ids, key=lambda i: (-d_values[i], i))
            d_rank = {i: r for r, i in enumerate(d_order)}
        else:
            d_rank = {}
        k = float(s["rrf_k"])
        fused = {i: 1 / (k + b_rank[i] + 1) + (1 / (k + d_rank[i] + 1) if d_rank else 0.0) for i in ids}
        top = sorted(ids, key=lambda i: (-fused[i], i))[: int(s["fused_k"])]
        top = [i for i in top if bm25_scores[cid][i] > 0 or (d_values and d_values[i] > 0)]
        rerank_scores: dict[int, float] = {}
        if reranker is not None and top and has_time():
            pairs = [(rules["hypotheses"][0], passages[i]["text"]) for i in top]
            values = reranker.predict(pairs, batch_size=16, show_progress_bar=False, convert_to_numpy=True)
            rerank_scores = {i: float(v) for i, v in zip(top, values)}
        elif top:
            skipped["rerank"] = True
        ordered = sorted(top, key=lambda i: (-rerank_scores.get(i, fused[i]), i)) if rerank_scores else top
        traps = [t.lower() for t in rules.get("traps", [])]
        for i in ordered[: int(s["candidates_k"])]:
            p = passages[i]
            candidate = {"document_id": p["document_id"], "page": p["page"], "text": p["text"],
                         "bm25": round(bm25_scores[cid][i], 4), "retrieval": round(fused[i], 6)}
            if d_values:
                candidate["dense"] = round(d_values[i], 4)
            if i in rerank_scores:
                candidate["rerank"] = round(rerank_scores[i], 4)
            hits = [t for t in traps if t in p["text"].lower()]
            if hits:
                candidate["trap_cues"] = hits
            out[cid]["candidates"].append(candidate)
    return out
