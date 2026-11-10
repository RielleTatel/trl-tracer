Status: ready-for-agent
Owner: agent
Blocked by: 02, 07

# 08 — entailment judge

Evidence stage part 2: score each candidate passage against the criterion hypotheses with `deberta-v3-base-zeroshot-v2.0-c`; complete the case evidence record. First end-to-end real assessment through the decision step.

## Done when

- [ ] Harness slow run on the tuning set: gates pass; dev score beats the always-abstain baseline; result logged.
- [ ] Evidence records cached in the run record for replay.

Spec user stories: 33, 34. Spec: `../spec.md`.
