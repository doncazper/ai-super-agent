# Agent Gateway / Runtime Kernel Boundary

Status: CANON-03 implemented as metadata contract scaffolding.

The Agent Gateway is the future request boundary for CLI, local app, iOS companion, Windows app, web dashboard, and channel frontends. The Runtime Kernel owns execution truth and safe routing state.

The current CLI remains the first frontend. CANON-03 does not create a web server, Fastify/TypeScript gateway, Mac/iOS/Windows UI, listener, Telegram/mobile channel, external tool exposure, or CLI replacement.

## Runtime Kernel Owns

- canonical runtime state
- durable execution records
- active job/prompt/workflow/action state
- approval-gated resume state
- checkpoints/recovery reports
- audit receipt references
- command/run summaries
- frontend/channel contracts
- no direct tool execution outside ToolBroker

## Gateway Responsibilities

- receive frontend/channel request envelopes
- normalize request envelopes
- assign request and correlation IDs
- route to runtime services safely
- require approval where needed
- return redacted summaries
- expose safe status
- never approve its own actions
- never execute tools directly
- never mutate policy or capabilities

## Commands

- `python smart_agent.py runtime gateway-status`
- `python smart_agent.py runtime kernel-status`
- `python smart_agent.py runtime frontend-contract`
