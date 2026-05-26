# Image Provider Candidates

Status: scaffolded in MEDIA-05.

This document records candidate image providers and models for future work. It is not an implementation claim.

| Candidate | Status | Notes |
| --- | --- | --- |
| ComfyUI workflows | stubbed | Disabled by default; no workflow submission or generation |
| Diffusers local provider | planned | No package install or model download in MEDIA-05 |
| SDXL | planned | License/model-card evidence required |
| FLUX.1-schnell / FLUX.1-dev | planned | License and commercial-use caveats required |
| Stable Diffusion 3.x | planned | License restrictions must be tracked |
| Qwen-Image | planned | Provider/model review required |
| ControlNet / LoRA workflows | future | Requires workflow vetting and personal-image policy |

## Current Rules

- Free/local/open providers first.
- Paid APIs disabled by default.
- No personal photos without future consent flow.
- No model downloads by default.
- No generated image output in MEDIA-05.
- Mock provider is for tests only and creates no real image.
