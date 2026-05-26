# Disposable QA Workspace

The command QA sandbox uses a repo-local disposable workspace for deeper command tests that need fixture files or bounded writes.

Default path:

```bash
reports/qa/workspaces/current
```

Supported commands:

```bash
python smart_agent.py qa sandbox init
python smart_agent.py qa sandbox status
python smart_agent.py qa sandbox clean
python smart_agent.py qa commands run --tier 3 --sandbox
```

Rules:

- The workspace must stay under `reports/qa/workspaces/`.
- Fixture data is synthetic and non-personal.
- Cleanup refuses to delete outside the disposable workspace path.
- Tier 3 command runs require `--sandbox`.
- Placeholder examples, personal-data commands, HIGH/CRITICAL commands, sends, and destructive actions remain blocked.
- Generated reports and workspaces are ignored by git except `.gitkeep`.

