---
prompt_id: SECRETS-04
pack_id: secrets-and-api-key-management-v1
title: Provider secret doctors
category: connector
risk_level: MEDIUM
approval_gate: false
depends_on: ["SECRETS-03"]
status: completed
order: 4
created_at: 2026-05-26T00:00:44+00:00
imported_at: 2026-05-26T00:00:44+00:00
source_pack: prompts/packs/secrets-and-api-key-management-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T00:15:25+00:00
completed_at: 2026-05-26T00:24:28+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: provider doctor/secrets tests: 34 passed; full suite: 1602 passed; commands validate ok with 534 commands; make policy-check passed
docs_updated: docs/secrets/PROVIDER_SECRET_DOCTORS.md, README, command registry/test matrix, trackers, changelog, completion report
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
notes: Provider secret doctors complete; config-only present/missing/setup metadata, no provider API calls, no paid API enablement, no values printed.
---

# Prompt

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
