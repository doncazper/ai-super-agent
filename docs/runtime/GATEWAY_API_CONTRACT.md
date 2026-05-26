# Gateway API Contract

Status: CANON-03 metadata contract.

## Request Envelope

- `request_id`
- `frontend_id`
- `frontend_type`
- `correlation_id`
- `requested_action`
- `capability_id`
- `payload`
- `trust_level`
- `risk_level`
- `approval_required`
- `created_at`

## Response Envelope

- `request_id`
- `correlation_id`
- `status`
- `requires_review`
- `summary`
- `redacted_payload`
- `tool_execution`
- `approved_by_gateway`
- `policy_mutation`
- `capability_mutation`
- `created_at`

## Rules

- Direct tool execution requests are blocked.
- HIGH/CRITICAL or approval-required requests return `requires_review`.
- Responses are redacted.
- No server starts during import or status commands.
- CLI remains supported.
