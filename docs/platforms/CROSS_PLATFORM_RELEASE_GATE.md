# Cross-Platform Release Gate

Date: 2026-05-25

This gate validates the current Cross-Platform Core + Platform Bridge groundwork. It does not approve real macOS, iOS companion, Windows, Microsoft Graph, EventKit, Contacts, Messages, Mail, UI Automation, or app frontend behavior.

## Scope

- Validate platform-neutral Python core boundaries.
- Validate platform registry, bridge interfaces, config/path/detection, read-only platform commands, fail-closed stubs, and App Bridge contract.
- Write future build guides for macOS, iOS companion, Windows, and app frontends.
- Update conservative maturity and release trackers.

## Non-Goals

- No new platform behavior.
- No Windows systems implementation.
- No native app frontend.
- No personal-data tools enabled by default.
- No send/write capabilities.
- No approval, policy, ToolBroker, PermissionManager, or audit bypass.

## Validation Checklist

| Check | Result | Evidence / note |
|---|---|---|
| Full test suite | pass | `./.venv/bin/python -m pytest -q`: 1104 passed, 1 skipped. |
| Startup policy validation | pass | `make policy-check`: `startup policy ok`. |
| Capability manifest validation | pass | `make policy-check` and `./.venv/bin/python -m agent.safety.validation config/capabilities.yaml`: exit 0. |
| Docs validation | pass | `tests/test_cross_platform_architecture_docs.py`: 6 passed; full suite passed. |
| Command registry validation | pass | `./.venv/bin/python smart_agent.py commands validate`: 387 commands, no problems. |
| Platform doctor | pass | `./.venv/bin/python smart_agent.py platform doctor`: status ok, read-only, bridges disabled, loaded bridge count 0. |
| Platform status | pass | `./.venv/bin/python smart_agent.py platform status`: status ok, metadata-only, bridges disabled/lazy. |
| Platform capabilities | pass | `./.venv/bin/python smart_agent.py platform capabilities`: 27 disabled planned/stubbed records. |
| Platform matrix | pass | `./.venv/bin/python smart_agent.py platform matrix`: macOS/iOS companion/Windows/web rows present. |
| Native/heavy platform imports at startup | pass | Import smoke showed no platform stub bridge modules or checked native/heavy platform modules loaded by `smart_agent` import. |
| Doctor/status personal-data access | pass | Platform doctor/status payloads are metadata-only and report `personal_data_accessed=false`. |
| Bridge action ToolBroker bypass | pass by design/tests | Direct `execute_action()` is blocked; broker-context stub execution returns `requires_setup`. |
| Real platform actions unavailable/stubbed/planned | pass by design/tests | Platform capabilities are metadata/stub records only; no native bridge action exists. |
| `APP_BRIDGE_ENABLED=false` default | pass by config/tests | App Bridge config defaults disabled and remote access forced off. |
| `PLATFORM_BRIDGES_ENABLED=false` default | pass by config/tests | Platform bridges default disabled and lazy-load enabled. |
| App bridge server not started by default | pass by tests | App Bridge contract import starts no server or polling loop. |
| Performance overhead minimal | pass | Registry/config/doctor are lightweight metadata-only paths; bridge stubs lazy-load on demand. |
| Future implementation path documented | pass | See the future bridge guides linked below. |
| Platform commands in registry | pass | `CMD-PLATFORM-001` through `CMD-PLATFORM-005` are active metadata commands. |
| Feature maturity conservative | pass | Real platform behavior remains stubbed/planned; no live platform bridge is user-ready. |

## Future Build Guides

- macOS: `docs/platforms/FUTURE_MACOS_BRIDGE_GUIDE.md`
- iOS companion: `docs/platforms/FUTURE_IOS_COMPANION_GUIDE.md`
- Windows: `docs/platforms/FUTURE_WINDOWS_BRIDGE_GUIDE.md`
- App frontend / App Bridge: `docs/platforms/FUTURE_APP_FRONTEND_GUIDE.md`
- Shared implementation guide: `docs/platforms/FUTURE_BRIDGE_IMPLEMENTATION_GUIDE.md`

## Maturity Assessment

