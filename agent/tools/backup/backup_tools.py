from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from agent.config.loader import load_yaml
from agent.config.schema import validate_capabilities_config
from agent.safety.redaction import SecretRedactor
from agent.tools.errors import ToolError
from agent.tools.low_risk.workspace_files import DENIED_HOME_PATHS


BACKUP_SCHEMA_VERSION = "1"
DEFAULT_BACKUP_DIR = "workspace/backups"
SECRET_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".netrc",
}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
TRACKING_FILES = [
    "SPEC.md",
    "SDLC.md",
    "AGENTS.md",
    "README.md",
    "CHANGELOG.md",
]
TRACKING_DIRS = [
    "docs",
    "native_skills",
]
CONFIG_PATTERNS = [
    "config/*.yaml",
    "config/*.yml",
    "config/*.json",
    ".env.example",
]


def make_backup_tools(project_root: str | Path) -> dict[str, Any]:
    manager = BackupManager(project_root)
    return {
        "backup.create": manager.create,
        "backup.list": manager.list_backups,
        "backup.inspect": manager.inspect,
        "backup.verify": manager.verify,
        "backup.export": manager.export,
        "backup.restore": manager.restore,
    }


class BackupManager:
    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.redactor = SecretRedactor()

    def create(
        self,
        *,
        backup_dir: str = "",
        include_captures: bool = False,
        include_audit_metadata: bool = False,
        redacted: bool = True,
    ) -> dict[str, Any]:
        if not redacted:
            raise ToolError("unredacted backups are not supported in v1")
        root = self._backup_root(backup_dir)
        backup_id = self._new_backup_id()
        archive = root / backup_id
        archive.mkdir(parents=True, exist_ok=False)
        manifest: dict[str, Any] = {
            "schema_version": BACKUP_SCHEMA_VERSION,
            "backup_id": backup_id,
            "created_at": _utc_now(),
            "project": self.project_root.name,
            "redacted": bool(redacted),
            "include_captures": bool(include_captures),
            "include_audit_metadata": bool(include_audit_metadata),
            "personal_connectors_read": False,
            "secrets_policy": "secret-looking files are excluded; copied text is redacted",
            "archive_type": "directory",
            "files": [],
            "data_exports": [],
            "excluded": [],
            "limitations": [
                "V1 stores a redacted memory export, not raw personal memory content.",
                "V1 does not fetch provider/calendar/contact/email/message data during backup.",
                "Restore is approval-gated and rejects capability manifests that weaken policy.",
            ],
        }
        files_read: list[str] = []
        files_written: list[str] = []

        for source, kind in self._candidate_files():
            if not source.exists() or not source.is_file():
                continue
            reason = self._secret_exclusion_reason(source)
            rel = _relative_to(source, self.project_root)
            if reason:
                manifest["excluded"].append({"path": rel, "reason": reason})
                continue
            stored = self._copy_redacted_file(source, archive, rel)
            files_read.append(str(source))
            files_written.append(str(stored))
            manifest["files"].append(self._file_entry(source, stored, archive, rel, kind))

        memory_export = self._export_memory(archive)
        if memory_export:
            manifest["data_exports"].append(memory_export)
            files_written.append(str(archive / memory_export["stored_path"]))
        action_export = self._export_actions(archive)
        if action_export:
            manifest["data_exports"].append(action_export)
            files_written.append(str(archive / action_export["stored_path"]))
        if include_captures:
            captures_export = self._export_captures(archive)
            if captures_export:
                manifest["data_exports"].append(captures_export)
                files_written.append(str(archive / captures_export["stored_path"]))
        if include_audit_metadata:
            audit_export = self._export_audit_metadata(archive)
            if audit_export:
                manifest["data_exports"].append(audit_export)
                files_written.append(str(archive / audit_export["stored_path"]))

        self._write_manifest(archive, manifest)
        files_written.append(str(archive / "manifest.json"))
        return {
            "status": "ok",
            "backup_id": backup_id,
            "path": str(archive),
            "redacted": bool(redacted),
            "manifest": {
                "schema_version": BACKUP_SCHEMA_VERSION,
                "file_count": len(manifest["files"]),
                "data_export_count": len(manifest["data_exports"]),
                "excluded_count": len(manifest["excluded"]),
                "integrity_hash": manifest["integrity_hash"],
            },
            "_audit": {
                "files_read": files_read,
                "files_written": files_written,
                "result_summary": f"Created redacted backup {backup_id}.",
            },
        }

    def export(
        self,
        *,
        backup_dir: str = "",
        include_captures: bool = False,
        include_audit_metadata: bool = False,
        redacted: bool = True,
    ) -> dict[str, Any]:
        if not redacted:
            raise ToolError("unredacted backup export is not supported in v1")
        result = self.create(
            backup_dir=backup_dir,
            include_captures=include_captures,
            include_audit_metadata=include_audit_metadata,
            redacted=True,
        )
        result["exported"] = True
        return result

    def list_backups(self, *, backup_dir: str = "") -> dict[str, Any]:
        root = self._backup_root(backup_dir)
        backups = []
        if root.exists():
            for child in sorted(root.iterdir(), reverse=True):
                if not child.is_dir():
                    continue
                manifest = self._read_manifest(child)
                if not manifest:
                    continue
                backups.append(
                    {
                        "backup_id": manifest.get("backup_id", child.name),
                        "created_at": manifest.get("created_at"),
                        "path": str(child),
                        "redacted": bool(manifest.get("redacted", True)),
                        "file_count": len(manifest.get("files", [])),
                        "data_export_count": len(manifest.get("data_exports", [])),
                    }
                )
        return {
            "status": "ok",
            "backup_dir": str(root),
            "backups": backups,
            "count": len(backups),
            "_audit": {"files_read": [str(root)], "result_summary": "Listed local backups."},
        }

    def inspect(self, *, backup_id: str, backup_dir: str = "") -> dict[str, Any]:
        archive = self._archive_path(backup_id, backup_dir)
        manifest = self._require_manifest(archive)
        return {
            "status": "ok",
            "backup_id": backup_id,
            "path": str(archive),
            "manifest": self._manifest_summary(manifest),
            "restore_preview": self._restore_preview(archive, manifest),
            "_audit": {"files_read": [str(archive / "manifest.json")], "result_summary": f"Inspected backup {backup_id}."},
        }

    def verify(self, *, backup_id: str, backup_dir: str = "") -> dict[str, Any]:
        archive = self._archive_path(backup_id, backup_dir)
        manifest = self._require_manifest(archive)
        problems = self._verify_manifest(archive, manifest)
        return {
            "status": "ok" if not problems else "error",
            "backup_id": backup_id,
            "valid": not problems,
            "problems": problems,
            "integrity_hash": manifest.get("integrity_hash"),
            "_audit": {"files_read": [str(archive / "manifest.json")], "result_summary": f"Verified backup {backup_id}."},
        }

    def restore(self, *, backup_id: str, backup_dir: str = "") -> dict[str, Any]:
        archive = self._archive_path(backup_id, backup_dir)
        manifest = self._require_manifest(archive)
        problems = self._verify_manifest(archive, manifest)
        if problems:
            return {
                "status": "error",
                "backup_id": backup_id,
                "restored": False,
                "error": "backup integrity verification failed",
                "problems": problems,
                "_audit": {"files_read": [str(archive / "manifest.json")], "result_summary": f"Restore blocked for {backup_id}: integrity failure."},
            }
        self._validate_restore_policy(archive, manifest)
        restored: list[dict[str, Any]] = []
        files_read = [str(archive / "manifest.json")]
        files_written: list[str] = []
        backup_before_restore = self.project_root / ".agent_restore_backups" / backup_id
        for entry in manifest.get("files", []):
            rel = str(entry.get("source_path", ""))
            if not self._restore_allowed(rel):
                restored.append({"path": rel, "status": "skipped", "reason": "path not restorable in v1"})
                continue
            stored = archive / str(entry.get("stored_path", ""))
            target = self.project_root / rel
            self._ensure_inside_project(target)
            if target.exists():
                pre_restore = backup_before_restore / rel
                pre_restore.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, pre_restore)
                files_written.append(str(pre_restore))
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stored, target)
            files_read.append(str(stored))
            files_written.append(str(target))
            restored.append({"path": rel, "status": "restored"})

        for data_entry in manifest.get("data_exports", []):
            stored = archive / str(data_entry.get("stored_path", ""))
            target_name = str(data_entry.get("restore_target", ""))
            if not target_name:
                continue
            target = self.project_root / target_name
            self._ensure_inside_project(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stored, target)
            files_read.append(str(stored))
            files_written.append(str(target))
            restored.append({"path": target_name, "status": "restored_redacted_export"})

        return {
            "status": "ok",
            "backup_id": backup_id,
            "restored": True,
            "restored_items": restored,
            "pre_restore_backup_dir": str(backup_before_restore),
            "policy_preserved": True,
            "_audit": {
                "files_read": files_read,
                "files_written": files_written,
                "result_summary": f"Restored backup {backup_id}.",
            },
        }

    def _candidate_files(self) -> list[tuple[Path, str]]:
        candidates: dict[Path, str] = {}
        for rel in TRACKING_FILES:
            path = self.project_root / rel
            if path.exists():
                candidates[path.resolve()] = "tracking"
        for pattern in CONFIG_PATTERNS:
            for path in self.project_root.glob(pattern):
                if path.is_file():
                    candidates[path.resolve()] = "config"
        for dirname in TRACKING_DIRS:
            root = self.project_root / dirname
            if root.exists():
                for path in root.rglob("*"):
                    if path.is_file() and path.suffix.lower() in {".md", ".json", ".yaml", ".yml"}:
                        candidates[path.resolve()] = "tracking"
        return sorted(candidates.items(), key=lambda item: str(item[0]))

    def _copy_redacted_file(self, source: Path, archive: Path, rel: str) -> Path:
        stored = archive / "files" / rel
        stored.parent.mkdir(parents=True, exist_ok=True)
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            stored.write_text("[binary file omitted from redacted backup]\n", encoding="utf-8")
            return stored
        stored.write_text(self.redactor.redact_text(text), encoding="utf-8")
        return stored

    def _file_entry(self, source: Path, stored: Path, archive: Path, rel: str, kind: str) -> dict[str, Any]:
        return {
            "source_path": rel,
            "stored_path": _relative_to(stored, archive),
            "kind": kind,
            "size": source.stat().st_size,
            "sha256": _sha256_file(stored),
            "redacted": True,
        }

    def _export_memory(self, archive: Path) -> dict[str, Any] | None:
        path = self.project_root / "data" / "memory.sqlite3"
        if not path.exists():
            return None
        records = []
        try:
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, category, scope, source_trust, metadata_json, created_at, content FROM memories ORDER BY created_at DESC"
            ).fetchall()
        except sqlite3.Error:
            return {
                "type": "memory",
                "stored_path": self._write_json(archive, "data/memory.redacted.json", {"status": "error", "error": "memory export failed"}),
                "restore_target": "data/memory.restored.redacted.json",
            }
        finally:
            try:
                conn.close()  # type: ignore[name-defined]
            except Exception:
                pass
        for row in rows:
            content = self.redactor.redact_text(str(row["content"]))
            records.append(
                {
                    "id": row["id"],
                    "category": row["category"],
                    "scope": row["scope"],
                    "source_trust": row["source_trust"],
                    "created_at": row["created_at"],
                    "metadata": self.redactor.redact(_safe_json(row["metadata_json"])),
                    "content": content,
                    "redacted": True,
                }
            )
        stored_path = self._write_json(
            archive,
            "data/memory.redacted.json",
            {"status": "ok", "records": records, "count": len(records), "raw_sqlite_included": False},
        )
        return {"type": "memory", "stored_path": stored_path, "restore_target": "data/memory.restored.redacted.json"}

    def _export_actions(self, archive: Path) -> dict[str, Any] | None:
        path = self.project_root / "data" / "actions.json"
        if not path.exists():
            return None
        payload = _safe_json(path.read_text(encoding="utf-8"))
        stored_path = self._write_json(
            archive,
            "data/actions.redacted.json",
            {"status": "ok", "actions": self.redactor.redact(payload), "redacted": True},
        )
        return {"type": "actions", "stored_path": stored_path, "restore_target": "data/actions.restored.redacted.json"}

    def _export_captures(self, archive: Path) -> dict[str, Any] | None:
        root = self.project_root / "workspace" / "captures"
        if not root.exists():
            return None
        captures = []
        for path in sorted(root.glob("*.json")):
            payload = _safe_json(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                payload["content"] = self.redactor.redact_text(str(payload.get("content", "")))
                payload["redacted"] = True
                captures.append(payload)
        stored_path = self._write_json(
            archive,
            "data/captures.redacted.json",
            {"status": "ok", "captures": self.redactor.redact(captures), "count": len(captures), "redacted": True},
        )
        return {"type": "captures", "stored_path": stored_path, "restore_target": "workspace/captures.restored.redacted.json"}

    def _export_audit_metadata(self, archive: Path) -> dict[str, Any] | None:
        path = self.project_root / "logs" / "audit.jsonl"
        if not path.exists():
            return None
        event_count = 0
        last_tool = None
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            event_count += 1
            try:
                parsed = json.loads(line)
                last_tool = parsed.get("tool_name")
            except json.JSONDecodeError:
                pass
        stored_path = self._write_json(
            archive,
            "data/audit_metadata.redacted.json",
            {
                "status": "ok",
                "audit_log_path": "logs/audit.jsonl",
                "size_bytes": path.stat().st_size,
                "event_count": event_count,
                "last_tool_name": last_tool,
                "raw_events_included": False,
            },
        )
        return {"type": "audit_metadata", "stored_path": stored_path, "restore_target": "data/audit_metadata.restored.redacted.json"}

    def _write_json(self, archive: Path, rel: str, payload: Any) -> str:
        target = archive / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return rel

    def _write_manifest(self, archive: Path, manifest: dict[str, Any]) -> None:
        manifest["integrity_hash"] = _manifest_integrity_hash(manifest)
        (archive / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    def _read_manifest(self, archive: Path) -> dict[str, Any] | None:
        path = archive / "manifest.json"
        if not path.exists():
            return None
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None

    def _require_manifest(self, archive: Path) -> dict[str, Any]:
        manifest = self._read_manifest(archive)
        if manifest is None:
            raise ToolError("backup manifest is missing or malformed")
        return manifest

    def _verify_manifest(self, archive: Path, manifest: dict[str, Any]) -> list[str]:
        problems = []
        expected_integrity = manifest.get("integrity_hash")
        actual_integrity = _manifest_integrity_hash(manifest)
        if expected_integrity != actual_integrity:
            problems.append("manifest integrity hash mismatch")
        for entry in manifest.get("files", []):
            stored = archive / str(entry.get("stored_path", ""))
            if not stored.exists():
                problems.append(f"missing stored file: {entry.get('stored_path')}")
                continue
            if _sha256_file(stored) != entry.get("sha256"):
                problems.append(f"hash mismatch: {entry.get('stored_path')}")
        for entry in manifest.get("data_exports", []):
            stored = archive / str(entry.get("stored_path", ""))
            if not stored.exists():
                problems.append(f"missing data export: {entry.get('stored_path')}")
        return problems

    def _manifest_summary(self, manifest: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema_version": manifest.get("schema_version"),
            "backup_id": manifest.get("backup_id"),
            "created_at": manifest.get("created_at"),
            "redacted": bool(manifest.get("redacted", True)),
            "file_count": len(manifest.get("files", [])),
            "data_export_count": len(manifest.get("data_exports", [])),
            "excluded": manifest.get("excluded", []),
            "integrity_hash": manifest.get("integrity_hash"),
            "personal_connectors_read": bool(manifest.get("personal_connectors_read", False)),
            "limitations": manifest.get("limitations", []),
        }

    def _restore_preview(self, archive: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
        preview = []
        for entry in manifest.get("files", []):
            rel = str(entry.get("source_path", ""))
            target = self.project_root / rel
            current_hash = _sha256_file(target) if target.exists() and target.is_file() else None
            preview.append(
                {
                    "path": rel,
                    "status": "would_restore" if self._restore_allowed(rel) else "skipped",
                    "exists": target.exists(),
                    "changed": current_hash != entry.get("sha256"),
                    "kind": entry.get("kind"),
                }
            )
        for entry in manifest.get("data_exports", []):
            preview.append(
                {
                    "path": entry.get("restore_target"),
                    "status": "would_restore_redacted_export",
                    "type": entry.get("type"),
                }
            )
        return preview

    def _validate_restore_policy(self, archive: Path, manifest: dict[str, Any]) -> None:
        for entry in manifest.get("files", []):
            if entry.get("source_path") != "config/capabilities.yaml":
                continue
            stored = archive / str(entry.get("stored_path", ""))
            try:
                validate_capabilities_config(load_yaml(stored))
            except Exception as exc:
                raise ToolError(f"restore blocked: backed-up capabilities manifest would weaken or violate policy ({exc})") from exc

    def _restore_allowed(self, rel: str) -> bool:
        return (
            rel in TRACKING_FILES
            or rel.startswith("docs/")
            or rel.startswith("config/")
            or rel.startswith("native_skills/")
            or rel == ".env.example"
        )

    def _backup_root(self, backup_dir: str) -> Path:
        raw = backup_dir or os.getenv("BACKUP_DIR") or DEFAULT_BACKUP_DIR
        path = Path(raw).expanduser()
        candidate = path if path.is_absolute() else self.project_root / path
        resolved = candidate.resolve() if candidate.exists() else candidate.parent.resolve() / candidate.name
        self._ensure_not_denied(resolved)
        if not (resolved == self.project_root or self.project_root in resolved.parents or backup_dir or os.getenv("BACKUP_DIR")):
            raise ToolError("backup directory must be inside the workspace unless BACKUP_DIR or --backup-dir is explicitly set")
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    def _archive_path(self, backup_id: str, backup_dir: str) -> Path:
        if "/" in backup_id or "\\" in backup_id or ".." in backup_id:
            raise ToolError("invalid backup id")
        return self._backup_root(backup_dir) / backup_id

    def _ensure_inside_project(self, path: Path) -> None:
        resolved = path.resolve() if path.exists() else path.parent.resolve() / path.name
        if not (resolved == self.project_root or self.project_root in resolved.parents):
            raise ToolError("restore target is outside the project workspace")
        self._ensure_not_denied(resolved)

    def _ensure_not_denied(self, path: Path) -> None:
        denied = tuple(Path(item).expanduser().resolve() for item in DENIED_HOME_PATHS)
        if any(path == root or root in path.parents for root in denied):
            raise ToolError("backup path points at a denied private system location")

    def _secret_exclusion_reason(self, source: Path) -> str:
        if source.name in SECRET_FILENAMES:
            return "secret config file excluded"
        if source.suffix.lower() in SECRET_SUFFIXES:
            return "secret key/certificate file excluded"
        return ""

    def _new_backup_id(self) -> str:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        return f"backup_{stamp}_{uuid4().hex[:8]}"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _relative_to(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_integrity_hash(manifest: dict[str, Any]) -> str:
    payload = dict(manifest)
    payload.pop("integrity_hash", None)
    stable = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def _safe_json(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


BACKUP_SCHEMAS = {
    "backup.create": {
        "type": "function",
        "function": {
            "name": "backup.create",
            "description": "Create a redacted local project backup inside the workspace or configured backup dir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "backup_dir": {"type": "string"},
                    "include_captures": {"type": "boolean"},
                    "include_audit_metadata": {"type": "boolean"},
                    "redacted": {"type": "boolean"},
                },
                "additionalProperties": False,
            },
        },
    },
    "backup.list": {
        "type": "function",
        "function": {
            "name": "backup.list",
            "description": "List local backup archives.",
            "parameters": {
                "type": "object",
                "properties": {"backup_dir": {"type": "string"}},
                "additionalProperties": False,
            },
        },
    },
    "backup.inspect": {
        "type": "function",
        "function": {
            "name": "backup.inspect",
            "description": "Inspect a backup manifest and restore preview.",
            "parameters": {
                "type": "object",
                "properties": {"backup_id": {"type": "string"}, "backup_dir": {"type": "string"}},
                "required": ["backup_id"],
                "additionalProperties": False,
            },
        },
    },
    "backup.verify": {
        "type": "function",
        "function": {
            "name": "backup.verify",
            "description": "Verify backup manifest and file hashes.",
            "parameters": {
                "type": "object",
                "properties": {"backup_id": {"type": "string"}, "backup_dir": {"type": "string"}},
                "required": ["backup_id"],
                "additionalProperties": False,
            },
        },
    },
    "backup.export": {
        "type": "function",
        "function": {
            "name": "backup.export",
            "description": "Create a portable redacted backup export.",
            "parameters": {
                "type": "object",
                "properties": {
                    "backup_dir": {"type": "string"},
                    "include_captures": {"type": "boolean"},
                    "include_audit_metadata": {"type": "boolean"},
                    "redacted": {"type": "boolean"},
                },
                "additionalProperties": False,
            },
        },
    },
    "backup.restore": {
        "type": "function",
        "function": {
            "name": "backup.restore",
            "description": "Restore a backup after approval, with policy validation and pre-restore backups.",
            "parameters": {
                "type": "object",
                "properties": {"backup_id": {"type": "string"}, "backup_dir": {"type": "string"}},
                "required": ["backup_id"],
                "additionalProperties": False,
            },
        },
    },
}
