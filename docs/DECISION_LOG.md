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
| 2026-05-22 | Use a disabled-by-default email adapter with optional IMAP connector for metadata, selected-thread reads, summaries, and draft-only replies. | Avoids Mail database scraping and Full Disk Access while supporting externally configured email access with no sending, no deletion, no moves, no archiving, and no body storage by default. | Accepted |
| 2026-05-22 | Use a disabled-by-default messages adapter stub plus manual `./workspace` text-file draft fallback. | No safe permissioned macOS Messages integration is available in this repo; this avoids `~/Library/Messages` scraping, Full Disk Access, bulk history reads, and sending while still allowing user-provided selected text to produce draft-only replies. | Accepted |
| 2026-05-22 | Add a controlled `smoke` harness with live-service skips and dry-run personal checks. | Supports real-world integration readiness without requiring personal data, production accounts, unsafe connectors, or policy weakening. | Accepted |
| 2026-05-22 | Plan Weather API as the next lowest-risk real-world connector candidate before implementation. | Weather can exercise live provider integration without personal account data, sends, writes, or macOS private-data access, while still requiring network, audit, rate-limit, and no-history safeguards. | Proposed |
| 2026-05-22 | Implement Weather API provider abstraction without a live provider. | Adds ToolBroker-only weather capabilities and structured disabled-provider behavior while avoiding device location, IP geolocation, personal data, writes, or memory storage. | Accepted |
| 2026-05-22 | Add Open-Meteo as the first real weather provider. | Open-Meteo supports no-key geocoding and forecast access for user-provided locations, allowing live weather utility without personal-data access, device location, writes, or memory storage. | Accepted |
| 2026-05-22 | Keep WeatherKit as an optional stub pending decision review. | WeatherKit requires Apple Developer credentials and JWT signing, so this pass adds a decision record and credential-presence stub only, with no private-key reading or Apple API calls. | Accepted |
