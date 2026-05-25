from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from agent.native_skills.loader import load_manifests
from agent.native_skills.models import NativeSkillManifest
from agent.tools.errors import ToolError


TRUST_LEVEL = "UNTRUSTED_DOCUMENT"
MAX_SKILL_BYTES = 250_000
MAX_FOLDER_FILES = 50

SCRIPT_SUFFIXES = {".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd", ".py", ".js", ".ts", ".rb", ".pl"}
BINARY_SUFFIXES = {".bin", ".exe", ".dylib", ".so", ".dll", ".app", ".pkg", ".jar", ".class"}
MANIFEST_NAMES = {"package.json", "pyproject.toml", "requirements.txt", "Pipfile", "Cargo.toml", "go.mod"}
SKILL_TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".toml"}


@dataclass(frozen=True)
class SkillInspection:
    skill_id: str
    path: str
    target_type: str
    trust_level: str = TRUST_LEVEL
    frontmatter: dict[str, Any] = field(default_factory=dict)
    manifest_fields: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, str]] = field(default_factory=list)
    folder_inventory: dict[str, Any] = field(default_factory=dict)
    missing_metadata: list[str] = field(default_factory=list)
    files_read: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def inspect_skill(project_root: str | Path, path_or_skill_id: str) -> SkillInspection:
    root = Path(project_root).resolve()
    target, manifest = resolve_skill_target(root, path_or_skill_id)
    if target.is_dir():
        return inspect_skill_folder(root, target, manifest=manifest)
    return inspect_skill_file(root, target, manifest=manifest)


def resolve_skill_target(project_root: Path, path_or_skill_id: str) -> tuple[Path, NativeSkillManifest | None]:
    if not path_or_skill_id:
        raise ToolError("path_or_skill_id is required")
    manifest = _manifest_by_id(project_root, path_or_skill_id)
    if manifest is not None:
        return Path(manifest.source_path).resolve(), manifest

    raw = Path(path_or_skill_id).expanduser()
    if ".." in raw.parts:
        raise ToolError("path traversal is blocked")
    candidate = raw if raw.is_absolute() else project_root / raw
    if not candidate.exists():
        raise ToolError("path does not exist")
    resolved = candidate.resolve()
    if not _is_approved_path(project_root, resolved):
        raise ToolError("native skill inspection is limited to approved workspace/project skill paths")
    return resolved, None


def inspect_skill_file(project_root: str | Path, path: str | Path, *, manifest: NativeSkillManifest | None = None) -> SkillInspection:
    root = Path(project_root).resolve()
    target = Path(path).resolve()
    if not target.is_file():
        raise ToolError("path is not a file")
    if not _is_approved_path(root, target):
        raise ToolError("native skill inspection is limited to approved workspace/project skill paths")

    findings: list[dict[str, str]] = []
    manifest_fields: dict[str, Any] = manifest.to_dict() if manifest is not None else {}
    frontmatter: dict[str, Any] = {}
    files_read: list[str] = [str(target)]
    text = ""
    if target.suffix in BINARY_SUFFIXES:
        findings.append(_finding("opaque_binary", "HIGH", target.name, "Skill file is an opaque binary artifact."))
    else:
        text = _read_text(target)
        frontmatter, body = parse_frontmatter(text)
        combined = f"{frontmatter}\n{body}"
        findings.extend(detect_text_findings(combined))
        if target.name in MANIFEST_NAMES or target.suffix in {".yaml", ".yml", ".json", ".toml"}:
            manifest_fields.update(_extract_manifest_fields(text, target))

    findings.extend(_metadata_findings(frontmatter, manifest_fields, text))
    return SkillInspection(
        skill_id=str(manifest.skill_id if manifest is not None else frontmatter.get("skill_id") or frontmatter.get("name") or target.stem),
        path=str(target),
        target_type="file",
        frontmatter=frontmatter,
        manifest_fields=_safe_manifest_fields(manifest_fields),
        findings=findings,
        missing_metadata=_missing_metadata(frontmatter, manifest_fields, text),
        files_read=files_read,
    )


