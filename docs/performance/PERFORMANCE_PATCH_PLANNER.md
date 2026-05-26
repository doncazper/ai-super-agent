# Performance Patch Planner

`PERF-09` adds metadata-only patch planning for optimization recommendations.

## Command

```bash
python smart_agent.py perf patch-plan
python smart_agent.py perf patch-plan --recommendation <recommendation_id>
```

The planner reads the latest redacted recommendation report and creates patch-plan records. It never applies patches.

## Patch Plan Fields

- patch id
- recommendation id
- allowed to patch
- reason
- risk level
- expected files
- expected behavior change
- tests required
- docs required
- rollback plan
- human review required
- self-heal compatible
- status

## Safety Rules

Safe-only default:

- broad refactors are blocked
- policy, approval, audit, ToolBroker, PermissionManager, and security-control changes require human review
- package installs are forbidden
- commits and pushes are forbidden
- live provider calls are forbidden
- patch application is not implemented in this command

Even when a plan is marked `allowed_to_patch=true`, this command still records `applied_patches=0`.
