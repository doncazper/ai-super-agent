# Natural-Language Parser and Deterministic Router

Status: implemented for metadata/planning v1.

The parser/router classifies loose user text into a single deterministic intent
candidate and returns a structured route decision. It does not execute commands,
call providers, access personal data, or write memory.

## Decision Fields

`NLRouteDecision` includes:

- `original_text`
- `normalized_text`
- `intent`
- `confidence`
- `command_suggestions`
- `safety_outcome`
- `risk_level`
- `approval_required`
- `dry_run_required`
- `clarification_required`
- `reason`
- `evidence`
- `audit_summary`

## Safety Rules

- Deterministic parser rules run first.
- LLM interpretation is not used in v1 and cannot override safety outcomes in
  future versions.
- Exact commands are recognized and left to the normal command path.
- No-tools mode returns chat/no-tool routing with no command suggestions.
- Ambiguous requests ask clarification.
- Personal-data and send/write/delete requests are never directly executable
  from natural language.
- HIGH, CRITICAL, and approval-required suggestions are preflight/approval-only.
- Unknown requests hand off to help/chat rather than guessing.
- Route decisions include audit-summary metadata for future preflight logging,
  but no audit record is written by the parser itself.

Future execution planners must still route real actions through ToolBroker,
PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger.
