# Test Plan

## Unit Tests

- Policy decisions.
- Tool broker execution and denial.
- LM Studio request payload construction.
- Audit entry redaction and hash chaining.
- Tool argument validation.

## Integration Tests

- No-tool chat sends no tools.
- Tool-call loop appends matching tool results.
- CLI modes construct expected orchestration options.
- Smoke harness tests use mocks for LM Studio, web search/fetch, and personal connector policy checks.
- Pytest markers identify `unit`, `integration`, `live_lmstudio`, `live_web`, `live_calendar`, `live_contacts`, `requires_approval`, and `personal_data`.
- Tests marked `personal_data` are skipped by default and must be explicitly selected.

## Policy Tests

- Unknown capabilities denied.
- SAFE actions allowed.
- HIGH actions ask approval.
- CRITICAL actions require per-action approval.
- FORBIDDEN actions denied.
- Capability manifest validation requires default state, approval requirement, storage flag, trust level, audit fields, and network rate limits where applicable.

## Approval Tests

- Approval required when policy returns `ASK`.
- Denial prevents execution.
- Critical actions do not reuse approvals.
- Interactive approval prompts display previews, allow details review, and execute only after explicit approval.

## Audit-Log Tests

- Executions are logged.
- Denials are logged.
- Approval results are logged.
- Hash chain links entries.
- Secrets are redacted.

## Prompt-Injection Tests

- Webpage instructions are ignored.
- Email/message instructions are ignored.
- Document instructions are ignored.
- Regression phrases include attempts to ignore instructions, reveal secrets, change policy, call tools, send email/text, disable audit logs, and store private data.

## Web Research Tests

- Web search provider missing returns a structured error.
- Brave/provider results normalize to compact untrusted records.
- `WEB_ACCESS_ENABLED=false` denies search/fetch through the broker.
- Fetch validates blocked domains, redirects, content types, and size limits.
- Scripts and event-handler content are stripped from extracted text.
- Fetched content is labeled and wrapped as `UNTRUSTED_WEB`.
- Research workflow does not fabricate sources.
- Research workflow reports fetch failures.
- Foreign-language titles/snippets/excerpts pass through without cloud translation.
- Audit logs include search and fetch actions.

## Live Smoke Tests

- `python smart_agent.py smoke --lmstudio` verifies no-tool chat, debug events, and the safe time-tool path when `LMSTUDIO_MODEL` and LM Studio are available.
- `python smart_agent.py smoke --web` verifies configured search, safe public fetch, and source-grounded research behavior without fabricating sources.
- `python smart_agent.py smoke --calendar --contacts` performs dry-run connector and policy checks only; it does not read personal data by default.
- Unconfigured live services are reported as skipped instead of faked as passing.

## Personal-Data Tests

- Personal modules disabled by default.
- Selected-scope reads require approval.
- Body text is not stored in long-term memory by default.
- Calendar selected-range reads require approval, enforce max date ranges, omit notes/body by default, redact locations by default, and audit accesses as `LOCAL_PRIVATE_DATA`.
- Calendar availability returns slots without leaking event details.
- Contacts search/read require approval, keep tools disabled by default, return compact search candidates, require a selected-scope token and explicit requested fields for selected reads, omit notes, redact email/phone/address values by default, deny bulk export attempts, and audit accesses as `LOCAL_PRIVATE_DATA`.
- Email metadata/read/summarize/draft require approval when enabled, keep tools disabled by default, return no body in metadata, wrap selected thread bodies as `UNTRUSTED_EMAIL`, ignore prompt injection, never send drafts, refuse bulk thread ids, avoid long-term body storage, and audit access.
- Messages read/summarize/draft require approval when enabled, keep tools disabled by default, do not implement sends or bulk history reads, refuse bulk thread ids, return clear setup errors for unsafe/unconfigured adapters, restrict manual draft context files to `./workspace`, wrap content as `UNTRUSTED_MESSAGE`, ignore prompt injection, avoid long-term body storage, and audit access.

## Self-Improvement Tests

- Proposal mode does not edit files.
- Implementation creates a branch.
- Policy weakening and audit disabling are blocked.
- Tests and diffs are produced before commit.

## Release-Gate Tests

- All selected milestone tests pass or failures are documented.
- Forbidden capabilities are absent.
- Audit and policy checks pass.
