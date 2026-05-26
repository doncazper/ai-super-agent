# Natural-Language Command Understanding Release Gate

Date: 2026-05-25

## Scope

Validate that natural-language command understanding improves CLI usability without replacing exact commands or weakening ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, command registry metadata, no-tools mode, or approval gates.

## Validation Results

| Check | Command / Evidence | Result |
|---|---|---|
| Full test suite | `./.venv/bin/python -m pytest -q` | Passed: 1437 passed, 1 skipped |
| Startup policy validation | `make policy-check` | Passed: startup policy ok |
| Capability manifest validation | `make policy-check` | Passed via `agent.safety.validation config/capabilities.yaml` |
| Docs validation | focused docs/registry tests in full suite; `smart_agent.py docs validate` checked | No dedicated docs validator is available; `docs validate` falls through to chat |
| Command registry validation | `./.venv/bin/python smart_agent.py commands validate` | Passed: 498 commands, no problems |
| Natural-language eval suite | `./.venv/bin/python smart_agent.py eval run --natural-language --json` | Passed: 15 pass, 0 fail, 5 personal-data skips |
| Natural-language dogfood core | `./.venv/bin/python smart_agent.py dogfood run natural_language_core` | Passed: 8 passed, 0 failed |
| Natural-language dogfood risky | `./.venv/bin/python smart_agent.py dogfood run natural_language_risky` | Passed: 4 passed, 0 failed |
| Exact command regression tests | focused NL CLI/parser/bug tests | Passed: 20 passed |

## Safety Findings

- Exact commands still dispatch separately from natural-language explanation mode.
- No-tools mode is preserved by parser/router and CLI UX tests.
- Natural-language requests produce suggestions, clarifications, preflight plans, or fixture/QA artifacts; they do not execute mapped commands.
- Ambiguous requests clarify.
- Risky requests require preflight, approval, setup, denial, or review metadata.
- Personal-data requests do not execute by default.
- HIGH/CRITICAL actions are not executed by natural-language commands.
- Command registry metadata remains the source of truth for command examples, risk, approval, docs, and testing status.
- Eval, dogfood, and feedback-loop coverage exists, but live/manual user validation remains limited.

## Remaining Blockers

- No long real user dogfood session has been reviewed for NL command UX.
- Generated NL regression fixtures require human review before promotion.
- The NL layer is not an execution engine; future execution must still route exact commands through existing safety controls.
- Dedicated docs validation command is not implemented.

## Gate Decision

Natural-Language Command Understanding is safe to rely on as a local, deterministic-first advisory UX and QA scaffold. It is not a mature autonomous execution layer.
