# Command QA Dogfood Runbook

Command QA dogfood suites are fixture/dry-run oriented.

Suites:

```bash
python smart_agent.py dogfood run command_qa_core --session
python smart_agent.py dogfood run command_qa_sandbox --session
python smart_agent.py dogfood run command_qa_self_heal --session
```

Safe manual sequence:

```bash
python smart_agent.py qa commands plan --safe-only
python smart_agent.py qa commands run --tier 0 --limit 1
python smart_agent.py qa next-batch --limit 5
python smart_agent.py qa sandbox init
python smart_agent.py qa commands run --tier 3 --sandbox --group "Command QA" --limit 1
python smart_agent.py qa sandbox clean
python smart_agent.py qa results rank --last
python smart_agent.py qa dashboard
```

Boundaries:

- No HIGH or CRITICAL commands are run automatically.
- No personal-data connectors are used.
- No sends, commits, pushes, or package installs are performed.
- Reports are written under `reports/qa/`.

