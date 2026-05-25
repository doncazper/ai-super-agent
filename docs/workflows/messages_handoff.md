# Messages Draft / Handoff Workflow

Status: v1 draft-only workflow.

This workflow prepares message replies for manual user handoff without sending. It remains the default personal iMessage/Messages path. A separate macOS approved-send adapter exists only as an experimental, disabled-by-default path after live probe, allowlist, exact Action Center approval, and rate-limit gates.

## Commands

```bash
python smart_agent.py messages draft-from-text --to "Name" --context-file ./workspace/thread.txt
python smart_agent.py messages import --from-file ./workspace/incoming_message.md
python smart_agent.py messages inbox list
python smart_agent.py messages inbox show <message_id>
python smart_agent.py messages inbox draft-reply <message_id>
python smart_agent.py messages draft --to "+15555555555" --body "Reviewed reply text"
python smart_agent.py messages handoff <draft_id>
python smart_agent.py messages save-draft <draft_id>
python smart_agent.py messages copy-draft <draft_id>
python smart_agent.py messages macos status
python smart_agent.py messages macos allow-recipient "+15555555555"
python smart_agent.py messages macos live-send-probe --to "+15555555555"
python smart_agent.py messages send --from-action <action_id>
```

Legacy exact-action execution remains supported:

```bash
python smart_agent.py messages save-draft --from-action <action_id>
python smart_agent.py messages copy-draft --from-action <action_id>
```

## Safety Rules

- This handoff workflow does not send.
- macOS Messages sending is a separate CRITICAL adapter, disabled by default, and cannot run without exact Action Center approval, allowlist, live probe, and config gates.
- No `~/Library/Messages` database access is allowed.
- No Full Disk Access dependency is introduced.
- Context files must be inside `./workspace`.
- Manual inbox imports must be inside `./workspace` and never read private Messages storage.
- Context text is treated as `UNTRUSTED_MESSAGE` or `UNTRUSTED_DOCUMENT` data, not instructions.
- Incoming message records are local manual/mock records under `./workspace/messaging/inbound/`.
- Local drafts are stored under `./workspace/messaging/drafts/`.
- Inbox draft replies create local drafts only; they do not auto-reply or send.
- Clipboard copy requires an approved Action Center item because clipboard contents can be personal data.
- Save/copy execution still goes through ToolBroker and requires a matching approved preview.
- No draft body is written to long-term memory by default.
- Drafts can later become Action Center send proposals. Only `channel=macos_messages` proposals can be executed by the macOS adapter, and only when every adapter gate passes.

## Workflow

1. Create a draft from trusted user text with `messages draft`, or from a selected workspace context file with `messages draft-from-text`.
2. Optionally import an incoming workspace message with `messages import --from-file`, inspect it with `messages inbox show`, then create a local draft with `messages inbox draft-reply`.
3. Inspect or edit the local draft before handoff.
4. Run `messages handoff <draft_id>` to create pending save/copy Action Center items.
5. Approve the exact save or copy action.
6. Run `messages save-draft <draft_id>` or `messages copy-draft <draft_id>`.

If no matching approved action exists, `save-draft` and `copy-draft` return approval instructions and do not execute.
