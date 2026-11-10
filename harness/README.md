# harness

The development loop for trl-tracer. Not part of the submission.

Each case runs in a fresh worker process with the base environment's Python, a restricted
environment and the 3-minute budget (interpreter start included), like the organizer's server.
The kit's own contract validator checks every result. Scripts started with any `python3`
re-run themselves with the kit's `.venv` Python.

## Commands

```bash
python3 harness/run.py --set tuning --note "what changed"   # slow cycle: tuning | heldout | smoke | all
python3 harness/run.py --cases USGS-SDG-012,USGS-SDG-075     # chosen cases
python3 harness/run.py --set smoke --settings try.json       # settings merged over submission.json
python3 harness/compare.py                                    # KEEP / REVERT for the latest run
python3 harness/compare.py --accept runs/<run>                # make a run the best (after you commit)
python3 harness/score.py runs/<run>                           # re-score, e.g. after adding labels
python3 harness/server_submit.py <request.json> ...           # through the real kit server
python3 harness/split.py                                      # made once: brain/split.json
```

## Where things go

| What | Where | In git |
|---|---|---|
| Run: meta (git commit, settings, package and rules hashes), per-case records (result, cached evidence, timings, peak memory, stderr tail), score | `runs/<run_id>/` | no |
| Best run per case set | `runs/best.json` | no |
| One line per run | `brain/experiments.md` | yes |
| Split (70 tuning / 29 held-out) | `brain/split.json` | yes |
| Hand labels (read for the evidence score B) | `brain/labels/<case_id>.json` | yes |

## Scores

- **A**: the official TRL table against the organizer's estimated TRLs (a proxy).
- **B**: the official evidence formula against the hand labels, over labelled cases only.
- **dev**: `(0.45 A + 0.40 B) / 0.85`, or A while there are no labels.
- **Gates**: no invalid or failed result, no timeout, slowest case ≤ 90 s, peak memory ≤ 10 GB.
- Runs are compared only with the best run on the same case set and the same labels.

Label file format (`brain/labels/<case_id>.json`):

```json
{"case_id": "USGS-SDG-012", "trl": 4, "criteria": {
  "APCTT-C04": {"status": "met", "pages": [{"document_id": "D001", "page": 7}], "note": "..."},
  "APCTT-C09": {"status": "insufficient evidence", "pages": [], "note": "..."}}}
```
