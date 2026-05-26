# Self-Healing Patch Loop

The command QA self-heal loop is intentionally conservative. It converts redacted bug evidence into a patch plan and can write a self-heal run report, but v1 does not commit, push, install packages, weaken policy, or apply broad refactors.

Commands:

```bash
python smart_agent.py qa self-heal plan
python smart_agent.py qa self-heal plan --bug BUG-0001
python smart_agent.py qa self-heal run --safe-only --bug BUG-0001
python smart_agent.py qa self-heal report --last
```

Patch plans include:

- `patch_id`
- `bug_id`
- `severity`
- `allowed_to_patch`
- `reason`
- `branch_name`
- `files_expected`
- `tests_required`
- `docs_required`
- `risk`
- `rollback_plan`
- `human_review_required`

Safety gates:

- P0/P1 issues require human review.
- Broad refactors, policy changes, approval/audit bypasses, and package installs are blocked.
- A linked regression test under `tests/` is required before any future patch attempt.
- No commit or push is performed.
- Reports are written under `reports/qa/` and are ignored by git.

