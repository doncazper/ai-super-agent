from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SurfaceRegressionLane:
    lane_id: str
    surface: str
    owner_docs: tuple[str, ...]
    expected_commands: tuple[str, ...]
    expected_tests: tuple[str, ...]
    dogfood_suite: str | None
    risk_level: str = "LOW"
    default_dry_run: bool = True
    excludes_personal_data: bool = True
    excludes_high_critical: bool = True
    live_provider_opt_in: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


SURFACE_LANES: tuple[SurfaceRegressionLane, ...] = (
    SurfaceRegressionLane(
        "surface_cli_core",
        "CLI core",
        ("README.md", "docs/COMMAND_REGISTRY.md"),
        ("python smart_agent.py doctor", "python smart_agent.py commands validate"),
        ("tests/test_ux_packaging.py", "tests/test_command_registry.py"),
        "surface_cli_core",
        "SAFE",
        notes="Covers CLI startup/help/registry health without provider calls.",
    ),
    SurfaceRegressionLane(
        "surface_command_registry",
        "Command registry",
        ("docs/COMMAND_REGISTRY.md", "docs/COMMAND_TEST_MATRIX.md"),
        ("python smart_agent.py commands list", "python smart_agent.py commands validate"),
        ("tests/test_command_registry.py",),
        "surface_cli_core",
        "SAFE",
    ),
    SurfaceRegressionLane(
        "surface_promptops",
        "PromptOps",
        ("docs/PROMPT_QUEUE.md", "docs/PROMPT_LEDGER.md", "docs/PROMPT_AUDIT.md"),
        ("python smart_agent.py prompts next", "python smart_agent.py work status"),
        ("tests/test_feature_maturity_docs.py", "tests/test_prompt_pack.py"),
        "surface_promptops",
        "SAFE",
    ),
    SurfaceRegressionLane(
        "surface_runtime_canonical",
        "Runtime/canonical state",
        ("docs/runtime/CANONICAL_RUNTIME_STATE_MODEL.md", "docs/runtime/SOURCE_OF_TRUTH_HIERARCHY.md"),
        ("python smart_agent.py runtime canonical-state", "python smart_agent.py runtime records validate"),
        ("tests/runtime/test_canonical_runtime_state.py", "tests/runtime/test_execution_records.py"),
        "surface_runtime_gateway",
        "SAFE",
    ),
    SurfaceRegressionLane(
        "surface_gateway_kernel",
        "Agent Gateway / Runtime Kernel",
        ("docs/runtime/AGENT_GATEWAY_RUNTIME_KERNEL.md", "docs/runtime/GATEWAY_API_CONTRACT.md"),
        ("python smart_agent.py runtime gateway-status", "python smart_agent.py runtime kernel-status"),
        ("tests/runtime/test_gateway_kernel_boundary.py",),
        "surface_runtime_gateway",
        "SAFE",
    ),
    SurfaceRegressionLane(
        "surface_action_center",
        "Action Center/approvals",
        ("docs/APPROVALS.md", "docs/RELEASE_CHECKLIST.md"),
        ("python smart_agent.py approvals list", "python smart_agent.py actions list"),
        ("tests/test_actions.py", "tests/test_approval_workflow.py"),
        "surface_action_center",
        "LOW",
        notes="Read-only listing only; no approval consumption or action execution.",
    ),
    SurfaceRegressionLane(
        "surface_toolbroker_policy_audit",
        "ToolBroker/policy/audit",
        ("docs/THREAT_MODEL.md", "docs/RISK_REGISTER.md"),
        ("make policy-check", "python smart_agent.py audit tail 5"),
        ("tests/test_tool_broker.py", "tests/test_policy.py", "tests/test_audit.py"),
        "surface_cli_core",
        "LOW",
    ),
    SurfaceRegressionLane(
        "surface_web_research",
        "Web/research",
        ("docs/web/SOURCE_GROUNDED_RESEARCH.md", "docs/web/SAFE_FETCH_AND_EXTRACTION.md"),
        ("python smart_agent.py web providers", "python smart_agent.py research --help"),
        ("tests/web/",),
        None,
        "MEDIUM",
        live_provider_opt_in=True,
    ),
    SurfaceRegressionLane("surface_reddit_forums", "Reddit/forums", ("docs/forums/FORUM_PROVIDER_REGISTRY.md",), ("python smart_agent.py forums providers",), ("tests/forums/",), None, "MEDIUM", live_provider_opt_in=True),
    SurfaceRegressionLane("surface_weather", "Weather", ("README.md", "docs/COMMAND_REGISTRY.md"), ("python smart_agent.py weather doctor",), ("tests/test_weather.py",), None, "LOW", live_provider_opt_in=True),
    SurfaceRegressionLane("surface_news_stubbed", "News planned/stubbed", ("docs/news/NEWS_INTELLIGENCE_TRACK.md",), ("python smart_agent.py commands search news",), ("tests/test_news_capabilities.py",), None, "LOW", notes="News remains planned/stubbed; lane validates docs/registry only."),
    SurfaceRegressionLane("surface_brain", "Brain providers", ("docs/brain/BRAIN_RUNTIME_RELEASE_GATE.md",), ("python smart_agent.py brain providers", "python smart_agent.py brain status"), ("tests/brain/",), None, "LOW"),
    SurfaceRegressionLane("surface_native_skills", "Native skills", ("docs/native_skills/",), ("python smart_agent.py skills status",), ("tests/test_native_skills.py",), None, "LOW"),
    SurfaceRegressionLane("surface_secrets", "Secrets", ("docs/secrets/",), ("python smart_agent.py secrets status",), ("tests/secrets/",), None, "SAFE"),
    SurfaceRegressionLane("surface_qa_sandbox", "QA sandbox", ("docs/qa/",), ("python smart_agent.py qa status", "python smart_agent.py qa dashboard"), ("tests/qa/",), "command_qa_core", "SAFE"),
    SurfaceRegressionLane("surface_media_stubbed", "Media planned/stubbed", ("docs/media/",), ("python smart_agent.py media providers",), ("tests/media/",), None, "LOW", notes="Media remains mock/dry-run only; no generation provider calls."),
    SurfaceRegressionLane("surface_platform_app_bridge", "Platform/app bridge", ("docs/platforms/",), ("python smart_agent.py platform doctor", "python smart_agent.py platform matrix"), ("tests/platforms/",), "surface_app_bridge_contract", "SAFE"),
    SurfaceRegressionLane("surface_channels", "Channels/Telegram/mobile", ("docs/channels/", "docs/autonomy/TELEGRAM_MOBILE_ACCESS.md"), ("python smart_agent.py channels status", "python smart_agent.py telegram status", "python smart_agent.py mobile status"), ("tests/channels/", "tests/autonomy/test_telegram_mobile_scaffolding.py"), "surface_channels_status", "LOW"),
    SurfaceRegressionLane("surface_memory", "Memory", ("docs/memory/",), ("python smart_agent.py memory status",), ("tests/memory/",), None, "LOW"),
    SurfaceRegressionLane("surface_backup_restore", "Backup/restore", ("docs/backup_restore/BACKUP_RESTORE.md",), ("python smart_agent.py backup list",), ("tests/test_backup_restore.py",), None, "MEDIUM", notes="Restore execution remains approval-gated and excluded from default lane."),
)


