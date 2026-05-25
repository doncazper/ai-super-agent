# Forum Dogfood and Eval Runbook

Forum Intelligence dogfood is a release-quality validation layer for Reddit, V2EX, multilingual translation, and Chinese forum discovery. It does not grant new provider permissions, enable scraping, store forum content, or make live credentials mandatory.

## Scope

- Validate Reddit setup/status/search/thread/summarization/retention behavior with setup-gated commands.
- Validate multilingual forum detection, local-model translation labeling, glossary extraction, and source-reference preservation.
- Validate V2EX read-only connector setup and optional live public-topic reads when explicitly configured.
- Validate Chinese forum discovery rules: approved site-filter search, selected public fetch only, and unavailable reporting for blocked/login/CAPTCHA pages.
- Validate fixture-backed eval invariants for source grounding, generated translation labels, prompt-injection resistance, no scraping bypass, no paid-provider defaults, no memory write, retention policy, and provider-call audit evidence.

## Non-Goals

- No Reddit or V2EX live calls unless the connector is explicitly configured.
- No platform-specific Chinese forum scraping.
- No login, cookie, browser-session, CAPTCHA, anti-bot, proxy, or robots bypass.
- No Reddit/forum posting, commenting, voting, DMs, moderation, or write actions.
- No paid providers by default.
- No forum-content training, search-history persistence, or memory writes.

## Suites

Review each suite before running it:

```bash
python smart_agent.py dogfood show reddit_core
python smart_agent.py dogfood show reddit_research
python smart_agent.py dogfood show forum_multilingual
python smart_agent.py dogfood show v2ex
python smart_agent.py dogfood show chinese_forum_discovery
```

Dry-run first:

```bash
python smart_agent.py dogfood run reddit_core --dry-run
python smart_agent.py dogfood run reddit_research --dry-run
python smart_agent.py dogfood run forum_multilingual --dry-run
python smart_agent.py dogfood run v2ex --dry-run
python smart_agent.py dogfood run chinese_forum_discovery --dry-run
```

Session run after review:

```bash
python smart_agent.py session start --name forum-intelligence-dogfood
python smart_agent.py dogfood run reddit_core --session
python smart_agent.py dogfood run reddit_research --session
python smart_agent.py dogfood run forum_multilingual --session
python smart_agent.py dogfood run v2ex --session
python smart_agent.py dogfood run chinese_forum_discovery --session
python smart_agent.py session review --last
python smart_agent.py session end
```

## Eval Commands

Forum evals are fixture-backed and make no live provider calls:

```bash
python smart_agent.py eval run --forums
python smart_agent.py eval report --forums
```

The forum eval category checks that source IDs and original references are preserved, translations are labeled `MODEL_GENERATED_TRANSLATION`, prompt-injection-like source text is ignored, deleted/removed Reddit content is not evidence, blocked Chinese-platform sources are reported as unavailable, paid providers are not used by default, no forum content is written to memory, retention metadata is present, and provider calls are represented in audit evidence.

## Live Provider Notes

- Reddit live validation requires `REDDIT_ENABLED=true` plus OAuth configuration. Setup/status commands must not fetch posts or comments.
- V2EX live validation requires `V2EX_ENABLED=true`; optional token values must remain redacted.
- Chinese forum discovery depends on configured web search providers and selected public fetch policy. If a platform blocks, requires login, or presents CAPTCHA/anti-bot controls, the expected behavior is `unavailable`, not bypass.
- Multilingual translation uses the local LM Studio/Qwopus path by default. Missing local model configuration should return setup guidance instead of cloud or paid translation fallback.

## Release-Gate Signals

Treat the forum dogfood/eval layer as locally ready when:

- Suite YAML validates.
- `all_safe` excludes live Reddit/V2EX/Chinese forum commands requiring credentials or public network access.
- Fixtures contain no real personal data.
- `eval run --forums` passes with mocks/fixtures.
- Command registry entries exist for the new dogfood/eval commands.
- Docs and feature maturity state that live validation remains opt-in.

## Failure Handling

A failure is actionable when output shows any of these:

- Fabricated source ID, permalink, URL, date, or headline.
- Translation without a generated-translation label.
- Source text treated as instructions.
- Deleted/removed Reddit content used as evidence.
- Cookie/session/browser automation or CAPTCHA/anti-bot bypass.
- Paid provider used by default.
- Raw author metadata, query history, or forum body exposed in cache/privacy reports.
- Missing audit evidence for provider/search/fetch/translation/cache/retention operations.
