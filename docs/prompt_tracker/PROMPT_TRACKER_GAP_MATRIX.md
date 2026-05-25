# Prompt Tracker Gap Matrix

Last updated: 2026-05-23

| Area | Before PTM Batch | Current State | Remaining Gap |
|---|---|---|---|
| Ledger schema | Basic records and imported PTM rows existed. | Records include status, dependencies, evidence fields, command registry status, and pack metadata in split prompt files. | Markdown ledger remains manually editable; richer machine storage could be added later. |
| Queue schema | Queue listed prompts but PTM prompts stayed queued. | Queue rows are updated by status commands and PTM-01 through PTM-10 are closed with evidence. | Queue ordering is still document-based. |
| Prompt pack parser | Worked for simple packs. | Preserves delimiter examples inside prompt bodies. | Deeply malformed packs still require manual review. |
| Prompt status CLI | Basic list/next/show/mark/audit/missing existed. | Added search, evidence, missed, superseded, stale, recover-plan, and reconcile. | Status commands are intentionally conservative and do not execute prompts. |
| Evidence audit | Basic heuristic audit existed. | Dedicated evidence classifier and prompt-specific audit added. | Evidence remains heuristic and should be periodically reviewed. |
| PROJECT_STATE integration | Active/next prompt fields existed. | Additional batch, audit, blockers, and resume fields supported. | Human-readable state updates still require discipline after each run. |
| FEATURE_MATURITY integration | Prompt fields existed in principle. | Prompt tracker maturity fields are documented and used for this batch. | Future feature rows need ongoing prompt evidence updates. |
| PromptOps Workbench | Import, next, status, review, run-next, autopilot existed. | Runner remains disabled by default; safety gates verified. | Actual Codex runner integration remains intentionally gated. |
| Dogfood and eval | General dogfood/eval existed. | Prompt tracker dogfood suites and prompt_tracker eval category added. | Live dogfood must still be run manually. |
| Recovery | No dedicated missed/superseded/stale/orphan commands. | Conservative recovery plan and reconcile commands added. | Recovery does not auto-fix state by design. |
| Release gate | No PTM-specific release gate artifact. | PTM release gate and maturity review artifacts added. | Full suite must be rerun after future large queue changes. |
