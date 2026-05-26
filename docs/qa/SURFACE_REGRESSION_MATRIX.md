# Surface Regression Matrix

The surface regression matrix is the compact view of `agent.qa.surface_lanes.SURFACE_LANES`.

| Surface | Default behavior | Risk | Live provider status | Notes |
|---|---|---|---|---|
| CLI core | dry-run/read-only smoke | SAFE | no | Doctor and command registry health. |
| Command registry | dry-run/read-only smoke | SAFE | no | Registry and command test matrix validation. |
| PromptOps | dry-run/read-only smoke | SAFE | no | Queue/ledger/audit state, no prompt execution. |
| Runtime/canonical state | dry-run/read-only smoke | SAFE | no | Canonical state and durable record validation. |
| Agent Gateway / Runtime Kernel | dry-run/read-only smoke | SAFE | no | Boundary/status metadata only. |
| Action Center/approvals | read-only list/status | LOW | no | No approval consumption or action execution. |
| ToolBroker/policy/audit | validation/status | LOW | no | Policy/capability checks and audit metadata. |
| Web/research | metadata/default-safe | MEDIUM | opt-in only | Live web/provider checks are excluded by default. |
| Reddit/forums | metadata/default-safe | MEDIUM | opt-in only | Forum providers remain source-policy gated. |
| Weather | metadata/default-safe | LOW | opt-in only | Live provider smoke is optional. |
| News planned/stubbed | registry/docs only | LOW | no | Runtime news remains planned/stubbed. |
| Brain providers | status/metadata | LOW | no by default | No generation/model download. |
| Native skills | inspection metadata | LOW | no | No external skill execution. |
| Secrets | status/metadata | SAFE | no | No real secret values printed. |
| QA sandbox | read-only/dashboard | SAFE | no | Safe-tier execution remains explicit elsewhere. |
| Media planned/stubbed | metadata/dry-run | LOW | no | No generation/provider call. |
| Platform/app bridge | status/matrix | SAFE | no | No native bridge action. |
| Channels/Telegram/mobile | status metadata | LOW | no | No bot/channel connection or send/read. |
| Memory | status/metadata | LOW | no | No personal-data inclusion by default. |
| Backup/restore | list/metadata | MEDIUM | no | Restore execution remains excluded and approval-gated. |

