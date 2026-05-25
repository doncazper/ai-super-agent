# Forum Provider Registry

Status: local tested v1

## Purpose

The Global Forum Provider Registry is the metadata source of truth for Reddit-like and community forum providers. It describes which providers are implemented, stubbed, disabled, discovery-only, or unsupported before any workflow tries to use them.

The registry is read-only. Status and doctor commands do not fetch forum content, validate logged-in sessions, use cookies, call provider APIs, or access personal data.

## Commands

```bash
python smart_agent.py forums providers
python smart_agent.py forums status reddit
python smart_agent.py forums doctor
python smart_agent.py forums capabilities zhihu
```

All commands execute through `ToolBroker` as `forums.providers`, `forums.status`, `forums.doctor`, or `forums.capabilities` and are audited with no network domains.

## Provider Status Values

| Status | Meaning |
|---|---|
| `active` | Provider implementation is available and ready under configured policy. |
| `configured` | Required config appears present, but live use still depends on the provider command and release gate. |
| `disabled` | Provider exists but is disabled by default or missing required config. |
| `stubbed` | Provider metadata exists; implementation is deferred. |
| `discovery_only` | Provider may only be discovered through approved search-provider site filters or selected public URL fetch where allowed. |
| `blocked` | Provider is blocked by policy or availability. |
| `unsupported` | Provider is unknown or unsupported and is not queried. |
| `deprecated` | Provider remains tracked but should no longer be used. |

## Initial Providers

| Provider | Status | Access path | Notes |
|---|---|---|---|
| `reddit` | disabled or configured | Official Reddit Data API | OAuth required; no web scraping fallback; read-only capabilities only. |
| `v2ex` | disabled by default | Documented V2EX API connector | Read-only connector exists and requires `V2EX_ENABLED=true`; no member/profile/notification/write endpoints. |
| `hackernews` | stubbed | Public API candidate | Connector deferred. |
| `stackexchange` | stubbed | Official API candidate | Connector deferred. |
| `lemmy` | stubbed | Federated public API candidate | Instance policy needed before implementation. |
| `zhihu` | discovery_only | `site:zhihu.com` | No login/cookie/session automation or CAPTCHA bypass. |
| `baidu_tieba` | discovery_only | `site:tieba.baidu.com` | Public discovery only where allowed. |
| `douban_groups` | discovery_only | `site:douban.com/group` | Login/private groups report unavailable. |
| `xiaohongshu` | discovery_only | `site:xiaohongshu.com` | Anti-bot or login walls report unavailable. |
| `weibo` | discovery_only | `site:weibo.com` | Public discovery only; no account automation. |
| `nga` | discovery_only | `site:bbs.nga.cn` | Public discovery only where allowed. |

## Safety Rules

- Provider status never performs personal or logged-in reads.
- Discovery-only providers use search-provider site filters, not platform-specific scraping.
- Write capabilities are absent in this track.
- Forum content remains `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`.
- Blocked, login-required, CAPTCHA-protected, anti-bot-protected, or private pages must be reported unavailable.
- Provider adapters cannot self-enable capabilities; executable future work must be declared in `config/capabilities.yaml` and run through `ToolBroker`, `PolicyEngine`, and `AuditLogger`.

## Retention

Registry commands do not store forum content, author metadata, or query history. Future provider caches must be TTL-bounded, public-only, and retention-aware. Deleted/removed content and author-identifying metadata must not be retained by default.
