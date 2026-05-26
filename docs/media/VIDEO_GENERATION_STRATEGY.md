# Video Generation Strategy

Status: MEDIA-07 local scaffold.
Last updated: 2026-05-25.

## Scope

MEDIA-07 prepares a safe boundary for future text-to-video and image-to-video work.

Current support is limited to:

- video provider candidate metadata
- dry-run video generation plans
- deterministic safety preflight
- provider/license uncertainty metadata
- hardware/resource warning metadata
- fake video metadata helpers for tests

## Non-Goals

MEDIA-07 does not:

- Download video models.
- Install video generation dependencies.
- Import video generation SDKs.
- Generate real videos.
- Read personal images or source videos.
- Run image-to-video workflows.
- Upload or post videos.
- Create real-person likeness videos.
- Start ComfyUI or submit workflows.
- Call paid APIs.

## Commands

```bash
python smart_agent.py media generate video "prompt" --dry-run
python smart_agent.py media video providers
python smart_agent.py media video plan "prompt"
```

`media generate video` requires `--dry-run`. Non-dry-run execution is blocked.

All commands route through ToolBroker and PolicyEngine.

## Resource Policy

Video generation can require large model files, high VRAM, long runtimes, disk space, and provider-specific licenses.

The current scaffold always reports:

- `model_downloads_enabled=false`
- `hardware_review_required=true`
- `estimated_runtime_known=false`
- `real_generation=false`

Future provider implementation must add explicit setup docs, hardware checks, timeout/rate limits, cost controls, and release-gate evidence.

## Safety Policy

Video prompts run deterministic local media safety checks. Real-person likeness, personal-image source workflows, deceptive before/after claims, violent/illegal instructional content, and commercial usage uncertainty require denial or review according to the media safety policy.

Image-to-video workflows are disabled until a future source-asset and consent policy exists.

## Mock Provider

`agent.media.providers.mock_video.MockVideoProvider` exists for tests and mock metadata only.

It can create fake `.txt` fixture assets under the controlled media workspace through `MediaAssetManager`. These are not videos and grant no usage rights.

## Future Gate

Before any real video provider can run, the repo must add:

- capability manifest entries for the exact provider/action
- ToolBroker mapping
- PolicyEngine tests
- ApprovalManager behavior for HIGH/CRITICAL cases
- AuditLogger fields for provider decisions, prompt safety, resource use, denials, approvals, asset writes, and results
- provider license and model-card review
- startup overhead/import tests
- mock and live opt-in validation
