# Skill Creation From Repeated Tasks

HERMES-04 adds proposal-only scaffolding for noticing repeated safe workflows and turning them into candidate native skill ideas. It does not create, import, enable, install, or execute skills.

## Scope

- Inputs are redacted command metadata and redacted session metadata only.
- Session files that are not explicitly marked redacted are skipped.
- Personal-data patterns are skipped by default.
- Higher-risk non-personal patterns can become proposals, but they are marked `needs_review`.
- Suggested manifests are candidate metadata, not executable skill manifests.

## Safety Boundary

The proposal flow must not:

- read raw session content by default
- inspect private connector data
- generate enabled skills
- update allowlists
- execute external skill scripts
- install packages
- call providers
- bypass skill vetting
- bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger

All proposed skills start as `candidate_unreviewed` or `needs_review`. A future implementation prompt must run static skill vetting, add tests and docs, update command registry entries, and pass the appropriate release gate before a proposal can become an actual native skill.

## Commands

```bash
python smart_agent.py skills propose-from-sessions
python smart_agent.py skills propose-from-commands
python smart_agent.py skills proposals list
python smart_agent.py skills proposals show <proposal_id>
python smart_agent.py skills proposals approve <proposal_id> --dry-run
```

The `approve` command is intentionally dry-run only. It previews the next review steps and never changes an allowlist, writes a skill file, or enables execution.

## Proposal Evidence

Proposal records include:

- proposal id and title
- observed repeated pattern
- redacted metadata sources
- frequency
- risk level and review status
- suggested disabled manifest metadata
- suggested tests and docs
- privacy review
- approval requirements

Generated reports are local redacted metadata under `reports/autonomy/`, which is gitignored except for `.gitkeep`.

