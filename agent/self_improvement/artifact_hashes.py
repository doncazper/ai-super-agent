from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Iterable, Mapping

from agent.secrets.redaction import SecretRedactor


DEFAULT_HASH_ALGORITHM = "sha256"
DEFAULT_REPORT_PATHS = (
    "reports/qa/last_run.json",
    "reports/performance/latest.json",
    "docs/COMPLETION_REPORT.md",
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build_artifact_hash_report(
    project_root: str | Path = ".",
    *,
    test_command_output: str = "",
    approval_preview: str = "",
    generated_report_paths: Iterable[str | Path] = DEFAULT_REPORT_PATHS,
) -> dict[str, object]:
    """Build deterministic artifact hashes without exposing raw artifact content."""

    root = Path(project_root).resolve()
    redactor = SecretRedactor()
    git_diff = _git_output(root, ["diff", "--no-ext-diff"])
    redacted_diff = redactor.redact_text(git_diff)
    return {
        "status": "ok",
        "algorithm": DEFAULT_HASH_ALGORITHM,
        "redacted": True,
        "side_effects": "none; hash-only report",
        "project_root_name": root.name,
        "git_diff_hash": sha256_text(redacted_diff),
        "touched_file_hashes": touched_file_hashes(root),
        "test_command_output_hash": sha256_text(redactor.redact_text(test_command_output)),
        "generated_report_hashes": generated_report_hashes(root, generated_report_paths),
        "approval_preview_hash": sha256_text(redactor.redact_text(approval_preview)),
        "command_registry_snapshot_hash": file_hash_or_missing(root / "docs/COMMAND_REGISTRY.md"),
        "capability_manifest_hash": file_hash_or_missing(root / "config/capabilities.yaml"),
    }


def touched_file_hashes(project_root: str | Path = ".") -> dict[str, str]:
    root = Path(project_root).resolve()
    status = _git_output(root, ["status", "--short"])
    hashes: dict[str, str] = {}
    for line in status.splitlines():
        rel_path = _status_path(line)
        if not rel_path:
            continue
        path = (root / rel_path).resolve()
        if root not in path.parents and path != root:
            continue
        if path.is_file():
            hashes[rel_path] = file_hash_or_missing(path)
        elif path.is_dir():
            continue
        else:
            hashes[rel_path] = "missing_or_not_file"
    return dict(sorted(hashes.items()))


def generated_report_hashes(project_root: str | Path, paths: Iterable[str | Path]) -> dict[str, str]:
    root = Path(project_root).resolve()
    hashes: dict[str, str] = {}
    for item in paths:
        rel_path = Path(item)
        if rel_path.is_absolute():
            try:
                display = rel_path.resolve().relative_to(root).as_posix()
            except ValueError:
                continue
            path = rel_path
        else:
            display = rel_path.as_posix()
            path = root / rel_path
        hashes[display] = file_hash_or_missing(path)
    return dict(sorted(hashes.items()))


def file_hash_or_missing(path: str | Path) -> str:
    target = Path(path)
    if not target.exists():
        return "missing"
    if not target.is_file():
        return "not_file"
    return sha256_bytes(target.read_bytes())


def redacted_payload_hash(payload: Mapping[str, object]) -> str:
    redacted = SecretRedactor().redact(dict(payload))
    return sha256_text(repr(sorted(redacted.items())))


def _git_output(root: Path, args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return completed.stdout if completed.returncode in {0, 1} else ""


def _status_path(line: str) -> str | None:
    if not line.strip() or len(line) < 4:
        return None
    raw = line[3:].strip()
    if " -> " in raw:
        raw = raw.split(" -> ", 1)[1]
    return raw.strip('"') or None
