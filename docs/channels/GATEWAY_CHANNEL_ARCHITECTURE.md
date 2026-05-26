# Gateway Channel Architecture

HERMES-02 adds a safe channel gateway scaffold for future CLI, mobile, native-app, dashboard, email, and mock channels. It is metadata and handoff plumbing only; it does not connect to external services, send messages, read personal data, start background workers, or approve actions.

## Scope

- Define channel request and response models.
- Define a static channel registry.
- Normalize channel trust and redacted metadata.
- Provide read-only CLI inspection commands.
- Provide a gateway submission object that can be handed to the orchestrator/runtime in future work.

## Non-Goals

- No real Telegram, Slack, Discord, WhatsApp, Signal, email, iOS companion, Mac app, Windows app, or web dashboard connector.
- No long-running server, webhook listener, polling loop, or background persistence.
- No message send/write path.
- No personal-data reads.
- No browser automation.
- No self-approval or ApprovalManager bypass.

## Channel Flow

1. A known channel submits a `ChannelRequest`.
2. The gateway redacts metadata and assigns trust.
3. The gateway returns a structured `GatewaySubmission`.
4. Future runtime work may pass that submission into the orchestrator.
5. Any tool execution must still go through ToolBroker, PolicyEngine, PermissionManager, ApprovalManager when required, and AuditLogger.

The gateway has no direct tool execution API for workflows. Its `execute_tool` and `approve_action` guards fail closed.

## Channel Defaults

| Channel | Default | Trust | Notes |
|---|---:|---|---|
| `cli` | enabled | `TRUSTED_USER` | Local CLI only. |
| `interactive_cli` | enabled | `TRUSTED_USER` | Local interactive shell only. |
| `manual_handoff` | enabled | `TRUSTED_USER` | User-mediated local handoff, no send. |
| `mock` | enabled | `UNTRUSTED_MESSAGE` | Tests and dogfood fixtures. |
| `telegram` | disabled | `UNTRUSTED_MESSAGE` | Future connector only. |
| `ios_companion` | disabled | `UNTRUSTED_MESSAGE` | Future paired companion only. |
| `mac_app` | disabled | `UNTRUSTED_MESSAGE` | Future local app bridge only. |
| `windows_app` | disabled | `UNTRUSTED_MESSAGE` | Future local app bridge only. |
| `local_web_dashboard` | disabled | `UNTRUSTED_MESSAGE` | No listener starts. |
| `email` | disabled | `UNTRUSTED_MESSAGE` | Existing explicit email workflows remain separate. |

## Commands

- `python smart_agent.py channels list`
- `python smart_agent.py channels status`
- `python smart_agent.py channels show <channel_id>`

These commands execute through brokered SAFE metadata capabilities: `channels.list`, `channels.status`, and `channels.show`.
