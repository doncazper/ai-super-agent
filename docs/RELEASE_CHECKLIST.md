# Release Checklist

- [x] All tests pass or failures are documented.
- [x] No forbidden capabilities introduced.
- [x] No accidental personal-data access.
- [x] Audit logs verified.
- [x] Policy behavior verified.
- [x] Approval behavior verified for high/critical actions in scope.
- [x] Approval lifecycle audit events verified for approval-required actions in scope.
- [x] Critical approval reuse is blocked.
- [x] Secrets redacted from debug and audit outputs.
- [x] Capability manifest includes trust levels, audit fields, storage flags, and web rate limits.
- [x] Sensitive path denylist includes SSH, GPG, Keychain, Messages, Mail, Application Support, AWS, config, and `.env`.
- [x] Prompt-injection regressions cover web, email, messages, and workspace-file content.
- [x] Weather hardening verified: ToolBroker-only current/forecast path, manifest entries, audit metadata, rate limits, opt-in default location, no system location inference, structured outputs/errors, no live-network unit tests, and no personal-data tools enabled by weather.
- [x] Weather cache avoids precise-looking street addresses and direct coordinates.
- [x] Docs updated.
- [x] `docs/COMPLETION_REPORT.md` updated.
- [x] Next milestone identified.
- [x] Approval gates checked.

## Release Gate Result

M0-M11 implementation tests pass locally. Real-world release/use still requires human review of disabled-by-default personal and write/send capabilities before enabling connectors.
