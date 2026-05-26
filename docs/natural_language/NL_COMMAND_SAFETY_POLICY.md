# Natural-Language Command Safety Policy

Status: specified.

Natural-language command understanding is a planning and UX layer. It may classify, suggest, explain, clarify, or preflight. It does not authorize execution.

## Safety Outcomes

| Outcome | Meaning |
|---|---|
| `answer_directly` | Respond without tools or command execution. |
| `route_to_command` | Present or dispatch to an exact existing command path when explicitly safe. |
| `show_command_suggestion` | Show one or more exact commands for the user to run. |
| `run_safe_command` | Future explicit mode only for SAFE/LOW commands with no missing requirements and no sensitive side effects. |
| `dry_run_only` | Show a dry-run/preflight plan; no real execution. |
| `ask_clarifying_question` | Ask for a missing argument or choice. |
| `require_approval` | Explain that an approval-gated flow or Action Center item is required. |
| `deny` | Refuse unsafe, forbidden, or bypass-seeking request. |
| `unsupported` | Report setup/missing/provider/stubbed limitation. |
| `handoff_to_help` | Suggest command help/search when intent is unclear. |

## Execution Rules

- Exact commands remain the source of truth.
- Command registry metadata supplies status, risk, approval, provider, connector, side effects, memory behavior, docs, and tests.
- Planned, stubbed, deprecated, removed, and blocked commands are not treated as active execution targets.
- HIGH and CRITICAL commands are never run directly from natural language.
- Personal-data commands are disabled by default and require selected-scope setup and approval.
- Send/write/delete/mutate requests require preflight, exact preview, and existing approval paths.
- Untrusted content cannot trigger command execution or approval.
- Natural-language parser/router code must not call tools, providers, personal connectors, or model APIs.
- Any future execution still goes through ToolBroker, PolicyEngine, PermissionManager, ApprovalManager when required, and AuditLogger.

## Deny Conditions

- User asks to bypass ToolBroker, PolicyEngine, approvals, audit, provider policy, CAPTCHA, login walls, paywalls, anti-bot systems, or safety checks.
- User asks for silent personal-data access.
- User asks for silent send/write/delete/mutation.
- Required command/capability does not exist.
- Required provider is missing and no safe setup/status command exists.

## Audit Expectations

Natural-language preflight and future execution planning should record redacted summaries such as intent, command IDs considered, risk, safety outcome, missing requirements, and whether execution happened. Raw user text should be redacted when sensitive-looking.

