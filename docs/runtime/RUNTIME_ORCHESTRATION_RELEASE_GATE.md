# Runtime Orchestration Release Gate

## Required Checks

- Full test suite passes.
- Startup policy validation passes.
- Capability manifest validation passes.
- Command registry validation passes.
- Runtime targeted tests pass.
- Runtime status and doctor work without `LMSTUDIO_MODEL`.
- Runtime import remains lightweight.
- No runtime command executes tools directly.
- No personal-data tool is enabled by default.
- HIGH actions still require approval.
- CRITICAL actions still require explicit per-action approval with no reuse.
- Event bus cannot approve or change policy.
- Workflow runner cannot bypass ToolBroker.
- Job queue cannot auto-run CRITICAL jobs.
- Scheduler blocks CRITICAL and hidden background persistence.
- Frontend bridge cannot bypass ApprovalManager.

## Current Result

Passed on 2026-05-23.

- Full suite: 750 passed, 2 skipped.
- Safe eval: 21 passed, 0 failed, 8 skipped.
- Startup policy validation: ok.
- Capability manifest validation: ok.
- Command registry validation: ok, 274 commands.
- Prompt pack validation: ok, 10 ORCH prompts.
- Native skills validation: ok.
- Runtime status/doctor smoke: no LM Studio checks, no tool execution, no personal-data access, no background persistence.
- Runtime prompt audit: zero active prompts, ORCH-01 through ORCH-10 complete with evidence.
