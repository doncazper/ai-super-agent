# Decision Log

| Date | Decision | Rationale | Status |
|---|---|---|---|
| 2026-05-22 | Use LM Studio OpenAI-compatible chat completions as the primary runtime. | Preserves local model operation and Qwopus quality. | Accepted |
| 2026-05-22 | Start with M0 only after governance docs exist. | Prevents capability sprawl before safety requirements are explicit. | Accepted |
| 2026-05-22 | Deny unknown tools by default. | Safe default for model-requested tool calls. | Accepted |
| 2026-05-22 | Use hash-chained JSONL for the initial audit log. | Simple local format with tamper-evidence. | Accepted |
| 2026-05-22 | Add centralized runtime config and `doctor` diagnostics before external connectors. | Keeps LM Studio/CLI troubleshooting safe and local without adding new capabilities. | Accepted |
| 2026-05-22 | Implement interactive CLI as a thin wrapper over the existing orchestrator path. | Preserves ToolBroker, policy, approval, and audit enforcement while improving local ergonomics. | Accepted |
| 2026-05-22 | Add Brave Search as the first opt-in real web provider. | Provides live search without hard-coded keys, while preserving ToolBroker, policy, rate limits, audit redaction, and untrusted-result labeling. | Accepted |
| 2026-05-22 | Use a disabled-by-default calendar adapter with optional Calendar.app AppleScript bridge for the first personal-data connector. | Avoids private database scraping and Full Disk Access while allowing selected-range, approval-gated calendar reads through macOS privacy prompts. | Accepted |
| 2026-05-22 | Use a disabled-by-default contacts adapter with optional Contacts.app AppleScript bridge for the next personal-data connector. | Keeps access selected-scope, approval-gated, compact in search mode, and avoids private AddressBook database scraping or Full Disk Access. | Accepted |
