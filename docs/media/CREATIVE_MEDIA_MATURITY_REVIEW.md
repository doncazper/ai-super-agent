# Creative Media Maturity Review

Status: MEDIA-12 conservative maturity assessment.
Last updated: 2026-05-25.

## Summary

Creative Media Generation is a tested local scaffold. It is ready as a safe foundation for future provider work, but it is not user-ready for real media generation.

Maturity level: `4 Tested`.
Readiness score: `77`.

## Assessment Table

| Area | Maturity | Evidence | Limitation | Next action |
|---|---:|---|---|---|
| Creative media roadmap | 4 Tested | Track docs, risk model, ADR, roadmap rows | Docs only for future provider implementation | Keep updated during provider work |
| Provider registry | 4 Tested | `agent/media/provider_registry.py`, provider/doctor tests | Metadata only; no provider SDKs | Add one reviewed provider stub-to-live path later |
| Asset manager | 4 Tested | Bounded path tests, redaction, metadata listing | Fake/test assets only; cleanup is dry-run | Add release-gated retention/write behavior if needed |
| Safety/license/consent policy | 4 Tested | Deterministic safety tests, license report, consent docs | Not a legal review or external moderation service | Add provider-specific policy tests later |
| ComfyUI provider stub | 4 Tested | Disabled stub tests and docs | No server start, workflow submission, or model validation | Future opt-in local validation prompt |
| Image generation scaffolding | 4 Tested | Dry-run planner, provider candidates, tests | No real image generation | Future provider implementation |
| Thumbnail/social workflows | 4 Tested | Templates, dry-run plans, tests | No editing, source media input, upload, or publish | Future reviewed source-media workflow |
| Video generation scaffolding | 4 Tested | Dry-run planner, resource warnings, tests | No video provider or hardware validation | Future provider/resource gate |
| Audio/music scaffolding | 4 Tested | Dry-run planner, artist/voice warnings, tests | No audio/music generation | Future provider/resource gate |
| TTS/voice strategy | 4 Tested | Voice category planner, consent policy, provider stubs | Voice clone/person imitation denied/deferred | Consent system required before cloning |
| NL routing/commands | 4 Tested | `media plan`, NL route metadata, tests | Advisory only; no execution | Keep no-auto-execute boundary |
| Dogfood/evals | 4 Tested | Media dogfood YAML, `eval --media`, fixture tests | Mock/fixture only; no manual session yet | Run manual media dogfood session |
| Release gate | 4 Tested | Release gate doc, release checklist, full suite, focused validations, media evals | Local/mock-only release gate; no live provider run | Re-run after any provider work |

## Conservative Readiness

Creative media can be used for:

- planning media workflows
- checking safety/license/consent metadata
- inspecting provider readiness
- validating no-generation boundaries
- designing future provider implementation

Creative media cannot yet be used for:

- generating images, video, audio, music, or TTS
- editing user media
- cloning voices
- imitating real people
- publishing/uploading media
- commercial rights assurance
- live provider QA

## Maturity Rationale

The scaffold has tests, docs, command tracking, capability entries, dogfood suites, and fixture evals. It remains at `4 Tested` rather than `5 Hardened` because no real provider failure modes, live resource constraints, generated-output safety review, manual dogfood session, consent-record workflow, or full provider release gate exists.
