# Full Feature Status and Maturity Audit

Prompt ID: `MATURITY-AUDIT-01`
Date: 2026-05-25
Scope: evidence-based review of major feature areas, command groups, support systems, platform tracks, and prompt tracker state.

## Executive Summary

The repo is broad and increasingly well-structured, but it should be treated as a large local-tested productization branch, not a release candidate. The strongest evidence is in the safety control plane, command registry, prompt tracking infrastructure, weather/web scaffolds, workspace/memory foundations, Action Center style approval flows, and metadata-only native skill/autonomy/platform tracks.

The largest maturity gap is not missing design. It is release boundary quality: a large dirty worktree, incomplete live/manual validation, several prompt tracker disagreements, generated artifact hygiene, and many mock-only provider tests. No P0 security blocker was verified during this audit, but several P1 productization blockers remain before feature expansion should accelerate.

## Evidence Caveats

- Full live provider validation was not run.
- Paid APIs were not used.
- No queued prompts were auto-run.
- No runtime feature behavior was added.
- Several areas are documented or scaffolded only. They are called out as such.
- Tests and dogfood evidence are mostly local, fixture, or mock based unless stated otherwise.

## Maturity Table By Major Area

| Area | Status | Maturity | Score | Evidence | Main Gap |
|---|---|---:|---:|---|---|
| A. Core Runtime | Implemented and hardened locally | 5 Hardened | 82 | `smart_agent.py`, `agent/`, CLI tests, startup guard docs, command registry | More live LM Studio and interactive-mode manual smoke evidence |
| B. Safety Control Plane | Strong local pattern | 5 Hardened | 86 | ToolBroker/PolicyEngine/ApprovalManager/AuditLogger tests, `config/capabilities.yaml`, `make policy-check` | More static bypass checks and release-gate evidence |
| C. Config and Startup Ergonomics | Tested local setup | 4 Tested | 75 | `scripts/agent`, `.env.example`, startup tests, doctor/setup docs | Manual clean-machine setup proof |
| D. Weather | Implemented and tested | 5 Hardened | 80 | provider abstraction, command docs, tests, risk docs | Live provider matrix and long-term rate-limit dogfood |
| E. Web / Internet Access | Broad local-tested framework | 5 Hardened | 79 | web acquisition, search providers, fetch, robots, citations, cache, dogfood/evals | Live provider validation and source-grounded manual QA |
| F. News | Manifest and roadmap only | 2 Scaffolded | 47 | news docs, capability manifest entries, provider policy docs | Runtime provider registry/status commands not implemented |
| G. Reddit / Forums | Mock/local tested | 4 Tested | 68 | Reddit policy/doctor/connectors, forum registry, V2EX/CN discovery docs/tests | Live Reddit/V2EX validation and retention dogfood |
| H. Workspace Files / Documents | Hardened local foundation | 5 Hardened | 78 | workspace guards, PDF skill, path tests, command registry | More manual file QA and generated artifact hygiene |
| I. Memory | Hardened local foundation | 5 Hardened | 76 | memory commands, privacy center, continuity tests | Live continuity UX and deletion/export manual QA |
| J. Personal Connectors | Disabled-by-default and mostly mock/local | 4 Tested | 63 | calendar/contacts/email/messages docs/tests/action gates | Live validation requires explicit setup and approvals |
| K. Workflows | Implemented local workflows | 4 Tested | 70 | daily briefing, meeting prep/follow-up, triage, task extraction, self-improvement | End-to-end manual dogfood across real data remains thin |
| L. Native Skills | Hardened metadata system | 5 Hardened | 74 | SKILL-01 through SKILL-10 evidence, lock/vetting/conflict/docs tests | External skill intake and lockfile provenance live practice |
| M. PromptOps | Hardened but inconsistent trackers | 5 Hardened | 78 | ledger/queue/audit commands and tests | Stale rows and missing queued prompt files need reconciliation |
| N. Command Registry / Manual QA | Validates cleanly | 5 Hardened | 76 | `commands validate` reports 484 valid commands | Manual QA coverage is not as strong as registry completeness |
| O. Dogfood / Session / Bugs / Regression | Good scaffold, uneven live evidence | 4 Tested | 72 | dogfood suites, eval cases, reports, bugs | Recent all-safe dogfood session and bug burn-down needed |
| P. Runtime Orchestration | Implemented local metadata runtime | 4 Tested | 72 | runtime kernel, service registry, flags, event/job/workflow docs/tests | Long-running/background execution deliberately deferred |
| Q. Brain Runtime Independence | Partially optional, tested locally | 4 Tested | 74 | Brain gateway/provider docs/tests, BRAIN-01 through BRAIN-11 evidence | More real provider smoke tests and default provider migration proof |
| R. Platform / Cross-Platform | Scaffolded and tested as stubs | 4 Tested | 67 | capability registry, bridge stubs, app bridge contract, platform commands | No real macOS/iOS/Windows bridge behavior by design |
| S. Docs / Cloneability | Strong docs foundation | 5 Hardened | 80 | Agent DNA, clone blueprint, tracker dashboard/index, docs validation tests | Clean clone dry-run and tracker compaction discipline |

