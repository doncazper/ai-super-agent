# App Bridge Pairing

Pairing is required before sensitive App Bridge requests. This document defines the v1 contract only; no pairing server or native app UI is implemented yet.

## Pairing States

- `unpaired`: frontend is known only as an untrusted/local metadata source.
- `pairing_required`: frontend attempted a sensitive request before pairing.
- `paired`: frontend is approved for sensitive metadata surfaces.
- `revoked`: previous pairing is no longer accepted.
- `expired`: previous pairing timed out.

## Sensitive Surfaces

The following surfaces require `pairing_status=paired`:

- `request_action_preview`
- `submit_approval_decision`
- `submit_action_result`
- `fetch_pending_actions`
- `fetch_audit_summary`
- `fetch_connector_status`

`status`, `capabilities`, and `health_check` may be unpaired because they must return only safe metadata and no personal data.

## Future Pairing Requirements

Future pairing must be local-only, auditable, revocable, and explicit. It must not rely on remote access, hidden background daemons, browser cookies, private app databases, or native permission prompts during import.

