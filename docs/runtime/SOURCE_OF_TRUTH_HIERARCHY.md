# Source-of-Truth Hierarchy

Status: CANON-01 implemented.

Canonical hierarchy:

1. `SPEC.md`
2. `docs/SDLC.md`
3. `AGENTS.md`
4. `config/capabilities.yaml`
5. actual code/tests
6. canonical runtime state JSON/model
7. `COMMAND_REGISTRY`
8. `FEATURE_REGISTRY` / `FEATURE_MATURITY`
9. `PROMPT_LEDGER` / `PROMPT_QUEUE` / `PROMPT_AUDIT`
10. `PROJECT_STATE` / `COMPLETION_REPORT` / `CHANGELOG`
11. summary dashboards

If sources disagree, prefer the highest-ranked available evidence. The canonical runtime state can surface conflicts, but it does not override trackers on its own.
