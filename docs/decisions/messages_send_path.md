# Messages Send Path Decision

Date: 2026-05-22

## Connector Name

Messages safe handoff and future send path.

## User Value

The assistant can draft text replies from selected, user-provided context and help the user move the draft to a place where they can send it manually. This improves usefulness without silently reading message history or sending texts.

## Data Accessed

- Manually provided workspace text files for `messages.draft_from_text`.
- Draft text produced by the agent from that user-provided context.
- Optional clipboard contents only as a write target for a reviewed draft.

The project does not read `~/Library/Messages`, Messages private SQLite databases, notification caches, or device backups.

## Actions Possible

Current v1 actions:

- Draft a reply from a workspace file.
- Queue Action Center handoff records for saving or copying a draft.
- Save an approved draft inside `./workspace`.
- Copy an approved draft to the clipboard.

Deferred actions:

- Automatic Messages/iMessage/SMS sending.
- Bulk message search or history ingestion.
- Direct Messages.app database access.

## Native Messages Automation Options

- AppleScript or UI scripting through Messages.app may be possible for some local setups, but reliability and recipient ambiguity are poor.
- Accessibility-driven clicking/typing risks sending to the wrong recipient or clicking a changed UI target.
- Private database scraping requires broad privacy access and violates the project safety model.
- Shortcuts/App Intents style handoff may be safer if a user-visible confirmation surface is available, but it still needs a separate design and approval gate.

## AppleScript / Accessibility Risks

- UI automation can silently send if a script presses Return or activates a send button.
- Recipient resolution may be ambiguous.
- Messages.app UI state can change between preview and execution.
- Accessibility permissions are broad and easy to misuse.
- Automation can bypass user-facing review if not tightly constrained.

## Clipboard Risks

- Clipboard contents may contain personal data.
- Other local apps can read clipboard contents.
- Clipboard copy is not reversible.
- Users may paste into the wrong conversation.

Mitigation in v1:

- Clipboard copy requires a reviewed Action Center item and approval.
- It never sends a message.
- Draft text is audited as a handoff action, not stored in long-term memory.
- Workspace save is available as a lower-surprise alternative.

## Manual Handoff Option

Manual handoff is the recommended v1 path:

1. Draft from a user-provided workspace file.
2. Review the draft and Action Center preview.
3. Save the draft to `./workspace` or copy it to clipboard after approval.
4. User manually sends from their preferred Messages app.

## Future Approved Send Requirements

Any future automatic send path must require:

- Separate connector decision record and threat model update.
- Explicit provider/automation path.
- Per-action CRITICAL approval.
- Exact recipient and exact message preview.
- No approval reuse.
- No bulk sending.
- No background sending.
- User-visible final confirmation in the target app where feasible.
- Audit of draft, approval, execution, failure, and provider result.
- Tests for wrong-recipient prevention, UI changes, denial, prompt injection, and no database scraping.

## Recommended Option

Use safe handoff only for v1. Save-to-workspace and copy-to-clipboard are useful enough and avoid the highest-risk automatic send behavior.

## Alternatives Rejected

- Scrape `~/Library/Messages`: rejected because it needs broad privacy access and bypasses selected-scope controls.
- AppleScript auto-send: rejected for v1 because recipient and UI state risks are too high.
- Accessibility auto-send: rejected for v1 because permissions are broad and UI automation is fragile.
- Background send connector: rejected because the project requires user-facing controls, per-action approvals, and auditability first.

## Tests Required

- Draft-from-text reads only workspace files.
- Unsafe paths are blocked.
- Content is labeled `UNTRUSTED_MESSAGE`.
- Prompt injection in message context is ignored.
- No `messages.send` automatic tool exists.
- Save/copy handoff requires approval.
- Saved drafts remain inside approved workspace roots.
- Clipboard copy is explicit and audited.
- Message body is not stored in long-term memory by default.
- Audit logs draft, approval, save/copy, and failures.
