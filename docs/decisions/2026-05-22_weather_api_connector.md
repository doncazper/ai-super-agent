# Weather API Connector Decision Record

## Connector Name

Weather API.

## User Value

Weather is a useful first post-hardening connector because it gives the agent live, practical information without requiring access to email, messages, contacts, calendar data, browser state, local files, or account content. It is a good test case for adding a real external data provider while preserving the ToolBroker, policy, approval, rate-limit, and audit path.

## Data Accessed

- User-provided location query, such as city, ZIP/postal code, coordinates, or a saved preference if explicitly configured later.
- Weather provider response data, such as current conditions, forecast, alerts, temperature, wind, precipitation, and observation timestamp.
- Provider metadata, such as API status, units, locale, and source timestamp.

The connector must not infer or silently read the user's current location from macOS, IP geolocation, browser state, contacts, calendar, photos, or other personal data.

## Actions Possible

- Fetch current weather for a user-provided location.
- Fetch forecast for a user-provided location and date range within provider limits.
- Normalize provider errors and stale/missing data.
- Return compact source-grounded weather data to the model as data only.

## Read Capabilities

Recommended initial capabilities:

- `weather.current`
- `weather.forecast`

Optional later capability:

- `weather.alerts`

## Write Capabilities

None.

The connector must not create calendar events, reminders, notes, notifications, automations, or stored location preferences in the initial implementation.

## Risk Level

Recommended risk level: `LOW`.

Rationale:

- The action is external network access with a user-provided query.
- It does not require private local data or account access.
- Location strings can still be sensitive, so audit redaction and no history storage are required.

If a future mode uses precise device location or persistent saved home/work locations, that mode should be reassessed as `HIGH` and approval-gated.

## Trust Level of Returned Data

Recommended trust level: `UNTRUSTED_WEB`.

Weather provider responses are external data. They should not instruct the agent, change policy, approve tools, or override user/system messages.

## Permissions Required

- `WEB_ACCESS_ENABLED=true`.
- Explicit provider configuration, such as `WEATHER_PROVIDER`.
- Capability enabled in `config/capabilities.yaml`.
- No macOS Location Services permission in the initial implementation.
- No Full Disk Access.
- No personal-data connector permission.

## Credentials and Secrets Needed

Recommended initial option: provider that supports either no-key access or an optional API key.

Possible environment variables:

- `WEATHER_PROVIDER`
- `WEATHER_API_KEY`
- `WEATHER_TIMEOUT_SECONDS`
- `WEATHER_MAX_FORECAST_DAYS`
- `WEATHER_DEFAULT_UNITS`

Secrets must not be hard-coded, printed in debug output, stored in memory, or written to audit logs.

## Storage Behavior

- Do not persist query history by default.
- Do not persist precise coordinates by default.
- Do not cache provider responses in the first implementation unless a later decision record defines TTL, privacy rules, and audit behavior.
- Audit records should include provider, status, sanitized location summary, network domain, and result summary.

## Memory Behavior

- Do not store locations automatically in long-term memory.
- A user preference such as "use Fahrenheit" may be stored under normal memory rules.
- A home/work/default location preference must require explicit user intent and should be reviewed separately because it can be personal data.

## Audit Requirements

Every weather tool call must be audited through `ToolBroker`.

Audit fields should include:

- `tool_name`
- `capability`
- `risk_level`
- `trust_level`
- `policy_decision`
- `sanitized_args` with location redacted or generalized where practical
- `result_summary`
- `network_domains`
- provider name
- request timestamp and response timestamp when available

Failures and denials must also be audited.

## Approval Requirements

Recommended initial approval requirement: no approval for user-provided city/ZIP weather lookups when capability is enabled and `WEB_ACCESS_ENABLED=true`.

Approval should be required later if:

- The connector reads precise device location.
- The connector stores a default location.
- The connector combines weather with personal calendar, contacts, messages, or email.
- The connector triggers notifications, reminders, automations, or writes.

## Failure Modes

- Provider not configured.
- API key missing or invalid.
- Provider unreachable or timed out.
- Rate limit exceeded.
- Location ambiguous or not found.
- Provider returns stale, partial, malformed, or unit-mismatched data.
- Network disabled by `WEB_ACCESS_ENABLED=false`.
- Capability disabled by policy.
- Audit log write failure.

Failures should return structured errors and should not cause hallucinated weather answers.

## Rollback Options

- Disable `weather.current` and `weather.forecast` in the capability manifest.
- Set `WEB_ACCESS_ENABLED=false`.
- Remove provider environment variables.
- Remove the provider module and tests if needed.
- Audit logs remain append-only evidence; do not silently delete them as rollback.

## Implementation Options

1. Open-Meteo provider, no API key.
   - Pros: no secret required, low setup friction, useful current/forecast data.
   - Cons: provider availability and terms must be reviewed before relying on it; geocoding may require another endpoint.

2. WeatherAPI.com or OpenWeather provider with API key.
   - Pros: mature API, clear current/forecast endpoints.
   - Cons: requires secret handling, account setup, quota/rate-limit management.

3. Generic provider interface only, no real provider.
   - Pros: safest from an external dependency standpoint.
   - Cons: does not advance live connector readiness.

## Recommended Option

Implement a provider abstraction first, then add Open-Meteo as the first real provider if its terms and availability remain acceptable at implementation time. Keep the connector opt-in through config, route all calls through `ToolBroker`, mark returned data as `UNTRUSTED_WEB`, add rate limits, and avoid storing location history.

If provider terms are unclear or unavailable at implementation time, implement only the interface and clear "provider not configured" behavior.

## Alternatives Rejected

- Precise macOS Location Services integration: rejected for the initial implementation because it turns a low-risk external lookup into sensitive personal-location access.
- IP-based geolocation: rejected because it silently infers location and may surprise the user.
- Weather combined with calendar planning: rejected for this connector phase because it combines web data with personal calendar data and should require a separate workflow decision.
- Notification/reminder creation: rejected because it introduces write/automation behavior.
- Storing default home/work locations automatically: rejected because it can persist personal data without clear user approval.

## Tests Required

- Provider missing returns a clear structured error.
- Network disabled by `WEB_ACCESS_ENABLED=false` denies through policy.
- Unknown weather capabilities are denied.
- Configured provider returns normalized current weather.
- Configured provider returns normalized forecast within max-day limits.
- Ambiguous or missing location returns structured error.
- Timeout returns structured error.
- Rate limit is enforced.
- API key is redacted from debug and audit output.
- Location query is not persisted as history by default.
- Results are labeled `UNTRUSTED_WEB`.
- Audit logs successful execution, denial, timeout, and provider errors.
- Tool calls execute only through `ToolBroker`.
