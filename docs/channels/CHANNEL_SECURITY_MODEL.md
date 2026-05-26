# Channel Security Model

Channel gateway content is treated as untrusted unless it comes from the trusted local CLI. This keeps future remote/mobile/native surfaces from becoming a shortcut around the agent safety control plane.

## Required Boundaries

- Channels cannot execute tools directly.
- Channels cannot approve their own actions.
- Channels cannot bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.
- Remote channels are disabled by default.
- No channel can send messages in this scaffold.
- Channel status checks must not access personal data.
- Channel metadata is redacted before it is stored in a request object or audit-adjacent payload.
- A correlation id is required for gateway submissions.

## Forbidden Without Future Approval

- Background polling, webhook listeners, or daemon/server startup.
- Telegram/mobile/email live reads or writes.
- Message, email, calendar, or contact sends/writes.
- Personal-data tools or private app database reads.
- Browser automation beyond explicit future policy.
- CAPTCHA, Cloudflare, proxy evasion, login-wall, paywall, anti-bot bypass, or human impersonation.
- Subagents with write permissions by default.

## Approval Rules

Future channel frontends may present approval UI, but they cannot manufacture approval. HIGH and CRITICAL actions must remain exact-preview, user-confirmed, per-action approvals through ApprovalManager. CRITICAL approval reuse remains forbidden.

## Audit Rules

Gateway submissions require a correlation id. Future channel runtimes must carry that id through ToolBroker calls, ApprovalManager decisions, and AuditLogger records so a user can trace the request from channel receipt to final response.

## Current State

HERMES-02 is safe scaffolding only. The gateway can normalize safe request metadata and expose read-only channel status. It does not connect to external services, retain channel history, start listeners, execute tools, approve actions, send messages, or read personal data.
