# Provider Secret Setup

Status: setup metadata only. Do not paste real values into this file.

Use provider doctor commands to check readiness without exposing values:

```bash
python smart_agent.py secrets doctor
python smart_agent.py secrets doctor all
python smart_agent.py secrets doctor reddit
python smart_agent.py connectors status reddit
python smart_agent.py secrets scan
python smart_agent.py git preflight
```

## Provider Matrix

| provider | secret/config names | cost/default policy | setup/status command | notes |
|---|---|---|---|---|
| Reddit | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_REFRESH_TOKEN`, `REDDIT_ACCESS_TOKEN`, `REDDIT_USER_AGENT` | official API only; disabled until configured | `python smart_agent.py secrets doctor reddit`; `python smart_agent.py reddit doctor` | read-only connector; no posting/commenting/voting/DMs |
| SerpAPI | `SERPAPI_API_KEY` | paid/quota-limited; skipped unless explicitly allowed | `python smart_agent.py secrets doctor serpapi`; `python smart_agent.py connectors status serpapi` | never selected by free-first policy just because a key exists |
| Brave Search | `BRAVE_SEARCH_API_KEY` | quota-limited; optional | `python smart_agent.py secrets doctor brave`; `python smart_agent.py connectors status brave` | no key value printed |
| WeatherAPI | `WEATHERAPI_API_KEY`, `WEATHER_API_KEY` | optional fallback; not default under free-first | `python smart_agent.py secrets doctor weatherapi`; `python smart_agent.py connectors status weatherapi` | Open-Meteo/NWS remain free-first where applicable |
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_IDS`, `TELEGRAM_DEFAULT_CHAT_ID` | disabled by default | `python smart_agent.py secrets doctor telegram`; `python smart_agent.py telegram doctor` | status only; no polling, webhook, chat read, or send |
| Gmail | `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_TOKEN_PATH`, `GMAIL_SCOPES` | disabled by default | `python smart_agent.py secrets doctor gmail`; `python smart_agent.py gmail doctor` | warns on broad/send-capable scopes and repo-local token paths |
| NewsAPI | `NEWSAPI_API_KEY` | optional/fallback; paid/quota policy-gated | `python smart_agent.py secrets doctor newsapi` | news runtime provider remains future/config-gated |
| Media Cloud | `MEDIACLOUD_API_KEY` | optional/configured only | `python smart_agent.py secrets doctor mediacloud` | no paid provider enabled by default |
| Microsoft Graph | `MICROSOFT_CLIENT_ID`, `MICROSOFT_TENANT_ID`, `MICROSOFT_CLIENT_SECRET` | future/stubbed; disabled by default | `python smart_agent.py secrets doctor microsoft` | no Graph calls or personal-data reads |
| GitHub | `GITHUB_TOKEN` | optional/future; scope-sensitive | `python smart_agent.py secrets doctor github` | prefer least-privilege tokens; do not commit PATs |
| Media providers | `MEDIA_PROVIDER_API_KEY`, `COMFYUI_BASE_URL` | real generation disabled/stubbed; no paid API default | `python smart_agent.py secrets doctor media` | `COMFYUI_BASE_URL` is config, not a secret |
| LM Studio / Ollama / llama.cpp | local host/model config | local runtime config; no API key by default | `python smart_agent.py secrets doctor lmstudio`; `ollama`; `llama_cpp` | status checks do not start servers |

## Rotation Checklist

If a secret is exposed:

1. Revoke or rotate it with the provider.
2. Remove the local value from tracked files.
3. Move the value to Keychain/password manager, environment, or ignored `.env`.
4. Rerun `python smart_agent.py secrets scan`.
5. Rerun `python smart_agent.py git preflight`.
6. Document the incident without including the value.
