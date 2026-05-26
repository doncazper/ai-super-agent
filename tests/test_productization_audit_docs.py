from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCTIZATION = ROOT / "docs" / "productization"


def read_doc(name: str) -> str:
    return (PRODUCTIZATION / name).read_text(encoding="utf-8")


def test_productization_audit_docs_exist():
    expected = [
        "FULL_FEATURE_STATUS_AND_MATURITY_AUDIT.md",
        "FEATURE_MATURITY_SCORECARD.md",
        "PROMPT_TRACKER_MISSED_PROMPTS_AUDIT.md",
        "NEXT_MATURITY_QUEUE.md",
        "NEXT_FEATURE_EXPANSION_CANDIDATES.md",
        "MANUAL_VALIDATION_PLAN.md",
    ]
    for name in expected:
        assert (PRODUCTIZATION / name).is_file(), name


def test_full_feature_audit_contains_required_areas_and_caveats():
    doc = read_doc("FULL_FEATURE_STATUS_AND_MATURITY_AUDIT.md")
    for phrase in [
        "Executive Summary",
        "A. Core Runtime",
        "B. Safety Control Plane",
        "F. News",
        "M. PromptOps",
        "S. Docs / Cloneability",
        "Live validation is incomplete",
        "Prompt tracker disagreement",
    ]:
        assert phrase in doc


def test_scorecard_has_requested_columns_and_conservative_rows():
    doc = read_doc("FEATURE_MATURITY_SCORECARD.md")
    for phrase in [
        "| Area | Feature | Status | Maturity Level | Readiness Score | Evidence |",
        "News | News strategy and manifest | Scaffolded",
        "Platform | Capability registry and bridge stubs | Tested scaffold",
        "PromptOps | Ledger/queue/audit/recovery | Hardened but inconsistent",
    ]:
        assert phrase in doc


def test_prompt_tracker_audit_records_stale_and_next_prompt():
    doc = read_doc("PROMPT_TRACKER_MISSED_PROMPTS_AUDIT.md")
    for phrase in [
        "queued_not_started",
        "orphaned_file",
        "missing_file",
        "news-capability-manifest-provider-policy",
        "prompts/queued/REDDIT-OAUTH-CONFIG-DOCTOR.md",
        "news-provider-registry-status-commands",
    ]:
        assert phrase in doc


def test_next_maturity_queue_prioritizes_release_hygiene():
    doc = read_doc("NEXT_MATURITY_QUEUE.md")
    for phrase in [
        "P1 Core Productization Blockers",
        "MATURITY-P1-001",
        "Clean release-candidate boundary",
        "MATURITY-P1-002",
        "Reconcile prompt tracker disagreements",
    ]:
        assert phrase in doc


def test_manual_validation_plan_keeps_live_work_opt_in():
    doc = read_doc("MANUAL_VALIDATION_PLAN.md")
    for phrase in [
        "Do not use live providers",
        "Do not install, execute, or enable external skills",
        "platform doctor",
        "Any secret appears unredacted",
    ]:
        assert phrase in doc

