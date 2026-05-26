# Whole-Codebase Static Bug Scan Report

Prompt ID: `CODEBUG-07`
Date: 2026-05-25

## Scope

Run static scans for common release-risk patterns and document actionable findings. Fix only clearly scoped bugs.

## Non-Goals

- No broad refactor.
- No removal of tests or fixtures.
- No package installation.
- No live provider calls.
- No policy weakening.
- No send/write enablement.

## Scans Run

- Risky execution/file primitives:
  - `os.system`
  - `subprocess.run` / `Popen` / `check_call`
  - `eval(` / `exec(`
  - `pickle.load`
  - `yaml.load`
  - `rmtree`
  - direct `unlink`
- Safety-control-plane references:
  - `ToolBroker`
  - `PolicyEngine`
  - `PermissionManager`
  - `ApprovalManager`
  - `AuditLogger`
  - bypass language
- Web bypass terms:
  - CAPTCHA
  - Cloudflare / anti-bot
  - paywall
  - login wall
  - proxy evasion
  - scraping
- Secret-pattern scan over tracked content, excluding prompt-pack source and current bugfix docs:
  - common API-key/token/private-key identifiers
  - OpenAI/GitHub/Slack/Google key prefixes

## Findings

| Finding | Severity | Status | Notes |
|---|---:|---|---|
| `subprocess.run` appears in approved wrappers/adapters, tests, doctors, promptops, session metadata, and disabled/stubbed personal-platform probes | P2 | reviewed/no scoped fix | Uses are expected but high-value for future deeper review. Several are intentionally bounded with timeouts, mocks, or explicit commands. No new direct ToolBroker bypass was confirmed in this pass. |
| `unlink` appears in cache/retention/local store cleanup paths | P3 | reviewed/no scoped fix | Uses are local cache/store deletion helpers or tests. No broad file deletion bug was confirmed. |
| Bypass terms are mostly denial-policy docs, tests, fixtures, and unavailable-result behavior | n/a | verified | Static hits indicate policy coverage rather than enabled bypass behavior. |
| Secret-pattern hits are env names, docs placeholders, redaction tests, or synthetic test secrets | n/a | verified | No committed real secret was confirmed by this best-effort pattern scan. |
| `CODEBUG-P2-002` static scan needed | P2 | completed | This report captures the first CODEBUG static scan. Future scans should add machine-readable allowlists for approved subprocess/network/file-access sites. |

## Deferred Review Items

| Item | Severity | Recommended Follow-Up |
|---|---:|---|
| Approved subprocess allowlist | P2 | Create a small registry of approved subprocess call sites, expected command prefixes, timeout requirements, and tests. |
| Direct cache/store deletion allowlist | P3 | Document allowed cache deletion paths and test workspace-bound deletion behavior. |
| Docs validation command gap | P2 | Decide whether to implement a real `docs validate` command or make unknown top-level command handling stricter. |
| Connector status verbosity/history | P3 | Consider a concise connector summary mode that hides historical errors unless `--verbose` is requested. |

## Tests And Validation

- Full suite was already run after CODEBUG-04: 1387 passed, 1 skipped.
- Prompt/tracker/docs focused tests after CODEBUG-06: 66 passed.
- No code changes were made in CODEBUG-07, so no new targeted regression test was required.

## Safety Notes

No confirmed enabled CAPTCHA/anti-bot/paywall/login bypass, secret leak, ToolBroker bypass, approval bypass, audit bypass, personal-data default enablement, or send/write backdoor was found by this static pass. Static grep is not proof of absence; CODEBUG-08 should keep these as release-gate checks.
