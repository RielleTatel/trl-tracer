Status: resolved
Owner: agent
Blocked by: 05

# 13 — ocr fallback

OCR pages with fewer than the configured number of characters using `rapidocr-onnxruntime`, capped per case and skipped when time is short. Verify the base's bundled OCR models load offline.

## Done when

- [x] USGS-SDG-030 (scanned) yields usable text within the time budget.
- [x] No other public case is slowed by OCR.

Spec user stories: 26, 27. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. `ocr.py`: rapidocr-onnxruntime (PP-OCRv4 ONNX models bundled in the base,
  offline) for documents whose text layer is mostly missing; at most 3 pages per case, time
  checked per page. Synthetic scanned version of USGS-SDG-012: 3 pages in 13.4 s, ~1,700-2,500
  characters each (words often run together). No public case triggers OCR, so none is slowed.
  USGS-SDG-030 has an OCR text layer already, so it needs no OCR.