## Actually Built

- CLI command registry with validation and extensive metadata.
- Safety control plane with brokered capability execution, risk labels, approvals, audit logging, and secret redaction patterns.
- Weather, web, workspace, memory, workflows, Action Center, dogfood, eval, prompt tracking, native skill, safe autonomy, brain runtime, and platform stub foundations.
- Many provider/connectors are local-tested with mocks or status-only doctors.

## Planned Or Stubbed Only

- News runtime providers and news commands beyond capability/policy planning.
- Real platform bridges for macOS, iOS companion, Windows, and app frontends.
- Many personal-data connector live paths.
- External native skill intake and execution.
- Background autonomy, remote channels, browser automation beyond policy/stub boundaries.

## Experimental

- Brain provider fallback and model routing.
- Safe autonomy proposal systems.
- Runtime orchestration metadata/job/workflow scaffolds.
- Cross-language forum research and Chinese forum discovery.
- Provider selection and local web cache/index reuse.

## Tested

Local targeted tests exist for most built feature families. Command registry validation is currently green with 484 commands. Startup policy and capability manifest validation pass through `make policy-check`.

## Live Validated

Live validation is incomplete. Existing evidence is strongest for local CLI behavior and mock/fixture suites. Provider, Reddit, V2EX, LM Studio, and personal connector live validation must remain conservative until explicit safe doctor or live test runs are recorded.

## User Ready

The safest user-ready surfaces are local read-only/status/doctor and dry-run commands. Features involving external providers, personal data, sends/writes, platform bridges, or autonomy remain gated, stubbed, or setup-dependent.

## Mature Patterns

- ToolBroker + PolicyEngine + ApprovalManager + AuditLogger gating.
- Command registry metadata and validation.
- Prompt tracking with evidence classes, despite current stale rows.
- Disabled-by-default and redacted doctor/status commands.
- Metadata-only stubs before live connector implementation.

## Missing Evidence

- Clean release-candidate branch with generated junk removed.
- Recent full manual QA pass across core command groups.
- Recent all-safe dogfood run with session evidence.
- Live provider validation matrix.
- Prompt tracker reconciliation for stale queue/audit entries.
- Clean clone or fresh setup run.

## Release Blockers

| Priority | Blocker | Evidence | Recommended Action |
|---|---|---|---|
| P1 | Dirty working tree is too large for release review | `git status -sb` shows many modified and untracked files | Create a release-candidate branch, stage intentionally, remove/generated-ignore junk with approval |
| P1 | Prompt tracker disagreement | `PROMPT_QUEUE`, `PROMPT_LEDGER`, `PROMPT_AUDIT`, and prompt files disagree on SKILL/news/Reddit states | Run prompt tracker reconciliation pass |
| P1 | Live/manual validation gap | Trackers show mock/local tests dominate provider and connector evidence | Run all-safe dogfood and provider-specific opt-in live doctors |
| P2 | Generated artifact hygiene | `__pycache__`, `.DS_Store`, and report artifacts appear in working tree | Confirm `.gitignore` and clean generated files with approval |
| P2 | Some maturity claims are broad | Feature maturity is dense and includes many complete local scaffolds | Keep maturity conservative and link evidence |

## Top Maturity Gaps

1. Clean release boundary.
2. Prompt tracker reconciliation.
3. Live/manual validation matrix.
4. Static safety bypass scan.
5. Generated artifact hygiene.
6. News runtime not implemented.
7. Provider live status commands incomplete for news.
8. Brain gateway live provider proof.
9. Native skill external intake proof.
10. Platform bridge remains stubs only.
11. Personal connectors remain setup-gated and mostly mock/local.
12. Dogfood reports need current run evidence.
13. Command manual QA coverage is thinner than registry coverage.
14. Release checklist needs a fresh pass after cleanup.
15. Cloneability needs a clean clone dry-run.

## Recommended Next Actions

1. Run prompt tracker reconciliation focused on stale queue/audit rows.
2. Run release-boundary cleanup with explicit staging and generated-file hygiene.
3. Run all-safe dogfood with session evidence.
4. Run `news-provider-registry-status-commands` as the next feature prompt only after tracker cleanup or as a small planned/stubbed milestone.
5. Run provider live doctor smoke tests only where configured and safe.

