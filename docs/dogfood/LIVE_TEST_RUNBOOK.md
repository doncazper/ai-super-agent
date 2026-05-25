# Live Test Runbook

This runbook defines the repeatable manual validation loop for exercising real features, collecting redacted session evidence, reviewing failures, generating bugs, and feeding the next fixes back into Codex.

## Scope

- Manual daily and weekly validation.
- Session logging, dogfood suites, feedback capture, session review, bug generation, and regression-test follow-up.
- Safe defaults only: no real email/text sending, no calendar/contact writes, and no personal-data reads unless a separate selected-scope approval is explicitly granted.

## Non-Goals

- No hidden background testing.
- No automatic sends or writes.
- No private macOS app database access.
- No personal-data dogfood by default.
- No automatic bug fixing.
- No regression test generation from raw unsanitized logs.

## Daily Safe Smoke

1. Start a redacted session:

   ```bash
   python smart_agent.py session start --name "daily-dogfood"
   ```

2. Run the core suite:

   ```bash
   python smart_agent.py dogfood run core --session
   ```

   Skip live LM Studio commands if `LMSTUDIO_MODEL` is not configured.

3. Run weather if configured:

   ```bash
   python smart_agent.py dogfood run weather --session
   ```

4. Run web if configured:

   ```bash
   python smart_agent.py dogfood run web --session
   ```

5. Run workspace files:

   ```bash
   python smart_agent.py dogfood run workspace_files --session
   ```

6. Run memory:

   ```bash
   python smart_agent.py dogfood run memory --session
   ```

7. Add feedback:

   ```bash
   python smart_agent.py feedback rate --last --score 4
   python smart_agent.py feedback bad --last --reason "clear short reason"
   ```

8. End the session:

   ```bash
   python smart_agent.py session end
   ```

9. Review the session:

   ```bash
   python smart_agent.py session review --last
   ```

10. Generate bugs after reviewing the report:

    ```bash
    python smart_agent.py session review --last --create-bugs
    python smart_agent.py bugs list
    ```

11. Pick the top bug and add a regression test when feasible:

    ```bash
    python smart_agent.py bugs create-regression BUG-0001
    ```

## Weekly Deeper Check

1. Start a weekly session.
2. Run `all_safe`.
3. Run `approvals`.
4. Run `native_skills`.
5. Run `personal_dry_run`.
6. Run `eval run --safe`.
7. Review `docs/FEATURE_MATURITY.md`.
8. Update `docs/FEATURE_ROADMAP.md`, `docs/PROJECT_STATE.md`, and `docs/COMPLETION_REPORT.md` with the evidence.

## Helper Commands

```bash
python smart_agent.py dogfood plan
python smart_agent.py dogfood next
python smart_agent.py dogfood checklist
```

`dogfood next` inspects the latest redacted session metadata and feature maturity notes to suggest the next safe step.

## Safety Rules

- No real email/text sending in dogfood by default.
- No calendar/contact writes in dogfood by default.
- Personal-data dogfood must use dry-run or selected mock fixtures unless explicitly approved.
- Every dogfood session must create a redacted session log.
- Every failure should become feedback or a bug.
- Every bug fix should add a regression test when feasible.

