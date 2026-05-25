---
prompt_id: PTM-07
pack_id: prompt-tracker-maturity-v1
title: PromptOps Workbench
category: prompt_tracking
risk_level: MEDIUM
approval_gate: false
depends_on: ["PTM-06"]
status: completed
order: 7
created_at: 2026-05-23T18:34:04+00:00
imported_at: 2026-05-23T18:34:04+00:00
source_pack: prompts/packs/prompt-tracker-maturity-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T19:28:15+00:00
completed_at: 2026-05-23T19:28:15+00:00
branch:
commit_hash:
related_feature_ids: [PROMPT-LEDGER, PROMPTOPS-WORKBENCH]
expected_outputs:
tests_expected:
tests_run:
test_result: targeted prompt tracker tests passed: 54 passed
docs_updated: yes
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
completion_report_updated:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes: Completed during controlled PTM batch run; evidence recorded in docs/prompt_tracker and targeted tests.
---

# Prompt

You are Codex working in this repo.

Task:
Build PromptOps Workbench v1.

Goal:
Reduce manual overhead. The user should be able to import prompt packs from stdin/clipboard/file, see the next prompt, copy it, and optionally run safe prompts through Codex runner if configured.

Scope:
- Workbench CLI.
- Import from stdin/clipboard/file.
- Next/copy/resume/status/review.
- Safe autopilot scaffolding.
- Runner disabled by default.

Non-goals:
- Do not execute prompt packs automatically.
- Do not enable execute_all.
- Do not run high/critical prompts automatically.
- Do not run personal-data work automatically.
- Do not enable Codex runner by default.
- Do not install packages.
- Do not access private files.

Commands:
- python smart_agent.py work import <file>
- python smart_agent.py work import --stdin
- python smart_agent.py work import-clipboard
- python smart_agent.py work next
- python smart_agent.py work copy-next
- python smart_agent.py work show-next
- python smart_agent.py work resume
- python smart_agent.py work status
- python smart_agent.py work review
- python smart_agent.py work run-next
- python smart_agent.py work autopilot --safe-only --max-prompts N
- python smart_agent.py work audit

Config:
- CODEX_RUNNER_ENABLED=false
- CODEX_RUNNER_COMMAND=codex
- CODEX_RUNNER_MODEL=gpt-5.5
- CODEX_RUNNER_REASONING=high
- CODEX_RUNNER_SANDBOX=workspace-write
- CODEX_RUNNER_APPROVAL_POLICY=on-request
- PROMPTOPS_AUTOPILOT_SAFE_ONLY=true
- PROMPTOPS_STOP_ON_APPROVAL_GATE=true
- PROMPTOPS_STOP_ON_TEST_FAILURE=true

Autopilot allowed categories:
- docs
- tests
- diagnostics
- evals
- prompt_tracking
- feature_maturity
- command_registry
- low_risk_refactor

Autopilot forbidden categories:
- personal_data
- message_send
- email_send
- calendar_write
- contact_write
- policy_relaxation
- external_script
- package_install
- persistence

Requirements:
1. import --stdin accepts pasted prompt pack.
2. import-clipboard uses pbpaste on macOS or degrades cleanly.
3. copy-next uses pbcopy on macOS or prints path/body.
4. run-next is disabled unless CODEX_RUNNER_ENABLED=true.
5. autopilot stops at approval gates.
6. Prompt text is UNTRUSTED_DOCUMENT.
7. Secrets redacted from run reports.
8. Reports stored under reports/promptops/.
9. PROJECT_STATE updated.

Tests:
- import stdin mocked
- import clipboard mocked
- copy-next mocked
- run-next disabled by default
- autopilot skips high/critical
- autopilot stops at approval gate
- prompt queue updated
- project state updated
- command registry updated

Update docs:
- docs/PROMPTOPS_WORKBENCH.md
- README
- AGENTS.md
- CHANGELOG.md
- tracking docs

Final report:
- commands added
- tests run/results
- new workflow examples
- limitations
- next recommended prompt
