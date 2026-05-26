# Skill Improvement From Experience

Status: HERMES-05 proposal-only scaffold.

## Scope

The skill improvement workflow turns redacted evidence into reviewable native skill improvement proposals. It is intended for bug reports, dogfood failures, command QA, regression findings, and user feedback that already exists as safe project metadata.

It does not edit skills, update lockfiles, enable skills, install packages, execute skill scripts, or increase feature maturity by itself.

## Commands

```bash
python smart_agent.py skills improve-propose native_skill_vetter
python smart_agent.py skills improve-from-bugs native_skill_vetter
python smart_agent.py skills improve-from-dogfood native_skill_vetter
python smart_agent.py skills improvements list
python smart_agent.py skills improvements show improvement_native_skill_vetter_abc123def0
```

All commands route through ToolBroker, PolicyEngine, and AuditLogger. The proposal commands write redacted proposal metadata under `reports/autonomy/skill_improvements.json` by default; this path is ignored except for the directory placeholder.

## Evidence Rules

Allowed evidence:

- Redacted bug metadata under `bugs/*.json`.
- Redacted dogfood/session metadata under `reports/sessions/*.json`.
- Explicitly provided redacted feedback metadata in tests or future reviewed workflows.

Skipped evidence:

- Unredacted records.
- Records marked as containing personal data.
- Records whose summaries include personal-data terms such as email, messages, contacts, calendar, phone, address, or local private data.
- Empty records.

The proposal engine uses evidence IDs and summaries only. It does not read raw session outputs, private connector data, or personal-data tool content.

## Proposal Contents

Each proposal records:

- `improvement_id`
- `skill_id`
- `evidence_sources`
- `bug_ids`
- `dogfood_failures`
- `user_feedback`
- `proposed_change`
- `risk_level`
- `files_expected`
- `tests_required`
- `docs_required`
- `lockfile_impact`
- `rollback_plan`
- `human_review_required`
- `status`

High-risk proposals are marked `needs_review`. Lower-risk proposals are still `candidate_unreviewed`; they are not approvals.

## Safety Boundaries

- No automatic skill modification.
- No automatic lockfile update.
- No automatic maturity increase.
- No skill import, enablement, package install, external script execution, or plugin runtime execution.
- No personal-data evidence by default.
- No ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger bypass.

Future implementation of a proposal requires a separate reviewed prompt, native skill vetting, tests, docs updates, command registry updates if commands change, and release-gate evidence.

