# Skill Compatibility Matrix

The native skill compatibility matrix records where a reviewed skill is expected to work and what setup it requires. It is metadata-only: it does not import native platform modules, execute skills, call providers, install dependencies, or enable platform-specific behavior.

Dimensions tracked:

- macOS
- iOS companion
- Windows
- Linux
- CLI-only
- Mac app bridge
- local web dashboard
- Python version
- LM Studio requirement
- model tool-call requirement
- required binaries
- required environment variables
- required connectors/providers
- required platform capabilities
- personal-data requirement
- approval requirement
- network requirement
- filesystem requirement
- native app bridge requirement
- status
- setup hint
- tests and dogfood availability

Status values:

- `supported`
- `unsupported`
- `planned`
- `stubbed`
- `requires_setup`
- `blocked`
- `unknown`
- `experimental`

Commands:

```bash
python smart_agent.py skills compatibility
python smart_agent.py skills compatibility native_skill_vetter
python smart_agent.py skills platform matrix
```

Compatibility does not override profiles or policy. A skill that appears supported still must be visible under the selected profile and must execute through `ToolBroker`, `PolicyEngine`, `PermissionManager`, `ApprovalManager`, and `AuditLogger`.
