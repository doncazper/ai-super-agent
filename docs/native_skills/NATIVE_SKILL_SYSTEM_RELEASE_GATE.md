# Native Skill System Release Gate

Status: local release gate passed for metadata-only native skill system v1 on 2026-05-25.

This gate validates the native skill system as a safe, trackable foundation for future reviewed native skills. It does not approve installing external skills, running skill scripts, enabling plugin runtimes, or enabling personal-data skills.

## Scope Confirmed

- Skill roots, scopes, and precedence.
- Manifest schema and dependency gating.
- Provenance, trust metadata, and lockfile verification.
- Static inspection and vetting.
- Per-profile allowlists.
- Compatibility matrix.
- Conflict detector.
- Test/dogfood harness.
- Docs generator/catalog.
- Release-gate documentation and maturity review.

## Non-Goals Confirmed

- No external skill installation.
- No external skill enablement.
- No external skill script execution.
- No plugin runtime execution.
- No personal-data skill enablement.
- No dependency installation.
- No provider or connector calls for skill metadata checks.
- No ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger bypass.

## Validation Results

| Check | Result | Evidence |
|---|---|---|
| Full test suite | Passed | `make test` -> 1205 passed, 1 skipped |
| Startup policy validation | Passed | `make policy-check` -> startup policy ok |
| Capability manifest validation | Passed | `make policy-check` capability validation exit 0 |
| Docs validation | Passed | tracker/release/prompt docs tests passed with 11 passed |
| Command registry validation | Passed | `python smart_agent.py commands validate` -> 428 commands ok |
| Native skill manifest validation | Passed | `python smart_agent.py skills validate` -> 3 valid manifests |
| Lockfile verification | Requires setup, expected | `skills lock verify` reports missing reviewed `native_skills.lock` records and writes nothing |
| Skill conflict detection | Passed | `skills conflicts` -> 0 conflicts |
| Native skill dogfood suites | Passed | `native_skills_core` 3/3 passed; `native_skill_vetting` 3/3 passed in redacted session `sess_20260525T110516Z_c5539999` |
| Native skill eval suite | Passed | `eval run --native-skills --json` -> native_skills 3 pass, personal-data evals skipped by default |
| Skill docs check | Passed | `skills docs-check` -> catalog current, 0 missing docs |

## Safety Findings

- Skill roots are metadata-only and deterministic.
- Experimental/unreviewed roots cannot silently override trusted native skills.
- Manifest validation requires risk, trust, memory, audit, approval, and capability metadata.
- Dependency gating is detection-only and does not install packages, execute scripts, call providers, call connectors, or scan personal files.
- Provenance and trust metadata exists for all three built-in native skill manifests.
- Lockfile verification exists and is intentionally read-only; a reviewed real `native_skills.lock` remains future work.
- Static vetting detects scripts, shell commands, secrets, network calls, filesystem escapes, browser/session access, personal-data requests, and approval-bypass language.
- Profiles are advisory visibility filters and do not grant capabilities or execution rights.
- Compatibility, conflict, harness, dogfood, and docs generation are metadata-only.
- No external skill execution occurs by default.
- No personal-data skill is enabled by default.
- All native skill commands are present in the command registry.

## Blockers And Limitations

- A reviewed real `native_skills.lock` has not been committed. Verification reports `requires_setup`, which is acceptable for this gate because the lockfile write/pinning flow is deferred.
- External marketplace skills are not trusted, installed, imported, enabled, or executed.
- Manual live QA for future external/native skill intake remains required before any user-ready claim.
- The native skill system is safe to rely on for metadata review, discovery, vetting, diagnostics, docs, and release-gate evidence. It is not a permission to run unreviewed external skills.

## Release Decision

Decision: pass for metadata-only native skill system v1.

Readiness: `Hardened` for the control-plane scaffolding and release-gate evidence. Not `User-Ready` for installing or executing third-party skills.
