Status: ready-for-agent
Owner: agent
Blocked by: 05

# 13 — ocr fallback

OCR pages with fewer than the configured number of characters using `rapidocr-onnxruntime`, capped per case and skipped when time is short. Verify the base's bundled OCR models load offline.

## Done when

- [ ] USGS-SDG-030 (scanned) yields usable text within the time budget.
- [ ] No other public case is slowed by OCR.

Spec user stories: 26, 27. Spec: `../spec.md`.
