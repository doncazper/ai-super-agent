# M4 Web Tools

## Scope

Add web search and webpage fetch with untrusted-content protections.

## Non-Goals

No form submission, binary downloads by default, authenticated browsing, or browser automation.

## Requirements

- `web.search`
- `web.fetch_url`
- Extraction utilities.
- `UntrustedContentManager`.
- Domain allow/block lists.
- Provider abstraction.
- Retrieval timestamp and URL in results.

## Risks

- Prompt injection from webpages.
- Hallucinated search results.
- Malicious scripts or downloads.
- Tracking or unsafe domains.

## Tests

- Web disabled returns a clear error.
- Blocked domain denied.
- Timeout handled.
- Scripts stripped.
- Untrusted wrapper applied.
- Webpage instruction injection not followed.
- Network domain audited.

## Approval Gate

Search provider configuration may require user setup.
