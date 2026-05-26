---
prompt_id: SECRETS-02
pack_id: secrets-and-api-key-management-v1
title: Secret registry and redaction layer
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["SECRETS-01"]
status: completed
order: 2
created_at: 2026-05-26T00:00:44+00:00
imported_at: 2026-05-26T00:00:44+00:00
source_pack: prompts/packs/secrets-and-api-key-management-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T00:05:48+00:00
completed_at: 2026-05-26T00:11:14+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused secrets tests: 21 passed; commands validate ok with 532 commands; make policy-check passed
docs_updated: docs/secrets/SECRET_REGISTRY.md, README, command registry/test matrix, trackers, changelog, completion report
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
notes: Secret registry/redaction layer complete with fake-secret-only tests and brokered metadata commands; no real values read or returned.
---

# Prompt

You are Codex working in this repo.

Task:
Build secret registry and redaction layer.

Goal:
Create a central registry of known secret names/patterns and a redaction utility used by logs, reports, doctor commands, QA, prompt tracker, and provider diagnostics.

Scope:
- Registry of secret names.
- Redaction utilities.
- Tests.

Non-goals:
- Do not read real secrets except presence checks if needed.
- Do not print real secrets.
- Do not store secrets.

Create:
- agent/secrets/
  - __init__.py
  - registry.py
  - redaction.py
  - models.py
  - errors.py
- tests/secrets/test_secret_registry_redaction.py
- docs/secrets/SECRET_REGISTRY.md

Secret registry fields:
- secret_id
- env_name
- provider
- description
- required_for
- sensitivity
- storage_recommendation
- docs_path
- rotation_url_or_note
- placeholder_value
- status

Redaction requirements:
1. Redact known env var values when provided.
2. Redact key-like patterns.
3. Redact GitHub tokens, OpenAI-style keys, Google OAuth tokens, Telegram tokens, API keys.
4. Preserve last 4 characters only if explicitly safe.
5. Never log raw values.
6. Handle nested dict/list/text.
7. Reusable by audit/reporting/doctor code.
8. Tests include representative fake secrets only.

Commands if practical:
- python smart_agent.py secrets list
- python smart_agent.py secrets redaction-test
- python smart_agent.py secrets policy

Tests:
- redacts fake API keys.
- redacts nested dict.
- redacts env var values.
- does not over-redact normal text too aggressively.
- command registry updated.

Update docs/tracking.

Final report:
- registry/redaction added
- tests run/results
- next recommended prompt
