# News Freshness Policy

## Freshness Is Part Of The Answer

News output must say what time window it used and when each source was retrieved. If a source lacks a publication time, the output must say the publication time is unknown rather than inventing one.

## Freshness Modes

Future commands may support these modes:

| Mode | Intended Use | Expected Window |
|---|---|---|
| `latest` | Breaking or newest headlines. | Most recent provider/cache/feed data. |
| `today` | Day-level current events. | Current local date or explicit user date. |
| `recent` | Default news freshness. | Recent provider-defined window, normally hours to days. |
| `week` | Slower-moving topics. | Last 7 days where supported. |
| `month` | Background context and trend scans. | Last 30 days where supported. |
| `custom` | User-supplied date range. | Explicit start/end dates. |

If the provider cannot support the requested mode, the workflow must say so and report the effective mode used.

## Date Rules

- Do not fabricate publication dates.
- Do not treat retrieval time as publication time.
- Do not claim an event happened "today" unless source data supports that exact date.
- Use absolute dates in summaries when the user asks about current or recent events.
- Preserve source time zones when provided, or label the time zone unknown.

## Staleness Rules

Future news answers should warn when:

- No source is recent enough for the requested freshness.
- Search results are snippet-only.
- Fetched articles have no publication time.
- Source coverage is sparse or one-sided.
- Provider/cache timestamps are older than configured TTLs.

## Cache Freshness

Cache use is allowed only when the cache entry has a source type, retrieved timestamp, TTL, and content/source hash. The cache must not hide staleness: cached news results must report that cache was used and show the cached retrieval time.

