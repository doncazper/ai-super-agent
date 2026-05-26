---
prompt_id: SECRETS-01
pack_id: secrets-and-api-key-management-v1
title: Secrets management architecture and policy
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-26T00:00:44+00:00
imported_at: 2026-05-26T00:00:44+00:00
source_pack: prompts/packs/secrets-and-api-key-management-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T00:01:50+00:00
completed_at: 2026-05-26T00:05:35+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/secrets/test_secrets_policy_docs.py: 3 passed
docs_updated: docs/secrets/* policy docs, docs/decisions/secrets_management_architecture.md, README, trackers, changelog, completion report
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
notes: Docs-only architecture/policy milestone complete; no real secrets, Keychain access, provider calls, paid API enablement, commit, or push.
---

# Prompt

You are Codex working in this repo.

Task:
Create Secrets and API Key Management architecture and policy.

Goal:
Create a secure, repo-safe way to manage API keys and secrets for all providers without committing or exposing secret values.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- README.md
- CHANGELOG.md
- .gitignore, if present
- .env.example, if present
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Scope:
- Policy docs.
- Secret inventory schema.
- .env.example placeholders.
- .gitignore protections.
- No real secrets.

Non-goals:
- Do not create tracked secrets file.
- Do not store real keys.
- Do not print real keys.
- Do not add paid provider usage.
- Do not access Keychain yet.

Create:
- docs/secrets/SECRETS_MANAGEMENT_POLICY.md
- docs/secrets/API_KEY_INVENTORY.md
- docs/secrets/LOCAL_ENV_SETUP.md
- docs/secrets/MACOS_KEYCHAIN_GUIDE.md
- docs/secrets/SECRET_REDATION_POLICY.md
- docs/decisions/secrets_management_architecture.md
- docs/templates/env_template.example

Secret categories:
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_REFRESH_TOKEN
- SERPAPI_API_KEY
- BRAVE_SEARCH_API_KEY
- WEATHERAPI_API_KEY
- TELEGRAM_BOT_TOKEN
- TELEGRAM_ALLOWED_CHAT_IDS
- GMAIL_CLIENT_ID
- GMAIL_CLIENT_SECRET
- GMAIL_TOKEN_PATH
- GMAIL_SCOPES
- NEWSAPI_API_KEY
- MEDIACLOUD_API_KEY
- MICROSOFT_CLIENT_ID
- MICROSOFT_TENANT_ID
- MICROSOFT_CLIENT_SECRET
- GITHUB_TOKEN
- COMFYUI_BASE_URL, not secret
- MEDIA_PROVIDER_API_KEY, future placeholder
- OPENAI_API_KEY, optional/future
- ANTHROPIC_API_KEY, optional/future
- OTHER_PROVIDER_API_KEY

Rules:
1. Real secrets must not be tracked.
2. .env must be gitignored.
3. .env.example contains placeholders only.
4. Keychain/password manager preferred.
5. Environment variables supported.
6. Local untracked .env supported only if gitignored.
7. Audit/log/report redaction mandatory.
8. Secret values never stored in memory.
9. Secret doctor only reports present/missing/redacted.
10. Secret rotation/revocation docs required.

Update:
- .gitignore to exclude .env, .env.*, token files, credential files, secrets files, local keychain exports, OAuth token caches, reports with raw secrets if needed.
- .env.example with placeholders only.
- README.md.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- docs/RISK_REGISTER.md.
- docs/THREAT_MODEL.md.
- CHANGELOG.md.

Run:
- secret scan best effort on tracked files.
- docs validation if present.
- full tests if practical.

Final report:
- docs created
- .gitignore changes
- .env.example changes
- secret scan result
- next recommended prompt
