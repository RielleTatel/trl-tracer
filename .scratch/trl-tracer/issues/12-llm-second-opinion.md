Status: resolved
Owner: agent
Blocked by: 08

# 12 — llm second opinion

Gate `qwen3-0.6b` (thinking off): load only after extraction and only if enough time remains; ask only borderline criteria, at most the configured number per case, `met`/`not met` answers only; skip when time is short. Add it to `models[]`. Measure load and per-call time.

## Done when

- [x] Harness slow run: gates pass with the LLM enabled; the run record shows how often it was used and skipped.
- [x] Compare against the run without it decides keep/revert.

Spec user stories: 35, 36. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. `llm.py`: qwen3-0.6b, thinking off, stricter instruction + two worked
  examples, P(yes) from one forward pass, loaded after judging only if 60 s remain, asked only for
  borderline criteria (cap 12). Decision step: borderline criterion met if P(yes) >= `llm_yes`.
  Tuning run: gates pass (slowest 62.6 s, peak 4.73 GB); with the swept settings (band 0.2-0.5,
  llm_yes 0.8) B 0.428 -> 0.474, dev 0.599 -> 0.620, A unchanged. Kept. See brain/decisions.md.
