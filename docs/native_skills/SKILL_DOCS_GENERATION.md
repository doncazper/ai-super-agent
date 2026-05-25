# Skill Docs Generation

Native skill docs generation keeps the catalog aligned with reviewed local manifests and tracker metadata. It is documentation automation only; it does not install, enable, import, or execute skills.

## Commands

```bash
python smart_agent.py skills docs-generate --dry-run
python smart_agent.py skills docs-generate
python smart_agent.py skills docs-generate --write
python smart_agent.py skills catalog
python smart_agent.py skills docs-check
```

`skills docs-generate` defaults to dry-run behavior. Use `--write` only after reviewing the dry-run payload.

## Sources

The generator reads:

- native skill manifests
- command registry metadata
- profile visibility metadata
- compatibility diagnostics
- provenance/trust metadata
- lockfile verification status
- test and dogfood declarations
- declared docs paths and known limitations

## Safety Rules

- No skill code is executed.
- No external skill scripts are executed.
- No dependencies are installed.
- No provider, connector, plugin runtime, or marketplace call is made.
- Maturity is copied from manifests and is never inferred or upgraded.
- Missing docs are reported instead of hidden.
- Deprecated and blocked skills remain visible in the catalog.
- Manual notes in the catalog are preserved outside the generated section.

## Generated Section

`docs/native_skills/SKILL_CATALOG.md` contains a marked generated section:

```text
<!-- BEGIN GENERATED NATIVE SKILL CATALOG -->
...
<!-- END GENERATED NATIVE SKILL CATALOG -->
```

Do not edit inside the generated section by hand. Put reviewed caveats or release notes in the manual notes block.

## Release Gate Use

Run these before promoting native skill docs:

```bash
python smart_agent.py skills docs-generate --dry-run
python smart_agent.py skills docs-check
python smart_agent.py skills validate
python smart_agent.py commands validate
```

If `docs-check` reports stale output or missing docs, update the manifest/docs first, then regenerate the catalog with `--write`.
