# API Key Inventory

This inventory tracks expected secret/config names without storing values.

| env_name | provider | secret? | required_for | default_enabled | storage recommendation | rotation note |
|---|---|---:|---|---:|---|---|
| `REDDIT_CLIENT_ID` | Reddit | no | Reddit OAuth app id | false | env or password manager | rotate app if exposed with secret |
| `REDDIT_CLIENT_SECRET` | Reddit | yes | Reddit OAuth | false | Keychain/password manager/env | rotate Reddit app secret |
| `REDDIT_REFRESH_TOKEN` | Reddit | yes | Reddit OAuth refresh flow | false | Keychain/password manager/env | revoke Reddit app grant |
| `SERPAPI_API_KEY` | SerpAPI | yes | optional paid/quota web search | false | Keychain/password manager/env | rotate in SerpAPI dashboard |
| `BRAVE_SEARCH_API_KEY` | Brave Search | yes | optional quota web search | false | Keychain/password manager/env | rotate in Brave dashboard |
| `WEATHERAPI_API_KEY` | WeatherAPI | yes | optional WeatherAPI provider | false | Keychain/password manager/env | rotate in provider dashboard |
| `TELEGRAM_BOT_TOKEN` | Telegram | yes | future Telegram status/send-gated workflows | false | Keychain/password manager/env | revoke token with BotFather |
| `TELEGRAM_ALLOWED_CHAT_IDS` | Telegram | sensitive config | future allowlist | false | env or password manager | review allowlist if exposed |
| `GMAIL_CLIENT_ID` | Gmail | no | OAuth app id | false | env or password manager | rotate app if paired with secret |
| `GMAIL_CLIENT_SECRET` | Gmail | yes | Gmail OAuth | false | Keychain/password manager/env | rotate OAuth client |
| `GMAIL_TOKEN_PATH` | Gmail | path to token | OAuth token cache location | false | outside repo | revoke OAuth grant if token exposed |
| `GMAIL_SCOPES` | Gmail | sensitive config | OAuth scope review | false | env or config | prefer narrow scopes |
| `NEWSAPI_API_KEY` | NewsAPI | yes | optional news provider | false | Keychain/password manager/env | rotate in provider dashboard |
| `MEDIACLOUD_API_KEY` | Media Cloud | yes | optional news provider | false | Keychain/password manager/env | rotate in provider dashboard |
| `MICROSOFT_CLIENT_ID` | Microsoft Graph | no | future app id | false | env or password manager | rotate app if paired with secret |
| `MICROSOFT_TENANT_ID` | Microsoft Graph | sensitive config | future tenant routing | false | env or password manager | review tenant exposure |
| `MICROSOFT_CLIENT_SECRET` | Microsoft Graph | yes | future OAuth | false | Keychain/password manager/env | rotate app secret |
| `GITHUB_TOKEN` | GitHub | yes | optional future GitHub API calls | false | Keychain/password manager/env | revoke/rotate PAT |
| `COMFYUI_BASE_URL` | ComfyUI | no | local media provider URL | false | `.env.example` placeholder ok | not a secret |
| `MEDIA_PROVIDER_API_KEY` | future media | yes | future provider | false | Keychain/password manager/env | provider-specific |
| `OPENAI_API_KEY` | optional/future | yes | future cloud model/API provider | false | Keychain/password manager/env | rotate in provider dashboard |
| `ANTHROPIC_API_KEY` | optional/future | yes | future cloud model/API provider | false | Keychain/password manager/env | rotate in provider dashboard |
| `OTHER_PROVIDER_API_KEY` | future provider | yes | future configured provider | false | Keychain/password manager/env | provider-specific |

All real values must stay outside tracked files. Placeholder-only rows are allowed in `.env.example` and templates.

Use `python smart_agent.py secrets doctor <provider>` to check provider-specific readiness without printing values. See `docs/secrets/PROVIDER_SECRET_SETUP.md` for command mapping, cost/default policy notes, and rotation guidance.
