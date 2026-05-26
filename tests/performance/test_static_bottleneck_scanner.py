from __future__ import annotations

from pathlib import Path

from agent.performance.patterns import DEFAULT_EXCLUDES
from agent.performance.static_scanner import iter_python_files, scan_static
from agent.tools.registry import default_registry


def test_static_scanner_excludes_generated_and_cache_dirs(tmp_path) -> None:
    (tmp_path / "agent").mkdir()
    (tmp_path / "agent" / "ok.py").write_text("print('ok')\n", encoding="utf-8")
    for excluded in DEFAULT_EXCLUDES:
        path = tmp_path / excluded
        path.mkdir(parents=True, exist_ok=True)
        (path / "ignored.py").write_text("subprocess.run(['x'])\n", encoding="utf-8")
    files = iter_python_files(tmp_path, max_files=100)
    assert files == [tmp_path / "agent" / "ok.py"]


def test_static_scanner_detects_core_heuristics_without_execution(tmp_path) -> None:
    source = tmp_path / "agent" / "slow.py"
    source.parent.mkdir()
    source.write_text(
        "\n".join(
            [
                "import subprocess",
                "import requests",
                "subprocess.run(['sleep', '10'])",
                "requests.get('https://example.test')",
                "for item in items:",
                "    data = Path(item).read_text()",
                "while True:",
                "    break",
            ]
        ),
        encoding="utf-8",
    )
    payload = scan_static(tmp_path, max_files=20, write_report=False)
    titles = {finding["title"] for finding in payload["findings"]}
    assert "Subprocess call without timeout" in titles
    assert "HTTP request without timeout" in titles
    assert "Potential unbounded file read" in titles
    assert "Unbounded retry loop candidate" in titles
    assert payload["files_scanned"] == 1


def test_static_scanner_detects_heavy_imports_in_startup_paths(tmp_path) -> None:
    startup = tmp_path / "smart_agent.py"
    startup.write_text("import llama_cpp\n", encoding="utf-8")
    payload = scan_static(tmp_path, max_files=20, write_report=False)
    assert any(finding["title"] == "Optional heavy import in startup path" for finding in payload["findings"])


def test_static_scan_writes_redacted_report(tmp_path) -> None:
    source = tmp_path / "agent" / "secret_slow.py"
    source.parent.mkdir()
    source.write_text("subprocess.run(['echo', 'token=sk-abcdefghijklmnopqrstuvwxyz'])\n", encoding="utf-8")
    payload = scan_static(tmp_path, max_files=20, write_report=True)
    report_path = Path(payload["report_path"])
    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "sk-abcdefghijklmnopqrstuvwxyz" not in text
    assert "[REDACTED]" in text


def test_static_scan_tool_registered_and_safe(tmp_path) -> None:
    source = tmp_path / "agent" / "slow.py"
    source.parent.mkdir()
    source.write_text("subprocess.run(['x'])\n", encoding="utf-8")
    registry = default_registry(project_root=tmp_path)
    tool = registry.get("perf.scan_static")
    assert tool is not None
    payload = tool.handler(max_files=10)
    assert payload["report_type"] == "static"
    assert payload["files_scanned"] == 1
