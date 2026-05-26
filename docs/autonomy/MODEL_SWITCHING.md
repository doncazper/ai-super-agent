# Model Switching Groundwork

Last updated: 2026-05-25

## Scope

HERMES-09 adds model-switching metadata and compatibility checks only. It does not persist provider changes, call a model, start a runtime, install/download a model, enable paid/cloud providers, or change the default provider away from LM Studio.

## Switch Record

Every switch preview creates a `ModelSwitchRecord` with:

- `switch_id`
- `from_provider`
- `from_model`
- `to_provider`
- `to_model`
- `reason`
- `session_id`
- `tool_call_support_required`
- `compatibility_check`
- `context_migration_summary`
- `risk_level`
- `approved_by_user`
- `audit_ids`
- `rollback_plan`

The record is intentionally metadata-only. `context_migration_summary` is redacted and states that no context is migrated by default.

## Compatibility Checks

Before any future provider/model switch can be executable, the agent must check:

- provider is registered;
- provider is configured;
- provider is available;
- tool-call support exists when the route requires tools;
- cloud/paid provider policy allows the target;
- fallback behavior is bounded and explicit;
- rollback can restore the previous provider/model.

Current non-dry-run requests are blocked with `persistent_model_switch_not_implemented`.

## CLI

```bash
python smart_agent.py brain switch lmstudio --dry-run
python smart_agent.py brain switch lmstudio
python smart_agent.py brain switch mock --dry-run --requires-tool-calls
```

`--dry-run` returns a preview. Without `--dry-run`, v1 returns a blocked response and changes no config.

## Safety Rules

- LM Studio remains the default compatibility provider unless explicit future config changes are approved.
- No model generation happens during switch preview.
- No tools execute during switch preview.
- No memory is written.
- No paid/cloud provider is selected by default.
- No context is migrated by default.
- No default provider config is persisted in v1.

## Future Requirements

Before real switching is allowed, a future prompt must add:

- ToolBroker/PolicyEngine mapping for executable switch operations;
- audit correlation IDs from the real approval/action path;
- user-visible exact preview;
- rollback execution tests;
- no-tools and tool-call compatibility tests;
- manual QA and release-gate evidence.
