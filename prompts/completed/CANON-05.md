---
prompt_id: CANON-05
pack_id: canonical-runtime-gateway-hardening-v1
title: Code Mode / self-heal artifact hash checks and safety lints
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-04"]
status: completed
order: 5
created_at: 2026-05-26T04:45:51+00:00
imported_at: 2026-05-26T04:45:51+00:00
source_pack: prompts/packs/canonical-runtime-gateway-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T05:08:20+00:00
completed_at: 2026-05-26T05:23:30+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: targeted self-improvement artifact/lint tests: 7 passed; command registry validation: status ok, 577 commands; make policy-check: startup policy ok and capability manifest validation ok; full suite: first run 1696 passed/2 tracker-format failures, fixed targeted docs checks 2 passed, final full suite 1698 passed
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
notes: Added read-only artifact hash reports and safety lints for code-mode/self-heal review; commands do not patch, commit, push, install packages, start services, run providers, or execute queued prompts.
---

# Prompt

Build Code Mode / self-heal artifact hash checks and safety lint strategy.

Create/update:
- docs/self_improvement/CODE_ARTIFACT_HASHES.md
- docs/self_improvement/SELF_HEAL_SAFETY_LINTS.md
- docs/self_improvement/CODE_MODE_TRUTH_BOUNDARY.md
- agent/self_improvement/artifact_hashes.py or agent/workflows/self_improvement_hashes.py
- agent/self_improvement/safety_lints.py or agent/workflows/self_improvement_lints.py
- tests/test_self_improvement_artifact_hashes.py
- tests/test_self_improvement_safety_lints.py

Artifact hash coverage:
- git diff hash
- touched file hashes
- test command output hash
- generated report hash
- approval preview hash
- command registry snapshot hash
- capability manifest hash

Safety lint checks:
- disables audit logging
- weakens PolicyEngine
- bypasses ToolBroker
- changes CRITICAL approval reuse
- enables personal-data capabilities by default
- adds background persistence
- expands filesystem access outside workspace
- removes redaction
- installs packages without approval
- adds live provider default
- starts server/listener by default
- stores secrets
- weakens backup restore policy

Commands if practical:
- python smart_agent.py improve lint-diff
- python smart_agent.py improve artifact-hashes
- python smart_agent.py improve verify-artifacts

Requirements:
- Does not patch files.
- Does not commit/push.
- Hashes deterministic.
- Secrets redacted.
- High-risk findings block self-heal safe-only plan.
- Tests use fixture diffs.
