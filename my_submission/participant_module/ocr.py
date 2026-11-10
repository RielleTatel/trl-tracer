"""OCR fallback for scanned documents, with rapidocr-onnxruntime (PP-OCRv4 models, in the base).

Only a document whose text layer is mostly missing is OCR'd (at least `ocr_doc_share` of its
pages under `ocr_min_chars` characters): figure and cover pages of normal reports are left alone,
so ordinary cases are never slowed down. At most `ocr_max_pages` pages per case are read, each
only while time remains; OCR text replaces a page's text only when it is longer.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

DEFAULTS: dict[str, Any] = {
    "use_ocr": True,
    "ocr_min_chars": 200,
    "ocr_doc_share": 0.5,
    "ocr_max_pages": 3,  # each page costs about 5-8 s on a laptop CPU
    "ocr_scale": 1.5,  # render scale (1.5 is about 108 dpi)
}


def needs_ocr(document: Mapping[str, Any], settings: Mapping[str, Any]) -> bool:
    s = {**DEFAULTS, **{k: v for k, v in settings.items() if k in DEFAULTS}}
    chars = document.get("chars") or []
    if not s["use_ocr"] or not chars:
        return False
    low = sum(1 for c in chars if c < int(s["ocr_min_chars"]))
    return low / len(chars) >= float(s["ocr_doc_share"])


def _reading_order(results: list[Any]) -> str:
    """RapidOCR returns [box, text, score]; sort lines top to bottom, then left to right."""
    lines = []
    for box, text, _score in results or []:
        top = min(point[1] for point in box)
        left = min(point[0] for point in box)
        lines.append((round(top / 12), left, text))
    return "\n".join(text for _, _, text in sorted(lines))


def ocr_document(document: dict[str, Any], path: str, settings: Mapping[str, Any],
                 has_time: Callable[[], bool], budget_pages: int) -> tuple[int, bool]:
    """OCR low-text pages of one document in place. Returns (pages read, stopped early)."""
    import numpy
    import pypdfium2 as pdfium
    from rapidocr_onnxruntime import RapidOCR

    s = {**DEFAULTS, **{k: v for k, v in settings.items() if k in DEFAULTS}}
    engine = RapidOCR()
    pdf = pdfium.PdfDocument(path)
    done = 0
    stopped = False
    try:
        for index, chars in enumerate(document["chars"]):
            if chars >= int(s["ocr_min_chars"]) or index >= len(pdf):
                continue
            if done >= budget_pages or not has_time():
                stopped = True
                break
            page = pdf[index]
            try:
                image = page.render(scale=float(s["ocr_scale"])).to_pil().convert("RGB")
                results, _ = engine(numpy.asarray(image))
                text = _reading_order(results)
                if len(text.strip()) > len(document["pages"][index].strip()):
                    document["pages"][index] = text
                    document["chars"][index] = len(text.strip())
                    document.setdefault("ocr_pages", []).append(index + 1)
            except Exception:
                pass  # one unreadable page must not lose the document
            finally:
                page.close()
            done += 1
    finally:
        pdf.close()
    return done, stopped
