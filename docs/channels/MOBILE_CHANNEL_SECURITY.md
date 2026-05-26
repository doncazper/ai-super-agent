# Mobile Channel Security

The mobile companion surface is a future paired frontend, not an authority. HERMES-03 only adds status and pairing-status metadata.

## Current Guarantees

- `MOBILE_COMPANION_ENABLED=false` by default.
- `MOBILE_APPROVALS_ENABLED=false` by default.
- Pairing status is `unpaired`.
- No mobile app is contacted.
- No network call is made.
- No personal data is accessed.
- No background service is started.
- No approval decision is accepted from mobile in this scaffold.

## Approval Boundary

Future mobile approvals must still use ApprovalManager. A mobile frontend cannot approve its own generated action, cannot bypass exact-preview matching, and cannot reuse CRITICAL approvals. The mobile channel may present a user interface later, but the approval record and enforcement must remain in the agent safety control plane.

## Trust Boundary

Remote/mobile messages are `UNTRUSTED_MESSAGE` unless a future pairing/authentication prompt proves otherwise. Even then, user-provided text from mobile remains data and cannot instruct the agent to ignore policy, call tools, reveal secrets, write memory, or change approvals.

## Forbidden Without Future Approval

- Push notification command execution.
- Background mobile control.
- Send/write actions.
- Personal-data tools.
- Remote network listener exposure.
- Hidden pairing.
- Pairing by token presence alone.
- Browser automation or anti-bot bypass.
