from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.safety.redaction import SecretRedactor

from .errors import PerformanceReportNotFoundError
from .models import PerformanceReport


REPORTS_DIR = Path("reports/performance")


class PerformanceReportStore:
    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root).resolve()
        self.reports_dir = self.project_root / REPORTS_DIR
        self.redactor = SecretRedactor()

    def ensure_dir(self) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def report_path(self, report_id: str, *, suffix: str = ".json") -> Path:
        safe_id = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in report_id)
        return self.reports_dir / f"{safe_id}{suffix}"

    def redact_payload(self, payload: Any) -> Any:
        return self.redactor.redact(payload)

    def write_report(self, report: PerformanceReport) -> Path:
        self.ensure_dir()
        payload = self.redact_payload(report.to_dict())
        path = self.report_path(report.report_id)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def write_markdown(self, report: PerformanceReport) -> Path:
        self.ensure_dir()
        path = self.report_path(report.report_id, suffix=".md")
        path.write_text(self.render_markdown(report), encoding="utf-8")
        return path

    def render_markdown(self, report: PerformanceReport) -> str:
        payload = self.redact_payload(report.to_dict())
        findings = payload.get("findings", []) if isinstance(payload, dict) else []
        lines = [
            f"# Performance Report {payload.get('report_id', report.report_id)}",
            "",
            f"- Type: {payload.get('report_type', report.report_type)}",
            f"- Status: {payload.get('status', report.status)}",
            f"- Generated: {payload.get('generated_at', report.generated_at)}",
            f"- Redacted: {payload.get('redacted', True)}",
            "",
            "## Summary",
            "",
            str(payload.get("summary", "")),
            "",
            "## Findings",
            "",
        ]
        if findings:
            for finding in findings:
                if isinstance(finding, dict):
                    lines.append(f"- `{finding.get('finding_id')}` [{finding.get('severity')}] {finding.get('title')}")
        else:
            lines.append("- none")
        lines.append("")
        return "\n".join(lines)

    def list_reports(self) -> list[Path]:
        if not self.reports_dir.exists():
            return []
        reports = [path for path in self.reports_dir.glob("*.json") if not path.name.endswith(".profile.json")]
        return sorted(reports, key=lambda path: path.stat().st_mtime, reverse=True)

    def latest_report_path(self) -> Path | None:
        reports = self.list_reports()
        return reports[0] if reports else None

    def read_report(self, report_id: str) -> dict[str, Any]:
        path = self.report_path(report_id)
        if not path.exists():
            raise PerformanceReportNotFoundError(f"performance report not found: {report_id}")
        return self.redact_payload(json.loads(path.read_text(encoding="utf-8")))

    def read_latest_report(self) -> dict[str, Any]:
        path = self.latest_report_path()
        if path is None:
            return {
                "status": "no_report",
                "message": "No performance reports found. Run a future safe scan or benchmark after PERF runtime commands are implemented.",
                "reports_dir": str(self.reports_dir),
            }
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload = self.redact_payload(payload)
        if isinstance(payload, dict):
            payload.setdefault("status", "ok")
            payload["report_path"] = str(path)
        return payload

    def read_latest_findings(self) -> dict[str, Any]:
        report = self.read_latest_report()
        if report.get("status") == "no_report":
            return {**report, "findings": []}
        findings = report.get("findings", [])
        if not isinstance(findings, list):
            findings = []
        return {
            "status": "ok",
            "report_id": report.get("report_id"),
            "report_path": report.get("report_path"),
            "finding_count": len(findings),
            "findings": findings,
        }
