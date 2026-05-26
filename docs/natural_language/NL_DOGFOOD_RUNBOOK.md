# Natural-Language Dogfood Runbook

These suites exercise natural-language command understanding with realistic user phrases. They are validation artifacts only: they must not grant permissions, approve actions, call providers, access personal data, send messages, write files, or run queued prompts.

## Suites

Core safe suite:

```bash
python smart_agent.py session start --name nl-command-dogfood
python smart_agent.py dogfood run natural_language_core --session
```

Risky phrase suite:

```bash
python smart_agent.py session start --name nl-command-risky-dogfood
python smart_agent.py dogfood run natural_language_risky --session
```

The risky suite is intentionally `nl preflight` only. It checks that send, personal-data, delete, and prompt-pack requests are classified as not safe to execute and require clarification, setup, dry-run, or approval.

## Failure Triage

After a failed dogfood run:

```bash
python smart_agent.py feedback bug --message "Natural-language dogfood failure: <short summary>"
python smart_agent.py session review --last --create-bugs
```

Attach the failed command id, expected behavior, and failure signal from the suite output. Do not paste raw personal data, secrets, unredacted logs, or web/article/forum content.

## Safety Checks

- Safe suite commands use `python smart_agent.py nl ...` and should state that no commands were executed.
- Risky suite commands use `python smart_agent.py nl preflight ...` only.
- No suite command may invoke send, delete, approval, provider, forum, email, message, calendar, contact, or prompt execution commands directly.
- Session logs are redacted dogfood artifacts, not memory.
- A successful suite is evidence for local dogfood coverage, not live validation.
