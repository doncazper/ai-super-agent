# Skill Dependency Gating

Dependency gates are detection-only checks. They must never install packages, execute scripts, import untrusted skill modules, call providers, call connectors, request permissions, or scan personal files.

Supported dependency declarations:

- environment variable presence
- config key presence
- local binary presence with `shutil.which`
- workspace/project file presence
- platform compatibility
- ToolBroker capability existence
- connector/provider setup metadata
- Python version
- model feature setup hints

Environment variable checks redact values and report only `[set]` or missing. Missing dependencies return `requires_setup`; unknown or unsupported capability/platform dependencies return `blocked` or `unsupported` as appropriate.

Dependency checks are advisory gates. ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger remain the final authority for any future native skill execution.
