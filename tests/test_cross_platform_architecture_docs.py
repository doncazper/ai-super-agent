from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_cross_platform_docs_exist_and_preserve_core_boundaries() -> None:
    required = [
        "docs/decisions/cross_platform_architecture.md",
        "docs/platforms/PLATFORM_BRIDGE_STRATEGY.md",
        "docs/platforms/CAPABILITY_MATRIX.md",
        "docs/platforms/PLATFORM_BOUNDARIES.md",
        "docs/platforms/PERFORMANCE_OVERHEAD_POLICY.md",
        "docs/platforms/FUTURE_BRIDGE_IMPLEMENTATION_GUIDE.md",
        "docs/platforms/FUTURE_MACOS_BRIDGE_GUIDE.md",
        "docs/platforms/FUTURE_IOS_COMPANION_GUIDE.md",
        "docs/platforms/FUTURE_WINDOWS_BRIDGE_GUIDE.md",
        "docs/platforms/FUTURE_APP_FRONTEND_GUIDE.md",
        "docs/platforms/CROSS_PLATFORM_RELEASE_GATE.md",
    ]
    for path in required:
        assert (ROOT / path).exists(), path

    decision = read("docs/decisions/cross_platform_architecture.md")
    assert "Python agent core remains platform-neutral" in decision
    assert "CLI-only mode must remain fully functional" in decision
    assert "No platform bridge may bypass ToolBroker" in decision
    assert "No platform bridge may bypass PolicyEngine" in decision
    assert "No platform bridge may bypass ApprovalManager or AuditLogger" in decision


def test_platform_capability_matrix_tracks_planned_capabilities_only() -> None:
    matrix = read("docs/platforms/CAPABILITY_MATRIX.md")
    for capability_id in [
        "macos.calendar.read",
        "macos.calendar.write",
        "macos.contacts.search",
        "macos.contacts.update",
        "macos.file_picker",
        "macos.security_scoped_bookmark",
        "macos.messages.probe",
        "macos.notifications",
        "ios.message_compose_handoff",
        "ios.mobile_approval",
        "windows.platform_doctor",
        "windows.ui_automation",
        "microsoft_graph.mail",
        "microsoft_graph.calendar",
        "microsoft_graph.contacts",
        "app_bridge.status",
        "app_bridge.pending_actions",
        "app_bridge.submit_approval",
        "app_bridge.audit_summary",
    ]:
        assert capability_id in matrix

    assert "not executable" in matrix
    assert "ToolBroker mapping" in matrix


def test_platform_overhead_policy_blocks_startup_imports_and_side_effects() -> None:
    policy = read("docs/platforms/PERFORMANCE_OVERHEAD_POLICY.md")
    assert "Do not import platform-specific native frameworks" in policy
    assert "Do not call network APIs" in policy
    assert "Do not start subprocesses" in policy
    assert "Do not scan personal files" in policy
    assert "Do not start app bridge servers" in policy


def test_planned_platform_commands_are_tracked() -> None:
    registry = read("docs/COMMAND_REGISTRY.md")
    for command in [
        "python smart_agent.py platform doctor",
        "python smart_agent.py platform status",
        "python smart_agent.py platform capabilities",
        "python smart_agent.py platform matrix",
        "python smart_agent.py platform explain <capability_id>",
    ]:
        assert command in registry
        assert "planned" in registry


def test_cross_platform_track_is_in_project_trackers() -> None:
    roadmap = read("docs/FEATURE_ROADMAP.md")
    registry = read("docs/FEATURE_REGISTRY.md")
    maturity = read("docs/FEATURE_MATURITY.md")
    assert "Cross-Platform Core + Platform Bridge Track" in roadmap
    assert "CROSS-PLATFORM-ARCHITECTURE-ROADMAP" in registry
    assert "Cross-Platform Core + Platform Bridge architecture roadmap" in maturity


def test_cross_platform_release_gate_and_future_guides_define_safe_build_path() -> None:
    release_gate = read("docs/platforms/CROSS_PLATFORM_RELEASE_GATE.md")
    assert "PLATFORM-CAPABILITY-MANIFEST-MAPPING" in release_gate
    assert "Direct bridge execution is guarded" in release_gate
    assert "APP_BRIDGE_ENABLED=false" in release_gate
    assert "PLATFORM_BRIDGES_ENABLED=false" in release_gate
    assert "Hardened" in release_gate
    assert "Tested" in release_gate
    assert "Specified" in release_gate

    for path in [
        "docs/platforms/FUTURE_MACOS_BRIDGE_GUIDE.md",
        "docs/platforms/FUTURE_IOS_COMPANION_GUIDE.md",
        "docs/platforms/FUTURE_WINDOWS_BRIDGE_GUIDE.md",
        "docs/platforms/FUTURE_APP_FRONTEND_GUIDE.md",
    ]:
        guide = read(path)
        assert "ToolBroker" in guide
        assert "PolicyEngine" in guide
        assert "ApprovalManager" in guide
        assert "AuditLogger" in guide
        assert "Command Registry" in guide
        assert "Startup Overhead Rules" in guide
        assert "Forbidden Without Explicit Future Approval" in guide
