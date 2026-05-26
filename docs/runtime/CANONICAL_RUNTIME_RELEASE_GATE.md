# Canonical Runtime Release Gate

Status: complete for CANON-10.
Last updated: 2026-05-26.

## Scope

This release gate validates the Canonical Runtime Gateway Hardening batch:

- CANON-01 canonical runtime state model and source-of-truth hierarchy.
- CANON-02 durable execution record contracts.
- CANON-03 Agent Gateway / Runtime Kernel boundary.
- CANON-04 resume, recovery, and checkpoint model.
- CANON-05 code-mode artifact hashes and self-heal safety lints.
- CANON-06 surface regression lanes.
- CANON-07 backup roundtrip and restore policy lane.
- CANON-08 canonical state dashboard and handoff docs.
- CANON-09 tracker-to-canonical-state migration plan.
- EXTREV-01 external architecture review hardening parity checks.
- CANON-10 release gate and maturity review.

## Non-Goals

- No web server, Fastify gateway, TypeScript gateway, or background service.
- No runtime architecture rewrite or CLI replacement.
- No personal-data tool enablement.
- No send/write enablement.
- No live provider calls, paid APIs, package installs, or model downloads.
- No tracker broad rewrite or automatic tracker overwrite.
- No approval, policy, ToolBroker, or audit bypass.

## Gate Results

| Check | Result | Evidence |
|---|---|---|
| Canonical state model exists and is JSON-serializable | Pass | `agent/runtime/canonical_state.py`, `tests/runtime/test_canonical_runtime_state.py`, `python smart_agent.py runtime canonical-state` |
| Durable execution record contracts exist | Pass | `agent/runtime/execution_records.py`, `tests/runtime/test_execution_records.py`, `python smart_agent.py runtime records validate` |
| Gateway / Kernel boundary is documented and no server starts | Pass | `agent/runtime/gateway_state.py`, `agent/runtime/kernel_contract.py`, `docs/runtime/AGENT_GATEWAY_RUNTIME_KERNEL.md`, `python smart_agent.py runtime gateway-status`, `python smart_agent.py runtime kernel-status` |
| CLI remains first frontend | Pass | Gateway status reports `primary_frontend=cli`; future frontends are metadata-only |
| Frontends/channels cannot bypass safety controls | Pass | Frontend contract says no direct tool execution and no self-approval; future execution remains ToolBroker-only |
| Checkpoints and recovery previews do not auto-resume | Pass | `agent/runtime/recovery.py`, `tests/runtime/test_resume_recovery_checkpoints.py`, `python smart_agent.py runtime recovery-preview` |
| CRITICAL resume requires fresh approval | Pass | Recovery preview reports `critical_resume_requires_fresh_approval=true`; tests cover the rule |
| Artifact hash and safety lint checks exist | Pass | `agent/self_improvement/artifact_hashes.py`, `agent/self_improvement/safety_lints.py`, related tests, `python smart_agent.py improve artifact-hashes` |
| Surface regression lanes exist | Pass | `agent/qa/surface_lanes.py`, `tests/qa/test_surface_regression_lanes.py`, `python smart_agent.py qa surfaces run --dry-run` |
| Backup policy weakening checks exist | Pass | `tests/test_backup_roundtrip_policy.py`, `docs/backup/RESTORE_POLICY_WEAKENING_GUARDS.md`, `python smart_agent.py backup policy-check` |
| Audit receipt gaps documented/planned | Pass with planned follow-up | EXTREV-01 adds planned-only `audit verify-chain` and `audit export-receipt` command registry rows |
| Native skill diagnostics status accurate | Pass | EXTREV-01 documents metadata-only status and avoids claiming external skill execution |
| Source/provider explainability status accurate | Pass | EXTREV-01 documents provider decision and source-grounding coverage as local/mock-first |
| Approval semantics regression status accurate | Pass | EXTREV-01 references existing exact-preview/no-reuse coverage |
| Overclaimed maturity corrected | Pass for this track | Maturity remains conservative: local-tested/hardened scaffolding, not live-validated or broadly user-ready |
| No personal-data tools enabled | Pass | Capability manifest and policy validation required; no prompt in this batch enabled personal-data defaults |
| No sends/writes enabled | Pass | Batch added metadata/read-only/dry-run commands only, except existing brokered backup checks remain gated |
| No package installs, live provider calls, or background services | Pass | No install/live/background commands were run; gateway status reports no server/listener |

## Validation Commands

Executed during CANON-10:

- `./.venv/bin/python smart_agent.py runtime canonical-state`
- `./.venv/bin/python smart_agent.py runtime gateway-status`
- `./.venv/bin/python smart_agent.py runtime records validate`
- `./.venv/bin/python smart_agent.py runtime recovery-preview`
- `./.venv/bin/python smart_agent.py runtime kernel-status`
- `./.venv/bin/python smart_agent.py runtime frontend-contract`
- `./.venv/bin/python smart_agent.py runtime canonical-dashboard`
- `./.venv/bin/python smart_agent.py runtime tracker-conflicts`
- `./.venv/bin/python smart_agent.py backup roundtrip --dry-run`
- `./.venv/bin/python smart_agent.py backup policy-check`
- `./.venv/bin/python smart_agent.py qa surfaces run --dry-run`
- `./.venv/bin/python smart_agent.py improve artifact-hashes`

Diagnostics:

- `runtime ... --json` form is not supported for these commands; text/default JSON output works without the flag.
- `backup restore-check` requires a `backup_id`; no backup id was invented during the release gate.

Final validation:

- Full suite: `1723 passed in 162.19s`.
- Focused canonical runtime release-gate tests: `58 passed in 6.90s`.
- Focused docs/registry/maturity tests: `24 passed in 1.11s`.
- Command registry validation: `status=ok`, `command_count=589`.
- Startup policy and capability manifest validation: passed via `make policy-check`.
- Prompt tracker validation: passed before mark-complete with `active_count=1` for `CANON-10`; `CANON-10` was then marked complete.
- Doctor checks: `./scripts/agent doctor` and `python smart_agent.py doctor` passed.
- Dogfood preview: `dogfood run all_safe --dry-run` passed with 8 skipped dry-run entries.

Full results are recorded in `docs/COMPLETION_REPORT.md`.

## Release Decision

The canonical runtime hardening track is safe to rely on for local metadata, release-gate, tracker, and diagnostic workflows.

It is not a replacement runtime gateway, not a background execution system, not a frontend server, and not live-validated against external providers.
