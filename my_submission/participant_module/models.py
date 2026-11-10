"""Catalogue models: where they are in the read-only model store, and offline loading.

Every model listed here must also be listed in submission.json models[] by catalog_id.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

CATALOG: dict[str, str] = {
    "bge-base-en-v1.5": "BAAI/bge-base-en-v1.5/a5beb1e3e68b9ab74eb54cfd186867f64f240e1a",
    "granite-embedding-reranker-english-r2": "ibm-granite/granite-embedding-reranker-english-r2/d09d3d6971b689bf9c23839e45a470874d46e13a",
    "deberta-v3-base-zeroshot-v2.0-c": "MoritzLaurer/deberta-v3-base-zeroshot-v2.0-c/bddf8c5411c34ac3565e16e04384fd68b2618dda",
    "qwen3-0.6b": "Qwen/Qwen3-0.6B/c1899de289a04d12100db370d81485cdf75e47ca",
}


def offline() -> None:
    """Must run before Hugging Face libraries are imported."""
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def path(catalog_id: str) -> Path:
    return Path(os.environ["APCTT_MODEL_STORE"]) / CATALOG[catalog_id]


def set_threads(threads: int) -> None:
    import torch

    torch.set_num_threads(max(1, int(threads)))


def embedder(catalog_id: str = "bge-base-en-v1.5") -> Any:
    offline()
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(str(path(catalog_id)), device="cpu", local_files_only=True)


def entailer(catalog_id: str = "deberta-v3-base-zeroshot-v2.0-c") -> Any:
    offline()
    from participant_module.judge import load_entailer

    return load_entailer(path(catalog_id))


def reranker(catalog_id: str = "granite-embedding-reranker-english-r2") -> Any:
    offline()
    from sentence_transformers import CrossEncoder

    return CrossEncoder(str(path(catalog_id)), device="cpu", local_files_only=True)
