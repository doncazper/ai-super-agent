# Core Runtime And Brain Provider Bug Review

Prompt ID: `CODEBUG-04`
Date: 2026-05-25

## Scope

Review core runtime, startup behavior, router/no-tools handling, LM Studio compatibility, Brain Runtime Gateway/provider scaffolding, fallback policy, and metadata-only brain commands.

## Non-Goals

- No provider migration.
- No removal of LM Studio/Qwopus behavior.
- No model downloads or runtime installs.
- No paid/cloud API calls.
- No MCP server enablement.
- No tool execution semantics changes.

## Evidence Reviewed

- `agent/core/orchestrator.py`
- `agent/core/router.py`
- `agent/core/lmstudio_client.py`
- `agent/config/runtime.py`
- `agent/brain/`
- `tests/brain/`
- `tests/runtime/`
- Startup/router/runtime tests listed below.

## Findings

| Finding | Severity | Status | Notes |
|---|---:|---|---|
| Core runtime and brain provider targeted tests pass | n/a | verified | Focused suite passed with 148 tests. |
| Full test suite passes after CODEBUG-04 | n/a | verified | Full suite passed with 1387 passed, 1 skipped. |
| Brain metadata commands remain no-generation/no-tool-execution | n/a | verified | `brain status`, `brain providers`, `brain route --no-tools`, and `brain doctor` returned metadata/status only. |
| LM Studio remains default compatibility provider | n/a | verified | `brain status` reports `lmstudio_default: true` and fallback disabled. |
| Optional providers remain disabled/lazy by default | n/a | verified | llama.cpp server, Ollama, in-process llama-cpp-python, and MLX report disabled unless explicitly configured. |

## Bugs Fixed

No CODEBUG-04 code fixes were needed. The scoped CLI pipe fix was completed under CODEBUG-03 and full-suite validation here verified it did not regress runtime behavior.

## Bugs Deferred

No new core runtime or brain provider bug was confirmed in this prompt. Continue monitoring provider setup UX and docs-validation command behavior under later CODEBUG prompts.

## Tests And Validation

- `./.venv/bin/python -m pytest -q tests/test_runtime_config.py tests/test_startup_ergonomics.py tests/test_router.py tests/test_lmstudio_loop.py tests/brain tests/runtime`: 148 passed.
- `./.venv/bin/python smart_agent.py brain status`: passed; metadata-only.
- `./.venv/bin/python smart_agent.py brain providers`: passed; metadata-only.
- `./.venv/bin/python smart_agent.py brain route "hello" --no-tools`: passed; selected `lmstudio` without model call or tool execution.
- `./.venv/bin/python smart_agent.py brain doctor`: passed; status-only health summary, no model generation.
- `./.venv/bin/python -m pytest -q`: 1387 passed, 1 skipped.

## Safety Notes

No evidence was found that the Brain Runtime Gateway starts servers, downloads models, enables paid/cloud providers, enables MCP, changes ToolBroker semantics, or attaches tools in no-tools mode by default.
