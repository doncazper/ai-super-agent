# Natural-Language Preflight

Natural-language preflight converts a loose request into advisory execution metadata. It does not execute commands, call tools, call providers, read personal data, write files, write memory, or consume approvals.

## Commands

- `python smart_agent.py nl preflight "<request>"` builds a structured plan.
- `python smart_agent.py nl explain "<request>"` shows the route, risk, approval, dry-run, and missing-requirement summary.
- `python smart_agent.py nl suggest "<request>"` shows the candidate exact command and whether it is safe to run manually.

## Plan Fields

Each plan includes `plan_id`, `original_request`, `intent`, `command`, `args`, `risk_level`, `trust_level`, `approval_required`, `dry_run_required`, `toolbroker_required`, `expected_side_effects`, `provider_requirements`, `missing_requirements`, `audit_preview`, `memory_behavior`, and `safe_to_execute`.

`safe_to_execute` can be true only for SAFE or LOW risk plans with no approval requirement, no dry-run requirement, no missing setup/provider requirements, and a command registry entry that is safe to run directly.

## Safety Rules

- HIGH and CRITICAL plans are never safe to execute from natural language.
- Personal-data requests require setup and approval context.
- Send/write requests require dry-run, preview, and approval through existing gates.
- Unknown or ambiguous requests are denied as execution plans and point back to command help.
- Provider-dependent web/research plans report missing setup rather than calling providers.
- The audit preview is metadata only and records `tools_called=[]` and `commands_executed=[]`.

Real execution must use the exact command path and existing ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger controls.
