# Subagent Isolation

Status: HERMES-07 scaffold.

## Scope

Subagent profiles are static policy records for future researcher, coder, tester, security reviewer, docs reviewer, planner, locked-down, and experimental subagents. This milestone does not launch subagents or run parallel workflows.

## Commands

```bash
python smart_agent.py subagents list
python smart_agent.py subagents show researcher
python smart_agent.py subagents policy
python smart_agent.py subagents dry-run coder "review this diff"
```

The `dry-run` command is mock-only. It reports `tools_executed=[]`, `execution_enabled=false`, `direct_tool_calls_allowed=false`, and `output_trust_level=MODEL_OUTPUT`.

## Isolation Rules

- No subagent has personal-data access by default.
- No subagent can execute CRITICAL actions.
- No subagent can bypass ToolBroker.
- No subagent can bypass PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.
- Write permissions are disabled by default.
- Network access is disabled unless an explicit safe config enables a profile and policy allows it.
- Subagent outputs are `MODEL_OUTPUT`, not trusted instructions.
- Subagents can propose actions, not approve them.
- Execution is stubbed/mock-only in this milestone.

## Future Execution Gate

Before any real subagent launches, the implementation must add:

- ToolBroker-routed tool calls.
- Per-profile capability allowlists.
- PolicyEngine checks for every attempted tool/action.
- ApprovalManager gates for HIGH/CRITICAL actions.
- AuditLogger events for task assignment, tool requests, decisions, outputs, and denials.
- Tests proving personal-data defaults remain disabled, CRITICAL execution is denied, write permissions are explicit, and subagent output cannot alter policy.

## Forbidden In This Track

- Autonomous subagent execution.
- Parallel workflow execution.
- Subagent write permissions by default.
- Direct tool calls.
- Personal-data access.
- Approval bypass.
- Background persistence.
- Package installation or external script execution.

