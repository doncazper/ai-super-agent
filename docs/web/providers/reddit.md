# Reddit Official API Provider

Status: read-only setup-gated stub.

The Reddit official API provider exists only as framework metadata in this milestone. It requires OAuth configuration before any future live use and explicitly forbids Reddit web scraping as an API substitute.

Commands:

```bash
python smart_agent.py web api-status reddit
python smart_agent.py web api-search reddit "topic"
```

Safe defaults:

- `REDDIT_ENABLED=false`
- OAuth required for future live calls.
- No unauthenticated traffic.
- No posting, commenting, voting, DMs, or moderator actions.
- No author metadata storage by default.
- No Reddit web scraping fallback.

Future Reddit implementation must remain read-only unless a later approved track changes that policy.

Secret setup is tracked in `docs/secrets/PROVIDER_SECRET_SETUP.md`. Run `python smart_agent.py secrets doctor reddit`, `python smart_agent.py reddit doctor`, or `python smart_agent.py connectors status reddit` to inspect OAuth readiness without printing client secrets, access tokens, refresh tokens, or fetching Reddit content.