def inspect_skill_folder(project_root: str | Path, folder: str | Path, *, manifest: NativeSkillManifest | None = None) -> SkillInspection:
    root = Path(project_root).resolve()
    target = Path(folder).resolve()
    if not target.is_dir():
        raise ToolError("path is not a folder")
    if not _is_approved_path(root, target):
        raise ToolError("native skill inspection is limited to approved workspace/project skill paths")
    files = [item for item in sorted(target.rglob("*")) if item.is_file()]
    if len(files) > MAX_FOLDER_FILES:
        raise ToolError("skill folder has too many files to inspect safely")

    skill_md = target / "SKILL.md"
    findings: list[dict[str, str]] = []
    frontmatter: dict[str, Any] = {}
    files_read: list[str] = []
    text = ""
    if skill_md.exists():
        text = _read_text(skill_md)
        frontmatter, body = parse_frontmatter(text)
        findings.extend(detect_text_findings(f"{frontmatter}\n{body}"))
        files_read.append(str(skill_md))
    else:
        findings.append(_finding("missing_skill_md", "MEDIUM", "SKILL.md not found", "Skill folder is missing a SKILL.md entry point."))

    inventory = folder_inventory(target, files)
    findings.extend(_inventory_findings(inventory))
    manifest_fields = manifest.to_dict() if manifest is not None else {}
    findings.extend(_metadata_findings(frontmatter, manifest_fields, text))
    return SkillInspection(
        skill_id=str(manifest.skill_id if manifest is not None else frontmatter.get("skill_id") or frontmatter.get("name") or target.name),
        path=str(target),
        target_type="folder",
        frontmatter=frontmatter,
        manifest_fields=_safe_manifest_fields(manifest_fields),
        findings=findings,
        folder_inventory=inventory,
        missing_metadata=_missing_metadata(frontmatter, manifest_fields, text),
        files_read=files_read or [str(target)],
    )


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw = parts[1]
    body = parts[2].lstrip("\n")
    parsed: dict[str, Any] = {}
    for line in raw.splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip("'\"")
    return parsed, body


def detect_text_findings(text: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for match in sorted(set(re.findall(r"\b[a-zA-Z_]+(?:\.[a-zA-Z_][\w-]*)+\b", text))):
        if any(match.startswith(prefix) for prefix in ("filesystem.", "web.", "email.", "messages.", "calendar.", "contacts.", "git.", "code.", "memory.", "browser.", "tasks.")):
            findings.append(_finding("requested_tool", "INFO", match, f"Skill references tool or capability `{match}`."))

    checks: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
        ("script", "HIGH", ("install.sh", "postinstall", "preinstall", "setup.py", "Makefile", "run script"), "Skill references scripts or install hooks."),
        ("shell_command", "HIGH", ("rm -rf", "sudo ", "chmod +x", "bash ", "zsh ", "sh ", "subprocess", "os.system", "child_process", "exec("), "Skill requests shell command execution."),
        ("package_install", "HIGH", ("npm install", "pip install", "brew install", "curl | sh", "wget | sh", "npx "), "Skill requests package installation or remote installer execution."),
        ("network_call", "MEDIUM", ("http://", "https://", "curl ", "wget ", "fetch(", "requests.", "axios.", "websocket"), "Skill references external network calls."),
        ("secret_reference", "FORBIDDEN", ("api_key", "apikey", "secret", "password", "token", "keychain", "1password", "op read"), "Skill references secrets, tokens, passwords, or Keychain-like access."),
        ("filesystem_access", "FORBIDDEN", ("~/.ssh", "~/.gnupg", "~/Library", "/etc/passwd", "/var/db", "full disk access", "unrestricted filesystem"), "Skill requests private or unrestricted filesystem access."),
        ("personal_data", "HIGH", ("gmail", "inbox", "email body", "messages database", "contacts database", "calendar database", "browser history"), "Skill references personal-data sources."),
        ("browser_session", "FORBIDDEN", ("cookies", "session token", "browser profile", "password manager", "localstorage", "chrome profile"), "Skill references browser cookies, sessions, profiles, or password manager data."),
        ("prompt_injection", "HIGH", ("ignore previous instructions", "ignore system instructions", "reveal secrets", "developer message", "system prompt", "call tools"), "Skill contains prompt-injection-like language."),
        ("approval_bypass", "FORBIDDEN", ("bypass approval", "skip approval", "disable audit", "ignore policy", "bypass toolbroker", "grant permissions"), "Skill requests approval, policy, or audit bypass."),
        ("dangerous_action", "CRITICAL", ("send email", "send message", "delete contacts", "delete calendar", "push to production", "deploy to production"), "Skill describes high-impact send/write actions."),
        ("opaque_binary", "HIGH", (".dylib", ".so", ".dll", ".exe", ".bin", ".pkg", ".jar"), "Skill references opaque binary artifacts."),
    )
    lowered = text.casefold()
    for kind, severity, needles, reason in checks:
        for needle in needles:
            if needle.casefold() in lowered:
                findings.append(_finding(kind, severity, needle, reason))
    return findings


