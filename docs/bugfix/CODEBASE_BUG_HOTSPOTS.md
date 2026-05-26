# Codebase Bug Hotspots

Prompt ID: `CODEBUG-01`
Date: 2026-05-25

## Highest-Risk Hotspots

| Priority | Hotspot | Evidence | Risk | Recommended Review |
|---|---|---|---|---|
| P1 | Large dirty working tree | `git status --short` shows many modified/untracked files | Release mistakes, accidental generated files, hard-to-review diffs | Clean release-candidate boundary pass |
| P1 | Prompt tracker drift | MATURITY-AUDIT-01 found stale queued rows/files; CODEBUG import added more queue records | Running prompts out of order or stale evidence claims | Prompt tracker reconciliation |
| P1 | Safety-control-plane regressions | Critical architecture; many features depend on ToolBroker/Policy/Audit | High impact if bypass exists | CODEBUG-02 targeted review |
| P2 | CLI/docs validation ambiguity | `smart_agent.py docs validate` falls through to chat | False confidence in docs validation | CODEBUG-03/CODEBUG-06 review |
| P2 | Runtime/Brain provider boundary | Brain gateway is partially optional; LM Studio still primary | Startup/default/provider confusion | CODEBUG-04 review |
| P2 | Connector/provider missing states | Many optional providers and personal connectors are disabled/setup-gated | Confusing UX or accidental live call | CODEBUG-05 review |
| P2 | Static safety anti-patterns | Large codebase with subprocess/network/file/cache paths | Hidden bypass or missing timeout | CODEBUG-07 static scan |

## Lower-Risk Hotspots

- Empty invocation UX is sparse but not unsafe.
- Command manual QA is thinner than automated registry coverage.
- News runtime remains scaffolded/planned only.
- Platform bridges remain stubs only and must not be mistaken for real support.

