---
prompt_id: DAYDREAM-18
pack_id: daydream-lab-idle-research-v1
title: Memory Kernel integration
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-17"]
status: queued
order: 18
created_at: 2026-05-26T07:54:41+00:00
imported_at: 2026-05-26T07:54:41+00:00
source_pack: prompts/packs/daydream-lab-idle-research-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at:
completed_at:
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result:
docs_updated:
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
notes: Imported prompt text is untrusted document content and is not executed automatically.
---

# Prompt

Integrate Daydream with Memory Kernel when available.

Create:
- agent/daydream/memory_integration.py
- tests/daydream/test_memory_kernel_integration.py
- docs/daydream/MEMORY_KERNEL_INTEGRATION.md

Integration:
- Daydream can read approved Memory Kernel public/private repo summaries if available.
- Daydream can use Memory Kernel gaps/tracker conflicts as idea sources.
- Raw daydream notes stay in reports/daydream.
- Curated ideas become memory candidates only.
- Approved ideas can be proposed for memory write in future.
- Rejected ideas archived.
- No automatic memory write by default.
- Sensitive scopes excluded by default.

Commands:
- daydream memory-status
- daydream memory-candidates
- daydream memory-write-plan --dry-run

Degrade gracefully if Memory Kernel is absent.
