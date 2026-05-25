# Weekly Release Check

The weekly check is a deeper manual validation pass. It still uses safe defaults and must not perform real personal-data reads, sends, or writes unless a separate explicit approval exists.

## Checklist

- [ ] Start a weekly redacted session:

  ```bash
  python smart_agent.py session start --name "weekly-dogfood"
  ```

- [ ] Run safe cross-feature suite:

  ```bash
  python smart_agent.py dogfood run all_safe --session
  ```

- [ ] Run approval suite:

  ```bash
  python smart_agent.py dogfood run approvals --session
  ```

- [ ] Run native skills suite:

  ```bash
  python smart_agent.py dogfood run native_skills --session
  ```

- [ ] Run personal dry-run suite:

  ```bash
  python smart_agent.py dogfood run personal_dry_run --session
  ```

- [ ] Run safe eval suite:

  ```bash
  python smart_agent.py eval run --safe
  ```

- [ ] End and review the session:

  ```bash
  python smart_agent.py session end
  python smart_agent.py session review --last
  ```

- [ ] Create bug records for confirmed failures:

  ```bash
  python smart_agent.py session review --last --create-bugs
  ```

- [ ] Review and update maturity/roadmap docs:

  ```bash
  python smart_agent.py files read docs/FEATURE_MATURITY.md
  python smart_agent.py files read docs/FEATURE_ROADMAP.md
  ```

## Release Gate Notes

- Personal-data dogfood remains dry-run or fixture-only by default.
- No real email/text sends are part of the weekly check.
- No calendar/contact writes are part of the weekly check.
- Bugs should get regression-test scaffolds when feasible before being marked fixed.

