# Canonical State Handoff

Status: Implemented as read-only metadata and Markdown output.

Commands:

```bash
python smart_agent.py runtime handoff
python smart_agent.py runtime handoff --for-chatgpt
```

The handoff command returns JSON with a Markdown handoff body embedded in the `markdown` field. It does not write `docs/HANDOFF_TO_CHATGPT.md`; that file remains an explicit reporting artifact when requested.

## Recommended Upload Bundle

Minimum bundle for ChatGPT review:

- `docs/HANDOFF_TO_CHATGPT.md`
- `docs/PROJECT_STATE.md`
- `docs/PROMPT_QUEUE.md`
- `docs/PROMPT_LEDGER.md`
- `docs/PROMPT_AUDIT.md`
- `docs/COMPLETION_REPORT.md`
- `CHANGELOG.md`

Feature-specific release docs should be added when reviewing a completed feature pack.

## Safety Rules

- No tool execution.
- No provider calls.
- No personal connector reads.
- No secret printing.
- No tracker mutation.
- No background service.
- No automatic resume.
- No file write.

The handoff output is a compact view over existing trackers and canonical state metadata. If it conflicts with detailed trackers, report the disagreement rather than guessing.