| Area | Classification | Evidence | Conservative limitation |
|---|---|---|---|
| Cross-platform architecture decision | Hardened | ADR, strategy, boundaries, performance policy, docs tests, and release-gate docs exist. | Architecture only; not proof of live platform integration. |
| Platform capability registry | Tested | Static metadata registry tests cover required fields, disabled defaults, CRITICAL approval metadata, and unknown handling. | Registry records are not executable. |
| Platform bridge interfaces | Tested | `NullPlatformBridge`, action payloads/results, lazy registry, and direct-execution guard tests exist. | No real platform bridge behavior exists. |
| Platform-aware config/paths/detection | Tested | Mocked macOS/Windows/Linux/unknown detection, safe defaults, no-scan paths, and secret-omission tests exist. | Detection is metadata-only and does not grant platform readiness. |
| Platform doctor commands | Tested | Brokered SAFE metadata command tests and CLI smokes cover doctor/status/capabilities/matrix/explain. | Manual/live platform bridge QA is not applicable yet. |
| macOS bridge stub | Tested | Lazy-load and fail-closed stub tests cover capability listing and blocked/requires_setup action results. | EventKit, Contacts, Messages, Mail, notifications, and file picker are not implemented. |
| iOS companion bridge stub | Tested | Lazy-load and fail-closed stub tests cover capability listing and blocked/requires_setup action results. | Pairing, approval app, notifications, quick actions, and compose handoff are not implemented. |
| Windows bridge stub | Tested | Lazy-load and fail-closed stub tests cover capability listing and blocked/requires_setup action results. | Windows UI Automation, notifications, file picker, Outlook, Teams, and Microsoft Graph are not implemented. |
| Web/app bridge stub | Tested | Lazy-load and fail-closed stub tests cover capability listing and blocked/requires_setup action results. | No server, frontend, approval submission runtime, or remote access exists. |
| App Bridge API contract | Tested | Schema/model validation tests cover pairing, audit correlation, approval constraints, CRITICAL exact-preview rules, and safe defaults. | Contract only; no App Bridge server or native/local frontend exists. |
| Capability manifest mapping | Specified | Future requirement documented in strategy and guide. | Dedicated manifest-mapping prompt remains planned before real actions. |
| Performance guardrails | Specified | Performance policy and current import/lazy-load tests exist. | Dedicated startup/lazy-load guardrail prompt remains planned before broader platform expansion. |

## Safety Findings

- Platform status surfaces are metadata-only.
- Platform bridges and App Bridge are disabled or lazy by default.
- Planned personal-data and write/send capabilities remain disabled and non-executable.
- Direct bridge execution is guarded.
- Future executable actions require capability manifest declaration, ToolBroker routing, PolicyEngine evaluation, PermissionManager checks, risk-based ApprovalManager enforcement, and AuditLogger correlation.
- Status/doctor commands must never access calendars, contacts, messages, mail, private app databases, browser profiles, personal files, remote endpoints, or OS permission prompts.

## Startup / Overhead Findings

- The default bridge registry stores loader callables and does not import stub bridge modules until a specific bridge is requested.
- The platform capability registry is static metadata.
- Detection reads platform identifiers and explicit environment flags only; it does not scan user files.
- App Bridge imports define schemas and validation helpers only; they start no server, no polling loop, no network listener, and no subprocess.
- Future real bridge code must keep native or heavy imports out of core startup, platform doctor/status, and module import paths.

## Ready For Future Windows Buildout

- A Windows platform kind and capability records exist.
- A Windows bridge stub exists and fails closed.
- `windows.platform_doctor`, `windows.file_picker`, `windows.notifications`, `windows.ui_automation`, `windows.outlook_bridge`, `windows.teams_bridge`, and Microsoft Graph capability examples are documented as planned/stubbed metadata.
- Platform commands can explain Windows readiness without Windows-specific imports.
- The Windows guide defines required manifest, ToolBroker, policy, approval, audit, tests, and startup-overhead gates before implementation.

## Still Stubbed Or Planned

- All real macOS/iOS/Windows/web bridge actions.
- Microsoft Graph, Windows UI Automation, EventKit, Contacts, Mail, Messages, notifications, file pickers, pairing, approval app, and app bridge server/frontend behavior.
- Platform capability manifest mapping safeguards.
- Dedicated startup overhead and lazy-load guardrail release prompt.
- Live/manual OS validation.

## Release Decision

Classification: YELLOW for cross-platform groundwork.

The scaffolding is safe to keep and ready for the next hardening prompt. It is not ready for live platform actions or native/app frontend implementation until manifest mapping and startup guardrail prompts are complete.

## Next Recommended Prompt

`PLATFORM-CAPABILITY-MANIFEST-MAPPING`
