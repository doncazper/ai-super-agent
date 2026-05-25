# App Bridge Payloads

`agent.platforms.app_bridge` defines model and validation contracts for future App Bridge payloads. Payloads are data envelopes, not permission to execute actions.

## Base Request Fields

- `request_id`
- `frontend_id`
- `frontend_platform`
- `surface`
- `pairing_status`
- `trust_level`
- `audit_correlation_id`

## Action Preview Payload

Action previews must include:

- `requested_capability`
- `action_payload`
- `risk_level`
- `trust_level`
- `audit_correlation_id`

CRITICAL action previews must include exact preview text and a preview hash. Preview creation must remain side-effect-free.

## Approval Payload

Approval payloads must include:

- `action_id`
- `decision`
- `user_interaction_confirmed`
- `approval_manager_required=true`
- `audit_correlation_id`

CRITICAL approvals must also include:

- `exact_preview_confirmed=true`
- `per_action_approval=true`
- `approval_reuse_requested=false`

The frontend cannot approve its own generated action without user interaction, and even a valid frontend approval payload is only input to `ApprovalManager`.

## Result Payload

Results must include:

- `action_id`
- `status`
- `audit_correlation_id`

Result payloads must not include personal data in v1. Future result payloads must be minimized, source-labeled, redacted where needed, and correlated to audit/action IDs.

## Redaction

Keys containing `secret`, `token`, `password`, `api_key`, `apikey`, `client_secret`, or `refresh` are redacted by the validation helper before logging/reporting.
