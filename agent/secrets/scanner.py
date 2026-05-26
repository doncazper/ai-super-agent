from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .redaction import SecretRedactor


PLACEHOLDER_MARKERS = (
    "...",
    "<",
    ">",
    "placeholder",
    "example",
    "fake",
    "test",
    "dummy",
    "not-a-real",
    "not_real",
    "your_",
    "changeme",
    "redacted",
    "secret-value",
    "super-secret",
)


PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
    ("github_token", re.compile(r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
    ("slack_token", re.compile(r"\bxoxb-[A-Za-z0-9-]{16,}\b")),
    ("google_api_key", re.compile(r"\bAIza[A-Za-z0-9_-]{20,}\b")),
    ("oauth_token", re.compile(r"\bya29\.[A-Za-z0-9_-]{16,}\b")),
    ("telegram_token", re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b")),
    (
        "key_value_secret",
        re.compile(
            r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|token|secret|password|authorization)\b\s*[:=]\s*([^\s,;'\"`]+)"
        ),
    ),
)


SENSITIVE_PATH_RE = re.compile(
    r"(?i)(^|/)(\.env($|\.)|.*(token|credential|credentials|client_secret|secret).*\.(json|txt|yaml|yml)$|.*\.(pem|key|p12|pfx)$)"
)


@dataclass(frozen=True)
class SecretFinding:
    path: str
    line: int | None
    kind: str
    severity: str
    redacted_sample: str
    source: str
    placeholder: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "kind": self.kind,
            "severity": self.severity,
            "redacted_sample": self.redacted_sample,
            "source": self.source,
            "placeholder": self.placeholder,
        }


class SecretLeakScanner:
    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root).resolve()
        self.redactor = SecretRedactor()

    def scan(self, *, staged: bool = False) -> dict[str, object]:
        findings = self.scan_staged() if staged else self.scan_tracked_files()
        fail_count = sum(1 for finding in findings if finding.severity == "fail")
        warn_count = sum(1 for finding in findings if finding.severity == "warn")
        return {
            "status": "fail" if fail_count else "ok",
            "scope": "staged" if staged else "tracked",
            "finding_count": len(findings),
            "fail_count": fail_count,
            "warn_count": warn_count,
            "findings": [finding.to_dict() for finding in findings],
            "values_redacted": True,
        }

    def scan_tracked_files(self) -> list[SecretFinding]:
        findings: list[SecretFinding] = []
        for rel_path in self._tracked_files():
            path = self.project_root / rel_path
            if SENSITIVE_PATH_RE.search(rel_path) and Path(rel_path).name != ".env.example":
                findings.append(
                    SecretFinding(
                        path=rel_path,
                        line=None,
                        kind="sensitive_path_tracked",
                        severity="fail" if Path(rel_path).name == ".env" else "warn",
                        redacted_sample="[REDACTED_PATH]",
                        source="tracked_file",
                    )
                )
            if not path.is_file() or self._looks_binary(path):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            findings.extend(self.scan_text(text, path=rel_path, source="tracked_file"))
        return findings

    def scan_staged(self) -> list[SecretFinding]:
        diff = self._git(["diff", "--staged", "--unified=0"]) or ""
        findings: list[SecretFinding] = []
        current_path = "<staged>"
        current_line: int | None = None
        for raw_line in diff.splitlines():
            if raw_line.startswith("+++ b/"):
                current_path = raw_line.removeprefix("+++ b/")
                current_line = None
                if SENSITIVE_PATH_RE.search(current_path):
                    findings.append(
                        SecretFinding(
                            path=current_path,
                            line=None,
                            kind="sensitive_path_staged",
                            severity="fail" if Path(current_path).name == ".env" else "warn",
                            redacted_sample="[REDACTED_PATH]",
                            source="staged_diff",
                        )
                    )
                continue
            if raw_line.startswith("@@"):
                match = re.search(r"\+(\d+)", raw_line)
                current_line = int(match.group(1)) if match else None
                continue
            if raw_line.startswith("+") and not raw_line.startswith("+++"):
                line_text = raw_line[1:]
                findings.extend(self.scan_text(line_text, path=current_path, source="staged_diff", start_line=current_line))
                if current_line is not None:
                    current_line += 1
        return findings

    def scan_text(self, text: str, *, path: str, source: str, start_line: int | None = 1) -> list[SecretFinding]:
        findings: list[SecretFinding] = []
        for offset, line in enumerate(text.splitlines() or [text]):
            line_number = None if start_line is None else start_line + offset
            for kind, pattern in PATTERNS:
                for match in pattern.finditer(line):
                    sample = match.group(0)
                    value = match.group(2) if kind == "key_value_secret" and match.lastindex and match.lastindex >= 2 else sample
                    if not value.strip():
                        continue
                    placeholder = _is_placeholder(value) or _is_placeholder(line) or _is_fixture_path(path)
                    if kind == "key_value_secret" and not _looks_like_literal_secret(value, line=line, path=path):
                        continue
                    severity = "info" if placeholder else "fail"
                    if kind == "key_value_secret" and placeholder:
                        continue
                    findings.append(
                        SecretFinding(
                            path=path,
                            line=line_number,
                            kind=kind,
                            severity=severity,
                            redacted_sample=self.redactor.redact_text(sample),
                            source=source,
                            placeholder=placeholder,
                        )
                    )
        return findings

    def _tracked_files(self) -> list[str]:
        output = self._git(["ls-files", "-z"]) or ""
        return [item for item in output.split("\0") if item]

    def _git(self, args: list[str]) -> str | None:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
        if completed.returncode != 0:
            return None
        return completed.stdout

    @staticmethod
    def _looks_binary(path: Path) -> bool:
        try:
            return b"\0" in path.read_bytes()[:2048]
        except OSError:
            return True


def _is_placeholder(value: str) -> bool:
    normalized = value.casefold()
    return any(marker in normalized for marker in PLACEHOLDER_MARKERS)


def _is_fixture_path(path: str) -> bool:
    parts = Path(path).parts
    return bool(parts and parts[0] in {"tests", "testdata", "fixtures", "qa_fixtures", "eval_cases"})


def _looks_like_literal_secret(value: str, *, line: str, path: str) -> bool:
    cleaned = value.strip().strip('"\'')
    if not cleaned:
        return False
    if any(pattern.search(cleaned) for kind, pattern in PATTERNS if kind != "key_value_secret"):
        return True
    if _is_placeholder(cleaned):
        return True
    code_suffixes = {".py", ".ts", ".tsx", ".js", ".jsx", ".swift"}
    if Path(path).suffix in code_suffixes:
        blocked_prefixes = (
            "self.",
            "os.",
            "env_",
            "parse_",
            "str(",
            "dict(",
            "payload.",
            "response.",
            "settings.",
            "config.",
        )
        if cleaned in {"str", "bytes", "None", "False", "True"} or cleaned.startswith(blocked_prefixes):
            return False
        if any(char in cleaned for char in "(){}[]"):
            return False
        if re.search(r":\s*(str|bytes|SecretStr|None)", line):
            return False
    has_letter = bool(re.search(r"[A-Za-z]", cleaned))
    has_digit = bool(re.search(r"\d", cleaned))
    return len(cleaned) >= 16 and has_letter and has_digit


def redact_findings(findings: Iterable[SecretFinding]) -> list[dict[str, object]]:
    return [finding.to_dict() for finding in findings]
