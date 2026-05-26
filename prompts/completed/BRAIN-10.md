---
prompt_id: BRAIN-10
pack_id: brain-runtime-independence-v1
title: Optional MCP interop decision and adapters
category: connector
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-09"]
status: completed
order: 10
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T17:07:08+00:00
completed_at: 2026-05-25T17:10:29+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: MCP adapter stub tests plus broader brain/docs/feature-maturity/command tests passed with 97 passed; command registry validation ok with 443 commands; startup policy and capability manifest validation passed via make policy-check; CLI smokes for brain mcp-decision and mcp status/doctor/server --dry-run/clients passed
docs_updated: docs/decisions/mcp_interop_strategy.md, docs/brain/MCP_IS_NOT_THE_BRAIN_RUNTIME.md, docs/mcp/MCP_ADAPTER_BOUNDARIES.md, README, .env.example, command registry/test matrix, feature registry, feature maturity, roadmap, risk register, threat model
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
command_registry_updated:
completion_report_updated:
evidence_links:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes: MCP remains optional, disabled by default, not brain runtime, no package install, no server/listener, no external connection, no tool exposure, no personal tools, and no safety-control bypass.
---

# Prompt

You are Codex working in this repo.

Task:
Create MCP interop decision and optional adapter scaffolding.

Goal:
Clarify that MCP is optional interoperability for tools/resources/prompts, not the model runtime. Prepare safe adapter boundaries for future MCP server/client support without allowing MCP to bypass ToolBroker, PolicyEngine, ApprovalManager, or AuditLogger.

Scope:
- Decision record.
- Adapter interface/stubs if safe.
- No MCP server running.
- No external MCP connections.
- Tests for stubs.

Non-goals:
- Do not implement full MCP server.
- Do not connect to external MCP servers.
- Do not expose tools externally.
- Do not bypass ToolBroker.
- Do not allow external clients to execute tools directly.
- Do not add network listener.
- Do not install MCP packages.
- Do not treat MCP as required to replace LM Studio.

Create:
- docs/decisions/mcp_interop_strategy.md
- docs/brain/MCP_IS_NOT_THE_BRAIN_RUNTIME.md
- docs/mcp/MCP_ADAPTER_BOUNDARIES.md
- agent/mcp/
  - __init__.py
  - models.py
  - adapter.py
  - server_stub.py
  - client_stub.py
- tests/mcp/test_mcp_adapter_stubs.py

MCP strategy:
1. MCP is optional.
2. MCP does not load the model.
3. MCP does not replace BrainRuntimeGateway.
4. MCP server, if later implemented, exposes only policy-gated tools through ToolBroker.
5. MCP client, if later implemented, consumes external tools only through ToolBroker-like policy wrappers.
6. No external MCP tool can bypass approval/audit.
7. MCP server disabled by default.
8. Network listeners disabled by default.
9. External client access requires pairing/auth and audit.
10. Personal-data tools remain disabled by default.

Commands as planned/stubbed if practical:
- python smart_agent.py mcp status
- python smart_agent.py mcp doctor
- python smart_agent.py mcp server --dry-run
- python smart_agent.py mcp clients

Tests:
- MCP stubs disabled by default.
- MCP server not started.
- external tool call stub requires ToolBroker route.
- personal tools not exposed.
- config defaults safe.
- command registry updated if commands added.

Update:
- docs/FEATURE_ROADMAP.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md if commands added
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- CHANGELOG.md

Run tests/validations.

Final report:
- MCP decision created
- stubs added or not
- tests run/results
- next recommended prompt
