# M2 Core Runtime

## Scope

Make the runtime reliable before adding risky tools.

## Non-Goals

No filesystem, web, memory, personal-data, or write/send tools.

## Requirements

- Session manager.
- Message manager.
- Router.
- Debug payload logging with redaction.
- Streaming support if straightforward.
- Reasoning-content cleanup.
- Config manager.
- CLI command structure.

## Risks

- Router may rewrite user intent.
- Debug logs may leak secrets.
- Malformed tool calls may crash the loop.

## Tests

- Normal chat attaches no tools.
- Time query routes to time tool.
- Debug output redacts secrets.
- Malformed tool calls handled safely.
- Reasoning content not displayed by default or fed back incorrectly.

## Approval Gate

None.
