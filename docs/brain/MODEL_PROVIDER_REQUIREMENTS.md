# Model Provider Requirements

Every future model provider must meet these requirements before it can be executable.

## Required Interface

- provider id and display name;
- configured/enabled checks;
- setup hints;
- chat completion call;
- optional tool-call capability declaration;
- health check;
- normalized errors;
- provider metadata for docs and command registry;
- deterministic mock path for tests.

## Safety Requirements

- No provider bypasses ToolBroker.
- No provider bypasses PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.
- No provider grants capabilities, approvals, permissions, connector access, or memory access.
- No paid/cloud provider is used by default.
- No provider stores prompts, search history, web content, personal data, or model output in memory by default.
- Secrets and API keys are never printed and must be redacted in logs/reports.

## Performance Requirements

- Provider modules are lazy-loaded.
- Optional heavy packages are not imported at startup.
- Provider health/status commands avoid model generation unless explicitly requested.
- Missing provider setup returns structured setup hints instead of crashing.

## Testing Requirements

- Mock provider tests.
- Provider configuration tests.
- Error normalization tests.
- No-tools chat preservation tests.
- Tool-call compatibility tests.
- Startup import guard tests.
- Command registry validation for user-facing commands.
- Quality/benchmark regression checks before default changes.

