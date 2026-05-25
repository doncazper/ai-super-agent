# Internet Routing Policy

## Scope

The deterministic router decides whether a user request should attach internet-capable tools. It does not call providers, fetch pages, rewrite the user message, or add router reasoning to the final model prompt.

## Internet Triggers

The router routes to internet-capable tools when the request asks for:

- current, latest, today, recent, news, price, availability, schedule, law, regulation, rule, version, release, or provider/API documentation information;
- an explicit public URL;
- explicit lookup/search/browse/verify/source behavior;
- citations, source lists, references, or source-grounded answers;
- named niche facts that are likely to become stale.

URL requests route to `web.fetch_url`. Citation/source-grounded/current-info requests route to a research-shaped tool set (`web.search` plus `web.fetch_url`) so downstream workflows can search, fetch selected sources, and report limitations. Plain explicit lookup/search requests route to `web.search`.

## Non-Internet Cases

The router keeps normal chat clean for:

- creative writing;
- stable explanations;
- coding questions about the local repo or local docs;
- personal advice without current facts;
- math/reasoning;
- summaries of user-provided text;
- no-tools mode.

Personal-data requests do not route through internet tools. They remain separate approval-gated connector flows.

## Routing Output

`python smart_agent.py router explain "<query>"` and `python smart_agent.py preflight "<query>"` expose:

- `needs_internet`;
- `reason`;
- `suggested_sources`;
- `provider_policy`;
- `tools`;
- `risk_hint`;
- `ask_clarification`.

The output is diagnostic metadata only. It is not inserted into the final model prompt and is not treated as source evidence.

## Safety Rules

- Deterministic rules run first.
- The LLM router is not used by default.
- No-tools mode always disables internet tool attachments.
- Prompt-injection-like text cannot force internet routing.
- Missing or unconfigured providers must return setup hints or structured unavailable results at execution time.
- Provider policy remains free-first, with paid APIs disabled by default.
- Search history and web content are not stored in memory by default.
- Web results remain `UNTRUSTED_WEB` and fetched documents remain `UNTRUSTED_DOCUMENT`.

## Examples

```bash
python smart_agent.py router explain "What is the latest OpenAI API pricing?"
python smart_agent.py router explain "Explain photosynthesis"
python smart_agent.py router explain "Read this page: https://example.com"
python smart_agent.py preflight "Give me a cited answer about SearXNG setup"
```

## Known Limits

The router is intentionally conservative and rule-based. It can suggest internet routing for ambiguous stale facts, but provider availability is resolved by the brokered web/search/research tools, not by the router itself.
