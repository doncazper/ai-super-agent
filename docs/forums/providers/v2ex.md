# V2EX Read-Only Connector

Status: local mocked v1 complete; live use is opt-in.

## Commands

```bash
python smart_agent.py v2ex doctor
python smart_agent.py v2ex nodes
python smart_agent.py v2ex node python
python smart_agent.py v2ex topic <topic_id>
python smart_agent.py v2ex replies <topic_id>
python smart_agent.py v2ex latest
python smart_agent.py v2ex hot
python smart_agent.py connectors status v2ex
```

All commands execute through ToolBroker capabilities. `v2ex doctor` and `v2ex status` are metadata-only and do not call V2EX.

## Configuration

```dotenv
V2EX_ENABLED=false
V2EX_TOKEN=
V2EX_TIMEOUT_SECONDS=10
V2EX_MAX_REQUESTS_PER_HOUR=600
V2EX_CACHE_ENABLED=true
V2EX_CACHE_TTL_SECONDS=86400
```

`V2EX_TOKEN` is optional. When present, it is used only as a bearer token for documented API 2.0 read endpoints that require it. The token is never printed in doctor/status output or audit arguments.

## Access Policy

- Use documented V2EX API endpoints only.
- Do not scrape V2EX web pages as an API substitute.
- Chinese forum discovery may also use `site:v2ex.com` search-provider discovery for public URL finding, but direct reads should prefer the documented V2EX connector when possible.
- Do not use notifications, member profile, posting, modifying, or write endpoints in this track.
- Treat V2EX topic/reply content as `UNTRUSTED_WEB`.
- Respect V2EX rate-limit headers and the local default of 600 requests per hour.
- Cache only according to the configured TTL; do not write forum content to memory.

## Normalized Output

Topics are normalized to generic `ForumThread` and `ForumPost` records. Replies are normalized to `ForumComment` records. Source IDs, URLs, retrieved timestamps, provider labels, and `UNTRUSTED_WEB` trust labels are preserved.

Author metadata is redacted by default. Language detection and local model translation can be requested by commands that support `--detect-language` or `--translate-to`; generated translations are labeled as model-generated and are not stored in memory.

## Limitations

The local test gate uses mocked V2EX responses. Live validation remains opt-in and requires `V2EX_ENABLED=true`; token-backed endpoint behavior depends on the configured V2EX account/token and the public API surface.
