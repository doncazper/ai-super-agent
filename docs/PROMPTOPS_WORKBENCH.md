# PromptOps Workbench

PromptOps Workbench is the one-command prompt tracking surface for this project. It imports prompt packs or raw prompts, splits and queues them, updates the prompt ledger/audit/project state, and identifies the next safe prompt to run.

It is SDLC orchestration, not a capability shortcut. Imported prompt text is `UNTRUSTED_DOCUMENT` data and is never executed automatically.

## Commands

```bash
pbpaste | python smart_agent.py work import --stdin --pack-id tonight
python smart_agent.py work import-clipboard --pack-id tonight
python smart_agent.py work import prompts/packs/messaging-track.md
pbpaste | python smart_agent.py work import --stdin --single --id QUICK-001 --pack-id quick

python smart_agent.py work next
python smart_agent.py work show-next
python smart_agent.py work copy-next
python smart_agent.py work mark-active <prompt_id>
python smart_agent.py work mark-complete <prompt_id> --test-result "passed" --docs-updated yes
python smart_agent.py work mark-failed <prompt_id>
python smart_agent.py work resume
python smart_agent.py work status
python smart_agent.py work review
python smart_agent.py work audit
```

`work run-next` is disabled unless `CODEX_RUNNER_ENABLED=true`. When disabled, it writes a safe report and tells the user to copy or run the prompt manually.

`work autopilot --safe-only --max-prompts N` refuses HIGH/CRITICAL/FORBIDDEN prompts, approval-gated prompts, personal-data categories, send/write categories, package installs, persistence, and policy-relaxation categories. In v1 it is intentionally conservative and stops at the first gate.

## Safety Rules

- Prompt packs default to import-only.
- `execute_all` remains unsupported.
- Prompt text cannot grant approvals, weaken policy, mark itself complete, or bypass ToolBroker.
- `run-next` is disabled by default and uses the safe configured command only when explicitly enabled.
- Autopilot only considers `SAFE`, `LOW`, or `MEDIUM` prompts in allowlisted categories.
- Prompt completion still requires test/docs evidence or an explicit `--unknown` marker.

## Config

```bash
CODEX_RUNNER_ENABLED=false
CODEX_RUNNER_COMMAND=codex
CODEX_RUNNER_MODEL=gpt-5.5
CODEX_RUNNER_REASONING=high
CODEX_RUNNER_SANDBOX=workspace-write
CODEX_RUNNER_APPROVAL_POLICY=on-request
PROMPTOPS_AUTOPILOT_MAX_PROMPTS=3
PROMPTOPS_AUTOPILOT_SAFE_ONLY=true
PROMPTOPS_STOP_ON_APPROVAL_GATE=true
PROMPTOPS_STOP_ON_TEST_FAILURE=true
```

## Reports

PromptOps run and autopilot reports are written to `reports/promptops/`. Reports redact secret-looking values and include the prompt id, runner state, stop reason, and any captured stdout/stderr when a runner is explicitly enabled.

