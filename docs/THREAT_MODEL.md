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
| Prompt injection from email | Mark email `UNTRUSTED_EMAIL`; selected-scope only; never follow embedded instructions. |
| Prompt injection from messages | Mark messages `UNTRUSTED_MESSAGE`; selected-scope only; no sends before approvals. |
| Malicious documents | Mark documents `UNTRUSTED_DOCUMENT`; no macro execution; web fetch refuses binary downloads by default. |
| Tool-broker bypass | Tools execute only through `ToolBroker`; tests verify unknown/direct paths are denied by policy boundaries. |
| Path traversal | Resolve absolute paths and enforce allowed roots before filesystem actions. |
| Secrets leakage | Deny known secret paths; redact audit/debug output; never store secrets. |
| Unsafe memory storage | Use categories and approvals; block secrets and default personal-body storage; redact memory content from audit arguments. |
| Overbroad personal-data access | Disable personal tools by default; selected-scope reads only; avoid private database scraping and broad Full Disk Access. |
| Email/text sending abuse | Draft-only workflows before send tools; M8 send tools disabled by default with critical per-action approval and preflight summaries. |
| Calendar/contact modification abuse | M8 write tools disabled by default with critical per-action approval and preflight summaries. |
| Self-improvement weakening safety | Branch-based changes; policy-reduction checks; protected safety files; tests and diff before approval-gated commit. |
| Audit-log tampering | Hash-chain audit entries; later verification command. |
| Configuration tampering | Validate capabilities at startup and deny unknown/dangerous entries. |
