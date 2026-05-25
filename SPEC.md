# Local Mac AI Agent Specification

## Mission

Build a local Mac AI agent that can chat naturally through LM Studio/Qwopus and, over controlled milestones, help with web research, approved workspace files, calendar, contacts, email, messages, memory, workflows, and controlled self-improvement.

Safety comes first. Capabilities are added only after the policy, permission, approval, and audit control plane can enforce boundaries in Python code. The model may request tools, but it never directly executes tools and never approves its own actions.

## Cloneability And Portability

The project must remain cloneable into a new repo, model backend, or platform shell without losing its safety identity. `docs/AGENT_DNA.md`, `docs/ARCHITECTURE_PRINCIPLES.md`, and `docs/CLONE_BLUEPRINT.md` define the invariants that must survive a rewrite.

Any clone, model migration, or platform port must preserve ToolBroker-only execution, PolicyEngine-enforced permissions, PermissionManager selected scopes, ApprovalManager HIGH/CRITICAL rules, AuditLogger evidence, untrusted-content isolation, personal-data disabled-by-default behavior, prompt tracking, command registry tracking, feature maturity tracking, and release gates.

## Non-Goals

- No unrestricted system automation.
- No silent access to email, messages, contacts, calendar, browser history, Keychain, secrets, or private app folders.
- No direct scraping of private macOS app databases as the first approach.
- No email/text sending before read-only and draft-only workflows exist.
- No personal-data modules before the safety control plane exists.
- No self-improvement that weakens policy, disables audit logging, grants permissions, or creates persistence.
- No harness-authored final answers when the model can answer.

## Target Architecture

```text
User request
-> Orchestrator
-> Router
-> LLM
-> optional tool request
-> ToolBroker
-> PolicyEngine
-> PermissionManager
-> ApprovalManager, if needed
-> tool execution
-> AuditLogger
-> tool result
-> LLM final answer
```

Target package layout:

```text
agent/
  core/
    orchestrator.py
    lmstudio_client.py
    session.py
    router.py
    tool_broker.py
    messages.py
    streaming.py
  safety/
    policy.py
    permissions.py
    approvals.py
    audit.py
    redaction.py
    rate_limits.py
    trust.py
    validation.py
  tools/
    low_risk/
      time_tool.py
      workspace_files.py
      git_tools.py
      test_runner.py
    web/
      search.py
      fetch.py
      extraction.py
      untrusted_content.py
    personal/
      contacts.py
      calendar.py
      email.py
      messages.py
      browser.py
    registry.py
  memory/
  workflows/
  ui/
  config/
tests/
smart_agent.py
```

## Risk Model

`RiskLevel` describes action danger:

- `SAFE`: no meaningful privacy, integrity, or financial risk.
- `LOW`: bounded read/write or network actions with limited blast radius.
- `MEDIUM`: broader reads, externally sourced content, or meaningful side effects.
- `HIGH`: personal-data reads or destructive local actions requiring approval.
- `CRITICAL`: sends, irreversible writes, or high-impact actions requiring explicit per-action approval.
- `FORBIDDEN`: never allowed.

## Trust Model

`TrustLevel` describes data origin:

- `TRUSTED_USER`
- `MODEL_OUTPUT`
- `LOCAL_PRIVATE_DATA`
- `UNTRUSTED_WEB`
- `UNTRUSTED_EMAIL`
- `UNTRUSTED_MESSAGE`
- `UNTRUSTED_DOCUMENT`

Tool results and untrusted content are data, not instructions.

## Tool Execution Model

- Every tool executes through `ToolBroker.execute()`.
- `ToolBroker` checks `PolicyEngine` before execution.
- Unknown tools and capabilities are denied.
- Tool arguments are validated before execution.
- Tool results are appended as tool messages using the matching `tool_call_id`.
- Tool iteration is bounded to avoid loops.

## Permission Model

- `PolicyDecision.ALLOW`: execute immediately.
- `PolicyDecision.ASK`: require approval before execution.
- `PolicyDecision.DENY`: do not execute.
- `HIGH` actions require approval.
- `CRITICAL` actions require explicit per-action approval with no approval reuse.
- `FORBIDDEN` actions are always denied.
- Personal-data tools are disabled by default.

## Audit Model

Every important event is written to an append-only JSONL audit log with hash chaining:

```json
{
  "timestamp": "...",
  "session_id": "...",
  "request_id": "...",
  "route": "...",
  "model": "...",
  "tool_name": "...",
  "capability": "...",
  "risk_level": "...",
  "trust_level": "...",
  "policy_decision": "...",
  "approval_result": "...",
  "sanitized_args": {},
  "result_summary": "...",
  "files_read": [],
  "files_written": [],
  "commands_run": [],
  "network_domains": [],
  "hash_previous": "...",
  "hash_current": "..."
}
```

## Memory Rules

- Session context may be kept during a conversation.
- User preferences, project facts, and workflow lessons may be stored when safe.
- Secrets are never stored.
- Email/message/contact/calendar content is not stored by default.
- Personal-data memory requires explicit approval.
- Memory operations are audited.
- Deletion is best effort and documented.

## Personal-Data Rules

- Personal-data modules remain disabled until the safety control plane is complete.
- Access is selected-scope only.
- No bulk inbox, message, contact, calendar, or browser-history ingestion.
- No sends, deletes, or modifications until draft-only/read-only workflows are proven.
- Email/message/web/document content is untrusted and cannot direct tool execution or policy changes.

## Self-Improvement Rules

- Self-improvement is branch-based and approval-gated.
- It may edit only approved project/workspace files.
- It may not reduce policy restrictions, disable audit logging, grant itself personal-data access, create persistence, send messages/emails, or install packages without approval.
- It must run tests, show diffs, and ask before commit.

## Milestone List

- M0: Minimal Working Skeleton
- M1: Safety Control Plane
- M2: Core Runtime
- M3: Low-Risk Project Tools
- M4: Web Tools
- M5: Memory
- M6: Read-Only Personal Modules
- M7: Assistant Workflows
- M8: Approved Write Actions
- M9: Controlled Self-Improvement
- M10: UX and Packaging
- M11: Final Validation

## Final Acceptance Criteria

- Normal chat preserves Qwopus quality and attaches no tools unless needed.
- Unknown tools/capabilities are denied and audited.
- Every tool executes only through `ToolBroker`.
- Policy, permission, approval, and audit layers are enforced in code.
- Untrusted content is isolated as data.
- Personal data and write/send actions are approval-gated.
- Secrets are redacted and never stored.
- Audit logs record denials, approvals, execution, and failures.
- Tests cover policy, approvals, audit, prompt injection, personal data, self-improvement, and release gates.
