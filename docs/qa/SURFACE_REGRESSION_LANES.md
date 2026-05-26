# Surface Regression Lanes

CANON-06 defines safe regression lanes for every major user/control surface. The lane registry is metadata-first and dry-run by default. It does not execute commands, run live providers, access personal data, consume approvals, or mutate QA/maturity state.

## Default Rules

- Surface lane inspection is read-only.
- `qa surfaces run --dry-run` previews only and reports `executed_commands=[]`.
- Personal-data and HIGH/CRITICAL commands are excluded by default.
- Live provider checks are opt-in and remain out of scope for the default lane.
- Each lane names owner docs, expected commands, expected tests, and an optional dogfood suite.
- Lane results are shaped so they can feed the QA dashboard later.

## Commands

```bash
python smart_agent.py qa surfaces
python smart_agent.py qa surfaces run --dry-run
python smart_agent.py qa surfaces matrix
```

These commands report lane metadata only. Future execution lanes must stay registry-gated, safe-tier only by default, and explicit about any live-provider or personal-data opt-in.

## Covered Surfaces

- CLI core
- Command registry
- PromptOps
- Runtime/canonical state
- Agent Gateway / Runtime Kernel
- Action Center/approvals
- ToolBroker/policy/audit
- Web/research
- Reddit/forums
- Weather
- News planned/stubbed
- Brain providers
- Native skills
- Secrets
- QA sandbox
- Media planned/stubbed
- Platform/app bridge
- Channels/Telegram/mobile
- Memory
- Backup/restore

