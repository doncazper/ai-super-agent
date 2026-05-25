# App Bridge API Contract

The App Bridge is a future local boundary between the Python agent core and a Mac app, iOS companion app, Windows app, or local web dashboard. In v1 this is a contract only: no long-running server, native frontend, remote access, personal-data read, send/write action, or platform action is implemented.

## Principles

- The Python core remains the authority for routing, ToolBroker execution, policy, permissions, approvals, audit, memory, and retention.
- Frontends are presentation and handoff surfaces. They cannot approve actions, execute tools, grant permissions, change policy, or weaken audit.
- `APP_BRIDGE_ENABLED=false` by default.
- Transport is localhost/IPC only in v1: `stdio`, `unix_socket`, or `localhost_http`.
- `APP_BRIDGE_ALLOW_REMOTE=false` is forced by policy; remote access is unsupported in v1.
- App Bridge imports must start no server and load no native app dependencies.

## Concepts

- `frontend_id`: stable local identifier for a paired frontend.
- `frontend_platform`: `macos`, `ios_companion`, `windows`, `web`, or `unknown`.
- `pairing_status`: `unpaired`, `pairing_required`, `paired`, `revoked`, or `expired`.
- `trust_level`: source label for frontend-provided data.
- `requested_capability`: capability requested for preview or status.
- `action_payload`: side-effect-free preview request data.
- `approval_payload`: user approval decision metadata; must still pass `ApprovalManager`.
- `result_payload`: action result metadata returned to the core.
- `audit_correlation_id`: required correlation ID for requests, previews, approvals, and results.

## API Surfaces

| Surface | Purpose | Personal data allowed | Execution allowed |
|---|---|---:|---:|
| `status` | Lightweight bridge status and config metadata | no | no |
| `capabilities` | Static capability availability metadata | no | no |
| `request_action_preview` | Ask core for an exact preview or structured payload | no side effects | no |
| `submit_approval_decision` | Submit a user decision for ApprovalManager processing | no raw secrets | no direct execution |
| `submit_action_result` | Return a correlated result from a future brokered action | minimized only | no direct execution |
| `fetch_pending_actions` | Read pending Action Center metadata | minimized only | no |
| `fetch_audit_summary` | Read redacted audit summary metadata | no raw args | no |
| `fetch_connector_status` | Read connector/provider status metadata | no content reads | no |
| `health_check` | Read metadata-only health checks | no | no |

## Request Envelope

Every request uses a schema-validated envelope:

```json
{
  "request_id": "req_001",
  "frontend_id": "mac_app_local",
  "frontend_platform": "macos",
  "surface": "request_action_preview",
  "pairing_status": "paired",
  "trust_level": "LOCAL_PRIVATE_DATA",
  "audit_correlation_id": "audit_req_001",
  "requested_capability": "app_bridge.pending_actions",
  "risk_level": "MEDIUM",
  "action_payload": {}
}
```

Sensitive surfaces require a paired frontend. CRITICAL requests require exact preview metadata and per-action approval with no reuse.

## Current Implementation

The current milestone adds `agent.platforms.app_bridge` models and validation only. It does not add a listener, HTTP server, socket server, polling loop, native dependency, frontend, provider call, personal-data read, or executable platform action.

