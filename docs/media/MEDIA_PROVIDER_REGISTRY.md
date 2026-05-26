# Media Provider Registry

Status: scaffolded in MEDIA-02.

The media provider registry is a static metadata layer for creative media providers. It does not generate media, import provider SDKs, download models, start servers, call paid APIs, upload files, or publish anything.

## Source Of Truth

- Runtime metadata: `agent/media/provider_registry.py`
- Provider models: `agent/media/models.py`
- ToolBroker command tools: `agent/tools/media.py`
- CLI command tracking: `docs/COMMAND_REGISTRY.md`
- Risk policy: `docs/media/MEDIA_RISK_MODEL.md`

## Provider Records

Each provider record includes:

- `provider_id`
- `name`
- `status`
- `capabilities`
- `default_enabled`
- `local_only`
- `paid_api`
- `requires_model_download`
- `risk_level`
- `trust_level`
- `setup_hint`
- `docs_path`
- `notes`

## Default Providers

| Provider | Status | Purpose | Default |
| --- | --- | --- | --- |
| `mock` | stubbed | Tests and future dogfood planning only | disabled |
| `comfyui` | planned | Future local image generation/editing bridge | disabled |
| `external_paid` | blocked | Placeholder for paid/cloud providers | disabled |

The mock provider is metadata-only. It does not produce images, audio, video, thumbnails, or any other generated output.

## CLI Commands

Implemented in MEDIA-02:

- `python smart_agent.py media providers`
- `python smart_agent.py media doctor`

Both commands route through ToolBroker and return metadata only.

## Forbidden In This Milestone

- Real media generation.
- Provider SDK imports at startup.
- Model downloads.
- Paid API calls.
- Uploads or publishing.
- Voice cloning.
- Real-person likeness workflows.
- Personal photo/video access.
