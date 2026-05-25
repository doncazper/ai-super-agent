---
prompt_id: SKILL-06
pack_id: native-skill-system-hardening-v1
title: Skill compatibility matrix
category: native_skills
risk_level: LOW
approval_gate: false
depends_on: ["SKILL-05"]
status: completed
order: 6
created_at: 2026-05-25T09:50:27+00:00
imported_at: 2026-05-25T09:50:27+00:00
source_pack: prompts/packs/native-skill-system-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T10:31:42+00:00
completed_at: 2026-05-25T10:38:30+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: targeted compatibility/profile/manifest/command tests 30 passed; docs/prompt/release artifact tests 21 passed; startup policy and capability manifest validation passed via make policy-check; command registry validation passed with 415 commands; native skill manifest validation passed with 3 valid; CLI smokes passed for skills compatibility, one-skill compatibility, and platform matrix; full suite passed with 1175 passed, 1 skipped
docs_updated: yes
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
notes: Completed metadata-only native skill compatibility matrix. Added compatibility records, registry methods, read-only compatibility/platform matrix commands, docs, command registry rows, and tracker updates. No skill execution, native platform imports, provider calls, dependency installation, plugin runtime execution, platform behavior enablement, personal-data access, permission grant, or safety bypass added.
---

# Prompt

You are Codex working in this repo.

Task:
Build native skill compatibility matrix.

Goal:
Track which skills work on macOS, iOS companion, Windows, Linux, CLI-only mode, app bridge mode, and future frontends, including dependencies and setup requirements.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/native_skills/SKILL_MANIFEST_SCHEMA.md
- docs/native_skills/SKILL_PROFILES.md
- docs/platforms/CAPABILITY_MATRIX.md, if present
- docs/PROJECT_STATE.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md

Scope:
- Compatibility matrix docs/model.
- CLI status if practical.
- Tests.
- No platform bridge implementation.

Non-goals:
- Do not implement Mac/iOS/Windows platform bridges.
- Do not enable platform-specific skills.
- Do not access personal data.
- Do not add native app code.
- Do not execute skills.

Create or update:
- agent/native_skills/compatibility.py
- tests/native_skills/test_skill_compatibility_matrix.py
- docs/native_skills/SKILL_COMPATIBILITY_MATRIX.md
- docs/templates/skill_compatibility_record_template.md

Compatibility dimensions:
- macOS
- iOS companion
- Windows
- Linux
- CLI-only
- Mac app bridge
- local web dashboard
- Python version
- LM Studio required
- model tool-call support required
- required binaries
- required env vars
- required connectors
- required providers
- required platform capabilities
- personal data required
- approval required
- network required
- filesystem required
- native app bridge required
- status
- setup hint
- tests available
- dogfood suite available

Status values:
- supported
- unsupported
- planned
- stubbed
- requires_setup
- blocked
- unknown
- experimental

Commands if practical:
- python smart_agent.py skills compatibility
- python smart_agent.py skills compatibility <skill_id>
- python smart_agent.py skills platform matrix

Requirements:
1. Compatibility can be computed from manifest dependencies.
2. Missing platform dependency returns requires_setup/unsupported.
3. Skills requiring personal-data capabilities show approval/disabled status.
4. Matrix does not import native platform modules.
5. Matrix does not execute skills.
6. Matrix is safe on all OSes.
7. Matrix should integrate with platform capability registry if present.
8. Command registry updated if commands added.

Tests:
- compatibility computed from manifest.
- macOS-only skill unsupported on mocked Windows.
- Windows-only skill unsupported on mocked macOS.
- missing binary returns requires_setup.
- personal-data skill flagged.
- matrix safe on all OSes.
- no native imports.
- command registry updated.

Update:
- docs/native_skills/SKILL_COMPATIBILITY_MATRIX.md.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- compatibility matrix added
- commands added
- tests run/results
- next recommended prompt
