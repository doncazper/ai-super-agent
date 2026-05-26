# TTS And Voice Generation Strategy

Status: MEDIA-09 local scaffold.
Last updated: 2026-05-25.

## Scope

MEDIA-09 prepares a safe path for future text-to-speech while explicitly separating ordinary generic TTS from voice cloning, public/private person voice imitation, and impersonation.

Current support is limited to:

- TTS/voice category planning.
- Voice consent policy metadata.
- TTS/voice provider candidate metadata.
- Safety/consent decisions for risky voice categories.
- No real voice generation.

## Voice Categories

| Category | Current status | Future risk |
|---|---|---|
| `generic_tts` | stubbed allowed as planning metadata | MEDIUM |
| `character_voice` | requires review | HIGH |
| `user_owned_voice_with_consent` | requires consent system | CRITICAL future |
| `public_figure_voice` | denied/deferred | CRITICAL or forbidden |
| `private_person_voice` | denied/deferred | CRITICAL or forbidden |
| `voice_clone` | denied/deferred | CRITICAL or forbidden |
| `impersonation` | denied/deferred | CRITICAL or forbidden |

## Commands

```bash
python smart_agent.py media tts plan "text"
python smart_agent.py media voice consent-policy
python smart_agent.py media voice providers
```

All commands route through ToolBroker and PolicyEngine.

## Non-Goals

MEDIA-09 does not:

- Implement voice cloning.
- Generate real voice audio.
- Imitate real people.
- Use personal voice samples.
- Upload or publish audio.
- Install TTS models or providers.
- Download voice models.
- Call paid APIs.

## Future Requirements

Future real TTS work must add:

- exact provider capability manifest entries
- ToolBroker mapping
- PolicyEngine tests
- ApprovalManager gates for HIGH/CRITICAL cases
- AuditLogger fields for provider decisions, text, voice category, consent references, denials, approvals, asset writes, and results
- watermark/provenance strategy
- provider/license review
- startup-overhead tests

Voice cloning remains denied/deferred until an explicit consent system exists.
