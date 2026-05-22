from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent.tools.errors import ToolError


DENIED_HOME_PATHS = (
    "~/.ssh",
    "~/.gnupg",
    "~/Library/Keychains",
    "~/Library/Messages",
    "~/Library/Mail",
    "~/Library/Application Support",
    "~/.aws",
    "~/.config",
)

DENIED_FILENAMES = {".env"}


@dataclass(frozen=True)
class WorkspaceGuard:
    project_root: Path
    allowed_roots: tuple[Path, ...] = field(default_factory=tuple)
    denied_roots: tuple[Path, ...] = field(default_factory=tuple)

    @classmethod
    def for_project(cls, project_root: str | Path) -> "WorkspaceGuard":
        root = Path(project_root).resolve()
        allowed = (
            root,
            (root / "workspace").resolve(),
            (root / "agent").resolve(),
            (root / "tests").resolve(),
        )
        denied = tuple(Path(path).expanduser().resolve() for path in DENIED_HOME_PATHS)
        return cls(project_root=root, allowed_roots=allowed, denied_roots=denied)

    def resolve(self, requested_path: str, *, must_exist: bool = False) -> Path:
        if not requested_path:
            raise ToolError("path is required")
        raw = Path(requested_path).expanduser()
        if ".." in raw.parts:
            raise ToolError("path traversal is blocked")
        candidate = raw if raw.is_absolute() else self.project_root / raw
        if must_exist and not candidate.exists():
            raise ToolError("path does not exist")
        resolved = candidate.resolve() if candidate.exists() else candidate.parent.resolve() / candidate.name
        self._check_allowed(resolved)
        return resolved

    def _check_allowed(self, path: Path) -> None:
        if path.name in DENIED_FILENAMES:
            raise ToolError("access to denied filename is blocked")
        if not any(path == root or root in path.parents for root in self.allowed_roots):
            raise ToolError("path is outside approved roots")
        if any(path == denied or denied in path.parents for denied in self.denied_roots):
            raise ToolError("access to private system paths is blocked")


def _audit(**metadata: Any) -> dict[str, Any]:
    return {"_audit": metadata}


def _backup_file(path: Path, project_root: Path) -> Path:
    backup_dir = project_root / ".agent_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{path.name}.{os.getpid()}.bak"
    shutil.copy2(path, backup_path)
    return backup_path


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def make_filesystem_tools(project_root: str | Path) -> dict[str, Any]:
    guard = WorkspaceGuard.for_project(project_root)

    def list_files(path: str = ".", recursive: bool = False, max_entries: int = 100) -> dict[str, Any]:
        root = guard.resolve(path, must_exist=True)
        if not root.is_dir():
            raise ToolError("path is not a directory")
        entries: list[dict[str, Any]] = []
        iterator = root.rglob("*") if recursive else root.iterdir()
        for index, item in enumerate(sorted(iterator)):
            if index >= max_entries:
                break
            entries.append(
                {
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                }
            )
        return {"path": str(root), "entries": entries, **_audit(files_read=[str(root)])}

    def read_file(path: str, max_bytes: int = 100_000) -> dict[str, Any]:
        target = guard.resolve(path, must_exist=True)
        if not target.is_file():
            raise ToolError("path is not a file")
        data = target.read_bytes()
        if len(data) > max_bytes:
            raise ToolError("file exceeds max_bytes")
        return {
            "path": str(target),
            "content": data.decode("utf-8"),
            **_audit(files_read=[str(target)]),
        }

    def write_file(path: str, content: str, overwrite: bool = False) -> dict[str, Any]:
        target = guard.resolve(path)
        backup_path = None
        if target.exists():
            if not target.is_file():
                raise ToolError("path is not a file")
            if not overwrite:
                raise ToolError("file exists; set overwrite=true to replace it")
            backup_path = _backup_file(target, guard.project_root)
        _atomic_write(target, content)
        result: dict[str, Any] = {"path": str(target), "bytes_written": len(content.encode("utf-8"))}
        if backup_path:
            result["backup_path"] = str(backup_path)
        return {**result, **_audit(files_written=[str(target)] + ([str(backup_path)] if backup_path else []))}

    def patch_file(path: str, old_text: str, new_text: str, expected_replacements: int = 1) -> dict[str, Any]:
        target = guard.resolve(path, must_exist=True)
        if not target.is_file():
            raise ToolError("path is not a file")
        original = target.read_text(encoding="utf-8")
        replacements = original.count(old_text)
        if replacements != expected_replacements:
            raise ToolError("patch did not match expected replacement count")
        backup_path = _backup_file(target, guard.project_root)
        _atomic_write(target, original.replace(old_text, new_text, expected_replacements))
        return {
            "path": str(target),
            "replacements": replacements,
            "backup_path": str(backup_path),
            **_audit(files_read=[str(target)], files_written=[str(target), str(backup_path)]),
        }

    def delete_file(path: str) -> dict[str, Any]:
        target = guard.resolve(path, must_exist=True)
        if target.is_dir():
            raise ToolError("directory deletion is not supported")
        target.unlink()
        return {"path": str(target), "deleted": True, **_audit(files_written=[str(target)])}

    return {
        "filesystem.list": list_files,
        "filesystem.read": read_file,
        "filesystem.write": write_file,
        "filesystem.patch": patch_file,
        "filesystem.delete": delete_file,
    }


FILESYSTEM_SCHEMAS = {
    "filesystem.list": {
        "type": "function",
        "function": {
            "name": "filesystem.list",
            "description": "List files within approved project roots.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "recursive": {"type": "boolean"},
                    "max_entries": {"type": "integer", "minimum": 1, "maximum": 500},
                },
                "additionalProperties": False,
            },
        },
    },
    "filesystem.read": {
        "type": "function",
        "function": {
            "name": "filesystem.read",
            "description": "Read a UTF-8 file within approved project roots.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "max_bytes": {"type": "integer", "minimum": 1, "maximum": 500000},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    "filesystem.write": {
        "type": "function",
        "function": {
            "name": "filesystem.write",
            "description": "Write a UTF-8 file inside approved project roots. Existing files require overwrite=true and are backed up.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "overwrite": {"type": "boolean"},
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
        },
    },
    "filesystem.patch": {
        "type": "function",
        "function": {
            "name": "filesystem.patch",
            "description": "Replace exact text in a UTF-8 file inside approved project roots, with backup.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"},
                    "expected_replacements": {"type": "integer", "minimum": 1},
                },
                "required": ["path", "old_text", "new_text"],
                "additionalProperties": False,
            },
        },
    },
    "filesystem.delete": {
        "type": "function",
        "function": {
            "name": "filesystem.delete",
            "description": "Delete a file inside approved project roots. Requires approval.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
}
