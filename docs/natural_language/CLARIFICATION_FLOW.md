# Natural-Language Clarification Flow

Status: implemented for metadata/preview v1.

The clarification flow turns ambiguous, risky, deprecated, stubbed, or
setup-gated route decisions into one clear question plus safe command examples.
It does not execute commands, request approvals, call providers, access personal
data, or write memory.

## Clarification Types

- `missing_required_argument`
- `multiple_matching_commands`
- `risky_action`
- `personal_data_request`
- `provider_missing`
- `ambiguous_intent`
- `unsupported_capability`
- `command_is_stubbed`
- `command_is_deprecated`

## Rules

- Ask one clear question when possible.
- Offer exact command examples from the command registry.
- Explain when approval or dry-run is required.
- Redact secret-looking values in previews.
- If a command is deprecated, show the replacement when registry metadata has
  one.
- If provider setup is missing, suggest doctor/status or setup paths.
- If intent is unknown, offer command help/search rather than guessing.

The future conversational CLI must continue to route real execution through
ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger.
