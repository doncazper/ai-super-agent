# Media Consent Policy

Status: scaffolded in MEDIA-03.

Consent-sensitive media workflows are disabled/deferred until explicit future implementation and release gates exist.

## Denied Or Deferred

- Voice cloning.
- Deepfake voice workflows.
- Real-person impersonation.
- Fake endorsement.
- Private-person likeness generation without explicit consent.
- Celebrity/living-person likeness workflows without consent and human review.

## Consent Requirements

Future consent evidence must be explicit, reviewable, and tied to the specific action. The agent must not infer consent from the prompt alone.

Future asset metadata must record:

- consent status
- consent evidence reference
- person/voice/likeness scope
- allowed use
- expiration or retention constraints, if any
- approving user/action id
- audit correlation id

## Current Implementation

MEDIA-03 exposes only:

- deterministic prompt safety preflight
- license metadata report
- consent policy status

It does not generate media, request permissions, access personal photos/videos, clone voices, or implement a consent workflow.
