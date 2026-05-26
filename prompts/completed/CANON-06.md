---
prompt_id: CANON-06
pack_id: canonical-runtime-gateway-hardening-v1
title: Surface regression lanes
category: qa
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-05"]
status: completed
order: 6
created_at: 2026-05-26T04:45:51+00:00
imported_at: 2026-05-26T04:45:51+00:00
source_pack: prompts/packs/canonical-runtime-gateway-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T05:23:34+00:00
completed_at: 2026-05-26T05:29:52+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: targeted surface regression lane tests: 5 passed; surface lane plus dogfood suite validation: 19 passed; command registry validation: status ok, 580 commands; make policy-check: startup policy ok and capability manifest validation ok
docs_updated: true
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
notes: Added static surface regression lane registry, dry-run-only qa surfaces commands, surface matrix docs, and fixture-safe surface dogfood suites; no lane command execution, personal-data access, live provider call, HIGH/CRITICAL execution, commit, or push.
---

# Prompt

Build Surface Regression Lanes so every frontend/control surface has a safe regression lane.

Create/update:
- docs/qa/SURFACE_REGRESSION_LANES.md
- docs/qa/SURFACE_REGRESSION_MATRIX.md
- agent/qa/surface_lanes.py
- tests/qa/test_surface_regression_lanes.py
- dogfood_suites/surface_cli_core.yaml
- dogfood_suites/surface_runtime_gateway.yaml
- dogfood_suites/surface_promptops.yaml
- dogfood_suites/surface_action_center.yaml
- dogfood_suites/surface_app_bridge_contract.yaml
- dogfood_suites/surface_channels_status.yaml

Surface lanes:
- CLI core
- Command registry
- PromptOps
- Runtime/canonical state
- Agent Gateway / Runtime Kernel
- Action Center/approvals
- ToolBroker/policy/audit
- Web/research
- Reddit/forums
- Weather
- News planned/stubbed
- Brain providers
- Native skills
- Secrets
- QA sandbox
- Media planned/stubbed
- Platform/app bridge
- Channels/Telegram/mobile
- Memory
- Backup/restore

Commands if practical:
- python smart_agent.py qa surfaces
- python smart_agent.py qa surfaces run --dry-run
- python smart_agent.py qa surfaces matrix

Requirements:
- Default dry-run/fixture-safe.
- Personal-data and HIGH/CRITICAL excluded by default.
- Live provider checks opt-in.
- Each lane has owner docs and expected commands/tests.
- Results can feed QA dashboard later.
