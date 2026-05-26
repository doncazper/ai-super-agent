# Command QA Tiers

| Tier | Name | Automatic? | Description |
|---:|---|---|---|
| Tier 0 | Registry/docs validation | yes | Validate command registry, test matrix, docs links, and structured metadata. |
| Tier 1 | Local read-only | yes | Help, status, doctor, list, show, explain, and other local metadata commands. |
| Tier 2 | Mocked provider | yes, with mocks | Commands that need provider-shaped responses but can run against fixtures/mocks only. |
| Tier 3 | Disposable workspace writes | yes, with sandbox | File/write commands restricted to `.qa_workspace/` or `reports/qa/workspaces/`. |
| Tier 4 | Dry-run personal data | no automatic real reads | Personal-data commands in dry-run/preflight/mock mode only. |
| Tier 5 | Safe live provider | opt-in only | Live provider checks that are configured, free/allowed, and non-personal. |
| Tier 6 | HIGH manual | manual only | Approval-gated HIGH commands. Never run automatically. |
| Tier 7 | CRITICAL manual | never automatic | Sends, irreversible writes, and high-impact operations. Manual approval/review only. |

## Tier Selection Rules

- Unknown risk defaults to blocked until metadata is fixed.
- Planned, stubbed, deprecated, legacy, blocked, or removed commands are skipped unless explicitly requested for metadata validation.
- Commands with setup requirements are marked `setup_required` rather than failed.
- Commands with provider requirements are not live-run unless the provider is configured and the run mode explicitly allows it.
- Write commands require a disposable workspace and are still denied if they target real user data.

## Tier 3 Workspace Rule

Tier 3 may write only under approved disposable QA roots. Cleanup must be bounded to the workspace root and must reject path traversal.
