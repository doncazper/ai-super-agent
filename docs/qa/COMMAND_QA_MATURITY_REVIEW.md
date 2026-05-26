# Command QA Maturity Review

Date: 2026-05-25

| Area | Maturity | Evidence | Limitation |
|---|---|---|---|
| QA architecture/policy | 5 Hardened | Safety, tier, result schema, self-heal policy docs and docs tests | Policy is local; no external QA scheduler |
| Command inventory/planner | 4 Tested | Registry-backed planner, tests, `qa commands plan` | Historical run age is not tracked yet |
| Safe runner | 4 Tested | Tier 0/1 runner, redaction, timeout, report tests | Broad safe command coverage is still incremental |
| Disposable workspace | 4 Tested | Repo-local fixtures, traversal cleanup tests, Tier 3 sandbox support | Only fixture-safe command groups should be run |
| Result ranking/bug generation | 4 Tested | Redacted failure ranking and bug report tests | Generated bugs require human review |
| Regression generation | 4 Tested | Skipped regression scaffold tests | Scaffolds must be converted to concrete assertions |
| Self-heal loop | 3 Implemented | Patch plans and reports with tests | V1 does not auto-apply patches |
| Progressive QA | 4 Tested | Daily/weekly dry-run reports and policy tests | No scheduler is enabled |
| Dashboard | 4 Tested | Local report/bug/registry dashboard tests | Trend history is basic |
| Dogfood/evals | 4 Tested | Suite YAML tests and `eval run --command-qa` | Dogfood was dry-run; manual session validation remains |
| Release gate | 5 Hardened | Full suite, policy, manifest, command registry, eval, dogfood dry-runs | Live/manual validation remains future work |

Readiness score: 78/100.

Conservative maturity: `5 Hardened` for the Command QA sandbox as a local/mock-safe quality system. It is not `Live-Validated` because no real live provider or manual user session validation was performed.

Next maturity work:

1. Add historical QA run age tracking for "oldest untested" selection.
2. Add manual QA evidence capture for Tier 2 and Tier 3 groups.
3. Convert generated regression scaffolds into concrete tests for reviewed bugs.
4. Add a dedicated docs validation command.
5. Run a human-supervised `command_qa_core --session` dogfood pass.

