# Media Provider Strategy

Status: specified with MEDIA-02 static registry scaffold.
Last updated: 2026-05-25.

## Provider Principles

Media providers are optional adapters. Provider status and doctor commands may inspect static configuration through ToolBroker-routed metadata tools, but generation commands must not run until a provider is explicitly implemented, capability-manifested, policy-reviewed, tested, and audited.

Provider loading must be lazy. Importing `smart_agent.py` or the media registry must not import ComfyUI, Diffusers, CUDA, Metal, audio, video, or cloud provider SDK modules.

## Candidate Providers

| Provider | Category | Default status | Notes |
|---|---|---|---|
| ComfyUI | image_generation, image_editing, video workflows | planned in registry | Future local server adapter only; no install or server start by default |
| Diffusers | image_generation, image_editing | planned | Optional local Python runtime; no package install or model download |
| Stable Diffusion / SDXL | image_generation | planned | License and model card evidence required |
| FLUX | image_generation | planned | License and commercial-use caveats required |
| Stable Diffusion 3.x | image_generation | planned | License restrictions must be tracked |
| Qwen-Image | image_generation, image_editing | planned | License/model-card review required |
| Wan / LTX / HunyuanVideo / Stable Video Diffusion | image_to_video, text_to_video | planned | Higher cost/resource and content-risk review required |
| AudioCraft / MusicGen / AudioGen | audio_generation, music_generation | planned | Copyright and dataset caveats required |
| Stable Audio Open | audio_generation, music_generation | planned | License evidence required |
| ACE-Step | music_generation | planned | License evidence required |
| TTS providers | tts | future only | Voice consent and privacy policy required before user-facing workflows |
| Voice generation providers | voice_generation | blocked until consent policy | Voice cloning is CRITICAL or FORBIDDEN until explicit consent workflow exists |
| Cloud providers | all applicable categories | optional, disabled by default | Paid/API use is config and approval gated |
| Mock provider | mock/test | stubbed in registry | Used for tests, dogfood, and command QA without creating real media |

MEDIA-02 implements static provider records for `mock`, `comfyui`, and `external_paid`. These records are not executable providers.

Media provider secret setup is tracked in `docs/secrets/PROVIDER_SECRET_SETUP.md`. `MEDIA_PROVIDER_API_KEY` is a future placeholder only, and `COMFYUI_BASE_URL` is configuration rather than a secret. Run `python smart_agent.py secrets doctor media` to inspect media provider secret/config metadata without enabling generation or printing values.

## Provider Selection Order

1. Mock/test provider for validation.
2. Local provider that is explicitly configured and license-reviewed.
3. User-selected local server provider.
4. Optional cloud provider only when explicitly configured, paid use is allowed, and approval policy permits it.
5. Graceful setup-required or unavailable response.

## Provider Metadata

Every future provider record must include:

- provider id
- provider name
- category list
- default enabled flag
- local/cloud classification
- paid/quota behavior
- supported media types
- license notes and docs path
- commercial-use status with evidence
- setup hint
- safety restrictions
- output asset policy
- rate/resource limits
- audit fields
