# Image Generation Strategy

Status: scaffolded in MEDIA-05.

Image generation remains dry-run only. MEDIA-05 adds request planning, provider candidate metadata, safety/license integration, and a mock image provider for fake test metadata. It does not generate real images.

## Requirements Before Real Generation

- Provider/model must be configured explicitly.
- Safety preflight must run first.
- License review must be complete before commercial-use claims.
- Output must go through the media asset manager.
- Provider actions must route through ToolBroker and PolicyEngine.
- HIGH/CRITICAL workflows must use ApprovalManager.
- AuditLogger must record provider, prompt safety, asset metadata, denials, and result summaries.

## Current Commands

- `python smart_agent.py media generate image "prompt" --dry-run`
- `python smart_agent.py media image providers`
- `python smart_agent.py media image plan "prompt"`

These commands do not generate images, import diffusion libraries, download models, or call providers.

## Current Provider Behavior

- `mock_image` can create fake asset metadata in tests only.
- `comfyui` is a disabled/stubbed workflow-engine candidate.
- `diffusers`, SDXL, FLUX, Stable Diffusion 3.x, Qwen-Image, ControlNet, and LoRA workflows remain planned/future.

## Personal Images

Personal image editing is not part of MEDIA-05. Future image-to-image, face, likeness, or private-photo workflows require explicit consent and privacy gates.
