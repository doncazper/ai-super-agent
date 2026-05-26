# Local Environment Setup

Use local environment variables for development, or a local `.env` file when it is ignored by git.

## Safe Setup

1. Copy placeholders from `.env.example` or `docs/templates/env_template.example`.
2. Put real values only in your shell profile, password manager, Keychain, or local `.env`.
3. Run `python smart_agent.py secrets doctor` to check presence without printing values.
4. Run `python smart_agent.py secrets sources` to verify source metadata and `.env` hygiene.
5. Run `python smart_agent.py secrets scan` and `python smart_agent.py git preflight` before committing.

## `.env` Rules

- `.env` and `.env.*` are ignored.
- `.env.example` is tracked and must contain placeholders only.
- Never paste real keys into docs, prompt packs, tests, fixtures, reports, or changelog entries.
- Token paths such as `GMAIL_TOKEN_PATH` should point outside the repo.

## Example

```dotenv
SERPAPI_API_KEY=
BRAVE_SEARCH_API_KEY=
GMAIL_CLIENT_SECRET=
TELEGRAM_BOT_TOKEN=
```

Empty placeholder values are safe. Replace them only in untracked local config.

## Provider Checks

```bash
python smart_agent.py secrets doctor all
python smart_agent.py secrets doctor github
python smart_agent.py secrets doctor microsoft
python smart_agent.py secrets doctor media
```

Provider doctors report present/missing/setup metadata only. They do not call provider APIs, enable paid providers, or print configured values.
