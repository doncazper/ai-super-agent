from __future__ import annotations

from pathlib import Path

from agent.ui.command_registry import COMMANDS


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_brain_runtime_architecture_docs_exist_and_preserve_lm_studio() -> None:
    for path in (
        "docs/decisions/brain_runtime_independence.md",
        "docs/brain/BRAIN_RUNTIME_STRATEGY.md",
        "docs/brain/MODEL_PROVIDER_STRATEGY.md",
        "docs/brain/LM_STUDIO_DECOUPLING_PLAN.md",
        "docs/brain/MODEL_PROVIDER_REQUIREMENTS.md",
        "docs/brain/MCP_INTEROP_DECISION.md",
        "docs/brain/BRAIN_RUNTIME_RELEASE_GATE.md",
        "docs/brain/BRAIN_RUNTIME_MATURITY_REVIEW.md",
    ):
        assert (ROOT / path).exists(), path

    decision = read("docs/decisions/brain_runtime_independence.md")
    strategy = read("docs/brain/BRAIN_RUNTIME_STRATEGY.md")
    providers = read("docs/brain/MODEL_PROVIDER_STRATEGY.md")
    decoupling = read("docs/brain/LM_STUDIO_DECOUPLING_PLAN.md")
    requirements = read("docs/brain/MODEL_PROVIDER_REQUIREMENTS.md")
    mcp = read("docs/brain/MCP_INTEROP_DECISION.md")
    release_gate = read("docs/brain/BRAIN_RUNTIME_RELEASE_GATE.md")
    maturity_review = read("docs/brain/BRAIN_RUNTIME_MATURITY_REVIEW.md")

    assert "BrainRuntimeGateway" in decision
    assert "LM Studio remains the current default provider" in decision
    assert "MCP is not a brain runtime" in decision
    assert "does not change this baseline" in strategy
    assert "Cloud API" in providers
    assert "forbidden by default" in providers
    assert "Existing `LMSTUDIO_*` environment variables continue to work." in decoupling
    assert "No provider bypasses ToolBroker." in requirements
    assert "No provider bypasses PolicyEngine" in requirements
    assert "No MCP server starts during import or normal startup." in mcp
    assert "LM Studio dependency status: partially optional" in release_gate
    assert "normal chat still uses the existing LM Studio" in maturity_review


def test_brain_planned_commands_are_conservative() -> None:
    brain_commands = [record for record in COMMANDS if record.command_id.startswith("CMD-BRAIN-")]
    brain_command_ids = {record.command_id for record in brain_commands}
    assert {
        "CMD-BRAIN-001",
        "CMD-BRAIN-002",
        "CMD-BRAIN-003",
        "CMD-BRAIN-004",
        "CMD-BRAIN-005",
        "CMD-BRAIN-006",
        "CMD-BRAIN-007",
        "CMD-BRAIN-008",
        "CMD-BRAIN-009",
        "CMD-BRAIN-010",
        "CMD-BRAIN-011",
    }.issubset(brain_command_ids)
    for record in brain_commands:
        assert record.status in {"active", "planned"}
        assert record.example
        assert record.docs_link.startswith("docs/brain/")
        assert record.risk_level in {"SAFE", "LOW", "MEDIUM"}
        if record.status == "planned":
            assert "not implemented" in record.manual_qa_status
        assert "no memory write" in record.memory_behavior
    active_commands = {record.command for record in brain_commands if record.status == "active"}
    assert {
        "python smart_agent.py brain providers",
        "python smart_agent.py brain status",
        "python smart_agent.py brain doctor",
    }.issubset(active_commands)
