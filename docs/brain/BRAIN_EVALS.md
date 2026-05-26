# Brain Evals

Status: mock-first v1.

Brain evals compare provider behavior with safe fixture prompts. Live provider evals are opt-in and must not call paid/cloud providers by default, access personal data, download models, or run HIGH/CRITICAL tools.

## Commands

```bash
python smart_agent.py brain eval --safe
python smart_agent.py brain eval --provider mock
python smart_agent.py brain report
```

`--safe` uses deterministic mock-provider checks. `--provider <provider>` does not automatically make a live provider generate text unless the command is explicitly run with a future-approved live path.

## Categories

- no-tool chat
- no-tools mode expectations
- safe tool-call compatibility
- malformed tool-call handling
- router prompt quality
- refusal and approval-gate behavior
- untrusted content handling
- latency/timeouts
- provider error handling
- final answer quality rubric

## Reports

Reports are written under `reports/brain/` and include provider, model, latency, pass/fail/skip status, safety flags, and skipped reasons. Reports must not contain secrets, personal data, or raw private prompts.
