# Media Asset Manager

Status: scaffolded in MEDIA-02.

The media asset manager controls where future generated media outputs and metadata may live. It supports fake/test assets for unit tests and redacted metadata inspection for CLI status commands. It does not generate media.

## Controlled Roots

Allowed media roots are project-local only:

- `workspace/media/`
- `media_outputs/`

MEDIA-02 defaults to `workspace/media/`. Paths must be relative to the media root. Absolute paths and `..` traversal are rejected.

## Metadata

Each asset metadata file is stored beside the output as:

```text
<asset filename>.media.json
```

Metadata includes:

- `asset_id`
- `asset_type`
- `path`
- `created_at`
- `provider`
- `prompt_hash`
- `prompt_redacted`
- `source_inputs`
- `metadata`
- `license_info`
- `safety_status`
- `audit_ids`
- `retention_status`

Raw prompts are not stored in metadata. Prompt hashes and redacted prompt previews are stored so assets can be traced without leaking secrets by default.

## CLI Commands

Implemented in MEDIA-02:

- `python smart_agent.py media assets list`
- `python smart_agent.py media assets show <asset_id>`
- `python smart_agent.py media assets cleanup --dry-run`

`cleanup` is dry-run only in MEDIA-02. It reports candidates and deletes nothing.

## Safety Rules

- No writes outside controlled media roots.
- No auto-publish.
- No raw secrets in metadata.
- No personal input media access.
- No generated assets are stored in memory by default.
- Future personal input images/videos require explicit tagging, policy, and approval gates.
