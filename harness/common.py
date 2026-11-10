"""Shared paths and helpers for the trl-tracer harness.

The harness runs in the kit's server environment (it needs the kit's contract validator); each
case runs in a fresh worker process with the common base environment's Python, as on the
organizer's server. Scripts re-execute themselves with the kit's Python when started with
another interpreter.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / "apctt-participant-kit-0.5.0-cpu"
KIT_PYTHON = KIT / ".venv" / "bin" / "python"
BASE_PYTHON = ROOT / "apctt-env" / "base" / "bin" / "python"
MODELS = ROOT / "models"
PDF_DIR = ROOT / "public_cases" / "pdf"
RUNS = ROOT / "runs"
SUBMISSION = ROOT / "my_submission"
BRAIN = ROOT / "brain"
LABELS = Path(os.environ.get("TRL_LABELS_DIR", BRAIN / "labels"))  # override for tests
CAPTURES = Path(os.environ.get("TRL_CAPTURES_FILE", BRAIN / "captures.jsonl"))
SPLIT = BRAIN / "split.json"
EXPERIMENTS = BRAIN / "experiments.md"
MANIFEST = KIT / "contracts" / "public-cases.json"
CHECKLIST = KIT / "contracts" / "checklist.official.json"

SCHEMA_VERSION = "apctt-pdf-example-v1"  # the dev profile's schema_version (GET /v1/package)
DEADLINE_MS = 180_000  # limits.deadline_ms: 3 minutes per case, interpreter start included
SEED = 42

# Hard gates (spec: Implementation Decisions > Harness).
GATE_SLOWEST_S = 90.0  # development target on the Mac, margin for the event laptop
GATE_PEAK_RSS_GB = 10.0  # the event worker has at least 12 GB


def ensure_kit_python() -> None:
    """Re-execute the current script with the kit's Python if the contract code is missing."""
    try:
        import apctt_contracts  # noqa: F401
    except ImportError:
        if Path(sys.executable).resolve() == KIT_PYTHON.resolve():
            raise
        os.execv(str(KIT_PYTHON), [str(KIT_PYTHON), *sys.argv])


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def manifest_cases() -> dict[str, dict[str, Any]]:
    return {case["case_id"]: case for case in read_json(MANIFEST)["cases"]}


def smoke_case_ids() -> list[str]:
    return list(read_json(MANIFEST)["smoke_cases"])


def checklist() -> dict[str, Any]:
    data = read_json(CHECKLIST)
    return {"version": data["version"], "criteria": data["criteria"]}


def submission() -> dict[str, Any]:
    return read_json(SUBMISSION / "submission.json")


def page_count(pdf: Path) -> int:
    """Page count as the server counts it (the kit's pypdf counter), cached per file hash."""
    from apctt_contracts.pdf import count_pages

    cache_path = RUNS / "page_counts.json"
    cache = read_json(cache_path) if cache_path.exists() else {}
    key = f"{pdf.name}:{pdf.stat().st_size}"
    if key not in cache:
        pages = count_pages(pdf)
        if pages is None:
            raise ValueError(f"{pdf} is not a readable PDF")
        cache[key] = pages
        write_json(cache_path, cache)
    return int(cache[key])


def worker_case(case_id: str) -> dict[str, Any]:
    """The case exactly as the server passes it to a module (worker view), built from the manifest."""
    entry = manifest_cases()[case_id]
    pdf = PDF_DIR / f"{case_id}.pdf"
    if not pdf.exists():
        raise FileNotFoundError(f"{pdf} is missing: run tools/get_public_cases.py --download")
    document = {**entry["document"], "sha256": entry["pdf_sha256"], "page_count": page_count(pdf), "path": str(pdf)}
    return {
        "schema_version": SCHEMA_VERSION,
        "input_profile": "pdf_report",
        "checklist_version": checklist()["version"],
        "case_id": case_id,
        "assessment_as_of": None,
        "title": entry["title"],
        "assessment_target": entry["assessment_target"],
        "intended_application": entry["intended_application"],
        "intended_environment": entry["intended_environment"],
        "sdg_targets": entry["sdg_targets"],
        "documents": [document],
    }


def estimated_trl(case_id: str) -> int:
    return int(manifest_cases()[case_id]["reference_labels"]["estimated_trl"])


def case_set(name: str) -> list[str]:
    """tuning | heldout | smoke | all."""
    if name == "smoke":
        return smoke_case_ids()
    if name == "all":
        return sorted(manifest_cases())
    if not SPLIT.exists():
        raise SystemExit("brain/split.json is missing: run harness/split.py first")
    split = read_json(SPLIT)
    if name not in split:
        raise SystemExit(f"unknown case set {name!r}: use tuning, heldout, smoke or all")
    return list(split[name])


def tree_hash(path: Path) -> str:
    """SHA-256 over the relative paths and bytes of every file under `path`."""
    digest = hashlib.sha256()
    if path.exists():
        for file in sorted(p for p in path.rglob("*") if p.is_file()):
            digest.update(file.relative_to(path).as_posix().encode())
            digest.update(file.read_bytes())
    return digest.hexdigest()


def git_state() -> dict[str, Any]:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()

    dirty = git("status", "--porcelain", "--", "my_submission", "harness")
    return {"commit": git("rev-parse", "--short", "HEAD"), "dirty": bool(dirty)}
