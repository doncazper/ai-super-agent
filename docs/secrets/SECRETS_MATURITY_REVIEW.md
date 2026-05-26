# Secrets Management Maturity Review

Prompt: `SECRETS-08`
Status: conservative local maturity review after local release gate.

## Maturity Summary

| area | maturity | evidence | limitations |
|---|---:|---|---|
| Secrets policy | 5 Hardened | policy docs, risk/threat docs, docs tests | human review still required before push |
| API key inventory | 4 Tested | inventory docs and provider setup matrix | live provider validation not included |
| `.env` / `.gitignore` hygiene | 5 Hardened | `.gitignore`, placeholder tests, scanner | Git history rewrite/remediation remains manual |
| Secret registry | 4 Tested | `agent/secrets/registry.py`, registry tests | static list must evolve with providers |
| Redaction layer | 5 Hardened | recursive redactor, shared safety redaction, regression tests | heuristic; not a substitute for avoiding secrets in inputs |
| Secret resolver/env loader | 4 Tested | dependency-free `.env` parser/resolver tests | no Keychain lookup in v1 |
| Provider secret doctors | 4 Tested | provider status tests, `secrets doctor all` smoke | config-only; no live credential validation |
| Keychain strategy/adapter | 3 Implemented / 4 Tested for dry-run | dry-run adapter tests and docs | real Keychain access blocked/future |
| Secret leak scanner | 5 Hardened | fixture tests, tracked/staged scan smokes, release gate | best-effort; not gitleaks/trufflehog |
| Git preflight | 5 Hardened | fixture tests and repo preflight smoke | large dirty worktree still needs human review |
| User docs | 5 Hardened | README/User Guide/provider docs plus docs tests and release gate | manual QA pending |

## Readiness

Secrets management is safe to rely on for:

- placeholder-only setup guidance;
- redacted provider readiness checks;
- local `.env` hygiene;
- dry-run Keychain metadata;
- best-effort tracked/staged scanning;
- Git preflight before commit/push.

It is not yet safe to rely on for:

- real Keychain reads/writes;
- guaranteed secret detection equivalent to dedicated scanners;
- live provider credential validation;
- automatic remediation, history rewrite, commit, or push decisions.

## Conservative Score

Readiness score: 82/100.

Rationale: policy, docs, tests, ToolBroker routing, redaction, local scanner evidence, and local release-gate evidence are strong. Live provider credential validation, real Keychain access, and dedicated external scanner coverage are intentionally absent.
