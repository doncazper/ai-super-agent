from __future__ import annotations

import json
from pathlib import Path

from agent.ui import cli_commands
from agent.ui.prompts import add_prompt_record, audit_prompts, list_prompt_records, mark_prompt, missing_prompts, next_prompt, show_prompt


ROOT = Path(__file__).resolve().parents[1]


def test_prompt_docs_exist_and_queue_has_ids() -> None:
    for path in (
        "docs/PROMPT_LEDGER.md",
        "docs/PROMPT_QUEUE.md",
        "docs/PROMPT_AUDIT.md",
        "docs/templates/prompt_record_template.md",
    ):
        assert (ROOT / path).exists(), path
    queue = (ROOT / "docs/PROMPT_QUEUE.md").read_text(encoding="utf-8")
    rows = [line for line in queue.splitlines() if line.startswith("| ") and "prompt_id" not in line and "---" not in line]
    assert rows
    assert all(line.split("|")[1].strip() for line in rows)


def test_prompt_list_next_and_audit_from_docs() -> None:
    records = list_prompt_records(ROOT)
    assert any(record.prompt_id == "PROMPT-LEDGER-QUEUE" and record.status == "completed" for record in records)
    prompt = next_prompt(ROOT)
    if prompt is not None:
        assert prompt.prompt_id in {
            "SEARXNG-PROVIDER",
            "BRAVE-PROVIDER",
            "WEB-FETCH-EXTRACTION-HARDENING",
                "SOURCE-GROUNDED-RESEARCH-V1",
                "INTERNET-ROUTING-POLICY",
                "CITATION-SOURCE-ATTRIBUTION",
                "WEB-CACHE-DEDUPE-INDEX",
                "INTERNET-DOGFOOD-EVAL-SUITE",
                "REDDIT-FORUM-INTELLIGENCE-TRACK",
                "REDDIT-PROVIDER-POLICY-COMPLIANCE",
                "REDDIT-OAUTH-CONFIG-DOCTOR",
                "REDDIT-READ-ONLY-CONNECTOR",
                "REDDIT-SEARCH-WORKFLOWS",
                "REDDIT-THREAD-FETCH-NORMALIZATION",
                "V2EX-CONNECTOR",
                "PLATFORM-CAPABILITY-REGISTRY",
                "PLATFORM-BRIDGE-BASE-INTERFACES",
                "PLATFORM-CONFIG-PATHS-DETECTION",
                "PLATFORM-DOCTOR-CAPABILITY-COMMANDS",
                "PLATFORM-BRIDGE-STUBS",
                "APP-BRIDGE-API-CONTRACT",
            "PLATFORM-CAPABILITY-MANIFEST-MAPPING",
            "news-capability-manifest-provider-policy",
            "news-provider-registry-status-commands",
            "CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01",
        }

    audit = audit_prompts(ROOT)
    assert audit["total"] >= 37
    assert audit["active_count"] <= 1
    assert audit["next_prompt_id"] in {
        "MESSAGE-SAFETY-ACTION-CENTER",
        "LEAD-INBOX-ABSTRACTION",
        "MACOS-MESSAGES-PROBE",
        "APPLE-MESSAGES-BUSINESS",
        "LEAD-RESPONSE-DRAFTING",
        "MESSAGING-DOGFOOD-SUITES",
        "MESSAGING-RELEASE-GATE",
        "WEB-ACQUISITION-LAYER",
        "WEB-SEARCH-PROVIDER-REGISTRY",
        "SEARXNG-PROVIDER",
        "BRAVE-PROVIDER",
            "WEB-FETCH-EXTRACTION-HARDENING",
                "SOURCE-GROUNDED-RESEARCH-V1",
                "INTERNET-ROUTING-POLICY",
                "CITATION-SOURCE-ATTRIBUTION",
                "WEB-CACHE-DEDUPE-INDEX",
                "INTERNET-DOGFOOD-EVAL-SUITE",
                "REDDIT-FORUM-INTELLIGENCE-TRACK",
                "REDDIT-PROVIDER-POLICY-COMPLIANCE",
                "REDDIT-OAUTH-CONFIG-DOCTOR",
                "REDDIT-READ-ONLY-CONNECTOR",
                "REDDIT-SEARCH-WORKFLOWS",
                "REDDIT-THREAD-FETCH-NORMALIZATION",
                "V2EX-CONNECTOR",
                "PLATFORM-CAPABILITY-REGISTRY",
                    "PLATFORM-BRIDGE-BASE-INTERFACES",
                    "PLATFORM-CONFIG-PATHS-DETECTION",
                    "PLATFORM-DOCTOR-CAPABILITY-COMMANDS",
                    "PLATFORM-BRIDGE-STUBS",
                        "APP-BRIDGE-API-CONTRACT",
                        "PLATFORM-CAPABILITY-MANIFEST-MAPPING",
                        "news-capability-manifest-provider-policy",
                        "news-provider-registry-status-commands",
                        "CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01",
                        None,
                    }


def test_prompt_add_and_mark_complete_requires_evidence_or_unknown(tmp_path) -> None:
    added = add_prompt_record("Demo Prompt", tmp_path)
    assert added["prompt_id"] == "demo-prompt"
    assert (tmp_path / "prompts/queued/demo-prompt.md").exists()

    active = mark_prompt("demo-prompt", "active", project_root=tmp_path)
    assert active["status"] == "active"
    assert (tmp_path / "prompts/active/demo-prompt.md").exists()

    try:
        mark_prompt("demo-prompt", "completed", project_root=tmp_path)
    except ValueError as exc:
        assert "--test-result" in str(exc)
    else:
        raise AssertionError("mark-complete should require test/docs status")

    completed = mark_prompt("demo-prompt", "completed", project_root=tmp_path, unknown=True)
    assert completed["status"] == "completed"
    assert (tmp_path / "prompts/completed/demo-prompt.md").exists()


def test_prompt_cli_commands(tmp_path, capsys) -> None:
    add_prompt_record("queued-one", tmp_path)

    assert cli_commands.dispatch_cli(["prompts", "list"], project_root=tmp_path) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["prompts"][0]["prompt_id"] == "queued-one"

    assert cli_commands.dispatch_cli(["prompts", "mark-complete", "queued-one"], project_root=tmp_path) == 2
    capsys.readouterr()

    assert cli_commands.dispatch_cli(["prompts", "mark-complete", "queued-one", "--unknown"], project_root=tmp_path) == 0
    completed = json.loads(capsys.readouterr().out)
    assert completed["status"] == "completed"


def test_prompt_missing_reports_queued_without_evidence(tmp_path) -> None:
    add_prompt_record("queued-missing", tmp_path)
    missing = missing_prompts(tmp_path)
    assert [record.prompt_id for record in missing] == ["queued-missing"]
    assert show_prompt("queued-missing", tmp_path)["prompt_id"] == "queued-missing"
