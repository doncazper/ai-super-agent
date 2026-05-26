# Decision: ComfyUI Provider Strategy

Date: 2026-05-25
Status: accepted for stub-only scaffold

## Context

Creative media workflows need a local-first provider candidate before any cloud or paid provider is considered. ComfyUI is flexible and widely used for image/video diffusion workflows, but it also carries model download, workflow JSON, custom-node, GPU/runtime, and output safety risks.

## Decision

Use ComfyUI as a planned local workflow-engine candidate, but keep MEDIA-04 stub-only:

- disabled by default
- no install
- no server start
- no model download
- no workflow submission
- no generation
- no custom nodes by default
- workflow JSON treated as `UNTRUSTED_DOCUMENT`
- safety preflight required before any future generation

## Consequences

The repo can expose setup/status and workflow-list metadata without runtime overhead or provider side effects. Real ComfyUI support requires a later release-gated implementation prompt with ToolBroker mapping, policy manifest entries, asset-manager writes, safety preflight enforcement, workflow vetting, and tests.
