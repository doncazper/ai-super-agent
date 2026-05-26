# Thumbnail And Social Creative Workflows

Status: MEDIA-06 local scaffold.
Last updated: 2026-05-25.

## Scope

MEDIA-06 adds dry-run workflow planning for future thumbnail, cover, social, product, ad, and marketing creative use cases.

The scaffold supports:

- YouTube thumbnails.
- Short-form video covers.
- Podcast covers.
- Real estate listing graphics.
- Food review thumbnails.
- Family vlog title cards.
- Social post images.
- Ad creatives.
- Before/after layouts.
- Product mockups.

## Non-Goals

MEDIA-06 does not:

- Edit real user images.
- Generate real media.
- Read personal photos or videos.
- Upload or post assets.
- Schedule social publishing.
- Create real-person likeness edits.
- Install image libraries, model runtimes, or provider SDKs.
- Download models.
- Call paid APIs.

## Commands

```bash
python smart_agent.py media thumbnail "prompt" --dry-run
python smart_agent.py media creative plan "prompt"
python smart_agent.py media creative templates
```

All commands are routed through ToolBroker and PolicyEngine.

`media thumbnail` requires `--dry-run`. Non-dry-run thumbnail requests are blocked.

## Workflow Template Metadata

Workflow templates are stored in `agent/media/creative_workflows.py` as local metadata, not model secrets. Each template records:

- workflow type
- name and description
- aspect ratio
- output size suggestion
- prompt template
- use cases
- risk notes
- commercial review recommendation

Template metadata can be moved to a config file later if product needs make that useful. It must remain reviewable, tracked, and non-secret.

## Safety And License Checks

Creative workflow plans run deterministic local media prompt safety checks and include provider/model license uncertainty metadata.

Plans include:

- redacted prompt metadata
- safety outcome
- license caution
- output size and aspect-ratio suggestion
- workflow-specific risk notes
- upload/publish disabled flags

Commercial/social workflows recommend license and claims review before production use. The report is operational risk metadata, not legal advice.

## Asset Manager Integration

`agent.media.creative_workflows.create_mock_workflow_asset()` can create fake test metadata under the controlled media workspace through `MediaAssetManager`.

This helper is for tests and dogfood scaffolding. CLI planning commands do not write generated assets.

Mock asset records state:

- `real_generation=false`
- `real_editing=false`
- `upload_publish_enabled=false`

## Approval Boundary

Current commands are LOW or SAFE because they are metadata/dry-run only.

Future real editing, real generation, personal-image input, likeness editing, upload, scheduling, or publishing must get separate capability manifest entries, ToolBroker routes, policy tests, approval behavior, audit fields, and release-gate evidence before execution.
