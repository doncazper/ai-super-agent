# Feeds And Sitemaps

RSS/Atom feeds and public sitemaps are preferred free-first acquisition sources before paid or quota-limited search providers.

## Sitemaps

- `python smart_agent.py web sitemap "<domain_or_url>"` discovers sitemap URLs from `robots.txt` and falls back to `/sitemap.xml`.
- Default URL limit: 500.
- Sitemap indexes are parsed for child sitemap URLs.
- URL entries are returned as `UNTRUSTED_WEB` source candidates.
- The XML document itself is treated as `UNTRUSTED_DOCUMENT`.
- Binary or unsupported content types are rejected before parsing.

## Feeds

- `python smart_agent.py web feed "<feed_url>"` fetches an explicit public RSS or Atom URL.
- Default item limit: 50.
- Feed items include title, URL, published date when present, summary/snippet, source URL, and trust label.
- Feed parsing does not fetch article bodies. Article/page fetching must use a later explicit fetch/acquisition command.
- Common RSS/Atom MIME types such as `application/rss+xml`, `application/atom+xml`, and `application/rdf+xml` are treated as text-like feed documents; binary payloads remain blocked.

## Safety

- No binary downloads by default.
- No form submission.
- No login, cookie, browser-profile, CAPTCHA, paywall, or anti-bot bypass.
- Blocked or unavailable pages return structured `unavailable` results with `bypass_attempted=false`.
- Domain blocklists and allowlists are enforced before network access.

## Cache And Audit

Feed and sitemap results use the Web Acquisition Layer TTL cache. Cache entries are operational metadata/source cache only and are not long-term memory. Brokered executions audit network domains, result status, and source type. Focused tests cover cache hits, default limits, malformed documents, blocked domains, binary denial, and RSS/Atom parsing.
