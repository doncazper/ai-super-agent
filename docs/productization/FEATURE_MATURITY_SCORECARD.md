# Feature Maturity Scorecard

Prompt ID: `MATURITY-AUDIT-01`
Date: 2026-05-25

| Area | Feature | Status | Maturity Level | Readiness Score | Evidence | Tests | Docs | Live Validation | Command Coverage | Risks | Next Action |
|---|---|---|---:|---:|---|---|---|---|---|---|---|
| Core Runtime | CLI and startup guard | Implemented | 5 | 82 | `smart_agent.py`, `scripts/agent`, startup/version guard docs | Present | Present | Partial local only | Broad | Runtime setup drift | Clean-machine smoke |
| Core Runtime | Router and orchestration | Implemented | 4 | 74 | `agent/`, router docs/tests | Present | Present | Not verified | Present | Wrong tool routing | Manual route QA |
| Safety | ToolBroker and PolicyEngine | Hardened local pattern | 5 | 86 | safety modules, capability manifest, tests | Present | Present | Local only | Present | Direct bypass regressions | Static bypass scan |
| Safety | ApprovalManager and Action Center | Hardened local pattern | 5 | 82 | approval/action tests and docs | Present | Present | Local only | Present | Approval reuse errors | Manual CRITICAL denial QA |
| Safety | AuditLogger and secret redaction | Implemented | 5 | 80 | audit/redaction tests, docs | Present | Present | Local only | Present | Raw logs or secrets | Session/log redaction review |
| Config | Python and `.env` setup | Tested | 4 | 75 | `.env.example`, setup docs, wrapper script | Present | Present | Partial | Present | User setup confusion | Fresh setup run |
| Weather | Provider abstraction and forecasts | Hardened local | 5 | 80 | weather modules, provider docs | Present | Present | Partial or stale | Present | Provider drift | Live weather smoke |
| Web | Search provider registry | Tested local | 4 | 72 | search provider code/docs/tests | Present | Present | Mock mostly | Present | Paid/default provider mistakes | Provider live doctors |
| Web | Safe fetch/extraction | Hardened local | 5 | 79 | fetch/extraction/robots/cache docs/tests | Present | Present | Mock mostly | Present | Prompt injection and robots edge cases | Dogfood safe URLs |
| Web | Source-grounded research | Tested local | 4 | 73 | research/citation docs/tests | Present | Present | Mock mostly | Present | Fabricated citation regressions | Current-source dogfood |
| News | News strategy and manifest | Scaffolded | 2 | 47 | news docs and capability policy | Policy tests only | Present | Not applicable | Planned/stubbed | Docs can outrun runtime | Run provider registry/status prompt |
| Reddit / Forums | Reddit connector and workflows | Tested local | 4 | 68 | Reddit/forum modules/docs/tests | Present | Present | Not verified | Present | API/rate-limit changes | Safe live doctor if configured |
| Reddit / Forums | V2EX and Chinese discovery | Tested/scaffolded | 3 | 60 | V2EX/CN docs/tests | Present | Present | Not verified | Present | Blocked pages/login walls | Public fixture dogfood |
| Language | Multilingual detection/translation | Tested local | 4 | 66 | language modules/tests/docs | Present | Present | Mock model mostly | Present | Translation overclaiming | Manual multilingual fixture run |
| Workspace | File/PDF/document handling | Hardened local | 5 | 78 | workspace guards, PDF docs/tests | Present | Present | Local only | Present | Path traversal/regression | Manual workspace QA |
| Memory | Memory and continuity | Hardened local | 5 | 76 | memory modules/docs/tests | Present | Present | Local only | Present | Personal-data retention | Privacy report QA |
| Personal Connectors | Calendar/contacts/email/messages | Tested gated | 4 | 63 | connector docs/tests, disabled defaults | Present | Present | Mostly not verified | Present | Personal data and sends | Explicit live doctor plan only |
| Workflows | Briefing, prep, triage, follow-up | Tested local | 4 | 70 | workflow modules/docs/tests | Present | Present | Limited | Present | Data-source availability | Manual workflow dogfood |
| Native Skills | Skill roots/manifests/vetting/lock/conflicts/docs | Hardened metadata | 5 | 74 | SKILL-01..10 evidence, tests/docs | Present | Present | Local metadata only | Present | External skill trust | Real lockfile/provenance dry-run |
| PromptOps | Ledger/queue/audit/recovery | Hardened but inconsistent | 5 | 78 | prompt docs, command tests | Present | Present | Local only | Present | Stale tracker rows | Reconciliation pass |
| Commands | Registry and manual QA | Hardened local | 5 | 76 | 484-command validation | Present | Present | Manual QA thin | Strong | Stale command docs | QA sample run |
| Dogfood | Suites/evals/reports/bugs | Tested local | 4 | 72 | `dogfood_suites/`, `eval_cases/`, `reports/`, `bugs/` | Present | Present | Incomplete current evidence | Present | Old report drift | Run all-safe dogfood |
| Runtime | Kernel/services/jobs/workflows | Tested local | 4 | 72 | runtime modules/docs/tests | Present | Present | Local only | Present | Background persistence | Keep background disabled |
| Brain | Provider gateway/router | Tested local | 4 | 74 | brain modules/docs/tests | Present | Present | Limited | Present | Provider fallback drift | Live provider smoke |
| Platform | Capability registry and bridge stubs | Tested scaffold | 4 | 67 | platform modules/docs/tests | Present | Present | Not applicable | Present | Stub mistaken as real | Keep maturity conservative |
| Docs | Agent DNA, cloneability, trackers | Hardened docs | 5 | 80 | README, Agent DNA, tracker docs | Present | Present | Clean clone not verified | Present | Dense tracker drift | Tracker reconciliation and clone dry-run |

