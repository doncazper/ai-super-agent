# Creative Media Generation Track

Status: release-gated local scaffold through MEDIA-12.
Last updated: 2026-05-25.

## Scope

The Creative Media Generation track prepares safe, provider-based support for:

- image generation
- image editing
- image-to-video
- text-to-video
- audio generation
- music generation
- text-to-speech
- future voice generation
- video editing
- thumbnail and social creative workflows
- mock/test media workflows

MEDIA-01 was documentation and roadmap only. MEDIA-02 adds provider-neutral models, a static/mock provider registry, a bounded asset metadata manager, and read-only/dry-run CLI inspection commands. MEDIA-03 adds deterministic local prompt safety, license reporting, and consent policy checks. MEDIA-04 adds a disabled-by-default ComfyUI provider stub. MEDIA-05 adds image-generation dry-run planning and mock image metadata scaffolding. MEDIA-06 adds thumbnail/social creative templates, dry-run creative workflow planning, and a mock workflow asset metadata helper. MEDIA-07 adds video provider candidate metadata, dry-run video planning, resource warnings, and a mock video metadata provider. MEDIA-08 adds audio/music provider metadata, dry-run audio/music planning, voice-clone denial, artist-imitation flags, and a mock audio metadata provider. MEDIA-09 adds TTS/voice category planning, voice consent policy metadata, and voice provider stubs. MEDIA-10 adds media workflow planning and natural-language routing metadata. MEDIA-11 adds mock/fixture-first dogfood suites and `eval --media` checks. MEDIA-12 adds the local release gate and conservative maturity review. The track still does not install ComfyUI, Diffusers, audio/video/TTS model runtimes, or provider SDKs. It does not download models, call paid APIs, edit or generate real media, read personal images/source videos/audio/voice samples, upload media, publish to social platforms, implement voice cloning, or implement real-person likeness workflows.

## Architecture Boundary

Creative media work must use the same safety control plane as the rest of the agent:

- ToolBroker is the only execution path for future tools.
- PolicyEngine remains the final safety authority.
- PermissionManager must enforce workspace and provider boundaries.
- ApprovalManager must gate HIGH and CRITICAL actions.
- AuditLogger must record provider decisions, prompts after redaction, asset writes, denials, approvals, and results.

Provider-specific code must stay behind optional adapters. The Python core must be able to start without importing media runtimes or GPU libraries.

## Track Order

| Order | Milestone | Status | Gate |
|---:|---|---|---|
| 1 | Creative media roadmap and risk model | complete for docs-only scope | No runtime media generation |
| 2 | Media provider registry and output asset manager | complete | Static/mock registry and bounded asset metadata only, no model installs |
| 3 | Media prompt/output safety, copyright, consent, and license policy | complete | No unsafe workflow enablement |
| 4 | ComfyUI provider strategy and stub | complete | Stub only, disabled by default |
| 5 | Image generation provider track | complete | Mock/local strategy first |
| 6 | Image editing, thumbnail, and social creative workflows | complete | Dry-run templates/plans only; no real editing or publishing |
| 7 | Video generation provider strategy | complete | Dry-run plans and mock metadata only |
| 8 | Audio, music, and sound generation strategy | complete | Dry-run plans and mock metadata only |
| 9 | TTS and voice generation strategy | complete | Voice cloning/person imitation denied/deferred |
| 10 | Media workflow commands and natural-language routing | complete | Natural language cannot bypass policy |
| 11 | Media dogfood and eval suite | complete | Mock/fixture first |
| 12 | Creative media release gate | complete | Conservative maturity review |

## Provider Categories

- `image_generation`
- `image_editing`
- `image_to_video`
- `text_to_video`
- `audio_generation`
- `music_generation`
- `tts`
- `voice_generation`
- `video_editing`
- `thumbnail/social_creative`
- `mock/test`

## CLI Surface

Implemented in MEDIA-02 through MEDIA-09 as metadata-only, preflight, or dry-run commands:

- `python smart_agent.py media providers`
- `python smart_agent.py media doctor`
- `python smart_agent.py media plan "request"`
- `python smart_agent.py media assets list`
- `python smart_agent.py media assets show <asset_id>`
- `python smart_agent.py media assets cleanup --dry-run`
- `python smart_agent.py media safety-check "prompt"`
- `python smart_agent.py media license report`
- `python smart_agent.py media consent policy`
- `python smart_agent.py media comfyui doctor`
- `python smart_agent.py media workflows list --provider comfyui`
- `python smart_agent.py media generate image "prompt" --dry-run`
- `python smart_agent.py media image providers`
- `python smart_agent.py media image plan "prompt"`
- `python smart_agent.py media thumbnail "prompt" --dry-run`
- `python smart_agent.py media creative plan "prompt"`
- `python smart_agent.py media creative templates`
- `python smart_agent.py media generate video "prompt" --dry-run`
- `python smart_agent.py media video providers`
- `python smart_agent.py media video plan "prompt"`
- `python smart_agent.py media generate audio "prompt" --dry-run`
- `python smart_agent.py media generate music "prompt" --dry-run`
- `python smart_agent.py media audio providers`
- `python smart_agent.py media music plan "prompt"`
- `python smart_agent.py media tts plan "text"`
- `python smart_agent.py media voice consent-policy`
- `python smart_agent.py media voice providers`
- `python smart_agent.py dogfood run media_core --session`
- `python smart_agent.py dogfood run media_safety --session`
- `python smart_agent.py dogfood run media_image_planning --session`
- `python smart_agent.py dogfood run media_video_audio_planning --session`
- `python smart_agent.py eval run --media`
- `python smart_agent.py eval report --media`

Release-gate evidence:

- `docs/media/CREATIVE_MEDIA_RELEASE_GATE.md`
- `docs/media/CREATIVE_MEDIA_MATURITY_REVIEW.md`

Planned/stubbed for future milestones:

- `python smart_agent.py media generate video "prompt"`
- `python smart_agent.py media generate audio "prompt"`
- `python smart_agent.py media generate music "prompt"`
- `python smart_agent.py media dogfood`

## Dogfood And Evals

MEDIA-11 adds four manual dogfood suites and fixture-backed eval cases:

- `media_core`: provider status, doctor output, asset list, and workflow planning.
- `media_safety`: safe prompt, unsafe prompt, voice-clone denial/deferment, and license warnings.
- `media_image_planning`: image, thumbnail, setup hint, and ComfyUI stub planning.
- `media_video_audio_planning`: video, audio, music, and image-to-video planning.

The eval category `media` checks that no real generation happens, paid APIs are not used, model downloads are not required, unsafe prompts are denied, voice cloning remains denied/deferred, license uncertainty is warned, asset roots stay bounded to `workspace/media`, and new dogfood/eval commands are present in the command registry.

## Current Stop Conditions

Stop before implementation if any milestone requires package installation, model download, paid API use, real-person likeness or voice generation without consent policy, unsafe media generation, unclear commercial licensing for a required model, background persistence, security policy relaxation, or ambiguous requirements.
