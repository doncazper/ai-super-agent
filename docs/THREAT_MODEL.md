# Threat Model

## Assets

- User privacy and personal data.
- Workspace files.
- Credentials and secrets.
- Audit integrity.
- Policy and approval integrity.
- Model output quality.

## Threats and Mitigations

| Threat | Mitigation |
|---|---|
| Model hallucination | Keep harness thin; model final answers are not proof of action; actions must have tool results. |
| Prompt injection from web pages | Mark fetched content `UNTRUSTED_WEB`; wrap it as data; strip scripts; do not follow page instructions; audit fetched domains. |
| Unsafe redirects or tracking URLs | Normalize URLs, strip common tracking parameters, validate redirect targets before following them, and block private/local hosts. |
| Search-provider query leakage | Keep search provider opt-in; allow `WEB_ACCESS_ENABLED=false`; redact `web.search` queries in audit logs by default; do not persist search history unless explicitly enabled. |
| Search-provider manipulation or outage | Treat search results as `UNTRUSTED_WEB`; normalize provider errors; return structured errors instead of hallucinated results. |
| Fabricated research citations | Research workflow builds summaries only from returned search/fetch data, includes source URLs, reports fetch failures, and avoids claiming unsupported current facts. |
| Approval confusion or click-through | Approval previews show request ID, risk, trust level, summary, redacted args, rollback availability, expiration, and allowed choices before approval. |
| Critical approval reuse | Critical actions are per-action only; approve-all/reuse choices are denied and tests verify reuse does not authorize a second critical action. |
| Prompt injection from email | Mark email `UNTRUSTED_EMAIL`; selected-thread only; wrap bodies with an untrusted-content warning; never follow embedded instructions or allow email text to approve actions, change policy, reveal secrets, or request tools. |
| Prompt injection from messages | Mark messages `UNTRUSTED_MESSAGE`; selected-scope only; wrap bodies with an untrusted-content warning; never follow embedded instructions or allow message text to approve actions, change policy, reveal secrets, or request tools. |
| Malicious documents | Mark documents `UNTRUSTED_DOCUMENT`; no macro execution; web fetch refuses binary downloads by default. |
| Tool-broker bypass | Tools execute only through `ToolBroker`; tests verify unknown/direct paths are denied by policy boundaries. |
| Path traversal | Resolve absolute paths and enforce allowed roots before filesystem actions. |
| Secrets leakage | Deny known secret paths; redact audit/debug output; never store secrets. |
| Unsafe memory storage | Use categories and approvals; block secrets and default personal-body storage; redact memory content from audit arguments. |
| Overbroad personal-data access | Disable personal tools by default; selected-scope reads only; avoid private database scraping and broad Full Disk Access. |
| Calendar read overreach | Calendar read connector is disabled by default, approval-gated, selected date range only, max-range limited, and returns compact summaries without notes/body or locations by default. The optional macOS path uses Calendar.app Automation permissions and does not scrape private databases or require Full Disk Access. |
| Contacts read overreach | Contacts connector is disabled by default, approval-gated, selected-scope only, and search returns compact candidates without email/phone values. Selected reads require a selected-scope token and explicit requested fields, omit notes, redact email/phone/address values by default, and do not scrape private databases or require Full Disk Access. |
| Email read overreach | Email connector is disabled by default and approval-gated. Metadata listing returns no body; thread reads require one selected thread id; bulk ids such as `all` are denied; summaries/drafts do not store body text; draft replies are never sent. |
| Messages read overreach | Messages connector is disabled by default and approval-gated. No live macOS Messages connector is implemented until a safe permissioned path exists; the project does not scrape `~/Library/Messages` or request Full Disk Access. Manual draft fallback reads only `./workspace` files, denies traversal/outside paths, wraps content as untrusted, and never sends. |
| Live smoke test overreach | Smoke tests do not enable personal-data tools by default. Calendar/contact smoke is dry-run/check-only unless a future explicit selected-scope live read path is approved. Tests marked `personal_data` are excluded by default. |
| Weather location leakage | Weather lookups use user-provided locations only, avoid silent IP or device geolocation, avoid long-term location history by default, redact location arguments in audit output, and require a separate approval-gated design before using precise device location or stored home/work locations. |
| Weather provider manipulation, outage, or stale data | Treat Open-Meteo geocoding and forecast responses as `UNTRUSTED_WEB`; include retrieval/provider timestamps when available; normalize provider errors, malformed responses, and geocoding failures; enforce timeouts and rate limits; return structured failures instead of hallucinated forecasts. |
| Manifest drift or missing safety metadata | Startup validation requires risk, default-enabled state, approval requirements, storage behavior, trust level, and audit field declarations for every capability. Web capabilities that can touch the network must declare rate limits. |
| Expanded prompt-injection attempts | Regression tests cover malicious instructions from web, email, messages, and workspace-file text that try to reveal secrets, change policy, call tools, send email/text, disable audit logs, or store private data. Such content remains data only. |
| Email/text sending abuse | Draft-only workflows before send tools; M8 send tools disabled by default with critical per-action approval and preflight summaries. |
| Calendar/contact modification abuse | M8 write tools disabled by default with critical per-action approval and preflight summaries. |
| Self-improvement weakening safety | Branch-based changes; policy-reduction checks; protected safety files; tests and diff before approval-gated commit. |
| Audit-log tampering | Hash-chain audit entries; later verification command. |
| Configuration tampering | Validate capabilities at startup and deny unknown/dangerous entries. |
