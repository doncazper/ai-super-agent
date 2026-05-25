# Release Readiness Audit

Date: 2026-05-25

Prompt: `RELEASE-HARDENING-LOOP-V2`

## Scope

Release Hardening Loop v2 audited repository state, command registry health, tests, policy validation, capability manifest validation, safe evals, dogfood availability, session/bug evidence, security scan signals, generated artifact hygiene, and tracker consistency before any major feature expansion.

## Non-Goals

- No new major features.
- No personal-data connector enablement.
- No new send/write capabilities.
- No package installation.
- No policy relaxation.
- No audit disabling.
- No CAPTCHA, anti-bot, login-wall, paywall, or scraping bypass.
- No hidden persistence or background autonomy.

## Repo State

- Branch: `checkpoint/large-working-tree-20260523`.
- Last commit: `e1dfdbf Add command registry and documentation tracking`.
- Working tree: large dirty tree with many modified and untracked implementation, docs, tests, prompts, dogfood, forum, language, web, runtime, and messaging files from prior feature batches.
- Generated/local artifacts observed: eval/session/bug outputs are present; `workspace/eval/`, local lead records, local messaging drafts, iOS compose payloads/results, and Reddit thread exports are generated local workspace data. `docs/release/GENERATED_ARTIFACT_HYGIENE.md` now classifies these artifacts and `.gitignore` has narrow rules for the generated paths while keeping `workspace/dogfood/` and `workspace/skills/` reviewable.
- Release boundary risk: high. A clean release candidate branch or reviewed commit series is needed before tagging or shipping.

## Test Results

- Full suite: latest continuation run `./.venv/bin/python -m pytest -q` passed with `1042 passed, 1 skipped in 62.50s`. Original v2 audit run passed with `1036 passed, 1 skipped in 64.17s`.
- Regression hardening added for the synthetic setup command bugs:
  - `tests/regressions/test_bug_0001_setup_command.py`
  - `tests/regressions/test_bug_0002.py`
- Targeted regression run: `2 passed in 0.53s`.
- Focused tracking/command/prompt tests: `23 passed in 0.43s`.
- Safe eval: `eval run --safe --json` returned status `ok`, summary `33 pass, 6 skipped`, quality score `100.0`.
- Dogfood dry-run: `dogfood run all_safe --dry-run` returned status `ok` with 8 dry-run skipped commands and 0 failures.
- Release artifact hygiene regression: `./.venv/bin/python -m pytest tests/test_release_artifact_hygiene.py -q` passed with `3 passed`.
- Focused release/tracker/maturity regression run after tracker updates: `19 passed`.

## Validation Results

- Python interpreter: `./.venv/bin/python`, Python `3.12.13`.
- Startup policy validation: passed through `make policy-check`.
- Capability manifest validation: passed through `make policy-check` with 185 configured tools.
- Command registry validation: passed with 382 commands and no invalid records.
- Safe eval suite: passed/skipped as designed, with personal-data evals skipped by default and web search skipped because no provider is configured.
- Command QA plan generation: succeeded.

## Command Registry Status

- Command registry is present and validates.
- Command test matrix is present and validates against registry metadata.
- Discovered command references were broad and consistent with the size of the current CLI surface:
  - `smart_agent.py`: 2 references.
  - `agent`: 450 references.
  - `tests`: 34 references.
  - `README.md`: 458 references.
  - `docs`: 1789 references.
  - `dogfood_suites`: 142 references.
  - Parser/command metadata references: 339.
- No new commands were added in this hardening pass, so no registry content change was required.

## Feature Maturity Status

- The project has strong local test coverage and policy/manifest/registry validation.
- Several implemented feature areas still lack live provider validation or manual QA evidence and must not be promoted to `Live-Validated`, `User-Ready`, or `Mature Pattern` solely from local mocks.
- Release Hardening Loop v2 itself is tracked as hardened local process evidence, not as proof that every feature is release-ready.

## Security Findings

- No P0/P1 security blocker was confirmed during this pass.
- Static scans found many policy/document/test references for CAPTCHA, anti-bot, robots, login, scraping, send/write, and bypass terms; spot checks indicated these are mostly denial rules, docs, tests, fixtures, or disabled/stubbed behavior.
- Secret-like literal scan found examples and fake test tokens only; no real credential was confirmed.
- Specific personal connector default scan confirmed calendar, contacts, email, and message read/write/send capabilities remain disabled by default or approval-gated according to risk.
- CRITICAL capability scan found no approval-reuse issue.
- Direct network/subprocess primitives exist in provider/tool implementations and tests; they must remain reachable only through registered ToolBroker paths. No immediate enabled bypass was confirmed.

## Docs Findings

- Core tracking docs are comprehensive but very large.
- `docs/release/` artifacts were missing before this hardening loop and are now created.
- Changelog, feature registry, feature maturity, roadmap, project state, completion report, risk register, threat model, test plan, and release checklist require this audit result.

## UX / Diagnostic Findings

- `smart_agent.py setup` currently exits 0 and prints setup guidance; both synthetic setup bug records are now fixed with concrete regressions.
- `commands list | head` can emit a `BrokenPipeError` if stdout is closed by the shell pipeline. This is cosmetic and should be treated as a P4 CLI polish issue.
- Provider-not-configured and setup guidance generally exist, but live/manual QA should keep focusing on the first-run path.

## Dogfood / Session Findings

- Latest session: `sess_20260523T182508Z_abdad880`, 1 command, 0 failures, 2 feedback records.
- Existing synthetic bug records were fixed and linked to regressions.
- `quality bugs` now reports zero open bugs.
- Manual/live dogfood evidence remains limited compared with the breadth of the repo. Run a full `all_safe --session` pass before a release candidate.

## Bug Findings

- `BUG-0001`: fixed. Regression added for `smart_agent.py setup`.
- `BUG-0002`: fixed. Skipped scaffold converted to a concrete setup command regression.
- Open bugs after hardening: 0.

## Release Readiness Score

Score: 83/100.

State: YELLOW.

Rationale: tests, startup policy, capability manifest, command registry, safe evals, and mocked dogfood checks are green; no open P0/P1/P2 bug remains. The repo is not GREEN because the working tree is very large/dirty, live provider validation is incomplete, and manual dogfood coverage is still thinner than the command surface.

## Recommended Next Fixes

1. Create a clean release candidate branch or reviewed commit series from the large working tree.
2. Run `dogfood run all_safe --session` and review the resulting session.
3. Add automated static checks for direct network/subprocess primitives that document allowed brokered modules.
4. Keep generated artifact hygiene regression coverage green and review ignored generated outputs before release packaging.
5. Run opt-in live provider validation for configured LM Studio, web, weather, Reddit, V2EX, and forum providers.
6. Improve CLI pipeline behavior for `commands list | head`.
7. Continue reducing manual QA gaps in `docs/COMMAND_TEST_MATRIX.md`.
