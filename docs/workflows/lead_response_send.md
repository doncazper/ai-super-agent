# Approved Lead Response Send Workflow v1

Approved Lead Response Send v1 turns a reviewed lead response draft into an exact Action Center item and then routes it through the safest available channel path. It is intentionally conservative: most channels return handoff or setup fallbacks instead of sending.

## Scope

- Create a CRITICAL Action Center send proposal from a lead-linked `MessageDraft`.
- Require exact recipient/body/channel preview before approval.
- Reject bulk recipients and attachments in v1.
- Route approved actions to existing channel gates:
  - `ios_compose`: create a user-confirmed compose handoff payload; the user still taps Send or Cancel.
  - `manual_handoff`: create save/copy handoff actions only.
  - `macos_messages`: use the existing disabled-by-default adapter only if config, allowlist, live probe, rate limit, and Action Center approval all pass.
  - `apple_messages_for_business`: return setup/fallback until a provider is configured.
  - `telegram`/`email`: return setup/fallback unless existing approved-send adapters are built and enabled.
- Record local lead status after a verified send or explicit handoff.

## Non-Goals

- No auto-send.
- No bulk lead responses.
- No provider send bypass.
- No direct `lead.send_approved` tool execution.
- No message database scraping.
- No Full Disk Access.
- No memory storage of lead or draft content by default.
- No silent iOS or macOS sending.

## Commands

```bash
python smart_agent.py leads create-send-action <lead_id> <draft_id>
python smart_agent.py leads send --from-action <action_id>
python smart_agent.py leads handoff <draft_id>
python smart_agent.py leads mark-responded <lead_id>
```

Useful review commands:

```bash
python smart_agent.py actions show <action_id>
python smart_agent.py actions approve <action_id>
python smart_agent.py actions deny <action_id>
```

## Workflow

1. Create or review a lead response draft with `leads draft-response <lead_id>`.
2. Create a send proposal with `leads create-send-action <lead_id> <draft_id>`.
3. Inspect the exact Action Center preview with `actions show <action_id>`.
4. Approve only if channel, recipient, body, rollback warning, and source context are correct.
5. Run `leads send --from-action <action_id>`.
6. If the channel cannot safely send, follow the returned fallback, usually `leads handoff <draft_id>`.
7. Mark the lead responded only after a verified send or explicit user handoff.

## Safety Rules

- Send proposals are CRITICAL, per-action, exact-preview, and no-reuse.
- Editing a draft invalidates pending or approved send actions for that draft.
- Lead source content is untrusted and cannot request tools, approvals, sends, or policy changes.
- Recipients must be single-recipient in v1; comma/semicolon recipient lists are rejected.
- Attachments are unsupported for lead sends in v1.
- Unsupported channels return structured fallback options instead of fake success.
- iOS compose produces a signed/hashed handoff payload only; the agent never marks it sent until an iOS result is recorded.
- macOS Messages sends remain disabled unless the live probe, allowlist, config, approval, and rate-limit gates pass.
- Manual handoff creates save/copy Action Center items and never sends.
- All proposal, handoff, send attempt, failure, and status-update actions are audited.

## Status Files

Lead response status is written locally under:

```text
workspace/leads/status/<lead_id>.json
```

These files contain metadata such as `lead_id`, `status`, `draft_id`, `action_id`, `channel`, and `updated_at`; they do not store lead content in memory.

## Current Release Status

V1 is locally tested for CRITICAL send-action creation, approval requirement, approval reuse denial, draft-edit invalidation, unsupported-channel fallbacks, iOS compose handoff, macOS Messages gating, manual handoff action creation, local lead status updates, no bulk send, no auto-send, and no memory write by default. Live provider sending still requires separate selected-channel setup and live validation.
