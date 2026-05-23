# Self-Improvement Overnight Runbook

This runbook defines the safe-mode process for a long unattended Codex run. It is a planning and review process, not permission to create background autonomy.

## Purpose

Use overnight time for low-risk project improvement work: tests, docs, diagnostics, evals, maturity tracking, and tiny behavior-preserving refactors. The run must stop at approval, policy, personal-data, package-install, network, persistence, and ambiguity gates.

## Allowed Overnight Work

- Add tests for existing behavior.
- Fix failing tests after one bounded diagnosis/fix attempt.
- Improve docs, setup instructions, command registry entries, and runbooks.
- Improve diagnostics, doctor output, eval reports, and scorecards.
- Improve feature registry, feature maturity tracking, prompt ledger, and project state accuracy.
- Refactor low-risk code without behavior changes.
- Add mocks and fixtures.
- Improve type hints.
- Improve error messages.
- Improve README/setup docs.
- Improve doctor/eval/reporting commands.

## Forbidden Overnight Work

- No personal-data connector implementation.
- No email or text sending.
- No calendar or contact writes.
- No policy weakening.
- No approval bypass.
- No audit disabling.
- No package installs.
- No external scripts.
- No Full Disk Access.
- No persistence, daemons, LaunchAgents, cron jobs, login items, or background agents.
- No commits without approval.
- No network unless explicitly required by an existing safe test.
- No changes to secrets handling except stricter redaction.

## Recommended Sandbox

- Codex sandbox: `workspace-write`.
- Do not use full filesystem access.
- Do not bypass approvals for dangerous commands.
- Do not grant additional connectors or personal-data access.
- Do not run prompt packs all at once.

## Branch Naming

Use:

```text
agent/overnight/YYYY-MM-DD
```

The branch name is documentation guidance for a user-approved overnight run. Current controlled self-improvement code still enforces `codex/` branches for regular implementation prompts.

## Loop Behavior

1. Read `SPEC.md`, `docs/SDLC.md`, `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/FEATURE_MATURITY.md`, `docs/FEATURE_ROADMAP.md`, `docs/COMPLETION_REPORT.md`, and `docs/PROMPT_QUEUE.md`.
2. Run `python smart_agent.py improve overnight-plan`.
3. Choose the safest open candidate from docs/tests/hardening/evals/diagnostics/tracking work.
4. Implement one small change.
5. Run targeted tests.
6. Update docs and tracking files.
7. Repeat only while all gates remain green and the next item is still low-risk.
8. Write a report under `reports/overnight/`.

## Stop Conditions

Stop immediately if any of these appear:

- Approval is required.
- Personal data is needed.
- Package installation is needed.
- A policy or approval rule change is needed.
- Audit logging would need to be disabled or weakened.
- A network call is unexpectedly needed.
- A hidden persistence/background runner is needed.
- Tests fail after one safe fix attempt.
- Requirements are unclear.
- A HIGH, CRITICAL, or FORBIDDEN capability is involved.

## Morning Review

1. Inspect the overnight report.
2. Inspect `git status` and `git diff`.
3. Run the full test suite.
4. Run startup policy validation.
5. Run capability manifest validation.
6. Check that no personal-data tools were enabled by default.
7. Check that no policy, approval, audit, memory, or ToolBroker restriction was weakened.
8. Approve, reject, or revise the changes.
9. Commit manually or through Action Center only after review.

## Planner Command

```bash
python smart_agent.py improve overnight-plan
python smart_agent.py improve overnight-plan --json
```

The command reads tracking docs through `ToolBroker` and returns a safe candidate list. It does not edit files, run tests, create a schedule, create a branch, or commit.

## Explicitly Blocked Follow-Up

`OVERNIGHT-SAFE-6H` remains blocked until the user explicitly approves a bounded run with this runbook, a time budget, a branch, and review criteria.
