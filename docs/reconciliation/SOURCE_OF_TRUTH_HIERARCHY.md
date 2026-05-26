# Source Of Truth Hierarchy

Last reconciled: 2026-05-25

This reconciliation uses the following hierarchy when trackers disagree:

1. `SPEC.md`: mission, non-goals, architecture, safety model, and acceptance criteria.
2. `docs/SDLC.md`: process rules and mini-SDLC.
3. `AGENTS.md`: permanent operating rules for Codex runs in this repo.
4. `config/capabilities.yaml`: runtime capability, risk, approval, and default-enable truth.
5. Actual code and tests: implementation truth.
6. `docs/COMMAND_REGISTRY.md`: CLI command truth after validation.
7. `docs/FEATURE_REGISTRY.md`: feature existence/status truth.
8. `docs/FEATURE_MATURITY.md`: readiness and maturity truth.
9. `docs/PROMPT_LEDGER.md`: historical prompt evidence truth.
10. `docs/PROMPT_QUEUE.md`: next prompt order truth.
11. `docs/PROMPT_AUDIT.md`: prompt reconciliation/audit truth.
12. `docs/PROJECT_STATE.md`: durable resume and project summary truth.
13. `docs/COMPLETION_REPORT.md`: completion and validation evidence truth.
14. `CHANGELOG.md`: human-readable change-history truth.
15. Tracker dashboard and productization docs: summary views only.

## Reconciliation Rules

- Prefer actual code, tests, and completion evidence over stale queue rows.
- Prefer `config/capabilities.yaml` for runtime risk/default/approval truth.
- Prefer `docs/COMMAND_REGISTRY.md` for command status when `commands validate` passes.
- Prefer completed prompt files plus ledger/completion evidence for prompt completion claims.
- If uncertainty remains, mark `needs_review` instead of guessing.
- Do not delete historical detail; correct stale rows with evidence or move old detail to an archive under a later explicit prompt.
