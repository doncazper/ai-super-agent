# Progressive QA Deepening

Command QA deepens in safe layers:

| Cadence | Scope | Execution |
|---|---|---|
| Daily | Tier 0-1 registry/read-only checks | Dry-run planning by default |
| Every few days | Tier 2 mocked provider checks | Manual or future reviewed automation |
| Weekly | Tier 3 disposable workspace checks | Dry-run planning by default, `--sandbox` required for execution |
| Manual | Tier 4-5 live/dry-run checks | Human selected |
| Never automatic | Tier 6-7 HIGH/CRITICAL checks | Human approval only |

Commands:

```bash
python smart_agent.py qa next-batch
python smart_agent.py qa daily --dry-run
python smart_agent.py qa weekly --dry-run
python smart_agent.py qa depth status
```

The progressive layer plans batches and writes reports. It does not start a scheduler, access personal data, run paid providers, or execute HIGH/CRITICAL commands.

