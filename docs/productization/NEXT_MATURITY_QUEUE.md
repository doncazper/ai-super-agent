# Next Maturity Queue

Prompt ID: `MATURITY-AUDIT-01`
Date: 2026-05-25

## P0 Safety / Security Blockers

No confirmed P0 blocker was verified during this audit. Keep feature expansion paused if a future secret scan, audit review, or policy validation finds one.

## P1 Core Productization Blockers

| task_id | title | area | current maturity | target maturity | why it matters | suggested prompt title | tests required | docs required | risk | approval gate | dependencies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MATURITY-P1-001 | Clean release-candidate boundary | Release | 4 | 6 | The dirty worktree is too large for safe release review | Release Candidate Boundary Cleanup | Full tests, command validation, policy check | Release readiness docs | MEDIUM | Stop before destructive git cleanup | User approval for cleanup/staging |
| MATURITY-P1-002 | Reconcile prompt tracker disagreements | PromptOps | 5 | 6 | Tracker disagreements make prompt sequencing risky | Prompt Tracker Reconciliation Pass | Prompt audit tests, tracker docs tests | Prompt audit, queue, ledger | LOW | None unless deleting files | Current audit |
| MATURITY-P1-003 | Generated artifact hygiene | Repo hygiene | 3 | 5 | Generated junk can hide unsafe files and pollute commits | Generated Artifact Hygiene Pass | Secret scan, full tests if cleanup broad | `.gitignore`, release docs | MEDIUM | Ask before deleting many files | Dirty worktree review |
| MATURITY-P1-004 | Static bypass scan release gate | Safety | 5 | 6 | Direct subprocess/network/personal-data bypass regressions are high impact | Safety Bypass Static Scan Gate | Static scan tests, policy check | Threat model, release checklist | HIGH | Stop on high-risk findings | Safety control plane |
| MATURITY-P1-005 | Current all-safe dogfood evidence | Dogfood | 4 | 6 | Mock tests are not enough for release confidence | All-Safe Dogfood Evidence Pass | Dogfood all-safe, eval safe, session review | Dogfood report, completion report | LOW | None if safe/local | Clean-ish worktree preferred |

## P2 Missing Tests / Docs / Dogfood

| task_id | title | area | current maturity | target maturity | why it matters | suggested prompt title | tests required | docs required | risk | approval gate | dependencies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MATURITY-P2-001 | News provider registry/status commands | News | 2 | 4 | News is currently mostly policy/docs | News Provider Registry Status Commands | Unit/CLI/manifest tests | News provider docs, command registry | LOW | No live API calls | News manifest |
| MATURITY-P2-002 | Brain provider live smoke plan | Brain | 4 | 6 | LM Studio optionality needs real runtime proof | Brain Runtime Live Smoke Runbook | Mock plus optional live doctor | Brain docs, release checklist | LOW/MEDIUM | Skip if runtime not configured | Brain gateway |
| MATURITY-P2-003 | Web provider live doctor matrix | Web | 5 | 6 | Search/fetch providers need opt-in live evidence | Web Provider Live Doctor Matrix | Provider doctors with mocks and safe live skips | Web runbook | LOW/MEDIUM | No paid APIs | Provider config |
| MATURITY-P2-004 | Native skill external intake dry-run | Native Skills | 5 | 6 | Trust/provenance needs real intake proof | Native Skill Intake Dry-Run | Lock/vetting/docs tests | Native skill runbook | MEDIUM | No external execution/install | Native skill lock |
| MATURITY-P2-005 | Platform manifest mapping | Platform | 4 | 5 | Future platform actions must map before execution | Platform Capability Manifest Mapping | Manifest/toolbroker mapping tests | Platform docs | MEDIUM/HIGH future | Stop on real platform action | Platform registry |

## P3 UX / Diagnostics Polish

| task_id | title | area | current maturity | target maturity | why it matters | suggested prompt title | tests required | docs required | risk | approval gate | dependencies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MATURITY-P3-001 | Clean setup diagnostics | Config | 4 | 6 | Users need clearer missing env/runtime guidance | Setup Diagnostics Polish | CLI output tests | README, setup docs | LOW | None | Startup ergonomics |
| MATURITY-P3-002 | Command QA sampling | Commands | 5 | 6 | Registry coverage is not the same as manual UX | Command QA Sample Pass | Command smoke matrix | QA runbook | LOW | None | Command registry |
| MATURITY-P3-003 | Tracker dashboard refresh | Trackers | 5 | 6 | Dense trackers need a short current view | Tracker Dashboard Refresh | Docs test | Dashboard/index | LOW | None | This audit |

## P4 Future Enhancements

| task_id | title | area | current maturity | target maturity | why it matters | suggested prompt title | tests required | docs required | risk | approval gate | dependencies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MATURITY-P4-001 | Clean clone dry-run | Cloneability | 5 | 6 | Clone blueprint needs proof | Clean Clone Validation Pass | Fresh clone tests | Clone docs | LOW | None | Release branch |
| MATURITY-P4-002 | Manual validation dashboard | Productization | 2 | 4 | Validation evidence needs a single UX | Manual Validation Dashboard | Docs/CLI tests | Productization docs | LOW | None | Dogfood evidence |
| MATURITY-P4-003 | Provider status summary | Providers | 3 | 5 | Users need one safe setup view | Provider Status Summary | CLI tests | README/provider docs | LOW | None | Existing doctors |

