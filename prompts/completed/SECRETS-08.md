---
prompt_id: SECRETS-08
pack_id: secrets-and-api-key-management-v1
title: Secrets management release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["SECRETS-07"]
status: completed
order: 8
created_at: 2026-05-26T00:00:44+00:00
imported_at: 2026-05-26T00:00:44+00:00
source_pack: prompts/packs/secrets-and-api-key-management-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T00:42:20+00:00
completed_at: 2026-05-26T00:50:50+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: full suite 1616 passed; tests/secrets 31 passed; commands validate 541 passed; policy-check passed; tracked/staged secrets scan and git preflight passed with no likely real secret findings
docs_updated: docs/secrets/SECRETS_RELEASE_GATE.md; docs/secrets/SECRETS_MATURITY_REVIEW.md; CHANGELOG.md; docs/PROJECT_STATE.md; docs/FEATURE_REGISTRY.md; docs/FEATURE_MATURITY.md; docs/FEATURE_ROADMAP.md; docs/COMPLETION_REPORT.md; docs/RISK_REGISTER.md; docs/THREAT_MODEL.md; docs/RELEASE_CHECKLIST.md
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
notes: Starting secrets management release gate; validation/maturity review only, no real secrets or provider calls.
---

# Prompt

You are Codex working in this repo.

Task:
Run Secrets and API Key Management release gate.

Goal:
Validate that secrets are handled safely: no real keys committed, .env ignored, .env.example placeholders only, redaction works, provider doctors are safe, and Git preflight scanning works.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation
5. command registry validation
6. secrets unit tests
7. secrets scan
8. git preflight
9. .gitignore check
10. .env.example placeholder check

Verify:
- no .env tracked
- no likely real secrets in tracked files
- no raw secrets in prompt packs
- no raw secrets in docs
- no raw secrets in reports/logs
- redaction tests pass
- provider doctors do not print values
- keychain adapter optional/dry-run by default
- secret scanner detects fake secrets in tests
- command registry updated
- feature maturity conservative

Create/update:
- docs/secrets/SECRETS_RELEASE_GATE.md
- docs/secrets/SECRETS_MATURITY_REVIEW.md

Maturity assessment:
- secrets policy
- API key inventory
- .env/.gitignore
- secret registry
- redaction layer
- secret resolver/env loader
- provider secret doctors
- Keychain strategy/adapter
- secret leak scanner
- git preflight
- user docs

Update:
- CHANGELOG.md
- README.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Final report:
- tests run/results
- scan results
- validation results
- secrets maturity score
- remaining blockers
- whether secrets management is safe to rely on
- next recommended feature track
