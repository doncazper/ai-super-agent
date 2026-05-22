# Master Plan

Build the agent in locked milestones. M0 proves the local model loop and brokered safe tool execution. M1 and M2 harden the safety and runtime planes before any broader tools. Personal data and send/write actions remain locked behind later approval gates.

## Sequence

1. M0 Minimal Working Skeleton
2. M1 Safety Control Plane
3. M2 Core Runtime
4. M3 Low-Risk Project Tools
5. M4 Web Tools
6. M5 Memory
7. M6 Read-Only Personal Modules
8. M7 Assistant Workflows
9. M8 Approved Write Actions
10. M9 Controlled Self-Improvement
11. M10 UX and Packaging
12. M11 Final Validation

## Gate Policy

- M6 requires explicit approval because it introduces personal-data reads.
- M8 requires explicit approval because it introduces critical write/send actions.
- M9 requires M1-M5 completion and approval because it lets the agent edit its own codebase.
