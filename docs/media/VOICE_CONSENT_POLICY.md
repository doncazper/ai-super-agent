# Voice Consent Policy

Status: MEDIA-09 policy scaffold.
Last updated: 2026-05-25.

## Policy

Voice cloning, public-figure voice imitation, private-person voice imitation, and impersonation are denied/deferred until a future explicit consent system exists and passes a separate release gate.

The agent must not infer voice consent from a prompt alone.

## Required Future Consent Record

A future consent record must include at minimum:

- consenting person identifier or relationship to the user
- consent scope
- allowed voice use cases
- expiration/revocation terms
- proof/evidence reference
- watermark/provenance requirement
- approval/audit correlation IDs

No consent record model or storage system is implemented in MEDIA-09.

## Forbidden In Current Scaffold

- Voice cloning.
- Public-figure voice imitation.
- Private-person voice imitation.
- Fake endorsement audio.
- Impersonation.
- Uploading or publishing voice output.
- Using personal voice samples.

## Generic TTS

Generic TTS may be a future MEDIUM-risk workflow after provider/model review. It still requires ToolBroker routing, policy tests, audit fields, provider/license review, and watermark/provenance strategy before real audio generation.
