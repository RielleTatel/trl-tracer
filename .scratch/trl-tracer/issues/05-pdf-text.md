Status: resolved
Owner: agent
Blocked by: 04

# 05 — pdf text

Per-page text extraction with `pypdfium2`, passage splitting that keeps document and page, and per-page character counts (input for OCR later). Record extraction time per case.

## Done when

- [x] Harness slow run over all 99 public cases: no failures; extraction time per case recorded; slowest extraction known (USGS-SDG-017, -075 checked).
- [x] Page numbers in passages match the server's page counts.

Spec user stories: 24, 25, 28. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. `pdf_text.py`: per-page text with pypdfium2 (`\r\n` normalised), exactly
  `page_count` pages per document (the server's count is the authority; a pdfium mismatch is
  recorded), per-page character counts, early stop with `complete: False` when time runs out;
  `passages()` groups consecutive sentences up to 700 chars keeping document and page (used by
  retrieval in ticket 07). The evidence record now carries the page texts.
  Harness run on all 99 cases: 0 invalid, 0 timeouts, slowest case 2.35 s, peak 0.31 GB.
  Extraction: slowest USGS-SDG-017 (168 pages) 2.25 s, USGS-SDG-075 (208 pages) 1.69 s, median
  0.19 s. Page counts match the manifest for all 99; no incomplete document. 306 pages across
  the set have fewer than 200 characters (covers, blank pages, figures) — relevant to the OCR
  cap in ticket 13. USGS-SDG-030 (scanned) already has an OCR text layer. A full 99-case run
  record is about 14 MB (cached page text).
