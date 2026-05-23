# Command Legacy Tracker

Deprecated, legacy, removed, and intentionally unavailable commands remain listed so users know the replacement path.

| Command ID | Command | Status | Replacement command | Removal target | Reason for deprecation | Compatibility notes |
|---|---|---|---|---|---|---|
| CMD-MSG-007 | `python smart_agent.py messages send --from-action <action_id>` | blocked | messages save-draft/copy-draft | not scheduled | Automatic message sending remains deferred. | Automatic text/message sending. |
| CMD-LEGACY-001 | `python smart_agent.py web fetch <url>` | legacy | browser read-url | not scheduled | Use browser read-url or research. | Legacy planned fetch shortcut that is not implemented. |
| CMD-LEGACY-002 | `python smart_agent.py weather providers` | legacy | weather doctor | not scheduled | Use weather doctor. | Legacy provider listing idea not implemented as a command. |
