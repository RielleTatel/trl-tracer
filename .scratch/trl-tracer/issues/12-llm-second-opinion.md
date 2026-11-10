Status: ready-for-agent
Owner: agent
Blocked by: 08

# 12 — llm second opinion

Gate `qwen3-0.6b` (thinking off): load only after extraction and only if enough time remains; ask only borderline criteria, at most the configured number per case, `met`/`not met` answers only; skip when time is short. Add it to `models[]`. Measure load and per-call time.

## Done when

- [ ] Harness slow run: gates pass with the LLM enabled; the run record shows how often it was used and skipped.
- [ ] Compare against the run without it decides keep/revert.

Spec user stories: 35, 36. Spec: `../spec.md`.
