---
prompt_id: SECRETS-07
pack_id: secrets-and-api-key-management-v1
title: Secrets documentation and user guide integration
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["SECRETS-06"]
status: completed
order: 7
created_at: 2026-05-26T00:00:44+00:00
imported_at: 2026-05-26T00:00:44+00:00
source_pack: prompts/packs/secrets-and-api-key-management-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T00:38:45+00:00
completed_at: 2026-05-26T00:42:11+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 11 secrets docs/scanner tests passed; commands validate passed with 541 commands; make policy-check passed; secrets doctor all smoke passed with redacted config-only output.
docs_updated: README, docs/USER_GUIDE.md, docs/secrets provider docs, provider docs, command registry/test matrix, feature registry/maturity, changelog, project state, completion report
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
notes: Starting secrets documentation and user guide integration; docs/tracker updates only, no real secrets or provider calls.
---

# Prompt

You are Codex working in this repo.

Task:
Integrate secrets management into README, USER_GUIDE, HELP, command registry, and connector docs.

Goal:
Make it clear how the user should store and use API keys safely.

Scope:
- Documentation.
- Command registry.
- User guide.
- No runtime changes unless docs command validation needs tiny fixes.

Non-goals:
- Do not include real secrets.
- Do not store tokens in docs.
- Do not mark providers ready unless evidence exists.

Update:
- README.md
- docs/USER_GUIDE.md if present
- docs/HELP.md if present
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present
- docs/secrets/API_KEY_INVENTORY.md
- docs/secrets/LOCAL_ENV_SETUP.md
- docs/secrets/MACOS_KEYCHAIN_GUIDE.md
- docs/secrets/SECRET_LEAK_SCANNING.md
- provider docs for Reddit, SerpAPI, Brave, WeatherAPI, Telegram, Gmail, NewsAPI, Media Cloud, Microsoft Graph, GitHub, Media

Docs must explain:
1. Do not put real keys in repo.
2. Use Keychain/password manager/env vars.
3. .env is local and gitignored.
4. .env.example has placeholders only.
5. How to run secrets doctor.
6. How to run secret scan before commit.
7. How to rotate/revoke if exposed.
8. Which providers are free/paid/quota-limited where relevant.
9. Which commands require which secret.
10. How to tell if provider is configured without showing keys.

Run docs validation and command registry validation if available.

Final report:
- docs updated
- validation run
- next recommended prompt
