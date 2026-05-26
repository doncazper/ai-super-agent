# Natural-Language Bug Triage

Use this flow when a natural-language request is misunderstood, mapped to the wrong command, should have asked a clarifying question, should have been denied, or should have required approval.

## Feedback Tags

- `misunderstood_intent`
- `wrong_command_suggested`
- `should_have_clarified`
- `should_have_denied`
- `should_have_required_approval`
- `executed_when_should_not`
- `failed_to_find_command`
- `poor_natural_language_answer`

## Commands

Attach feedback to the last redacted session command and create a local bug report:

```bash
python smart_agent.py feedback nl-bug --last --expected-intent weather.current --tag should_have_clarified
```

Create a sanitized natural-language eval regression fixture from that bug:

```bash
python smart_agent.py bugs create-nl-regression BUG-0001
```

List generated natural-language regression fixtures:

```bash
python smart_agent.py nl regressions list
```

## Rules

- Feedback attaches to an active or recent session command.
- Bug reports and generated fixtures are redacted local QA artifacts.
- Generated fixtures default to `should_execute: false` until reviewed.
- Personal data, secrets, raw logs, and unredacted provider output must not be copied into regression fixtures.
- Creating a regression fixture does not fix the bug and does not mark the natural-language layer mature by itself.
