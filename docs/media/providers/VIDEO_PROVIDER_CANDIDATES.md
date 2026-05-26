# Video Provider Candidates

Status: MEDIA-07 metadata-only.
Last updated: 2026-05-25.

These candidates are planning metadata. Their presence does not mean provider availability, model installation, license approval, hardware readiness, or generation support.

| Provider | Status | Default enabled | Real generation | Notes |
|---|---|---:|---:|---|
| Mock video provider | stubbed | false | false | Test-only fake metadata/results. |
| ComfyUI video workflows | stubbed | false | false | Workflow submission remains disabled. |
| Wan | planned | false | false | Requires model, license, hardware, and runtime review. |
| LTX-Video | planned | false | false | Future provider/runtime work only. |
| HunyuanVideo | planned | false | false | Large runtime/model footprint expected. |
| Stable Video Diffusion | planned | false | false | Image-to-video policy and source-image consent required. |
| Image-to-video workflows | future | false | false | Disabled until personal-image/source-asset policy exists. |
| Text-to-video workflows | future | false | false | Disabled until provider/runtime/resource policy exists. |

## Default Policy

- No provider is enabled by default.
- No model is downloaded.
- No runtime is installed.
- No paid API is called.
- No video is generated.
- No video is uploaded or posted.
- No real-person likeness video workflow exists.

## Resource Warnings

Video providers must be treated as resource-sensitive. Future implementation needs explicit controls for:

- model size and storage
- GPU/VRAM requirements
- timeout and cancellation
- queueing
- cost and paid-provider policy
- source media privacy
- output retention

## License Warnings

Provider and model licenses must be reviewed before production use. Mock provider records grant no production rights.
