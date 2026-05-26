from __future__ import annotations

import re
from dataclasses import dataclass


DEFAULT_EXCLUDES = (
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "logs",
    "reports",
    "media_outputs",
    ".qa_workspace",
)


@dataclass(frozen=True)
class StaticPattern:
    pattern_id: str
    title: str
    category: str
    severity: str
    regex: re.Pattern[str]
    likely_cause: str
    recommendation: str


STATIC_PATTERNS: tuple[StaticPattern, ...] = (
    StaticPattern(
        "subprocess_without_timeout",
        "Subprocess call without timeout",
        "Subprocess timeout",
        "P2",
        re.compile(r"\bsubprocess\.(run|call|check_call|check_output|Popen)\([^#\n]*(?!timeout\s*=)"),
        "A subprocess may hang indefinitely when no timeout is provided.",
        "Add an explicit timeout and structured failure handling.",
    ),
    StaticPattern(
        "http_without_timeout",
        "HTTP request without timeout",
        "Missing timeouts",
        "P2",
        re.compile(r"\b(requests|httpx)\.(get|post|put|delete|request)\([^#\n]*(?!timeout\s*=)"),
        "Network calls without timeouts can block CLI/status flows.",
        "Pass a bounded timeout and return structured unavailable/setup errors.",
    ),
    StaticPattern(
        "broad_rglob",
        "Broad recursive file traversal",
        "Broad traversal",
        "P3",
        re.compile(r"\.(rglob|glob)\([\"']\*\*?/?\*?[\"']\)|\bos\.walk\("),
        "Broad traversal can scan caches, generated files, or large trees.",
        "Constrain roots, exclude generated directories, and cap files.",
    ),
    StaticPattern(
        "unbounded_read",
        "Potential unbounded file read",
        "Unbounded IO",
        "P3",
        re.compile(r"\.(read_text|read_bytes|read)\(\)"),
        "Whole-file reads can be expensive on large files or generated artifacts.",
        "Bound reads by size or use streaming for large inputs.",
    ),
    StaticPattern(
        "full_pytest_in_command",
        "Full test suite from normal command path",
        "Slow commands",
        "P2",
        re.compile(r"([\"']pytest[\"']|\bpython\s+-m\s+pytest\b|\b-m\s+pytest\b)(?![^\"'\n]*(tests/|--maxfail|-q))"),
        "Normal commands should not unexpectedly run the full suite.",
        "Move full-suite runs to explicit QA/release-gate commands.",
    ),
    StaticPattern(
        "module_level_io",
        "Module-level IO/network call",
        "Startup/import overhead",
        "P2",
        re.compile(r"^(?!\s)(.*\b(open|read_text|read_bytes|requests\.|httpx\.)\()"),
        "Top-level IO/network work can slow startup or introduce side effects on import.",
        "Move IO/network work behind explicit functions or lazy providers.",
    ),
    StaticPattern(
        "regex_compile",
        "Repeated regex compilation candidate",
        "Repeated regex compilation",
        "P4",
        re.compile(r"\bre\.compile\("),
        "Regex compilation inside hot paths or loops can add avoidable overhead.",
        "Keep reusable regexes at module scope unless the pattern is dynamic.",
    ),
    StaticPattern(
        "unbounded_retry_loop",
        "Unbounded retry loop candidate",
        "Unbounded retries",
        "P2",
        re.compile(r"\bwhile\s+True\s*:"),
        "Unbounded loops can hang workflows without a max attempt or timeout.",
        "Add max attempts, timeout, and cancellation/denial behavior.",
    ),
)


HEAVY_OPTIONAL_IMPORTS = {
    "llama_cpp",
    "mlx",
    "mlx_lm",
    "ollama",
    "torch",
    "tensorflow",
    "pandas",
    "numpy",
    "cv2",
    "PIL",
}
