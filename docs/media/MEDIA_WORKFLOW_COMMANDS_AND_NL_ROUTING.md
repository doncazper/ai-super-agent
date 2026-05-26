# Media Workflow Commands and Natural-Language Routing

Status: local tested scaffold through MEDIA-10.

## Scope

`python smart_agent.py media plan "request"` turns a user media request into a dry-run plan. It infers a target such as thumbnail, image, video, audio, music, TTS, or creative image, runs media safety preflight first, and returns the exact dry-run command the user can inspect next.

The command does not generate media, call providers, upload, publish, read personal media, store request history, write generated assets, or approve future generation.

## Natural-Language Behavior

The natural-language command layer can recognize media creation requests such as:

- make me a thumbnail for this vlog
- create a 10-second intro animation
- make a lo-fi music bed for a food review
- generate sound effects for my video
- turn this image into a short video
- make a podcast cover
- create a real estate listing graphic

Those requests route to `media.plan` as dry-run/preflight metadata only. Natural-language routing must not execute generation commands automatically and must not bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.

## Safety Contract

- Safety preflight runs before target-specific generation planning.
- Unsafe prompts return `status=blocked` and no target plan.
- Real generation remains unavailable until a future reviewed provider is configured and capability-manifested.
- Results include `provider_calls_performed=false`, `generated_media=false`, `asset_write_performed=false`, and `upload_publish_enabled=false`.
- Future generation, editing, upload, publish, voice cloning, and real-person likeness workflows require separate policy, consent, command registry, approval, audit, tests, and release-gate work.

## Commands

- `python smart_agent.py media plan "make me a thumbnail for this vlog"`
- `python smart_agent.py media thumbnail "make me a thumbnail for this vlog" --dry-run`
- `python smart_agent.py media generate image "a product sketch" --dry-run`
- `python smart_agent.py media generate video "a 10-second intro animation" --dry-run`
- `python smart_agent.py media generate audio "soft notification chime" --dry-run`
- `python smart_agent.py media generate music "short lo-fi bed" --dry-run`
- `python smart_agent.py media tts plan "Read this announcement"`

## Limitations

MEDIA-10 is still planning-only. It does not make Creative Media user-ready for real generation. Dogfood/evals and the creative media release gate remain future milestones.
