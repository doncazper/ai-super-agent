---
prompt_id: MEDIA-02
pack_id: creative-media-generation-v1
title: Media provider registry and output asset manager
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-01"]
status: completed
order: 2
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T22:22:18+00:00
completed_at: 2026-05-25T22:31:27+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: media model/registry/asset tests passed 10 tests; focused media/docs/command registry tests passed 19 tests; media CLI smokes passed; command registry validation ok with 522 commands; make policy-check passed startup policy and capability manifest validation; policy/toolbroker tests passed 22
docs_updated: yes
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
command_registry_updated:
completion_report_updated:
evidence_links:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes: Implemented provider-neutral media models, static/mock provider registry, bounded asset metadata manager, brokered read-only/dry-run media CLI commands, docs, manifest entries, and tracker updates. No real media generation/providers/downloads/paid APIs/uploads/voice/likeness/personal-data access.
---

# Prompt

You are Codex working in this repo.

Task:
Build Media Provider Registry and Output Asset Manager.

Goal:
Create provider-neutral models and a controlled asset workspace for generated media.

Scope:
- Models.
- Provider registry.
- Asset manager.
- Tests.
- No real generation providers yet.

Non-goals:
- Do not generate media.
- Do not install providers.
- Do not call paid APIs.
- Do not upload/publish assets.
- Do not access personal photos/videos outside approved inputs.

Create:
- agent/media/
  - __init__.py
  - models.py
  - provider_registry.py
  - asset_manager.py
  - errors.py
  - redaction.py
- tests/media/test_media_models_registry.py
- tests/media/test_media_asset_manager.py
- docs/media/MEDIA_PROVIDER_REGISTRY.md
- docs/media/MEDIA_ASSET_MANAGER.md

Models:
- MediaProvider
- MediaProviderStatus
- MediaProviderCapability
- MediaGenerationRequest
- MediaGenerationResult
- MediaAsset
- MediaAssetType
- MediaPrompt
- MediaSafetyReview
- MediaLicenseInfo
- MediaProviderError

Asset fields:
- asset_id
- asset_type
- path
- created_at
- provider
- prompt_hash
- prompt_redacted
- source_inputs
- metadata
- license_info
- safety_status
- audit_ids
- retention_status

Asset manager requirements:
1. Store generated outputs under a controlled media workspace, e.g. media_outputs/ or workspace/media/.
2. Do not write outside approved roots.
3. Prompt text redacted where needed.
4. Personal input images/videos require explicit tagging and approval later.
5. Asset metadata JSON stored alongside output.
6. No raw secrets.
7. No auto-publish.
8. Deletion/cleanup bounded to media workspace.
9. Asset list/status commands read-only.
10. Tests use fake assets only.

Commands:
- python smart_agent.py media providers
- python smart_agent.py media doctor
- python smart_agent.py media assets list
- python smart_agent.py media assets show <asset_id>
- python smart_agent.py media assets cleanup --dry-run

Tests:
- provider registry loads mock provider.
- unknown provider handled.
- asset path bounded.
- path traversal blocked.
- metadata written for fake asset.
- cleanup dry-run writes nothing.
- prompt redaction works.
- command registry updated.

Update docs/tracking.

Final report:
- provider registry added
- asset manager added
- commands added
- tests run/results
- next recommended prompt
