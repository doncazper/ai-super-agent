---
prompt_id: SECRETS-03
pack_id: secrets-and-api-key-management-v1
title: Secret source resolver and local environment loader
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["SECRETS-02"]
status: completed
order: 3
created_at: 2026-05-26T00:00:44+00:00
imported_at: 2026-05-26T00:00:44+00:00
source_pack: prompts/packs/secrets-and-api-key-management-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T00:11:23+00:00
completed_at: 2026-05-26T00:15:14+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: resolver/env-loader/registry/doctor tests: 26 passed; commands validate ok with 533 commands; make policy-check passed
docs_updated: docs/secrets/SECRET_SOURCES.md, README, command registry/test matrix, trackers, changelog, completion report
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
notes: Secret resolver/env loader complete; reports presence/source metadata only, .env invalid-line warnings omit raw contents, no Keychain access.
---

# Prompt

You are Codex working in this repo.

Task:
Build secret source resolver and local environment loader.

Goal:
Resolve secrets from approved sources in a safe order without committing secrets to repo. Support environment variables, optional untracked .env, and future macOS Keychain.

Scope:
- Secret source resolver.
- Optional .env loader if dependencies already exist or simple parser is safe.
- Tests.

Non-goals:
- Do not require python-dotenv unless already installed.
- Do not install packages.
- Do not access macOS Keychain yet.
- Do not print values.
- Do not store values.

Create:
- agent/secrets/sources.py
- agent/secrets/resolver.py
- agent/secrets/env_loader.py
- tests/secrets/test_secret_resolver_env_loader.py
- docs/secrets/SECRET_SOURCES.md

Secret source order:
1. explicit runtime config, if existing safe config supports it
2. environment variables
3. local untracked .env
4. macOS Keychain, future
5. password manager manual entry, docs only

.env rules:
- .env ignored by git.
- .env.local ignored.
- .env.example tracked.
- missing .env is okay.
- parser handles KEY=value.
- values redacted in diagnostics.
- invalid lines warn without printing secrets.

Commands:
- python smart_agent.py secrets sources
- python smart_agent.py secrets doctor
- python smart_agent.py secrets status

Requirements:
1. Presence/status only in output.
2. No values printed.
3. Missing secrets show setup hints.
4. .env path checked for gitignore.
5. Warn if .env is tracked.
6. Warn if token paths are inside repo.
7. Tests use fake temp .env only.

Tests:
- resolves env var.
- resolves fake .env.
- env var overrides .env.
- missing secret returns missing.
- invalid .env line warning.
- .env tracked warning mocked.
- values redacted.
- command registry updated.

Update docs/tracking.

Final report:
- resolver added
- tests run/results
- next recommended prompt
