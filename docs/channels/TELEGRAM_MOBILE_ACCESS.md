# Telegram and Mobile Access Scaffolding

HERMES-03 prepares safe configuration/status scaffolding for Telegram and a future mobile companion without enabling remote command execution.

## Scope

- Telegram config doctor/status only.
- Mobile companion status and pairing-status only.
- Allowlisted chat/user policy metadata.
- Disabled-by-default send, polling, webhook, and mobile approval flags.
- Brokered CLI status commands with redacted secrets.

## Non-Goals

- No Telegram bot startup.
- No Telegram send.
- No Telegram polling loop.
- No Telegram webhook server.
- No public network listener.
- No remote command execution.
- No personal-data tools.
- No mobile companion app behavior.

## Config Defaults

```bash
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_CHAT_IDS=
TELEGRAM_DEFAULT_CHAT_ID=
TELEGRAM_ALLOW_SEND=false
TELEGRAM_ALLOW_POLLING=false
TELEGRAM_ALLOW_WEBHOOK=false
MOBILE_COMPANION_ENABLED=false
MOBILE_APPROVALS_ENABLED=false
```

Token presence is reported as a boolean only. Token values are never printed. Chat IDs are not required for status checks, but `TELEGRAM_ALLOWED_CHAT_IDS` is required before any future send-capable connector can even be considered.

## Commands

- `python smart_agent.py telegram doctor`
- `python smart_agent.py telegram status`
- `python smart_agent.py mobile status`
- `python smart_agent.py mobile pairing-status`

All four commands are brokered SAFE metadata commands. They make no Telegram API call, start no loop/server, read no chats, send no messages, access no personal data, and write no memory.

## Future Gates

Future Telegram or mobile access must add a separate decision record, explicit config gates, ToolBroker capabilities, PolicyEngine rules, ApprovalManager behavior for HIGH/CRITICAL actions, AuditLogger correlation, no-background default checks, rate-limit handling, allowlist enforcement, and dogfood/eval coverage before live use.
