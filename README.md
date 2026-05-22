# Local Mac AI Agent

A local-first Mac AI agent built safety-first. The initial runtime talks to LM Studio through the OpenAI-compatible chat completions API and can execute only approved tools through a brokered policy/audit layer.

## Current Status

M0-M11 are complete:

- LM Studio chat client.
- Thin orchestrator.
- `--no-tools` mode for clean Qwopus chat.
- Safe `time.get_current_time` tool.
- `ToolBroker` enforcement.
- Manifest-backed `PolicyEngine`.
- Approval manager that denies approval-gated actions by default until a user UI exists.
- Hash-chained audit JSONL.
- Deterministic router so normal chat attaches no tools by default.
- Redacted debug payload formatting.
- Workspace-bounded filesystem tools.
- Fixed git status/diff/branch tools, with commit approval-gated.
- Fixed pytest runner inside the project repo.
- Web search tool with clear provider-not-configured behavior.
- Web fetch tool with blocked-domain checks, binary-download refusal, script-stripping extraction, and untrusted-content wrapping.
- Session and SQLite-backed persistent memory.
- Memory tools refuse secrets and personal content by default.
- Personal-memory storage is approval-gated.
- Read-only personal module interfaces are present but disabled by default.
- Email/message reply drafting is draft-only and never sends.
- Assistant workflows compose existing tools only through `ToolBroker`.
- Workflow action reports show each step and result.
- Approved write/send action tools are present but disabled by default.
- Critical write/send actions require explicit per-action approval with preflight summaries.
- Controlled self-improvement manager supports propose, branch-bound implement, run-tests, show-diff, and approval-gated commit.
- Self-improvement blocks protected safety file edits and safety-weakening content.
- CLI inspection commands for tools, permissions, audit, memory, config, setup, and interactive entry.
- Local packaging/setup docs.
- Release-gate validation tests.
- M0-M11 tests.

Higher-risk capabilities are documented but locked until their prerequisites pass.

## Setup

1. Install Python 3.11+.
2. Create a virtual environment.
3. Install test dependencies:

```bash
python -m pip install -e ".[dev]"
```

4. Start LM Studio with the OpenAI-compatible server enabled at `http://localhost:1234/v1`.
5. Set the model:

```bash
export LMSTUDIO_MODEL="your-local-model-name"
```

## Usage

No-tool chat:

```bash
python smart_agent.py --no-tools "Explain RCS vs iMessage"
```

Tool-enabled chat:

```bash
python smart_agent.py --debug "What time is it?"
```

Web tools:

```bash
python smart_agent.py --debug "Read this URL https://example.com"
python smart_agent.py --debug "Look up local AI news"
```

`web.search` currently returns a clear error until a supported provider is configured. `web.fetch_url` treats fetched pages as untrusted data and refuses binary downloads by default.

Memory tools:

```bash
python smart_agent.py --debug "Remember that I prefer concise answers"
```

Memory refuses secrets and personal email/message/contact/calendar content by default. Approval-gated personal memory exists as a separate capability.

Inspection commands:

```bash
python smart_agent.py tools list
python smart_agent.py permissions show
python smart_agent.py audit tail
python smart_agent.py memory list
python smart_agent.py config show
python smart_agent.py setup
```

## Architecture

Runtime flow:

```text
User request
-> Orchestrator
-> Router
-> LLM
-> optional tool request
-> ToolBroker
-> PolicyEngine
-> PermissionManager/ApprovalManager when present
-> tool execution
-> AuditLogger
-> tool result
-> LLM final answer
```

The model writes final answers. The harness executes only validated tool calls through `ToolBroker`.

## Safety Boundaries

- Unknown tools are denied.
- Unknown capabilities are denied.
- Forbidden actions are denied.
- Higher-risk actions require approval in later milestones.
- Tool calls and denials are audited.
- Webpage content is wrapped as untrusted data.
- Long-term memory refuses secrets and personal content by default.
- Personal modules are disabled by default and selected-scope only.
- Email/message drafts do not send.
- Approved send/write actions are disabled by default and require per-action approval.
- Personal-data and write/send modules are locked until later approval gates.
