# Release Hardening Plan

Date: 2026-05-25

Prompt: `RELEASE-HARDENING-LOOP-V2`

## Top 10 Fixes

| Priority | Fix | Expected Files Affected | Risk | Tests Required | Docs Required | Approval Gate |
|---:|---|---|---|---|---|---|
| 1 | Establish a clean release candidate boundary from the large dirty working tree | Git branch/commit organization, source/diff review; generated artifact hygiene now has narrow ignore rules and docs | LOW process risk, HIGH release clarity impact | Full suite, startup policy, manifest, command registry | Release audit/blockers/checklist | Human review before tag/merge |
| 2 | Run full `all_safe --session` dogfood and session review | `reports/sessions/`, `bugs/`, `docs/release/*`, maturity docs | LOW | Dogfood dry-run first, then session review | Completion report, release audit | Stop if P0/P1/P2 bug appears |
| 3 | Add static direct network/subprocess allowlist check | Tests, possibly docs/security scan helper | LOW/MEDIUM | New regression/static test plus full suite | Threat model, risk register, test plan | Stop if a real bypass is found |
| 4 | Keep generated artifact hygiene verified | `.gitignore`, `docs/release/GENERATED_ARTIFACT_HYGIENE.md`, release docs | LOW | `tests/test_release_artifact_hygiene.py`, git ignored-output check | Release audit/checklist | None unless deleting user data |
| 5 | Run opt-in live provider validation batch | Reports/evals/session logs, provider docs | LOW when configured; MEDIUM if network providers are live | Provider-specific safe live smokes only | Completion report, maturity docs | User/provider configuration required |
| 6 | Improve CLI closed-pipe behavior for command listing | `smart_agent.py` or `agent/ui/cli_commands.py`, tests | LOW | CLI subprocess regression for piped output if practical | Changelog, command QA notes if behavior changes | None |
| 7 | Reconcile manual QA status for highest-risk commands | `docs/COMMAND_TEST_MATRIX.md`, QA runbook | LOW | Registry validation | Command QA runbook, maturity docs | Approval gates remain documented |
| 8 | Add release readiness score history | `docs/release/*`, completion report | LOW | Docs validation if present | Release docs | None |
| 9 | Expand provider-not-configured setup hint regressions | Provider tests, CLI tests | LOW | Targeted provider tests | README/provider docs as needed | None |
| 10 | Prepare next release gate prompt with exact validation sequence | Prompt queue/ledger, release docs | LOW | Prompt audit | Prompt ledger/queue/project state | Do not auto-run without user request |

## Current Approval Gates

- Do not enable personal-data connectors by default.
- Do not add or exercise send/write actions in this hardening loop.
- Do not run live Reddit, V2EX, Chinese forum, paid provider, or personal-data checks unless explicitly configured and requested.
- Do not install packages or start background services.
- Stop and report if any P0/P1 safety issue appears.

## Recommended Next Prompt

`Continue Release Hardening Loop v2. Pick the highest-priority safe release blocker: establish a clean release candidate boundary and generated artifact hygiene without changing runtime behavior. Run targeted validation, update release docs, and stop at approval gates.`
