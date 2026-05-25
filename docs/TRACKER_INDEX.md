# Tracker Index

Last updated: 2026-05-25

This index explains where to look first and which tracker owns each kind of truth. Dense trackers are expected; this file is the map.

## Source-Of-Truth Hierarchy

1. `SPEC.md`: product mission, safety contract, trust/risk model, and non-negotiable system behavior.
2. `docs/SDLC.md`: process rules, release gates, and mini-SDLC requirements.
3. `AGENTS.md`: permanent Codex working rules for this repository.
4. `docs/PROJECT_STATE.md`: current resumable state, active prompt, branch, test result, next action, and latest status.
5. `docs/FEATURE_ROADMAP.md`: planned order and track-level sequencing.
6. `docs/FEATURE_REGISTRY.md`: durable feature status, safety posture, docs, tests, and release-gate evidence.
7. `docs/FEATURE_MATURITY.md`: conservative readiness and maturity assessment.
8. `docs/COMMAND_REGISTRY.md`: durable command catalog and CLI source of truth.
9. `docs/COMMAND_TEST_MATRIX.md`: command-level automated and manual QA evidence.
10. `docs/COMPLETION_REPORT.md`: append-only run evidence and milestone outcomes.

If trackers disagree, report the disagreement and update the smallest relevant source-of-truth record instead of guessing.

## Tracker Map

| Tracker | Purpose | Detail level | Update when | Ownership |
|---|---|---|---|---|
| `docs/TRACKER_DASHBOARD.md` | Short current-state summary | Summary | After major batches or release gates | Manual |
| `docs/TRACKER_INDEX.md` | Map of tracker roles and hierarchy | Summary/index | When tracker files or ownership changes | Manual |
| `docs/TRACKER_MAINTENANCE.md` | How to maintain trackers safely | Process | When tracker workflow changes | Manual |
| `docs/TRACKER_ARCHIVE_POLICY.md` | What can move to archive and how | Process | When archive rules change | Manual |
| `docs/TRACKER_CONSISTENCY_REPORT.md` | Current consistency findings | Mixed report | During release gates and tracker hygiene passes | Mixed |
| `docs/PROJECT_STATE.md` | Current resumable state | Summary plus active details | Every Codex run | Manual |
| `docs/FEATURE_ROADMAP.md` | Work ordering and track sequence | Detailed roadmap | Any roadmap status/order change | Manual |
| `docs/FEATURE_REGISTRY.md` | Feature status and safety posture | Detailed table | Any feature/connector/workflow/policy change | Manual |
| `docs/FEATURE_MATURITY.md` | Readiness, maturity, limitations | Detailed table | Any feature maturity-affecting change | Manual |
| `docs/COMMAND_REGISTRY.md` | Command catalog | Detailed table | Any command add/change/deprecation/removal | Manual with validation |
| `docs/COMMAND_TEST_MATRIX.md` | Command test and manual QA evidence | Detailed table | Any command QA behavior or evidence change | Manual |
| `docs/COMMAND_LEGACY.md` | Legacy command history | Detailed list | Command deprecation/removal | Manual |
| `CHANGELOG.md` | User-visible changes | Detailed chronological list | User-visible feature/docs/process changes | Manual |
| `docs/COMPLETION_REPORT.md` | Run and milestone evidence | Append-heavy detailed log | Every milestone attempt | Manual |
| `docs/RISK_REGISTER.md` | Risk inventory and mitigations | Detailed table | Risk posture changes | Manual |
| `docs/THREAT_MODEL.md` | Threats and mitigations | Detailed list | Threat surface changes | Manual |
| `docs/TEST_PLAN.md` | Test coverage map | Detailed list | Test strategy or coverage changes | Manual |
| `docs/RELEASE_CHECKLIST.md` | Release gate evidence checklist | Detailed checklist | Release gates and major validation passes | Manual |
| `docs/PROMPT_LEDGER.md` | Prompt status ledger | Detailed table | Prompt status changes | Mixed CLI/manual |
| `docs/PROMPT_QUEUE.md` | Current prompt queue/order | Detailed table | Queue/order changes | Mixed CLI/manual |
| `docs/PROMPT_AUDIT.md` | Prompt evidence audit | Summary/report | Major prompt batches and audits | Mixed CLI/manual |
| `docs/release/*` | Release audit, blockers, plans | Detailed release artifacts | Release hardening loops | Manual |

## Summary Views

- Start here for current status: `docs/TRACKER_DASHBOARD.md`.
- Start here for tracker ownership: `docs/TRACKER_INDEX.md`.
- Start here for release state: `docs/release/RELEASE_READINESS_AUDIT.md`.
- Start here for next work: `docs/PROJECT_STATE.md` and `docs/FEATURE_ROADMAP.md`.
- Start here for command QA: `docs/COMMAND_REGISTRY.md` and `docs/COMMAND_TEST_MATRIX.md`.

## Detailed Views

The detailed source-of-truth trackers are intentionally dense:

- `CHANGELOG.md`
- `docs/COMPLETION_REPORT.md`
- `docs/COMMAND_REGISTRY.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_MATURITY.md`
- `docs/PROMPT_LEDGER.md`
- `docs/RISK_REGISTER.md`
- `docs/THREAT_MODEL.md`
- `docs/TEST_PLAN.md`
- `docs/RELEASE_CHECKLIST.md`

Do not broadly rewrite these files for readability. Add anchored edits, summary links, or archive references.

