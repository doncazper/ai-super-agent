<<<PROMPT_PACK_START>>>
pack_id: secrets-and-api-key-management-v1
pack_title: Secrets and API Key Management Track
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - This prompt pack creates a secure secrets/API-key management system for the agent.
  - It must not store real API keys in the repo.
  - It must create .env.example placeholders, .gitignore protections, macOS Keychain/password-manager guidance, runtime secret discovery, redaction, doctor commands, and connector status.
  - It should support keys for Reddit, SerpAPI, Brave, WeatherAPI, Telegram, Gmail, NewsAPI, Media Cloud, Microsoft Graph, GitHub, and future media providers without committing secret values.
  - Real secrets belong in macOS Keychain, user environment variables, or a local untracked .env file if absolutely necessary.
  - The agent should never store secrets in memory, audit logs, reports, prompt packs, docs, or Git history.

global_rules:
  - Follow SPEC.md.
  - Follow docs/SDLC.md.
  - Follow AGENTS.md.
  - Build safety first, capabilities second.
  - Do not weaken policy.
  - Do not bypass ToolBroker.
  - Do not bypass PolicyEngine.
  - Do not bypass PermissionManager.
  - Do not bypass ApprovalManager.
  - Do not bypass AuditLogger.
  - Do not commit real secrets.
  - Do not print real secrets.
  - Do not store secrets in memory.
  - Do not store secrets in reports.
  - Do not store secrets in prompt packs.
  - Do not store secrets in docs except placeholders.
  - Do not create a tracked secrets file.
  - Do not add real .env to Git.
  - Do not require paid APIs.
  - Update CHANGELOG.md.
  - Update docs/PROJECT_STATE.md.
  - Update docs/FEATURE_REGISTRY.md.
  - Update docs/FEATURE_MATURITY.md.
  - Update docs/FEATURE_ROADMAP.md if status/order changes.
  - Update docs/COMMAND_REGISTRY.md if commands are added/changed.
  - Update docs/COMMAND_TEST_MATRIX.md if QA steps are added/changed.
  - Update docs/COMPLETION_REPORT.md.
  - Update docs/RISK_REGISTER.md if risk changed.
  - Update docs/THREAT_MODEL.md if threat surface changed.
  - Update docs/RELEASE_CHECKLIST.md where release-gate checks change.

stop_conditions:
  - real_secret_detected_in_tracked_file
  - approval_gate
  - failing_tests_not_safely_fixable
  - package_install_required
  - keychain_access_requires_interactive_permission
  - ambiguous_requirements
  - security_policy_change_required

expected_prompt_ids:
  - SECRETS-01
  - SECRETS-02
  - SECRETS-03
  - SECRETS-04
  - SECRETS-05
  - SECRETS-06
  - SECRETS-07
  - SECRETS-08

<<<PROMPT_START id="SECRETS-01" order="1">>
title: Secrets management architecture and policy
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: []
status: queued

PROMPT:
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
<<<PROMPT_END id="SECRETS-01">>

<<<PROMPT_START id="SECRETS-02" order="2">>
title: Secret registry and redaction layer
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["SECRETS-01"]
status: queued

PROMPT:
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
<<<PROMPT_END id="SECRETS-02">>

<<<PROMPT_START id="SECRETS-03" order="3">>
title: Secret source resolver and local environment loader
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["SECRETS-02"]
status: queued

PROMPT:
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
<<<PROMPT_END id="SECRETS-03">>

<<<PROMPT_START id="SECRETS-04" order="4">>
title: Provider secret doctors
category: connector
risk_level: MEDIUM
approval_gate: false
depends_on: ["SECRETS-03"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build provider secret doctors.

Goal:
Create safe status/doctor checks for provider credentials without printing or using secret values unnecessarily.

Scope:
- Doctor commands.
- Provider-specific secret checks.
- Tests.

Non-goals:
- Do not call live APIs unless explicitly in existing provider doctor and safe.
- Do not print values.
- Do not use paid APIs.
- Do not enable providers.

Providers:
- Reddit
- SerpAPI
- Brave Search
- WeatherAPI
- Telegram
- Gmail
- NewsAPI
- Media Cloud
- Microsoft Graph
- GitHub
- ComfyUI/media providers
- LM Studio, not secret but config
- Ollama/llama.cpp, not secret but config

Commands:
- python smart_agent.py secrets doctor reddit
- python smart_agent.py secrets doctor serpapi
- python smart_agent.py secrets doctor brave
- python smart_agent.py secrets doctor weatherapi
- python smart_agent.py secrets doctor telegram
- python smart_agent.py secrets doctor gmail
- python smart_agent.py secrets doctor newsapi
- python smart_agent.py secrets doctor mediacloud
- python smart_agent.py secrets doctor microsoft
- python smart_agent.py secrets doctor github
- python smart_agent.py secrets doctor media
- python smart_agent.py secrets doctor all

Requirements:
1. Reports present/missing only.
2. Setup hints.
3. Provider disabled/enabled status if config exists.
4. Cost policy note for paid/quota providers.
5. Broad-scope warning for Gmail/Microsoft.
6. Token path inside repo warning.
7. OAuth secrets redacted.
8. Command registry updated.

Tests:
- missing provider secrets show hints.
- fake present provider shows present without value.
- broad scope warning.
- token path warning.
- paid provider policy note.
- command registry updated.

Update docs/tracking.

Final report:
- provider doctors added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="SECRETS-04">>

<<<PROMPT_START id="SECRETS-05" order="5">>
title: macOS Keychain integration strategy and optional adapter
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["SECRETS-04"]
status: queued

PROMPT:
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
<<<PROMPT_END id="SECRETS-05">>

<<<PROMPT_START id="SECRETS-06" order="6">>
title: Secret leak scanner and Git preflight
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["SECRETS-05"]
status: queued

PROMPT:
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
<<<PROMPT_END id="SECRETS-06">>

<<<PROMPT_START id="SECRETS-07" order="7">>
title: Secrets documentation and user guide integration
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["SECRETS-06"]
status: queued

PROMPT:
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
<<<PROMPT_END id="SECRETS-07">>

<<<PROMPT_START id="SECRETS-08" order="8">>
title: Secrets management release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["SECRETS-07"]
status: queued

PROMPT:
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
<<<PROMPT_END id="SECRETS-08">>

<<<PROMPT_PACK_END>>>
