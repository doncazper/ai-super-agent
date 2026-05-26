# Command Intent Index

Status: implemented for metadata/index v1.

The command intent index converts structured command registry records into
natural-language suggestion metadata. It does not execute commands. It exists so
future natural-language routing can reuse `docs/COMMAND_REGISTRY.md` and
`agent.ui.command_registry` as the source of truth instead of inventing a
parallel command catalog.

## Indexed Fields

Each indexed command records:

- `command_id`
- `command`
- `group`
- `description`
- `examples`
- `aliases`
- `natural_language_triggers`
- `intent_ids`
- `risk_level`
- `approval_required`
- `provider_required`
- `connector_required`
- `safe_to_run_directly`
- `dry_run_available`
- `docs_link`
- `status`

## Safety Rules

- Exact command registry records remain source of truth.
- Missing or empty registries return an empty index, not a crash.
- Planned, stubbed, deprecated, legacy, removed, and blocked commands are labeled
  and are not primary active suggestions.
- HIGH, CRITICAL, and FORBIDDEN commands are never marked
  `safe_to_run_directly`.
- Commands with approval requirements are not marked `safe_to_run_directly`.
- Provider or connector requirements produce setup hints.
- Suggestions are fuzzy and deterministic; no LLM is needed.
- Suggestions do not execute commands, call providers, access personal data, or
  write memory.

## CLI

```bash
python smart_agent.py commands intents
python smart_agent.py commands suggest "what is the weather in phoenix"
```

Both commands print metadata only. Future natural-language execution planners
must still route any real action through ToolBroker, PolicyEngine,
PermissionManager, ApprovalManager, and AuditLogger.
