# Media Risk Model

Status: specified only.
Last updated: 2026-05-25.

## Risk Levels

| Activity | Risk | Required posture |
|---|---|---|
| Media provider status | SAFE | Metadata only, no provider call, no model import |
| Prompt planning | LOW | No generation, no personal data memory write |
| Local image generation | MEDIUM | ToolBroker routed, audited, content safety checked |
| Image editing with user images | MEDIUM/HIGH | HIGH if image may contain a real person, private location, document, or sensitive subject |
| Video generation | MEDIUM/HIGH | Resource, content, cost, and license constraints required |
| Audio/music generation | MEDIUM | Copyright/license caveats required |
| TTS | MEDIUM/HIGH | Depends on source text, personal data, and voice identity |
| Voice cloning | CRITICAL or FORBIDDEN | Forbidden until explicit consent workflow, provenance, and approval policy exist |
| Social posting/uploading | CRITICAL | Not in this track; explicit per-action approval required for any future upload |
| Paid API generation | MEDIUM/HIGH | Config and approval gated, never default |
| Real-person likeness generation | HIGH/CRITICAL | Approval and consent policy gated |
| Copyrighted/style imitation | MEDIUM/HIGH | Review and caveat gated |
| Unsafe/NSFW/extremist/abusive media | FORBIDDEN | Not supported unless a future policy explicitly allows narrow safe cases |

## Threats

- Prompt text attempts to bypass safety policy.
- Provider output contains unsafe, infringing, or misleading content.
- User images contain personal data or real-person likeness.
- Generated assets are mistaken for licensed commercial work without evidence.
- Paid providers are used accidentally.
- Heavy model imports slow startup or crash CLI-only mode.
- Future upload/publish flows bypass approval.

## Mitigations

- Treat prompts and source media metadata as data, not authority.
- Require capability manifest entries before execution.
- Require policy checks before prompt planning and generation.
- Keep providers disabled until configured.
- Use mock/test providers for dogfood and evals.
- Store outputs only in a controlled media workspace.
- Redact raw prompts and secrets from logs.
- Keep voice cloning and social publishing blocked until separate approved tracks exist.

