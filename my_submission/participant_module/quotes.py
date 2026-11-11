"""Quotations: verbatim sentences from the cited page, never generated text.

A quotation is valid only if it appears in the page's extracted text after normalising
whitespace and hyphenated line breaks, and it is not a sentence that asserts a TRL number
(experts judge those NOT_SUPPORTS). Because experts judge the first quotation of a claim, a
quotation is also tidied without leaving the page text: running headers and section headings
glued to its start are dropped, a fragment cut at an abbreviation ("U.S.", "fig.") is widened to
the whole sentence, and complete sentences that report something are tried before purpose
statements, fragments and sentences that need shortening.
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


_ABBREVIATION = re.compile(
    r"(?:\b(?:U\.S|U\.K|e\.g|i\.e|et al|[Ff]igs?|[Ee]qs?|[Nn]os?|vs|approx|ca|cf|St|Dr|Mr|Ms|Inc|Co|sec|vol|pp?|v)"
    r"|(?<![A-Za-z])[A-Z])\.$"
)
_PAGE_NUMBER = r"(?:\d{1,4}|[ivxlc]{1,7})"
_RUNNING_HEADER = re.compile(rf"^{_PAGE_NUMBER}\s+\S|\S\s+{_PAGE_NUMBER}$")
_DOT_LEADER = re.compile(r"\.{4,}|(?:\. ){4,}")
_PURPOSE = re.compile(
    r"^(?:purpose and scope\b|the (?:purpose|objective|goal|aim)s? of (?:this|the) (?:report|study|paper|investigation)"
    r"|this (?:report|study|paper) (?:describes|documents|presents|summarizes|provides))",
    re.IGNORECASE,
)


_CITATION = re.compile(r"^[A-Z][\w'’-]+, (?:[A-Z]\.\s?){1,3},.{0,200}\b(?:19|20)\d\d\b")


def normalize(text: str) -> str:
    """Join hyphenated line breaks and collapse whitespace."""
    return _SPACE.sub(" ", _HYPHEN_BREAK.sub(r"\1\2", text)).strip()


def sentences(text: str) -> list[str]:
    """Sentences of `text`; a full stop after an abbreviation or an initial does not end one."""
    out: list[str] = []
    for piece in (s.strip() for s in _SENTENCE_END.split(normalize(text))):
        if not piece:
            continue
        if out and _ABBREVIATION.search(out[-1]):
            out[-1] += " " + piece
        else:
            out.append(piece)
    return out


def dot_leaders(text: str) -> bool:
    """A contents-style line: a title, a row of dots, a page number."""
    return bool(_DOT_LEADER.search(text))


def is_purpose(sentence: str) -> bool:
    """A purpose statement ("The purpose of this report is ..."): what was intended, not what was done."""
    return bool(_PURPOSE.search(sentence))


def is_fragment(sentence: str) -> bool:
    """Not a sentence of the report's own text: starts mid-sentence, closes a bracket it never
    opened, is a table row, or is a reference-list entry ("Smith, J.A., 2004, ...")."""
    digits = sum(ch.isdigit() for ch in sentence)
    return (not (sentence[0].isupper() or sentence[0].isdigit()) or sentence.count(")") > sentence.count("(")
            or digits > 0.3 * len(sentence) or bool(_CITATION.search(sentence)))


def lead_ins(page_text: str) -> tuple[set[str], set[str]]:
    """Lines of a page that are not part of its sentences: (running headers, headings).

    A running header is the first line when it starts or ends with a page number. A heading is a
    short line without closing punctuation that is followed by a line starting with a capital.
    """
    lines = [line for line in (normalize(raw) for raw in page_text.splitlines()) if line]
    headers: set[str] = set()
    headings: set[str] = set()
    if not lines:
        return headers, headings
    if _RUNNING_HEADER.search(lines[0]) or re.fullmatch(_PAGE_NUMBER, lines[0]):
        headers.add(lines[0])
    lengths = sorted(len(line) for line in lines)
    short = 0.8 * lengths[len(lengths) // 2]
    for line, following in zip(lines, lines[1:]):
        if (len(line) <= short and len(line.split()) <= 12 and line[-1].isalnum() and following[:1].isupper()
                and (line[0].isupper() or line[0].isdigit())):
            headings.add(line)
    return headers, headings


def strip_lead_ins(sentence: str, headers: set[str], headings: set[str]) -> str:
    """Drop running headers and headings glued to the start of `sentence` (still verbatim page text)."""
    for _ in range(4):
        for lead in sorted(headers | headings, key=len, reverse=True):
            rest = sentence[len(lead):].lstrip()
            if sentence.startswith(lead + " ") and rest and (lead in headers or rest[0].isupper()):
                sentence = rest
                break
        else:
            break
    return sentence


def _whole_sentence(fragment: str, page: str, page_sentences: list[str]) -> str:
    """The page sentence that contains `fragment` (a fragment arises from a cut at an abbreviation)."""
    at = page.find(fragment)
    if at < 0:
        return fragment
    position = 0
    for sentence in page_sentences:
        start = page.find(sentence, position)
        if start < 0:
            break
        position = start + len(sentence)
        if start <= at and at + len(fragment) <= position:
            return sentence
        if start > at:
            break
    return fragment


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
              ranked: list[str] | None = None, purpose_ok: bool = False) -> str | None:
    """The best quotable sentence of `passage` that is on `page_text`, or None.

    `ranked` lets the evidence stage pass sentences already ordered by support; otherwise the
    passage's sentences are tried in order. Within that order, complete sentences that report
    something come first, then purpose statements and fragments (unless `purpose_ok`: for a
    criterion about the intended use, a purpose statement is the evidence), then sentences that
    must be shortened.
    """
    page = normalize(page_text)
    page_sentences = sentences(page)
    headers, headings = lead_ins(page_text)
    usable: list[tuple[tuple[bool, bool], int, str]] = []
    for order, sentence in enumerate(ranked if ranked else sentences(passage)):
        sentence = _whole_sentence(normalize(sentence), page, page_sentences)
        sentence = strip_lead_ins(sentence, headers, headings)
        if len(sentence) < min_chars or asserts_trl(sentence) or dot_leaders(sentence):
            continue
        weak = (is_purpose(sentence) and not purpose_ok) or is_fragment(sentence)
        usable.append(((weak, len(sentence) > max_chars), order, sentence))
    for _, _, sentence in sorted(usable):
        span = shorten(sentence, max_chars)
        if len(span) >= min_chars and span in page:
            return span
    return None
