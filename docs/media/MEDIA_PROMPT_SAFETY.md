# Media Prompt Safety

Status: scaffolded in MEDIA-03.

Media prompt safety is a deterministic local preflight that runs before any future media generation. It does not call external moderation APIs, invoke a model, generate media, upload media, or approve a request by itself.

## Categories

- `safe_general`
- `commercial_use_unclear`
- `copyrighted_character_or_brand`
- `living_person_likeness`
- `private_person_likeness`
- `celebrity_likeness`
- `voice_clone`
- `impersonation`
- `sexual_content`
- `graphic_violence`
- `extremist_or_hate`
- `illegal_instructional_content`
- `medical/legal/financial claim risk`
- `political persuasion risk`
- `privacy_sensitive_input`
- `unknown_risk`

## Outcomes

- `allow`
- `warn`
- `require_license_review`
- `require_consent`
- `require_human_review`
- `deny`

## Rules

- Safe generic prompts may be allowed by preflight, but future generation still needs a configured provider and ToolBroker policy.
- Commercial use with unclear provider/model terms requires license review.
- Copyrighted characters, franchises, brands, and style/identity references require license review.
- Living-person, private-person, and celebrity likeness requests require consent and human review.
- Voice cloning is denied/deferred until an explicit consent workflow exists.
- Impersonation, fake endorsement, illegal instructional content, extremist/hate content, explicit sexual content, and graphic violence are denied.
- Personal/private input media requires explicit tagging and future approval gates.

The checker is operational safety metadata, not legal advice.
