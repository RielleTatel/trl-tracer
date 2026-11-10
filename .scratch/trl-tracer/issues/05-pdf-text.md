Status: ready-for-agent
Owner: agent
Blocked by: 04

# 05 — pdf text

Per-page text extraction with `pypdfium2`, passage splitting that keeps document and page, and per-page character counts (input for OCR later). Record extraction time per case.

## Done when

- [ ] Harness slow run over all 99 public cases: no failures; extraction time per case recorded; slowest extraction known (USGS-SDG-017, -075 checked).
- [ ] Page numbers in passages match the server's page counts.

Spec user stories: 24, 25, 28. Spec: `../spec.md`.
