# Personal Connector Readiness Gate

Date: 2026-05-22 16:25 PDT

Overall result: PASS for readiness to proceed to the next selected-scope personal connector implementation gate.

This checklist verifies readiness only. It does not enable personal-data tools, perform live personal-data reads, implement new connectors, or approve any high-risk action.

## Scope

- Verify safety control plane readiness for selected-scope personal-data access.
- Verify personal connectors remain disabled by default.
- Verify HIGH and CRITICAL approval behavior remains strict.
- Verify memory, untrusted-content, audit, and broker boundaries are in place.
- Stop before live personal-data connector execution.

## Gate Results

| Requirement | Status | Evidence |
|---|---|---|
| ToolBroker verified | PASS | Full tests pass; direct execution scan found runtime tool execution through `ToolBroker.execute()` or `ToolBroker.dry_run()`. Personal tool adapter calls are inside registered tool handlers. |
| PolicyEngine verified | PASS | Startup policy validation passed; capability manifest validation passed; unknown capabilities are denied by policy tests. |
| Approval UI exists | PASS | `agent/ui/approvals_ui.py` and `python smart_agent.py approvals ...` commands exist; approval lifecycle tests pass. |
| Dry-run/preflight exists | PASS | `ToolBroker.dry_run()` and `python smart_agent.py preflight "<request>"` exist; dry-run/preflight tests pass in full suite. |
| AuditLogger verified | PASS | Full tests cover denials, approvals, executions, failures, dry-runs, files, commands, and network domains where relevant. |
| Secret redaction verified | PASS | Redaction tests pass; connector status redacts secrets; audit redaction is exercised in full suite. |
| Connector registry exists | PASS | `agent/connectors/registry.py`, status, and health modules exist; connector framework tests pass. |
| Personal connectors disabled by default | PASS | `calendar.*`, `contacts.*`, `email.*`, `messages.*`, and `browser.read_selected_tab` manifest entries use `default_enabled: false`. |
| HIGH actions require approval | PASS | Personal read capabilities are HIGH and `approval_required: true`; policy and personal-module tests pass. |
| CRITICAL actions require per-action approval | PASS | Send/write capabilities are CRITICAL, disabled by default, `approval_required: per_action`, and `approval_reuse_allowed: false`. |
| Untrusted content manager exists | PASS | Web uses `agent/tools/web/untrusted_content.py`; email/message wrappers mark bodies as `UNTRUSTED_EMAIL` and `UNTRUSTED_MESSAGE`; workspace documents are `UNTRUSTED_DOCUMENT`. |
| Memory does not store personal content by default | PASS | Memory v2 rejects personal/email/message content by default and requires approval for `memory.store_personal`; context injection excludes personal memory by default. |
| Tests cover denial paths | PASS | Full suite includes denial tests for unknown tools/capabilities, disabled personal modules, approval-required actions, path traversal, forbidden paths, and missing providers. |
| Non-interactive mode blocks approval-required actions | PASS | Default `ApprovalManager` denies approval-required actions unless an approval path is explicitly provided; tests cover non-interactive approval blocking. |
| No direct connector calls outside ToolBroker | PASS | Runtime scans found personal connector adapter calls only inside registered personal tool handlers; CLI/workflows call `broker.execute()` or `broker.dry_run()`. |

## Checks Run

- Full tests: `320 passed in 2.90s` before documentation updates and `320 passed in 2.94s` after documentation updates.
- Startup policy validation: `startup policy ok`.
- Capability manifest validation: `capability manifest ok`.
- Docs validation: `7 passed in 0.01s`.
- Diff whitespace check: passed.
- Direct personal-data access search:
  - Searched personal read/send/write call names across `agent/` and `smart_agent.py`.
  - Searched private macOS paths, Messages/Mail databases, Full Disk Access references, `osascript`, IMAP, and SQLite usage.
  - Result: no direct private database scraping found. Calendar/Contacts optional AppleScript paths remain permissioned adapters behind disabled-by-default brokered tools. Email IMAP adapter remains disabled by default and approval-gated.
- ToolBroker bypass search:
  - Searched for direct handler calls and registry access.
  - Result: tool handler execution occurs inside `ToolBroker`; status/doctor paths inspect metadata only and do not execute personal-data actions.

## Blockers

None for proceeding to the next connector-specific selected-scope implementation gate.

## Required Fixes

None from this readiness run.

## Notes

- `.DS_Store` files remain untracked local noise and should not be committed.
- `memory.store_personal` is not a connector; it remains HIGH risk and approval-gated.
- This gate does not approve live personal-data reads. The next connector still needs its own selected-scope setup, dry-run, approval, audit, and live-smoke review.

## Next Connector Recommendation

Calendar read-only selected date range is the next safest connector to validate because it is already modeled as HIGH risk, disabled by default, selected-range only, approval-required, audited, and non-writing.
