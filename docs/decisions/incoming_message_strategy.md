# Incoming Message Strategy

Status: accepted for v1

Date: 2026-05-23

## Context

The agent needs a path for receiving and responding to messages, but consumer Messages/iMessage does not provide a safe general inbox API for this project today. Reading `~/Library/Messages/chat.db`, requesting broad Full Disk Access, or running a hidden watcher would violate the project safety model.

## Decision

Incoming message v1 uses only:

- Manual import from a user-selected file inside `./workspace`.
- A mock inbox provider for tests, demos, and dogfood.
- Lead Inbox conversion metadata so imported messages can later feed draft-only lead workflows.
- Planning placeholders for Apple Messages for Business/webhooks and selected Gmail/Telegram mappings, without reading those providers in v1.

The manual/mock inbox stores local records under `./workspace/messaging/inbound/`. Imported content is `UNTRUSTED_MESSAGE` and is data only. The inbox can create a local draft reply, but it cannot send, auto-reply, poll, or watch.

## Commands

```bash
python smart_agent.py messages import --from-file ./workspace/incoming_message.md
python smart_agent.py messages inbox list
python smart_agent.py messages inbox show <message_id>
python smart_agent.py messages inbox draft-reply <message_id>
```

## Safety Rules

- No `~/Library/Messages` or `chat.db` access.
- No Full Disk Access dependency.
- No background watcher, polling loop, launch agent, or daemon.
- No automatic reply.
- No message send path.
- Imported files must resolve inside `./workspace`.
- Message content is labeled `UNTRUSTED_MESSAGE`.
- Message text cannot approve actions, change policy, request tools, reveal secrets, or trigger sends.
- Draft replies create local `MessageDraft` records only.
- No message body is written to long-term memory by default.
- All import, list, show, and draft-reply operations go through ToolBroker and AuditLogger.

## Future Provider Mapping

| Source | v1 behavior | Future gate |
|---|---|---|
| Manual selected text/file | Supported through workspace import | Keep workspace-bounded and audited |
| Mock provider | Supported for tests/dogfood | Keep synthetic only |
| Apple Messages for Business | Placeholder only | Provider decision, webhook auth, consent, Action Center send gate |
| Gmail | Placeholder only | Selected-thread adapter and Lead Inbox mapping; no bulk inbox |
| Telegram | Placeholder only | Selected chat/lead adapter; no token-presence reads |
| Personal iMessage | Manual import/handoff only | No private DB or Full Disk Access; any send path requires a later explicit decision |

## Lead Inbox Conversion

Imported message records expose a Lead Inbox candidate with:

- source/provider
- channel
- sender display
- received timestamp
- subject/context
- redacted preview
- selected full-message reference
- `UNTRUSTED_MESSAGE` trust label

Conversion is metadata-only in v1. It does not sync a CRM, create a contact, write memory, or send a response.

## Non-Goals

- No private Messages database scraping.
- No hidden inbox polling.
- No AppleScript/Accessibility send automation.
- No silent or bulk send.
- No real Gmail/Telegram/Apple Messages for Business reads.
- No long-term memory storage of message bodies by default.
