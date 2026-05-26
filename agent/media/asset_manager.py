from __future__ import annotations

import json
import shutil
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent.media.errors import MediaAssetError, MediaPathError
from agent.media.models import MediaAsset, MediaAssetType, MediaLicenseInfo, MediaPrompt
from agent.media.redaction import prompt_hash, redact_media_prompt


class MediaAssetManager:
    """Bounded media output metadata manager.

    The manager is intentionally boring: it can write fake/test assets and JSON
    metadata inside a project-local media workspace, list/show metadata, and
    plan cleanup. It does not generate media or publish anything.
    """

    def __init__(self, project_root: str | Path = ".", media_root: str | Path | None = None) -> None:
        self.project_root = Path(project_root).resolve()
        self.media_root = (Path(media_root).resolve() if media_root is not None else self.project_root / "workspace" / "media").resolve()
        self._ensure_allowed_root(self.media_root)

    def status(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "media_root": str(self.media_root),
            "exists": self.media_root.exists(),
            "asset_count": len(self.list_assets()),
            "writes_bounded_to_media_root": True,
            "auto_publish_enabled": False,
            "real_generation_enabled": False,
        }

    def resolve_asset_path(self, relative_path: str | Path) -> Path:
        candidate = Path(relative_path)
        if candidate.is_absolute():
            raise MediaPathError("media asset paths must be relative to the controlled media workspace")
        if any(part == ".." for part in candidate.parts):
            raise MediaPathError("path traversal is not allowed for media assets")
        resolved = (self.media_root / candidate).resolve()
        self._ensure_within_media_root(resolved)
        return resolved

    def create_fake_asset(
        self,
        *,
        relative_path: str,
        content: bytes = b"fake media fixture",
        prompt: MediaPrompt | str,
        provider: str = "mock",
        asset_type: MediaAssetType = MediaAssetType.IMAGE,
        metadata: dict[str, Any] | None = None,
        source_inputs: tuple[dict[str, Any], ...] = (),
        audit_ids: tuple[str, ...] = (),
    ) -> MediaAsset:
        output_path = self.resolve_asset_path(relative_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(content)
        media_prompt = prompt if isinstance(prompt, MediaPrompt) else MediaPrompt(str(prompt))
        asset = MediaAsset(
            asset_id=_new_asset_id(),
            asset_type=asset_type,
            path=str(output_path),
            created_at=_now_iso(),
            provider=provider,
            prompt_hash=prompt_hash(media_prompt.text),
            prompt_redacted=redact_media_prompt(media_prompt.text),
            source_inputs=source_inputs,
            metadata=_safe_metadata(metadata or {}),
            license_info=MediaLicenseInfo(
                status="not_reviewed",
                notes=("Fake/test asset metadata only; no usage rights are implied.",),
            ),
            safety_status="not_reviewed",
            audit_ids=audit_ids,
            retention_status="ttl_pending",
        )
        self.write_metadata(asset)
        return asset

    def write_metadata(self, asset: MediaAsset) -> Path:
        asset_path = Path(asset.path).resolve()
        self._ensure_within_media_root(asset_path)
        metadata_path = self.metadata_path(asset_path)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(asset.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return metadata_path

    def list_assets(self) -> tuple[MediaAsset, ...]:
        if not self.media_root.exists():
            return ()
        assets: list[MediaAsset] = []
        for path in sorted(self.media_root.rglob("*.media.json")):
            try:
                assets.append(MediaAsset.from_dict(json.loads(path.read_text(encoding="utf-8"))))
            except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError):
                continue
        return tuple(assets)

    def get_asset(self, asset_id: str) -> MediaAsset | None:
        for asset in self.list_assets():
            if asset.asset_id == asset_id:
                return asset
        return None

    def cleanup(self, *, dry_run: bool = True, older_than_seconds: int = 0) -> dict[str, Any]:
        if not dry_run:
            raise MediaAssetError("MEDIA-02 cleanup command supports dry-run only")
        now = time.time()
        candidates = []
        for asset in self.list_assets():
            path = Path(asset.path)
            try:
                age_seconds = max(0, int(now - path.stat().st_mtime))
            except OSError:
                age_seconds = 0
            if age_seconds >= older_than_seconds:
                candidates.append(
                    {
                        "asset_id": asset.asset_id,
                        "path": asset.path,
                        "metadata_path": str(self.metadata_path(path)),
                        "age_seconds": age_seconds,
                    }
                )
        return {
            "status": "ok",
            "dry_run": True,
            "deleted": [],
            "candidates": candidates,
            "media_root": str(self.media_root),
            "writes_performed": False,
        }

    def clear_all_for_tests(self) -> None:
        """Remove the test media workspace after path bounds are enforced."""

        self._ensure_within_media_root(self.media_root)
        if self.media_root.exists():
            shutil.rmtree(self.media_root)

    def metadata_path(self, asset_path: Path) -> Path:
        resolved = asset_path.resolve()
        self._ensure_within_media_root(resolved)
        return resolved.with_name(resolved.name + ".media.json")

    def _ensure_allowed_root(self, root: Path) -> None:
        allowed_roots = (
            (self.project_root / "workspace" / "media").resolve(),
            (self.project_root / "media_outputs").resolve(),
        )
        if not any(_is_relative_to(root, allowed_root) for allowed_root in allowed_roots):
            raise MediaPathError(
                "media root must be inside workspace/media or media_outputs under the project root"
            )

    def _ensure_within_media_root(self, path: Path) -> None:
        if not _is_relative_to(path.resolve(), self.media_root):
            raise MediaPathError("media asset operation escaped the controlled media workspace")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _new_asset_id() -> str:
    return f"media_{uuid.uuid4().hex[:16]}"


def _safe_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in metadata.items():
        lowered = str(key).lower()
        if any(part in lowered for part in ("secret", "token", "password", "api_key")):
            safe[str(key)] = "[REDACTED]"
        else:
            safe[str(key)] = value
    return safe
