# Feature And Maturity Reconciliation

Last reconciled: 2026-05-25

## Summary

Feature maturity should stay conservative. Many tracks are implemented and mock/local-tested, but live validation and manual QA are still thin.

## Major Area Status

| Area | Reconciled Status | Maturity Note |
|---|---|---|
| Core Runtime | implemented/tested | CLI/runtime exists; provider independence is partial and LM Studio remains the live baseline. |
| Safety Control Plane | hardened local pattern | ToolBroker, PolicyEngine, ApprovalManager, AuditLogger, capability manifest, denial tests, and policy checks exist. Continue guarding approval reuse and direct-tool bypass. |
| Command Registry | hardened metadata pattern | `commands validate` passes with 522 commands. Manual QA coverage remains uneven. |
| PromptOps / Prompt Tracker | tested, needs hygiene | Prompt audit passes; stale imported rows were reconciled. Dense trackers still need periodic archive/index maintenance. |
| Command QA Sandbox | hardened local/mock | Safe-tier QA and frontend/backend boundary exist; no HIGH/CRITICAL auto-run. Needs more manual/live command QA. |
| Weather | tested with some live/local evidence | Provider abstractions and commands exist. Live validation must remain provider/config-specific. |
| Web / Internet Access | implemented/tested with policy | Free-first acquisition, search/fetch/citations exist. Live provider validation remains opt-in. |
| News | specified/scaffolded | Roadmap, manifest, and provider policy exist; provider runtime is documented/planned only. |
| Reddit / Forums | implemented/tested with mocks/fixtures | API connector/search/thread/summarization/retention/multilingual/V2EX/forum discovery exist; live validation remains limited. |
| Workspace Files / Documents | implemented/tested | Workspace paths and trust labels exist; broad filesystem/personal-data access remains gated/forbidden. |
| Memory / Continuity | implemented/tested locally | Redaction and no-default personal writes remain important; live/user validation is limited. |
| Personal Connectors | mixed, gated | Read/draft/write tracks exist in places, but personal tools remain disabled by default and sends/writes require explicit gates. |
| Workflows | implemented, cautious | Daily/meeting/lead/task workflows exist with draft/approval boundaries. Manual dogfood remains needed. |
| Native Skills | completed/hardened local | Native skill hardening pack completed; no external skill execution/installation by default. |
| Runtime Orchestration | implemented/tested | Scheduler/job/event abstractions exist, with background/risky execution gated. |
| Brain Runtime Independence | implemented/scaffolded | Provider interface and alternate providers exist, but LM Studio remains compatibility baseline; alternate providers are mostly disabled/stub/mock. |
| Hermes Safe Autonomy | specified/scaffolded/tested | Safe autonomy groundwork exists; high-risk autonomy remains forbidden/deferred. |
| Cross-platform/App Bridge | scaffolded/tested | Platform registry/stubs/API contracts exist; no real native OS behavior. |
| Secrets/API Key Management | needs_review | Prompt pack exists but has not been imported/run; older secret doctor exists. |
| Creative Media Generation | needs_review | Prompt pack exists but has not been imported/run; media generation providers are not enabled. |
| QA Frontend/Backend Boundary | implemented/tested | QA service/API boundary exists; no GUI/server/background runtime. |

## Corrections

- No feature was upgraded to live-validated or user-ready in this pass.
- News, platform native behavior, creative media, secrets pack work, and real app bridge behavior remain documented/planned/stubbed unless code/tests prove otherwise.
- Mock-only and fixture-only tests remain labeled as mock/local evidence, not live validation.
