---
prompt_id: SECRETS-05
pack_id: secrets-and-api-key-management-v1
title: macOS Keychain integration strategy and optional adapter
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["SECRETS-04"]
status: completed
order: 5
created_at: 2026-05-26T00:00:44+00:00
imported_at: 2026-05-26T00:00:44+00:00
source_pack: prompts/packs/secrets-and-api-key-management-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T00:24:39+00:00
completed_at: 2026-05-26T00:31:49+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 37 focused tests passed; keychain status/get/set dry-run smokes passed; commands validate passed with 537 commands; make policy-check passed.
docs_updated: docs/secrets/MACOS_KEYCHAIN_INTEGRATION.md, README, command registry/test matrix, feature registry/maturity, changelog, project state, completion report
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
notes: Starting optional macOS Keychain strategy/adapter; mock/dry-run only, no real Keychain reads or writes.
---

# Prompt

You are Codex working in this repo.

Task:
Build macOS Keychain integration strategy and optional adapter.

Goal:
Prefer macOS Keychain for local secret storage where practical, while keeping the adapter optional and safe.

Scope:
- Decision docs.
- Optional adapter if safe with standard system commands.
- Tests with mocks.
- No real keychain writes by default.

Non-goals:
- Do not write real secrets to Keychain.
- Do not read real secrets in tests.
- Do not prompt for Keychain access unexpectedly.
- Do not require Keychain for all users.
- Do not store secrets in repo.

Create:
- agent/secrets/keychain.py
- tests/secrets/test_keychain_adapter.py
- docs/secrets/MACOS_KEYCHAIN_INTEGRATION.md

Commands:
- python smart_agent.py secrets keychain status
- python smart_agent.py secrets keychain get <secret_id> --dry-run
- python smart_agent.py secrets keychain set <secret_id> --dry-run

Requirements:
1. Disabled/optional by default.
2. Dry-run default for set.
3. Mock tests only.
4. Real get/set require explicit user action.
5. Never print values.
6. Setup docs show how to store via Keychain manually.
7. Non-macOS returns unsupported.
8. Command registry updated.

Tests:
- non-mac unsupported.
- status works.
- dry-run set does not write.
- get output redacted.
- command registry updated.

Update docs/tracking.

Final report:
- Keychain strategy/adapter added
- tests run/results
- next recommended prompt
