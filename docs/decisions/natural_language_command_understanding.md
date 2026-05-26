# Decision: Natural-Language Command Understanding

Date: 2026-05-25
Status: accepted for staged implementation

## Context

The project has hundreds of tracked commands and many users naturally ask for outcomes instead of exact CLI syntax. A natural-language command layer can reduce friction, but it can also become a safety bypass if loose requests are treated as executable instructions.

## Decision

Build a deterministic-first natural-language command understanding layer that maps user requests to intent IDs, command registry records, clarification questions, and preflight plans. It must use command registry metadata as the source of truth and must keep PolicyEngine/ToolBroker/ApprovalManager/AuditLogger as the execution boundary.

LLM interpretation may be added later as advisory metadata only. It cannot override deterministic safety outcomes, risk labels, provider policy, approval requirements, or command registry status.

## Consequences

- Exact commands keep working unchanged.
- Early milestones are docs/index/parser/preflight before any execution UX.
- Natural-language requests for HIGH, CRITICAL, personal-data, send/write, destructive, or provider-gated behavior become clarification/preflight/approval paths, not direct execution.
- Eval and dogfood fixtures must include misunderstood intent, ambiguity, personal-data requests, send/write requests, and unsupported/planned command cases.

## Alternatives Rejected

- LLM-only command routing: rejected because it cannot be the safety boundary.
- Auto-execute everything that matches a command: rejected because command risk and approval requirements matter.
- Replace exact commands with natural language: rejected because CLI/manual operation must remain inspectable and reproducible.

