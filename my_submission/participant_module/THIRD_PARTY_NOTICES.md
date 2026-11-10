# Third-party notices

This package contains no third-party code. It ships no Python packages and no model weights.

At run time it uses:

- the common base environment `apctt-base-9e7fe1324bb6`, installed by the organizer (not shipped);
- catalogue models from the organizer's read-only model store (not shipped), listed in
  `submission.json` `models[]`:
  - `bge-base-en-v1.5` (BAAI/bge-base-en-v1.5), MIT licence;
  - `granite-embedding-reranker-english-r2` (ibm-granite/granite-embedding-reranker-english-r2), Apache-2.0 licence.
  - `deberta-v3-base-zeroshot-v2.0-c` (MoritzLaurer/deberta-v3-base-zeroshot-v2.0-c), MIT licence.
  - `qwen3-0.6b` (Qwen/Qwen3-0.6B), Apache-2.0 licence.
