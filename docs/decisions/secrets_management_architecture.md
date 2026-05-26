# Decision: Secrets Management Architecture

Status: accepted for local implementation.

## Context

The agent uses optional providers for weather, web search, forums, messaging scaffolds, news, media planning, brain runtimes, and future platform bridges. Some providers require API keys, OAuth client secrets, or token cache paths. The repo needs a single safe pattern for documenting, detecting, redacting, and preflighting those secrets without storing values.

## Decision

Secrets management is metadata-first:

- A static registry describes known secret identifiers and setup hints.
- Resolvers may check approved sources for presence/status but must not print values.
- Redaction utilities are shared by doctors, audits, reports, QA, prompt tracking, and provider diagnostics.
- Local `.env` support is allowed only when ignored and untracked.
- Keychain support is optional and dry-run/mock-first until explicitly enabled later.
- Secret scans and git preflight checks are local best-effort safeguards, not replacements for provider rotation or GitHub secret scanning.

## Boundaries

- No real secrets in tracked files.
- No secret memory writes.
- No provider calls by default.
- No paid API enablement by key presence.
- No Keychain access unless an explicit future command requests it safely.
- No bypass of ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger for executable behavior.

## Consequences

This keeps setup ergonomic while preserving local-first safety. It also means credential validity is usually not proven by the generic doctor; live provider checks remain explicit, opt-in, and provider-specific.
