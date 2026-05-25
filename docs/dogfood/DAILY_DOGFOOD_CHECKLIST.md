# Daily Dogfood Checklist

Use this checklist for the normal daily safe smoke. Every run should create a session log, capture feedback, review failures, and turn confirmed problems into bugs.

## Checklist

- [ ] Start session log:

  ```bash
  python smart_agent.py session start --name "daily-dogfood"
  ```

- [ ] Run core suite:

  ```bash
  python smart_agent.py dogfood run core --session
  ```

- [ ] Run weather suite if configured:

  ```bash
  python smart_agent.py dogfood run weather --session
  ```

- [ ] Run web suite if configured:

  ```bash
  python smart_agent.py dogfood run web --session
  ```

- [ ] Run workspace suite:

  ```bash
  python smart_agent.py dogfood run workspace_files --session
  ```

- [ ] Run memory suite:

  ```bash
  python smart_agent.py dogfood run memory --session
  ```

- [ ] Add feedback:

  ```bash
  python smart_agent.py feedback rate --last --score 4
  ```

- [ ] End session:

  ```bash
  python smart_agent.py session end
  ```

- [ ] Review session:

  ```bash
  python smart_agent.py session review --last
  ```

- [ ] Generate bugs after reviewing the redacted report:

  ```bash
  python smart_agent.py session review --last --create-bugs
  ```

- [ ] Pick top bug:

  ```bash
  python smart_agent.py bugs list
  ```

## Failure Rule

Every failed command should get feedback or a bug record before the session is treated as reviewed.

