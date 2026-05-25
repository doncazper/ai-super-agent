# News Source Grounding

## Grounding Contract

News Intelligence must answer from returned source data, not from model memory. For current facts, source data is mandatory.

Future outputs must distinguish:

- Source-backed fact.
- Source-derived quote or paraphrase.
- Inference from multiple sources.
- Missing source data.
- Conflicting or sparse coverage.

## Source Bundle Requirements

Each news source reference should include:

- Stable source ID.
- Title/headline.
- URL or provider identifier.
- Domain/source name.
- Provider/acquisition path.
- Retrieved timestamp.
- Published timestamp, if available.
- Evidence type: `snippet_only`, `feed_item`, `sitemap_entry`, `fetched_article`, `provider_metadata`, or `failed`.
- Trust label: `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`.
- Reliability signals when available.

## Citation Rules

- Never cite a fabricated URL.
- Never cite a failed fetch as supporting evidence.
- Label snippet-only results clearly.
- Report blocked, paywalled, login-required, CAPTCHA, robots-disallowed, malformed, unavailable, and fetch-failed sources in a failure/limitations section.
- Do not cite a source for claims it did not support.
- If source claims conflict, say which sources conflict and avoid false certainty.

## Summary Rules

Future news summaries should include:

- Short answer or brief.
- Key source-backed facts.
- Source list.
- Coverage and freshness limitations.
- Fetch/provider failures when applicable.
- Clear inference labels.

## Multilingual Sources

Translations are generated interpretations, not new sources. Multilingual news output must preserve source IDs, note original language when known, label translations as model-generated, and avoid claiming cross-language consensus from sparse data.