def list_surface_lanes() -> dict[str, Any]:
    lanes = [lane.to_dict() for lane in SURFACE_LANES]
    return {
        "status": "ok",
        "lane_count": len(lanes),
        "default_dry_run": True,
        "personal_data_excluded_by_default": True,
        "high_critical_excluded_by_default": True,
        "live_provider_checks_opt_in": True,
        "lanes": lanes,
    }


def surface_matrix() -> dict[str, Any]:
    return {
        "status": "ok",
        "columns": ["lane_id", "surface", "risk_level", "dogfood_suite", "default_dry_run", "live_provider_opt_in"],
        "rows": [
            {
                "lane_id": lane.lane_id,
                "surface": lane.surface,
                "risk_level": lane.risk_level,
                "dogfood_suite": lane.dogfood_suite or "none",
                "default_dry_run": lane.default_dry_run,
                "live_provider_opt_in": lane.live_provider_opt_in,
            }
            for lane in SURFACE_LANES
        ],
    }


def dry_run_surface_lanes() -> dict[str, Any]:
    return {
        "status": "dry_run",
        "executed_commands": [],
        "would_run_count": sum(1 for lane in SURFACE_LANES for _ in lane.expected_commands),
        "blocked_by_default": [
            lane.lane_id
            for lane in SURFACE_LANES
            if lane.live_provider_opt_in or lane.risk_level in {"HIGH", "CRITICAL", "FORBIDDEN"}
        ],
        "notes": [
            "Dry-run only; no commands were executed.",
            "Personal-data and HIGH/CRITICAL commands are excluded by default.",
            "Live provider checks require explicit future opt-in.",
        ],
        "lanes": [lane.to_dict() for lane in SURFACE_LANES],
    }

