# Sandbox Backend Abstraction

Status: HERMES-08 scaffold.

This document defines the safe boundary for future sandboxed execution. The current implementation is metadata and dry-run only. It does not execute commands, install Docker or VM tools, run browser automation, start networked sandboxes, mount broad filesystem roots, or run untrusted scripts.

## Scope

- `mock` backend: available by default for policy previews and dry-runs.
- `local_workspace_safe` backend: stubbed; no command execution in v1.
- `docker_rootless`, `macos_sandbox`, `firecracker_vm`, and `browser_sandbox`: planned only.
- `cloud_sandbox`: deferred.

All future executable backends must be routed through ToolBroker, checked by PolicyEngine, approval-gated when risk is HIGH or CRITICAL, and audited.

## Request Model

Sandbox requests carry:

- `sandbox_id`
- `task_type`
- `risk_level`
- `network_allowed`
- `filesystem_roots`
- `time_limit_seconds`
- `memory_limit_mb`
- `command_allowlist`
- `personal_data_allowed`
- `audit_required`

`command` is accepted only so policy can reject attempted arbitrary execution in dry-run output. It is not executed.

## Current Commands

- `python smart_agent.py sandbox backends`
- `python smart_agent.py sandbox policy`
- `python smart_agent.py sandbox dry-run`

These commands are brokered metadata commands. They create no sandbox process and execute no tools inside a sandbox.

## Backend Rules

1. Mock backend only by default.
2. No arbitrary command execution.
3. No network by default.
4. Workspace roots only.
5. Personal data disabled by default.
6. Sandbox operations cannot bypass ToolBroker or PolicyEngine.
7. Sandbox operations must be auditable.
8. Docker, VM, browser, and cloud backends remain planned/stubbed/deferred.
9. Unsupported or planned backends return setup hints.

## Future Implementation Requirements

Before any backend executes real code, add a new prompt and release gate that covers:

- capability manifest entries for executable sandbox operations;
- command allowlist design and tests;
- filesystem mount allowlist;
- network egress policy;
- process timeout and memory enforcement;
- audit correlation IDs;
- HIGH/CRITICAL approval behavior;
- untrusted-script handling;
- cleanup and artifact-retention rules;
- manual QA and dogfood evidence.
