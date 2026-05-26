---
prompt_id: SECRETS-06
pack_id: secrets-and-api-key-management-v1
title: Secret leak scanner and Git preflight
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["SECRETS-05"]
status: completed
order: 6
created_at: 2026-05-26T00:00:44+00:00
imported_at: 2026-05-26T00:00:44+00:00
source_pack: prompts/packs/secrets-and-api-key-management-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T00:31:59+00:00
completed_at: 2026-05-26T00:38:34+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 7 scanner/preflight fixture tests passed; combined secrets tests passed with 19 tests; commands validate passed with 541 commands; staged and tracked secret scan/preflight smokes passed; make policy-check passed.
docs_updated: docs/secrets/SECRET_LEAK_SCANNING.md, docs/git/SAFE_GIT_PREFLIGHT.md, README, command registry/test matrix, feature registry/maturity, changelog, project state, completion report
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
notes: Starting secret leak scanner and Git preflight; best-effort local scan only, no package installs, no secret values printed.
---

# Prompt

You are Codex working in this repo.

Task:
Build secret leak scanner and Git preflight.

Goal:
Before commits/pushes, scan tracked files, staged diffs, prompt packs, reports, logs, and docs for accidental secrets.

Scope:
- Best-effort scanner.
- Git preflight command.
- Tests.
- No external scanner installation.

Non-goals:
- Do not install gitleaks/trufflehog.
- Do not print secrets.
- Do not rewrite Git history.
- Do not commit/push.

Create:
- agent/secrets/scanner.py
- agent/secrets/git_preflight.py
- tests/secrets/test_secret_scanner_git_preflight.py
- docs/secrets/SECRET_LEAK_SCANNING.md
- docs/git/SAFE_GIT_PREFLIGHT.md

Commands:
- python smart_agent.py secrets scan
- python smart_agent.py secrets scan --staged
- python smart_agent.py git preflight
- python smart_agent.py git preflight --staged

Scanner should check:
- tracked files
- staged diff
- .env tracked
- prompt packs
- docs
- reports
- logs
- token files
- private key patterns
- common provider key patterns
- OAuth token patterns
- GitHub PAT patterns

Requirements:
1. Redact findings.
2. Report file path and line number if possible.
3. Distinguish placeholder from likely secret.
4. Block/flag .env if tracked.
5. Warn on token files in repo.
6. Do not print raw values.
7. Exit nonzero or structured fail when likely secret found.
8. Command registry updated.

Tests:
- fake secret detected and redacted.
- placeholder ignored.
- .env tracked flagged.
- staged scan fixture.
- private key pattern flagged.
- command registry updated.

Update docs/tracking.

Final report:
- scanner added
- tests run/results
- next recommended prompt
