# Safe Fetch And Extraction

Direct page fetching is a selected-URL workflow. It is bounded, audited, and treats source text as untrusted data.

## Commands

```bash
python smart_agent.py web fetch "https://example.com/article"
python smart_agent.py web extract "https://example.com/article"
python smart_agent.py web metadata "https://example.com/article"
```

- `web fetch` returns the full structured fetch result, including sanitized HTML, readable text, source metadata, trust label, blocked reason, and audit metadata.
- `web extract` returns readable text for the selected URL.
- `web metadata` returns source metadata such as title, canonical URL, author, published date when available, and retrieval time.

All three commands execute through `ToolBroker`, `PolicyEngine`, and `AuditLogger` as `web.fetch_url`, `web.extract_readable_text`, and `web.extract_metadata`.

## Safety Rules

- Only `http` and `https` URLs are allowed.
- Private/local hosts and configured blocked domains are denied before network access.
- Tracking query parameters are stripped by default where safe.
- Redirects, timeouts, content type, and response size are bounded.
- Binary downloads are disabled by default.
- Cookies, sessions, form submission, browser profiles, CAPTCHA bypass, paywall bypass, login-wall bypass, proxy evasion, and anti-bot bypass are not implemented.
- Scripts, event-handler attributes, unsafe URL attributes, and embedded active content are stripped during sanitization.
- CAPTCHA, anti-bot, and blocked pages return `status=unavailable` with a `blocked_reason`; no bypass is attempted.

## Trust And Prompt Injection

Fetched page text is labeled `UNTRUSTED_WEB`. Downloaded/fetched documents remain `UNTRUSTED_DOCUMENT` in acquisition workflows. The final model receives fetched text as source data only; web content cannot instruct the agent to call tools, reveal secrets, alter policy, ignore system rules, or weaken safety gates.

The wrapped `content` field starts with an untrusted-content warning. Use `text` and `source_metadata` for summarization or citation, and preserve `retrieved_at` for freshness-sensitive answers.

## Memory And Audit

Fetch and extraction commands do not write web content or search history to memory by default. Brokered executions audit the network domains and result status. The audit log records sanitized arguments, not browser cookies, session tokens, or raw secret values.
