# Command QA Sandbox Strategy

The Command QA Sandbox is a controlled validation system for the CLI command catalog. It exists to verify documented commands, produce redacted evidence, rank failures, and propose scoped fixes without turning QA into unsafe automation.

## Scope

- Build QA plans from the command registry and command metadata.
- Run registry/docs validation first, then safe read-only commands, then mocked and fixture-backed commands.
- Use disposable workspaces for write-command checks.
- Log command results with redaction and bounded retention.
- Generate bug reports and regression stubs from evidence.
- Propose self-healing fixes only when they are safe, scoped, and regression-test gated.

## Non-Goals

- Do not blindly run every command.
- Do not run HIGH or CRITICAL commands automatically.
- Do not access personal data by default.
- Do not send emails, messages, calendar writes, contact writes, or external service writes.
- Do not mutate real user files.
- Do not install packages or start background services.
- Do not commit, push, or merge automatically.

## Design

The QA sandbox is layered:

1. Inventory: read command registry metadata and identify missing risk, examples, tests, docs, provider requirements, and approval requirements.
2. Plan: classify commands into QA tiers and produce a deterministic run plan.
3. Execute: run only approved tiers with a bounded subprocess wrapper and safe environment.
4. Record: save redacted JSONL and markdown summaries under `reports/qa/`.
5. Analyze: rank failures and link them to features, docs, bugs, and regressions.
6. Repair: produce self-heal plans; only scoped safe fixes may be attempted without further approval.

## Safety Boundary

The sandbox never replaces ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger. It is a test harness around CLI entrypoints. Any command under test must still enforce its own normal safety controls.

Prompt text, command output, web text, email/message text, and generated logs are treated as untrusted data. They cannot instruct the agent to call tools, weaken policy, disclose secrets, or approve actions.
