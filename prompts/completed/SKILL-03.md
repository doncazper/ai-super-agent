---
prompt_id: SKILL-03
pack_id: native-skill-system-hardening-v1
title: Skill provenance, trust metadata, and lockfile
category: native_skills
risk_level: MEDIUM
approval_gate: false
depends_on: ["SKILL-02"]
status: completed
order: 3
created_at: 2026-05-25T09:50:27+00:00
imported_at: 2026-05-25T09:50:27+00:00
source_pack: prompts/packs/native-skill-system-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T10:06:21+00:00
completed_at: 2026-05-25T22:00:02+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: completed prompt file and prompt audit evidence verified during SOURCE-TRUTH-RECONCILE-01
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
notes: Reconciled stale imported row from completed prompt file and prompt audit evidence; no prompt was run by this reconciliation.
---

# Prompt

You are Codex working in this repo.

Task:
Build native skill provenance, trust metadata, and lockfile support.

Goal:
Track where every skill came from, whether it has been reviewed, whether it is pinned, and whether it is allowed to change. Prevent silent skill changes from altering agent behavior.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/native_skills/SKILL_MANIFEST_SCHEMA.md
- docs/native_skills/SKILL_DEPENDENCY_GATING.md
- docs/PROJECT_STATE.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md

Scope:
- Provenance model.
- Trust metadata.
- Lockfile.
- Pin/unpin planning.
- Tests.
- Docs.

Non-goals:
- Do not auto-update skills.
- Do not install external skills.
- Do not enable unreviewed skills.
- Do not run scripts.
- Do not connect to external marketplaces.

Create or update:
- agent/native_skills/provenance.py
- agent/native_skills/lockfile.py
- agent/native_skills/trust.py
- tests/native_skills/test_skill_provenance_lockfile.py
- docs/native_skills/SKILL_PROVENANCE.md
- docs/native_skills/SKILL_LOCKFILE.md
- native_skills.lock.example or docs/templates/native_skills_lock_template.yaml

Provenance fields:
- source_type: native | bundled | local | external | clawhub_candidate | reconstructed | imported | unknown
- source_path
- source_url, optional
- source_pack_id, optional
- author
- license
- version
- hash
- reviewed_by
- reviewed_at
- review_status
- trust_level
- install_status
- pinned
- pin_reason
- last_updated
- known_risks
- caveats

Trust statuses:
- trusted_native
- reviewed_local
- reviewed_external
- candidate
- unreviewed_external
- blocked
- unknown

Install/status values:
- candidate
- approved
- installed
- disabled
- blocked
- pinned
- deprecated
- removed

Lockfile must track:
- skill_id
- version
- source_type
- source_path/source_url
- hash
- pinned
- reviewed_at
- trust_status
- manifest_hash
- dependencies_hash
- effective_root
- winning_precedence
- shadowed_by
- generated_at

Commands if practical:
- python smart_agent.py skills lock status
- python smart_agent.py skills lock verify
- python smart_agent.py skills pin <skill_id>
- python smart_agent.py skills unpin <skill_id>
- python smart_agent.py skills provenance <skill_id>
- python smart_agent.py skills trust <skill_id>

Requirements:
1. Lockfile verification detects changed manifest/hash.
2. Unreviewed external skills are not trusted.
3. Candidate skills are not enabled by default.
4. Pinned skills cannot be silently updated.
5. Missing license triggers warning.
6. Unknown source triggers warning.
7. Hashes computed without executing files.
8. Secrets redacted.
9. Trust metadata visible in skill status.
10. Reconstructed skills clearly marked reconstructed and not exact originals unless evidence.

Tests:
- provenance record validates.
- unknown source warns.
- missing license warns.
- lockfile generated from fixture manifests.
- lockfile verify passes unchanged fixture.
- lockfile verify detects changed manifest.
- pinned skill cannot be silently updated.
- candidate skill disabled by default.
- reconstructed skill labeled correctly.
- command registry updated if commands added.

Update:
- docs/native_skills/NATIVE_SKILL_CRITERIA.md if present.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/COMMAND_REGISTRY.md if commands added.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.
- docs/RISK_REGISTER.md.
- docs/THREAT_MODEL.md.

Run tests/validations.

Final report:
- provenance model added
- lockfile support added
- tests run/results
- next recommended prompt
