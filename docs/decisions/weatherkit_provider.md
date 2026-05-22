# WeatherKit Provider Decision Record

Date: 2026-05-22

Status: Planning stub only. Full JWT signing and live API calls are not implemented.

## Connector Name

WeatherKit REST API provider (`weatherkit`).

## User Value

WeatherKit may provide Apple-sourced weather forecasts and alerts through the same weather abstraction used by Open-Meteo and NWS. It is useful only for users who already have Apple Developer Program access and want Apple Weather data specifically.

## Data Accessed

- User-provided location coordinates or a location string resolved by an approved geocoder.
- WeatherKit weather datasets, potentially including current weather, forecast data, and weather alerts depending on requested endpoint and Apple API support.
- No device location, IP geolocation, macOS Location Services, personal contacts, calendar, email, messages, or browser history.

## APIs Available

Apple documents WeatherKit as a REST API for apps and services that need current and forecast weather information. Apple also documents weather alert resources and request authentication for the REST API.

Relevant official documentation:

- [WeatherKit REST API](https://developer.apple.com/documentation/weatherkitrestapi)
- [Request authentication for WeatherKit REST API](https://developer.apple.com/documentation/weatherkitrestapi/request-authentication-for-weatherkit-rest-api)
- [Create a services identifier and private key for WeatherKit](https://developer.apple.com/help/account/capabilities/create-a-services-identifier-and-private-key-for-weatherkit/)

## Credentials Needed

WeatherKit REST access requires Apple developer credentials, not a simple static API key:

- Apple Developer Program membership.
- WeatherKit-enabled Services ID.
- Team ID.
- Key ID.
- WeatherKit private key file, normally a `.p8` file.

Planned local environment variables:

- `WEATHERKIT_TEAM_ID`
- `WEATHERKIT_SERVICE_ID`
- `WEATHERKIT_KEY_ID`
- `WEATHERKIT_PRIVATE_KEY_PATH`

Secrets must not be committed, printed, logged, cached, or stored in memory.

## Apple Developer Requirements

The user must create/configure WeatherKit access in the Apple Developer account. Apple’s account help says WeatherKit web communication uses an authentication private key to sign developer tokens. The provider should remain optional because many users will not have this account setup and because Open-Meteo/NWS already cover no-key weather use cases.

## JWT / Signing Requirements

WeatherKit REST requests require signed developer tokens. Apple documents JWT-based authentication and a key identifier (`kid`). Implementing full support would require:

- Reading the private key from `WEATHERKIT_PRIVATE_KEY_PATH`.
- Generating an ES256 JWT with Apple-required claims and headers.
- Setting the request authorization header.
- Refreshing short-lived tokens safely.
- Redacting token, key path, Team ID, Service ID, and Key ID from debug output and audit logs.

This pass intentionally does not implement signing.

## Risk Level

LOW for public weather lookup by user-provided location, matching existing weather capabilities.

Security posture:

- `UNTRUSTED_WEB` returned data.
- ToolBroker-only execution.
- PolicyEngine checked.
- AuditLogger records calls and denials without credential values.
- No memory storage by default.
- No inferred location.

## Config Needed

Minimum:

```bash
WEATHER_PROVIDER=weatherkit
WEATHERKIT_TEAM_ID=
WEATHERKIT_SERVICE_ID=
WEATHERKIT_KEY_ID=
WEATHERKIT_PRIVATE_KEY_PATH=
```

Optional existing weather config still applies:

```bash
WEATHER_UNITS=metric
WEATHER_CACHE_ENABLED=true
WEATHER_CACHE_TTL_SECONDS=
WEATHER_DEFAULT_LOCATION=
```

## Why Optional

WeatherKit is optional because:

- It requires Apple Developer Program access and WeatherKit setup.
- It requires private-key/JWT signing, increasing secret-handling complexity.
- Open-Meteo is no-key and global.
- NWS is no-key for U.S. forecasts and alerts.
- The project already has usable safe weather functionality without Apple credentials.

## Comparison

| Provider | Credentials | Coverage | Alerts | Complexity | Current Status |
|---|---|---|---|---|---|
| Open-Meteo | None | Broad/global | Not supported in current provider | Low | Implemented default provider |
| NWS | None | U.S. only | Supported | Medium | Implemented optional provider |
| WeatherKit | Apple Developer credentials and JWT signing | Apple Weather-supported regions | Available through WeatherKit resources where supported | High | Stub only |

## Recommended Option

Keep WeatherKit as a stub until the user explicitly approves JWT/signing implementation after reviewing this decision record. Continue using Open-Meteo as default and NWS for U.S. alerts.

## Alternatives Rejected

- Hard-code WeatherKit credentials: rejected because secrets must never be committed.
- Read credentials from Keychain automatically: rejected for this phase because it would introduce new secret and macOS privacy handling.
- Implement signing before decision review: rejected by scope.
- Use device location to improve WeatherKit calls: rejected; no location inference or macOS Location Services.

## Tests Required

- WeatherKit not configured returns a clear structured error.
- WeatherKit env presence check works.
- WeatherKit secrets are not returned in tool output.
- WeatherKit secrets are not written to audit logs.
- WeatherKit provider is not selected unless `WEATHER_PROVIDER=weatherkit` or per-request provider override is used.
- Full signing tests only after explicit approval for implementation.