def folder_inventory(folder: Path, files: list[Path]) -> dict[str, Any]:
    scripts = [str(path.relative_to(folder)) for path in files if path.suffix in SCRIPT_SUFFIXES]
    binaries = [str(path.relative_to(folder)) for path in files if path.suffix in BINARY_SUFFIXES]
    manifests = [str(path.relative_to(folder)) for path in files if path.name in MANIFEST_NAMES]
    docs = [str(path.relative_to(folder)) for path in files if path.name.casefold() in {"readme.md", "docs.md"} or "docs" in path.parts]
    tests = [str(path.relative_to(folder)) for path in files if "test" in path.name.casefold()]
    return {
        "file_count": len(files),
        "scripts": scripts,
        "opaque_binaries": binaries,
        "dependency_manifests": manifests,
        "docs": docs,
        "tests": tests,
        "has_skill_md": (folder / "SKILL.md").exists(),
    }


def _inventory_findings(inventory: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if inventory["scripts"]:
        findings.append(_finding("script", "HIGH", ", ".join(inventory["scripts"]), "Skill folder contains executable script files; they were not run."))
    if inventory["opaque_binaries"]:
        findings.append(_finding("opaque_binary", "HIGH", ", ".join(inventory["opaque_binaries"]), "Skill folder contains opaque binary artifacts."))
    if inventory["dependency_manifests"]:
        findings.append(_finding("package_install", "HIGH", ", ".join(inventory["dependency_manifests"]), "Skill folder includes dependency manifests that require separate review."))
    if not inventory["tests"]:
        findings.append(_finding("missing_tests", "LOW", "tests not found", "Skill folder does not include an obvious test file."))
    if not inventory["docs"]:
        findings.append(_finding("missing_docs", "LOW", "docs not found", "Skill folder does not include obvious docs beyond SKILL.md."))
    return findings


def _metadata_findings(frontmatter: dict[str, Any], manifest_fields: dict[str, Any], text: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    missing = _missing_metadata(frontmatter, manifest_fields, text)
    for field_name in missing:
        kind = "missing_license" if field_name == "license" else "missing_metadata"
        findings.append(_finding(kind, "LOW", field_name, f"Skill is missing {field_name} metadata."))
    return findings


def _missing_metadata(frontmatter: dict[str, Any], manifest_fields: dict[str, Any], text: str) -> list[str]:
    available = {key.casefold() for key in frontmatter} | {key.casefold() for key in manifest_fields}
    missing: list[str] = []
    if "license" not in available and not re.search(r"(?im)^\s*license\s*[:#-]\s*(.+)$", text):
        missing.append("license")
    if "risk_level" not in available and "risk-level" not in available:
        missing.append("risk_level")
    if "trust_level" not in available and "trust-level" not in available:
        missing.append("trust_level")
    if not ({"docs", "docs_path", "docs-path"} & available):
        missing.append("docs")
    if not ({"tests", "tests_path", "tests-path"} & available):
        missing.append("tests")
    return missing


def _read_text(path: Path) -> str:
    data = path.read_bytes()
    if len(data) > MAX_SKILL_BYTES:
        raise ToolError("skill file exceeds max inspection size")
    if b"\x00" in data:
        raise ToolError("skill file appears to be binary")
    return data.decode("utf-8", errors="replace")


def _extract_manifest_fields(text: str, target: Path) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for line in text.splitlines():
        if line[:1].isspace():
            continue
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key:
            fields[key] = value.strip().strip("'\"")
    fields.setdefault("source_file", target.name)
    return fields


def _safe_manifest_fields(fields: dict[str, Any]) -> dict[str, Any]:
    denied = {"raw", "inputs_schema", "outputs_schema"}
    return {key: value for key, value in fields.items() if key not in denied}


def _manifest_by_id(project_root: Path, skill_id: str) -> NativeSkillManifest | None:
    for manifest in load_manifests(project_root):
        if manifest.skill_id == skill_id:
            return manifest
    return None


def _is_approved_path(project_root: Path, path: Path) -> bool:
    approved_roots = [
        project_root / "workspace",
        project_root / "native_skills",
        project_root / "docs" / "native_skills",
    ]
    return any(path == root.resolve() or root.resolve() in path.parents for root in approved_roots if root.exists())


def _finding(kind: str, severity: str, evidence: str, reason: str) -> dict[str, str]:
    return {"kind": kind, "severity": severity, "evidence": str(evidence)[:180], "reason": reason}
