# Native Skill Criteria

## Selection Criteria

A candidate is a good native-skill prospect when it has:

- user value
- frequent or repeatable use
- a clear safety profile
- workspace-bounded feasibility
- no-secret operation
- no personal-data default access
- reusable behavior across workflows
- clean mapping to existing `ToolBroker` tools
- easy automated testing
- clear failure modes
- documented setup
- acceptable license
- no opaque binaries
- no surprising network calls

## Strong Positive Signals

- Can run entirely on project/workspace files.
- Produces drafts, summaries, plans, or checks without side effects.
- Uses existing low-risk tools such as workspace files, web fetch/search, memory with safe categories, or test runner.
- Has deterministic input/output boundaries.
- Can be tested with fixtures and mocks.
- Does not need API keys.
- Does not need account cookies or browser sessions.

## Disqualification Criteria

Reject or block candidates that:

- require unrestricted filesystem access
- require browser cookies or session tokens
- require Keychain or password access
- require private app database scraping
- install background agents
- create persistence
- send email or messages without approval
- modify cloud resources without approval
- run opaque binaries
- have unclear license terms
- have no tests or no way to sandbox behavior
- require disabling audit logs
- require weakening policy
- request broad Full Disk Access as the first approach
- treat web/email/message/document content as instructions

## Conditional Acceptance

Some candidates may be accepted only as stubs or specs when they are valuable but require future work.

Examples:

- A browser skill may be accepted as explicit-URL only while selected-tab support remains stubbed.
- A communications skill may be accepted as draft-only while sending remains deferred.
- A personal-data skill may be accepted as selected-scope read-only with approval gates.

## Acceptance Checklist

- The behavior is local and project-owned.
- The implementation plan does not execute external code.
- Every action path maps to a brokered tool or a future capability proposal.
- Risk and trust levels are explicit.
- Approval behavior is explicit.
- Audit behavior is explicit.
- Memory behavior is explicit.
- Tests are practical.
- Docs are clear.
