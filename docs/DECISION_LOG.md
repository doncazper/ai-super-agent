# Decision Log

| Date | Decision | Rationale | Status |
|---|---|---|---|
| 2026-05-22 | Use LM Studio OpenAI-compatible chat completions as the primary runtime. | Preserves local model operation and Qwopus quality. | Accepted |
| 2026-05-22 | Start with M0 only after governance docs exist. | Prevents capability sprawl before safety requirements are explicit. | Accepted |
| 2026-05-22 | Deny unknown tools by default. | Safe default for model-requested tool calls. | Accepted |
| 2026-05-22 | Use hash-chained JSONL for the initial audit log. | Simple local format with tamper-evidence. | Accepted |
