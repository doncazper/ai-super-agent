# Milestone Queue

| Milestone | Status | Prerequisites | Approval Requirements | Test Requirements | Last Update |
|---|---|---|---|---|---|
| M0 Minimal Working Skeleton | complete | Governance docs created | None | M0 unit tests passed: 6 tests | 2026-05-22 |
| M1 Safety Control Plane | complete | M0 complete | None | Policy, approval, audit, redaction tests passed | 2026-05-22 |
| M2 Core Runtime | complete | M1 complete | None | Routing, debug, malformed tool-call tests passed | 2026-05-22 |
| M3 Low-Risk Project Tools | complete | M2 complete | Delete/commit approvals enforced and denied by default without user approval | Filesystem/git/test-runner tests passed | 2026-05-22 |
| M4 Web Tools | complete | M3 complete | Search provider not configured; tool returns clear error | Web fetch/search and injection tests passed | 2026-05-22 |
| M5 Memory | complete | M4 complete | Personal-data memory approval enforced and denied by default without user approval | Memory and deletion tests passed | 2026-05-22 |
| M6 Read-Only Personal Modules | complete | M5 complete | Implemented as disabled-by-default selected-scope interfaces only | Personal-data selected-scope tests passed | 2026-05-22 |
| M7 Assistant Workflows | complete | M6 complete | Personal-data workflow steps remain approval-gated | Workflow permission/audit tests passed | 2026-05-22 |
| M8 Approved Write Actions | complete | M7 complete | Implemented disabled-by-default with per-action approval and preflight summaries | Write/send approval tests passed | 2026-05-22 |
| M9 Controlled Self-Improvement | complete | M1-M5 complete, M8 not required | Implemented branch/diff/test boundaries and approval-gated commit | Self-improvement safety tests passed | 2026-05-22 |
| M10 UX and Packaging | complete | M8 or approved subset complete | None beyond included tools | CLI/config/audit/memory/permission tests passed | 2026-05-22 |
| M11 Final Validation | complete | All selected milestones complete | Release approval still required before real-world use | Full release-gate tests passed | 2026-05-22 |
