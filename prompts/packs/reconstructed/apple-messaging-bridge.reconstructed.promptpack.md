# Apple Messaging Bridge Reconstructed Prompt Pack

```yaml
pack_id: apple-messaging-bridge.reconstructed
title: Apple Messaging Bridge
status: reconstructed
exact_original: false
reconstruction_sources:
  - docs/decisions/apple_messaging_architecture.md
  - docs/decisions/ios_companion_message_compose.md
  - docs/workflows/messaging_rollout_plan.md
related_features:
  - MESSAGE-CHANNEL-ABSTRACTION
  - MESSAGE-SAFETY-ACTION-CENTER
  - IOS-CONFIRMED-COMPOSE
related_docs:
  - docs/THREAT_MODEL.md
  - docs/RISK_REGISTER.md
related_commits:
  - unknown
confidence: medium
caveats:
  - Reconstructed from current decision records and implementation docs, not exact prompts.
prompt_ids:
  - APPLE-MSG-01
```

## Prompt Records

### APPLE-MSG-01

type: reconstructed_summary

Plan and implement messaging foundations without sending: channel-neutral schema, Action Center send previews, manual handoff, iOS user-confirmed compose payloads, decision records, and no private Messages database scraping or silent sends.
