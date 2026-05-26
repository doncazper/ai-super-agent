# Next Feature Expansion Candidates

Prompt ID: `MATURITY-AUDIT-01`
Date: 2026-05-25

Feature expansion should wait until the P1 maturity queue is at least partially burned down, especially prompt tracker reconciliation and release-candidate cleanup.

| Feature title | Why it matters | Prerequisites | Risk | Should wait for maturity work? | Suggested prompt pack name | Expected user value |
|---|---|---|---|---|---|---|
| News Provider Registry and Status Commands | Turns news planning into inspectable runtime scaffolding | News manifest, command registry | LOW | No, if scoped and no live APIs | `news-provider-registry-v1` | Users can see configured news sources safely |
| GDELT News Provider | Adds free-first global news search | News provider registry, cache policy | MEDIUM | Yes | `news-gdelt-provider-v1` | Current global news without paid API default |
| News Brief and Timeline with Sources | Builds source-grounded news UX | Provider registry, citation layer, fetch policy | MEDIUM | Yes | `news-brief-timeline-v1` | Useful sourced answers for current events |
| Brain Runtime Live Smoke and Fallback | Proves LM Studio is optional in practice | Brain gateway, provider doctors | MEDIUM | Yes | `brain-runtime-live-validation-v1` | More resilient local model runtime |
| Platform Capability Manifest Mapping | Hardens future platform actions before implementation | Platform registry/stubs | MEDIUM/HIGH future | No, if no real actions | `platform-manifest-mapping-v1` | Safer future macOS/iOS/Windows work |
| Native Skill External Intake Dry-Run | Proves provenance and vetting path | Native skill lock/vetting | MEDIUM | Yes | `native-skill-intake-release-v1` | Safer skill ecosystem |
| Web Provider Live Doctor Matrix | Verifies configured providers without paid defaults | Web provider docs/config | LOW/MEDIUM | Yes | `web-provider-live-doctors-v1` | Clear setup confidence |
| Weather Live Validation Pack | Turns weather from mock-strong to live-validated | Weather provider policy | LOW | Yes | `weather-live-validation-v1` | Reliable daily weather use |
| Manual Validation Dashboard | Gives one place for user QA status | Dogfood/session reports | LOW | Yes | `manual-validation-dashboard-v1` | Easier release decisions |
| Privacy Center Expansion | Consolidates retention/cache/connector privacy | Existing privacy center and cache policies | MEDIUM | Yes | `privacy-center-release-v1` | User trust and cleanup clarity |

