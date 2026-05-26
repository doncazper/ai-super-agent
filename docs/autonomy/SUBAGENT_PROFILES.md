# Subagent Profiles

Status: HERMES-07 profile catalog.

| Profile | Purpose | Default tools | Risk ceiling | Network | Writes | Personal data | Status |
|---|---|---|---|---:|---:|---:|---|
| researcher | Draft public-source research plans and summaries | none unless `SUBAGENT_NETWORK_ENABLED=true` | LOW/MEDIUM | config-gated | no | no | stubbed |
| coder | Draft implementation plans and patch proposals | read/diff metadata | MEDIUM | no | no | no | stubbed |
| tester | Propose test plans and safe test commands | test metadata | LOW | no | no | no | stubbed |
| security_reviewer | Review policy, audit, approval, and secret-handling evidence | read/command metadata | MEDIUM | no | no | no | stubbed |
| docs_reviewer | Review docs consistency and propose doc-only updates | read/docs metadata | LOW | no | no | no | stubbed |
| planner | Break work into safe prompts and milestones | prompt metadata | LOW | no | no | no | stubbed |
| locked_down | No-tool reasoning and policy checks | none | SAFE | no | no | no | stubbed |
| experimental | Placeholder for future reviewed experiments | none | SAFE | no | no | no | disabled |

Profile visibility does not grant execution permission. These records are advisory safety metadata until a future prompt adds a real subagent runner through ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger.

