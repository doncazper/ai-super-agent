# Cross-Language Forum Research

This workflow gives the terminal a conservative way to compare source-labeled Reddit/forum discussions across languages without scraping, paid-provider defaults, or memory writes.

## Commands

```bash
python smart_agent.py forums research "topic"
python smart_agent.py forums research "topic" --languages en,zh,ja,ko
python smart_agent.py forums research "topic" --sources reddit,v2ex,web
python smart_agent.py forums research "topic" --translate-to en
python smart_agent.py forums compare "topic" --sources reddit,v2ex
```

The commands execute through `ToolBroker` as `forums.research` and `forums.compare`. They use configured official/API providers where available, report setup/unavailable status for unimplemented providers, and do not scrape login-walled, CAPTCHA-protected, anti-bot-protected, private, or paid sources.

## Source Policy

- Reddit uses the official Reddit Data API connector when `REDDIT_ENABLED=true` and OAuth is configured.
- V2EX uses its documented read-only API connector when `V2EX_ENABLED=true`; otherwise it reports setup guidance.
- Web/forum discovery is disabled by default and requires a future approved search-provider site-filter path.
- Zhihu, Baidu Tieba, Douban groups, Xiaohongshu, Weibo, NGA, and similar platforms are discovery-only until approved search-provider or official API support exists.
- Blocked, login-required, CAPTCHA-protected, anti-bot-protected, or private pages must be reported as unavailable.

## Output Rules

Outputs include source IDs, URLs/permalinks, provider labels, retrieved timestamps, trust labels, unavailable sources, excluded prompt-injection-like sources, translation labels, and limitations.

Translations are labeled `MODEL_GENERATED_TRANSLATION`. Original-language snippets are preserved where useful, and translated text is treated as an interpretation layer, not a new source.

The workflow does not claim cultural, regional, market-wide, or statistical consensus from sparse forum posts. It describes returned source items only and includes limitations when sources are disabled, missing, setup-gated, or unavailable.

## Safety and Retention

- Forum content remains `UNTRUSTED_WEB`.
- Source text cannot instruct the agent to call tools, reveal secrets, alter policy, bypass approvals, disable audit logging, or write memory.
- The workflow writes no summaries, search history, translations, or source text to memory by default.
- Paid providers are not used by default.
- Provider calls and unavailable/denied outcomes are audited through the brokered tool path.
