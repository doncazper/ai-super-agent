# macOS Messages Probe Results

Status: metadata-only probe implemented; approved-send adapter uses a separate gated live-send probe

Date: 2026-05-23

## Scope

Determine whether this Mac can safely support Messages.app automation metadata checks without sending. The approved-send adapter has its own disabled-by-default live-send probe and never treats this metadata probe as send proof.

## Command

```bash
python smart_agent.py messages probe
python smart_agent.py messages probe --explain-permissions
```

## Result Schema

- `supported`: `false`, `true`, or `unknown`
- `platform`
- `messages_app_found`
- `automation_permission_status`
- `send_capability_known`: always false in this task
- `limitations`
- `next_steps`
- `risk_level`
- `requires_user_setup`

## Safety Boundaries

- No real send.
- No private Messages database read.
- No `~/Library/Messages` access.
- No Full Disk Access requirement.
- No AppleScript send implementation.
- No UI scripting that presses Send.
- No Messages account status scraping.
- No message content reads.

## Interpretation

The metadata probe can show whether macOS, Messages.app, and harmless AppleScript metadata lookup are available. It cannot prove send safety. The macOS approved iMessage send adapter v1 therefore requires `messages macos live-send-probe --to ...` plus connector enablement, recipient allowlisting, rate-limit checks, exact Action Center preview, CRITICAL per-action approval, and no approval reuse before `messages send --from-action ...` can attempt a send.
