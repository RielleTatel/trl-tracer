"""Quotations: verbatim sentences from the cited page, never generated text.

A quotation is valid only if it appears in the page's extracted text after normalising
whitespace and hyphenated line breaks, and it is not a sentence that asserts a TRL number
(experts judge those NOT_SUPPORTS).
"""

from __future__ import annotations

import re

_HYPHEN_BREAK = re.compile(r"(\w)-\s*\n\s*(\w)")
_SPACE = re.compile(r"\s+")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])")
_TRL_ASSERTION = re.compile(
    r"\bTRLs?\s*[-:=]?\s*\(?[1-9]\b|\btechnology[\s-]+readiness[\s-]+levels?\s*(?:of\s*|is\s*|=\s*)?\(?[1-9]\b",
    re.IGNORECASE,
)


def normalize(text: str) -> str:
    """Join hyphenated line breaks and collapse whitespace."""
    return _SPACE.sub(" ", _HYPHEN_BREAK.sub(r"\1\2", text)).strip()


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(normalize(text)) if s.strip()]


def asserts_trl(sentence: str) -> bool:
    return bool(_TRL_ASSERTION.search(sentence))


def shorten(sentence: str, max_chars: int) -> str:
    """Cut at a word boundary; the result is still a verbatim substring."""
    if len(sentence) <= max_chars:
        return sentence
    cut = sentence[:max_chars]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:")


def quotation(passage: str, page_text: str, *, min_chars: int, max_chars: int,
              ranked: list[str] | None = None) -> str | None:
    """The best quotable sentence of `passage` that is on `page_text`, or None.

    `ranked` lets the evidence stage pass sentences already ordered by support; otherwise the
    passage's sentences are tried in order.
    """
    page = normalize(page_text)
    for sentence in ranked if ranked else sentences(passage):
        sentence = normalize(sentence)
        if len(sentence) < min_chars or asserts_trl(sentence):
            continue
        span = shorten(sentence, max_chars)
        if len(span) >= min_chars and span in page:
            return span
    return None
