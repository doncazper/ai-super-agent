# Natural-Language CLI UX

Natural-language CLI UX is an explanation surface for users who type requests instead of exact commands. It does not make natural language the required interface, and it does not execute tools or commands.

## Modes

- Exact command mode remains unchanged. Existing commands continue through their normal CLI path.
- `python smart_agent.py nl "<request>"` shows what the parser understood, the matched command, safety flags, setup requirements, and the next safe step.
- `python smart_agent.py ask "<request>"` is a friendlier alias for the same explanation surface.
- `python smart_agent.py nl preflight "<request>"`, `nl explain`, and `nl suggest` provide structured metadata for automation/testing.
- `python smart_agent.py nl --no-tools "<request>"` preserves no-tools behavior and avoids command/tool suggestions.

## Safety Behavior

Safe or LOW read-only requests can show a command candidate and say it is safe to run manually. Risky requests show the approval/preflight path instead. Ambiguous or unknown requests ask for clarification or suggest command search.

All outputs include “No commands have been executed.” Real execution must still use exact commands and the existing ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger paths.
