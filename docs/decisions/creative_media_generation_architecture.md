# Decision: Creative Media Generation Architecture

Date: 2026-05-25
Status: accepted for docs-only roadmap

## Context

The agent needs a future path for image, video, audio, music, TTS, thumbnails, social creatives, and mock media workflows without installing models, downloading large assets, calling paid APIs, generating unsafe content, weakening safety controls, or coupling core startup to heavy media runtimes.

## Decision

Creative media will use a provider-based architecture:

- provider metadata and mock/test providers first
- optional local providers behind lazy adapters
- cloud providers optional and disabled by default
- no provider imports at core startup
- no generation without capability manifest entries
- all future generation through ToolBroker, PolicyEngine, PermissionManager, ApprovalManager where required, and AuditLogger
- all output assets written only to approved workspace media paths
- license, consent, safety, and retention metadata tracked before user-ready claims

## Consequences

This keeps the current Python CLI stable and avoids hidden runtime dependencies. It also means early media milestones are intentionally conservative: docs, metadata, stubs, mocks, safety policy, asset policy, and evals before real generation.

Voice cloning, real-person likeness generation, and social publishing remain blocked or deferred until separate consent, approval, and release-gate prompts exist.

