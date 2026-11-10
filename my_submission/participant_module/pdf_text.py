"""PDF text: per-page text with pypdfium2, and passages that keep their page number.

The server's page count (`page_count`, counted with pypdf) is the authority for citations, so
the page list always has exactly that many entries; any difference from pypdfium2's count is
recorded. OCR for pages with little text is added in ticket 13.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from participant_module import quotes


def _clean(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "").replace("￾", "")


def extract_document(document: Mapping[str, Any], has_time: Callable[[], bool]) -> dict[str, Any]:
    """Text of every page of one case document. Stops early (with `complete: False`) when time runs out."""
    import pypdfium2 as pdfium

    count = int(document["page_count"])
    pages = [""] * count
    out: dict[str, Any] = {"document_id": document["document_id"], "page_count": count, "pages": pages,
                           "complete": True}
    pdf = pdfium.PdfDocument(document["path"])
    try:
        readable = len(pdf)
        if readable != count:
            out["pdfium_page_count"] = readable
        for index in range(min(count, readable)):
            if not has_time():
                out["complete"] = False
                break
            page = pdf[index]
            try:
                textpage = page.get_textpage()
                try:
                    pages[index] = _clean(textpage.get_text_range())
                finally:
                    textpage.close()
            except Exception:
                pages[index] = ""  # one unreadable page must not lose the document
            finally:
                page.close()
    finally:
        pdf.close()
    out["chars"] = [len(p.strip()) for p in pages]
    return out


def passages(documents: list[Mapping[str, Any]], *, max_chars: int = 700, min_chars: int = 40) -> list[dict[str, Any]]:
    """Consecutive sentences of a page grouped up to `max_chars`; each passage keeps document and page."""
    out: list[dict[str, Any]] = []
    for document in documents:
        for number, text in enumerate(document["pages"], start=1):
            chunk: list[str] = []
            size = 0
            for sentence in quotes.sentences(text):
                if chunk and size + len(sentence) > max_chars:
                    out.append(_passage(document["document_id"], number, chunk))
                    chunk, size = [], 0
                chunk.append(sentence)
                size += len(sentence) + 1
            if chunk:
                out.append(_passage(document["document_id"], number, chunk))
    return [p for p in out if len(p["text"]) >= min_chars]


def _passage(document_id: str, page: int, chunk: list[str]) -> dict[str, Any]:
    return {"document_id": document_id, "page": page, "text": " ".join(chunk)}
