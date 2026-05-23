# Prompt Pack Format

Prompt packs let the user paste or save one large prompt file that contains multiple individual Codex prompts. Importing a pack validates and splits it into queued prompt records. It does not execute any prompt.

## Safety Rules

- Default mode is `import_only`.
- `execute_all` is rejected.
- Imported prompts are run one at a time only.
- Prompt text is stored as data, not executed instructions.
- Imported prompts may be HIGH, CRITICAL, or FORBIDDEN risk, but they are not selected by `prompts next` when their approval gate blocks execution.
- Imported prompt bodies are preserved exactly in split files.

## Commands

```bash
python smart_agent.py prompts validate-pack ./my-pack.md
python smart_agent.py prompts import ./my-pack.md
python smart_agent.py prompts split ./my-pack.md
python smart_agent.py prompts next
python smart_agent.py prompts show EXAMPLE-01
python smart_agent.py prompts audit
pbpaste | python smart_agent.py work import --stdin --pack-id tonight
python smart_agent.py work import-clipboard --pack-id tonight
python smart_agent.py work next
```

`validate-pack` reads and validates only. `import` and `split` validate, copy the original file into `prompts/packs/`, write split prompt files into `prompts/queued/`, and append ledger, queue, and audit entries.

`work import` is the higher-level PromptOps Workbench path for pasted mega prompts. It updates the same ledger, queue, audit, and project state files, and it still does not execute imported prompts automatically.

## Required Structure

```text
<<<PROMPT_PACK_START>>>
pack_id: example-pack-v1
pack_title: Example Prompt Pack
mode: import_only
default_execution: one_prompt_at_a_time
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true

<<<PROMPT_START id="EXAMPLE-01" order="1">>
title: Example first prompt
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
...
<<<PROMPT_END id="EXAMPLE-01">>
<<<PROMPT_PACK_END>>>
```

## Validation

The importer rejects packs when:

- There is not exactly one pack start and pack end marker.
- A prompt start/end pair is missing or mismatched.
- Prompt ids or order values are duplicated.
- Required metadata is missing.
- `risk_level` is not `SAFE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, or `FORBIDDEN`.
- A dependency references a missing prompt.
- Dependencies contain a cycle.
- A prompt is marked complete on import.
- Pack mode is anything other than `import_only`.
- Default execution is anything other than `one_prompt_at_a_time`.

## Split Prompt File Format

```markdown
---
prompt_id: EXAMPLE-01
pack_id: example-pack-v1
title: Example first prompt
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: queued
created_at: ...
imported_at: ...
source_pack: prompts/packs/example-pack-v1.md
trust_level: UNTRUSTED_DOCUMENT
---

# Prompt

...
```
