# Cloneability Release Gate

Date: 2026-05-23

## Scope

Validate the Agent DNA / Cloneability track as docs, provenance, prompt reconstruction, and migration guidance only.

## Non-Goals

- No runtime behavior changes.
- No personal-data tools enabled.
- No policy weakening.
- No ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger bypass.

## Checks

- `docs/AGENT_DNA.md` exists and defines safety invariants.
- `docs/ARCHITECTURE_PRINCIPLES.md` exists and defines forbidden shortcuts.
- `docs/CLONE_BLUEPRINT.md` exists and defines minimum clone architecture.
- `docs/MODEL_MIGRATION_GUIDE.md` exists and preserves model/tool boundaries.
- `docs/PLATFORM_MIGRATION_GUIDE.md` exists and preserves bridge boundaries.
- `docs/REWRITE_CHECKLIST.md` exists.
- `docs/BUILD_HISTORY.md`, `docs/BUILD_PROVENANCE.md`, and `docs/DECISION_INDEX.md` exist.
- `docs/RECONSTRUCTED_PROMPT_PACKS.md` and `prompts/packs/reconstructed/` exist.
- Reconstructed prompt packs are labeled reconstructed and not exact unless proven.
- `README.md`, `AGENTS.md`, `SPEC.md`, and `docs/SDLC.md` reference cloneability rules.
- Feature registry, maturity, roadmap, project state, completion report, changelog, prompt ledger, queue, and audit are updated.

## Result

Passed locally for docs/provenance scope.

- Focused docs validation: `./.venv/bin/python -m pytest tests/test_feature_maturity_docs.py -q` passed with 11 passed.
- Prompt pack validation: `./scripts/agent prompts validate-pack prompts/packs/agent-dna-cloneability-v1.promptpack.md` returned ok for 6 prompts.
- Prompt audit: zero active prompts, DNA-01 through DNA-06 definitely complete, `MACOS-MESSAGES-PROBE` next.
- Startup policy validation: ok.
- Capability manifest validation: ok.
- Command registry validation: ok with 281 commands.
- Full test suite: `./.venv/bin/python -m pytest -q` passed with 768 passed, 2 skipped.

No runtime behavior, personal-data capability, send/write path, policy rule, approval rule, or audit behavior changed.
