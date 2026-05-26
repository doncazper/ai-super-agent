# Media Asset Policy

Status: specified with MEDIA-02 asset manager scaffold.
Last updated: 2026-05-25.

## Storage Boundary

Future media assets must be written only to approved workspace media directories such as `workspace/media/` or a configured project-local media output directory. MEDIA-02 adds a bounded metadata manager for fake/test assets and future generated-output metadata, with CLI inspection routed through ToolBroker. It writes no real generated media.

## Asset Metadata

Asset records include:

- asset id
- media type
- provider id
- model id when known
- created_at
- prompt summary or redacted prompt hash
- safety status
- license status
- source references when inputs were used
- file path under approved workspace roots
- content hash

## Retention

Generated assets are user-visible workspace artifacts, not memory records. They must not be stored in long-term memory by default. Future cache or report metadata must avoid raw personal prompts and raw personal input-image metadata unless explicitly approved.

## Forbidden Asset Handling

- No uploads or publishing in this track.
- No binary downloads as provider setup.
- No writing outside approved workspace paths.
- No hidden background generation.
- No automatic use of personal photos or private files.
