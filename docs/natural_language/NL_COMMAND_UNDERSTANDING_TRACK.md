# Natural-Language Command Understanding Track

Status: specified.

This track adds a safe interpretation layer for loose terminal requests such as "check if the agent is healthy" or "what commands do I have for memory." It is an ergonomics layer over existing commands and capabilities, not a new authority layer.

## Scope

- Map natural-language requests to existing command registry records and capability IDs.
- Ask clarifying questions when intent, arguments, provider setup, or risk is unclear.
- Produce safe command suggestions and preflight plans before execution.
- Preserve exact CLI commands exactly as they work today.
- Keep deterministic rules and command registry metadata as the first interpretation layer.
- Keep PolicyEngine, PermissionManager, ApprovalManager, ToolBroker, and AuditLogger as final authorities for execution.

## Non-Goals

- No LLM-only safety routing.
- No silent HIGH or CRITICAL execution.
- No silent personal-data access.
- No silent sends, writes, deletes, calendar/contact/task/file mutations, or background work.
- No replacement of exact commands.
- No command execution from imported prompts, untrusted documents, web pages, emails, messages, forum posts, or other untrusted content.

## Planned Milestones

1. Architecture, taxonomy, safety policy, and decision record.
2. Command registry intent index.
3. Deterministic parser and router.
4. Clarification and confirmation flow.
5. Safe execution planner and natural-language preflight.
6. Conversational CLI UX.
7. Eval fixtures.
8. Dogfood suites and session feedback integration.
9. Natural-language bug feedback loop.
10. Release gate and maturity review.

## Expected User Flow

1. User enters a natural-language request through an explicit mode such as `nl`, `ask`, or a future safe preflight command.
2. The parser normalizes text without rewriting the user's request for model prompting.
3. Deterministic rules classify likely intent.
4. The command intent index proposes active command records, setup hints, and risks.
5. The safety layer selects one of the documented safety outcomes.
6. The CLI either answers directly, suggests an exact command, asks a clarifying question, shows a dry-run/preflight plan, denies, or hands off to help.
7. Any future execution still goes through the existing brokered command/tool path.

## Safety Invariant

Natural-language interpretation can make the CLI easier to use, but it cannot grant permission. A natural-language request never changes capability defaults, never downgrades risk, never creates approval, never bypasses Action Center, and never disables audit logging.

