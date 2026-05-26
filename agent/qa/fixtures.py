from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


FIXTURE_ROOTS = ("files", "docs", "web", "memory", "commands")


@dataclass(frozen=True)
class FixtureFile:
    relative_path: str
    content: str


DEFAULT_FIXTURES = (
    FixtureFile("files/notes.txt", "Fake QA note for command sandbox testing.\n"),
    FixtureFile("docs/report.md", "# Fake QA Report\n\nThis fixture contains no personal data.\n"),
    FixtureFile("web/page.html", "<html><head><title>QA Fixture</title></head><body>Fake public page.</body></html>\n"),
    FixtureFile("memory/memory.json", '{"records": [{"category": "qa", "content": "synthetic fixture only"}]}\n'),
    FixtureFile("commands/echo.txt", "safe fixture command input\n"),
)


def ensure_fixture_source_tree(project_root: str | Path = ".") -> Path:
    root = Path(project_root) / "qa_fixtures"
    for name in FIXTURE_ROOTS:
        (root / name).mkdir(parents=True, exist_ok=True)
    for fixture in DEFAULT_FIXTURES:
        path = root / fixture.relative_path
        if not path.exists():
            path.write_text(fixture.content, encoding="utf-8")
    return root

