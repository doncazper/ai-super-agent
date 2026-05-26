# Memory Injection Policy

Memory context injection is an explicit, brokered operation. Web, email, message, forum, document, or model content cannot instruct the agent to inject memory, reveal secrets, weaken policy, or call tools.

## Preview Before Injection

```bash
python smart_agent.py memory context-preview "query" --max-records 3 --max-chars 1200
```

`context-preview` returns the exact bounded context candidate without injecting it into a prompt. It reports selected memory IDs, truncation status, and the character budget.

## Injection Rules

- Use `memory.context` only through `ToolBroker`.
- Exclude personal memory by default.
- Refuse `include_personal=true` until a future approved personal-memory design exists.
- Redact secret-looking values, email addresses, and phone-like values.
- Enforce record and character limits.
- Audit selected memory IDs in the result summary.
- Do not write memory during preview or injection.

## Forbidden

- Secret injection.
- Personal-data injection without explicit future approval.
- Untrusted content controlling memory selection.
- Cloud embedding calls by default.
- Memory query/history persistence by default.
