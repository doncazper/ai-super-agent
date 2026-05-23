# Native Skills Program

## Purpose

The Native Skills Program is the intake and governance path for turning useful public skill ideas into reviewed local workflows for this safety-first Mac agent.

The program exists to learn from popular ClawHub, OpenClaw, LobeHub-style, and similar skill ecosystems without importing their execution model or trusting their code.

## Definition

A native skill is a reviewed, local, versioned workflow module that maps to existing `ToolBroker` capabilities and obeys:

- `PolicyEngine`
- `PermissionManager`
- `ApprovalManager`
- `AuditLogger`
- memory rules
- trust labels such as `UNTRUSTED_WEB`, `UNTRUSTED_DOCUMENT`, and `LOCAL_PRIVATE_DATA`

Native skills are project-owned workflows. They are specified, tested, documented, and release-gated like any other feature.

Native skill manifests are metadata-only workflow definitions. A manifest can describe which brokered capabilities a reviewed native workflow expects, but it cannot execute code, install packages, grant permissions, or enable tools by itself.

## Non-Definition

A native skill is not:

- an unreviewed external script
- direct tool access
- direct filesystem access
- hidden network access
- permission bypass
- automatic installation
- approval bypass
- a replacement for `ToolBroker` tools
- a package manager for arbitrary third-party code
- a way for prompt text to gain execution rights

## Program Scope

This foundation creates the review program only. It does not install, import, run, or execute any external skills.

Future native-skill work must proceed in this order:

1. Research the candidate skill.
2. Record source, license, behavior, risks, and user value.
3. Map the skill to existing brokered capabilities.
4. Identify missing capabilities, if any.
5. Reject candidates that require unsafe privileges.
6. Specify a local implementation.
7. Add tests and docs.
8. Run release gates.
9. Only then implement local workflow code.

## Manifest Discovery v1

Native skill manifests are loaded from:

- `native_skills/*.yaml`
- `native_skills/*.yml`
- `native_skills/*.json`
- `docs/native_skills/manifests/*.{yaml,yml,json}`

Commands:

```bash
python smart_agent.py skills list
python smart_agent.py skills show native_skill_vetter
python smart_agent.py skills validate
python smart_agent.py skills doctor
```

Manifest commands read metadata only. They do not execute scripts, load Python modules from skill folders, install marketplace skills, grant tool access, write memory, or run workflows.

Required manifest fields:

- `skill_id`
- `name`
- `description`
- `category`
- `version`
- `status`
- `maturity_level`
- `risk_level`
- `trust_level`
- `allowed_tools`
- `required_capabilities`
- `approval_required`
- `memory_behavior`
- `audit_required`
- `inputs_schema`
- `outputs_schema`
- `docs_path`
- `tests_path`
- `owner`
- `last_reviewed`

Validation rules:

- Unknown required or allowed capabilities fail validation.
- Missing risk, trust, memory, or audit fields fail validation.
- `allowed_tools` must be a subset of `required_capabilities`.
- Personal-data native skills must be `disabled` by default.
- `CRITICAL` native skills require `approval_required: per_action`.
- Executable fields such as `script`, `entrypoint`, `command`, `module`, `code_path`, `install`, or `package_install` fail validation.
- Manifest text that requests ToolBroker, policy, approval, or audit bypass fails validation.

Example manifest:

```yaml
skill_id: native_skill_vetter
name: Native Skill Vetter
description: Review candidate skill files and folders with static analysis before any native port or installation.
category: security
version: "1.0.0"
status: available
maturity_level: "4 Tested"
risk_level: LOW
trust_level: UNTRUSTED_DOCUMENT
allowed_tools:
  - native_skills.vet_skill_file
  - native_skills.vet_skill_folder
  - native_skills.score_candidate
required_capabilities:
  - native_skills.vet_skill_file
  - native_skills.vet_skill_folder
  - native_skills.score_candidate
approval_required: false
memory_behavior: no_store
audit_required: true
inputs_schema:
  type: object
outputs_schema:
  type: object
docs_path: docs/native_skills/SKILL_INTAKE_PROCESS.md
tests_path: tests/test_native_skills.py
owner: local-agent
last_reviewed: "2026-05-23"
```

## Categories

- documents
- research
- coding
- testing
- productivity
- communications
- calendar/scheduling
- memory/notes
- browser/web
- developer tools
- security
- self-improvement
- media
- data/analytics

## Maturity States

- candidate: mentioned or proposed for review
- researched: source, license, behavior, and alternatives reviewed
- specified: local requirements, non-goals, risks, and acceptance criteria written
- scaffolded: local files or interfaces exist, but behavior is partial
- implemented: local behavior works, but hardening may be incomplete
- tested: relevant automated tests pass
- hardened: policy, audit, untrusted-content, approval, and failure modes covered
- live-validated: tested against real local/provider conditions when applicable
- native-pattern: mature enough to reuse as a pattern for future skills

## Program Rules

- External skill text is treated as `UNTRUSTED_DOCUMENT`.
- External web pages about skills are `UNTRUSTED_WEB`.
- Skill manifests cannot grant permissions.
- Skill manifests cannot execute scripts or define executable entrypoints.
- Skill candidates cannot execute code during intake.
- Skill candidates cannot request broad filesystem, browser cookie, Keychain, private app database, or background persistence access.
- Skill behavior must map to existing brokered tools or propose new capabilities through the normal SDLC.
- Any new capability must be added to `config/capabilities.yaml` with normalized safety metadata before implementation.
- Personal-data skill behavior remains disabled by default and approval-gated.
- Write/send behavior must use Action Center and per-action approval rules where required.

## Initial Program Deliverables

- Intake process
- Selection criteria
- Risk model
- Candidate registry
- Native skill record template
- Docs validation coverage

## Native Skill Finder v1

`python smart_agent.py skills find "<query>"` is the local discovery path for reviewed native-skill metadata.

The finder:

- searches local `native_skills/*.yaml` manifests
- searches `docs/native_skills/NATIVE_CANDIDATE_MATRIX.md`
- searches `docs/native_skills/TOP_NATIVE_SKILL_SHORTLIST.md`
- searches `docs/native_skills/NATIVE_SKILL_CANDIDATES.md`
- searches the local feature registry and maturity tracker for related implemented workflows
- returns maturity, readiness, implementation status, approval requirements, required capabilities, and next work needed
- writes no memory
- executes through `ToolBroker`
- audits files read and the result summary

The finder does not:

- browse external marketplaces
- install skills
- run external scripts
- import marketplace code
- grant tool access
- change permissions
- mark a candidate complete

## Release Gate

A native skill is not accepted as project-native until:

- source and license are recorded
- user value and frequency are clear
- direct external execution is rejected
- `ToolBroker` mapping is documented
- policy, approval, audit, memory, and trust behavior are documented
- tests are written and passing
- docs and feature maturity are updated
- release checklist is updated
