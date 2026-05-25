# Prompt Tracker Dogfood Runbook

Use this runbook to verify prompt queue reliability without running queued feature prompts.

## Safe Smoke

```bash
python smart_agent.py dogfood show prompt_tracker_core
python smart_agent.py dogfood run prompt_tracker_core --dry-run
python smart_agent.py prompts audit
python smart_agent.py prompts evidence
python smart_agent.py prompts recover-plan
python smart_agent.py work status
python smart_agent.py work review
python smart_agent.py eval run --prompt-tracker
```

## Pack Import Smoke

Use a disposable prompt pack fixture when testing import. Do not import an entire production pack unless the goal is only to queue it.

```bash
python smart_agent.py prompts validate-pack prompts/packs/prompt-tracker-maturity-v1.promptpack.md
```

## Stop Conditions

- More than one active prompt.
- Prompt body is executed instead of queued.
- High/critical prompt is selected for autopilot.
- Evidence audit marks completed prompts stale.
- Prompt queue changes without ledger/audit/project-state updates.
