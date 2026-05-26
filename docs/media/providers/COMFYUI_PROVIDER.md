# ComfyUI Provider Stub

Status: stubbed in MEDIA-04.

ComfyUI is the primary local workflow-engine candidate for future image, image-editing, video, and adjacent diffusion workflows. MEDIA-04 creates only a provider stub and status/doctor metadata.

## What Exists

- `agent/media/providers/comfyui.py`
- `python smart_agent.py media comfyui doctor`
- `python smart_agent.py media workflows list --provider comfyui`
- Safe config defaults in `.env.example`
- Mocked tests for status behavior

## What Does Not Exist

- No ComfyUI install.
- No server startup.
- No model download.
- No workflow submission.
- No generated media.
- No custom-node execution.
- No provider SDK/runtime import at startup.

## Config

```text
COMFYUI_ENABLED=false
COMFYUI_BASE_URL=http://127.0.0.1:8188
COMFYUI_TIMEOUT_SECONDS=120
COMFYUI_OUTPUT_DIR=
COMFYUI_ALLOW_WORKFLOW_SUBMIT=false
COMFYUI_ALLOW_CUSTOM_NODES=false
COMFYUI_REQUIRE_SAFETY_PREFLIGHT=true
```

## Status Values

- `disabled`
- `not_configured`
- `server_unreachable`
- `reachable`
- `workflow_submit_disabled`
- `ready_mock_only`
- `ready`

## Safety Notes

ComfyUI workflow JSON is treated as `UNTRUSTED_DOCUMENT` unless vetted. Custom nodes are treated as supply-chain risk and remain disabled by default. Future workflow submission must run prompt safety preflight, use ToolBroker, respect PolicyEngine and ApprovalManager, write bounded asset metadata, and audit provider decisions and outputs.
