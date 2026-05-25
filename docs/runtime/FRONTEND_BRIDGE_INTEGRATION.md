# Frontend Bridge Integration

Runtime frontend bridge v1 is a Python contract, not a server.

## Supported Requests

- `runtime.status`
- `runtime.snapshot`

## Explicitly Unsupported Requests

- `approval.approve`
- `approval.deny`
- `tool.execute`
- `policy.change`

Unsupported approval/tool/policy requests must fail closed and use the existing approval and ToolBroker paths instead.

