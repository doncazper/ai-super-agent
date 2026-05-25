# Chinese Forum Strategy

Status: planning policy

## Purpose

Define a compliant path for Chinese-language and China-adjacent forum discovery without scraping login-protected or anti-bot-protected platforms.

## Provider Posture

| Platform | Initial status | Access posture |
|---|---|---|
| V2EX | Read-only API connector | Use documented API endpoints first; token optional only where endpoints require it; no member/profile/notification/write endpoints in this track. |
| Zhihu | Discovery-only candidate | Search-provider discovery and public selected URL fetch where allowed; no login/cookie/session automation. |
| Baidu Tieba | Discovery-only candidate | Search-provider discovery and public selected URL fetch where allowed; no platform-specific scraping. |
| Douban groups | Discovery-only candidate | Search-provider discovery and public selected URL fetch where allowed; no private group access. |
| Xiaohongshu | Discovery-only candidate | Search-provider discovery only unless a compliant public/API path is documented. |
| Weibo | Discovery-only candidate | Search-provider discovery only unless a compliant public/API path is documented. |
| NGA | Discovery-only candidate | Search-provider discovery and public selected URL fetch where allowed. |
| Other domain-specific forums | Case-by-case | Prefer documented APIs, feeds, or search discovery; otherwise unavailable. |

## Discovery Rules

- Use approved search providers with site filters when policy allows.
- Use V2EX documented APIs before direct page fetch; direct V2EX page fetching is not an API substitute.
- Direct public URL fetch is allowed only through safe fetch/extraction and only when not blocked by login/CAPTCHA/anti-bot controls.
- If a platform blocks access, requires login, or presents CAPTCHA/anti-bot controls, report unavailable.
- Do not use cookies, saved browser sessions, private account state, or proxy evasion.

## Translation And Grounding

Chinese-language results must keep original snippets where useful, label generated translations, and preserve source references. Summaries must not imply broad Chinese-market or cultural consensus from sparse discovered posts.

The V2EX connector can request local language detection and model-generated translation for fetched topics or replies. Translation remains interpretive, source content remains `UNTRUSTED_WEB`, and no translation or source text is written to memory by default.

## Initial Site Filters

Future discovery workflows may use these filters through approved search providers:

- `site:zhihu.com`
- `site:tieba.baidu.com`
- `site:douban.com/group`
- `site:xiaohongshu.com`
- `site:weibo.com`
- `site:v2ex.com`
- `site:bbs.nga.cn`
