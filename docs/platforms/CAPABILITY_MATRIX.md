# Platform Capability Matrix

This matrix lists future platform capabilities for planning. Listed capabilities are not executable unless a later milestone adds disabled manifest entries, ToolBroker mappings, PolicyEngine rules, approval behavior, audit evidence, and tests.

## Status Values

| Status | Meaning |
|---|---|
| planned | Design target only; no runtime behavior. |
| stubbed | A future stub may return unsupported or requires_setup only. |
| disabled | Capability exists but is off by default. |
| unavailable | Platform or setup is missing. |
| blocked | Forbidden until a future decision changes the boundary. |

## Matrix

| Capability | Platform | Intended use | Risk | Trust | Default | Approval | Status |
|---|---|---|---|---|---|---|---|
| `macos.calendar.read` | macOS | Selected calendar reads through a permissioned bridge | HIGH | LOCAL_PRIVATE_DATA | disabled | required | planned |
| `macos.calendar.write` | macOS | Approved calendar creates/updates/deletes | CRITICAL | LOCAL_PRIVATE_DATA | disabled | per-action required | planned |
| `macos.contacts.search` | macOS | Selected contact search | HIGH | LOCAL_PRIVATE_DATA | disabled | required | planned |
| `macos.contacts.update` | macOS | Approved contact edits | CRITICAL | LOCAL_PRIVATE_DATA | disabled | per-action required | planned |
| `macos.file_picker` | macOS | User-selected file or folder handoff | MEDIUM | TRUSTED_USER / LOCAL_PRIVATE_DATA | disabled | contextual | planned |
| `macos.security_scoped_bookmark` | macOS | Persist user-granted scoped file access | HIGH | LOCAL_PRIVATE_DATA | disabled | required | planned |
| `macos.messages.probe` | macOS | Metadata-only feasibility/status probe | LOW/MEDIUM | LOCAL_PRIVATE_DATA metadata | disabled | no for metadata, required for future sensitive checks | planned |
| `macos.notifications` | macOS | Local notifications | LOW/MEDIUM | TRUSTED_USER | disabled | contextual | planned |
| `ios.message_compose_handoff` | iOS companion | User-confirmed compose handoff | CRITICAL | LOCAL_PRIVATE_DATA / UNTRUSTED_MESSAGE | disabled | per-action required | planned |
| `ios.mobile_approval` | iOS companion | Mobile approval review | HIGH/CRITICAL | TRUSTED_USER | disabled | per-action for CRITICAL | planned |
| `ios.notification` | iOS companion | Mobile notifications | LOW/MEDIUM | TRUSTED_USER | disabled | contextual | planned |
| `ios.quick_action` | iOS companion | User-initiated quick action | MEDIUM/HIGH | TRUSTED_USER | disabled | contextual | planned |
| `ios.pairing` | iOS companion | Local pairing flow | HIGH | TRUSTED_USER / LOCAL_PRIVATE_DATA metadata | disabled | required | planned |
| `windows.platform_doctor` | Windows | Metadata-only platform status | SAFE | LOCAL_PRIVATE_DATA metadata | disabled | no | stubbed |
| `windows.file_picker` | Windows | User-selected file or folder handoff | MEDIUM/HIGH | TRUSTED_USER / LOCAL_PRIVATE_DATA | disabled | contextual | planned |
| `windows.notifications` | Windows | Local notifications | LOW/MEDIUM | TRUSTED_USER | disabled | contextual | planned |
| `windows.ui_automation` | Windows | Future UI Automation workflows | HIGH/CRITICAL | LOCAL_PRIVATE_DATA / UNTRUSTED_DOCUMENT | disabled | required or per-action | planned |
| `microsoft_graph.mail` | Microsoft Graph | Future selected mail read or send actions | HIGH/CRITICAL | LOCAL_PRIVATE_DATA / UNTRUSTED_EMAIL | disabled | required or per-action | planned |
| `microsoft_graph.calendar` | Microsoft Graph | Future selected calendar read/write actions | HIGH/CRITICAL | LOCAL_PRIVATE_DATA | disabled | required or per-action | planned |
| `microsoft_graph.contacts` | Microsoft Graph | Future selected contact read/write actions | HIGH/CRITICAL | LOCAL_PRIVATE_DATA | disabled | required or per-action | planned |
| `windows.outlook_bridge` | Windows | Future Outlook bridge | HIGH/CRITICAL | LOCAL_PRIVATE_DATA / UNTRUSTED_EMAIL | disabled | required or per-action | planned |
| `windows.teams_bridge` | Windows | Future Teams bridge | HIGH/CRITICAL | LOCAL_PRIVATE_DATA / UNTRUSTED_MESSAGE | disabled | required or per-action | planned |
| `app_bridge.status` | Generic app bridge | Local status endpoint | SAFE | LOCAL_PRIVATE_DATA metadata | disabled | no | planned |
| `app_bridge.pending_actions` | Generic app bridge | Pending Action Center metadata | MEDIUM | LOCAL_PRIVATE_DATA metadata | disabled | no for read, approval for action decisions | planned |
| `app_bridge.submit_approval` | Generic app bridge | Submit user approval decision through ApprovalManager | HIGH/CRITICAL | TRUSTED_USER | disabled | required | planned |
| `app_bridge.audit_summary` | Generic app bridge | Redacted audit summary | SAFE/MEDIUM | Audit metadata | disabled | contextual | planned |
| `app_bridge.connector_status` | Generic app bridge | Connector/provider status metadata | SAFE | LOCAL_PRIVATE_DATA metadata | disabled | no | planned |

## Readiness Rule

Every row above remains non-executable until it is backed by:

- Capability manifest declaration.
- ToolBroker mapping.
- PolicyEngine evaluation.
- ApprovalManager behavior for HIGH and CRITICAL risk.
- AuditLogger correlation fields.
- Unsupported-platform tests.
- Command registry and maturity tracker updates.

## Inspection Commands

The matrix can now be inspected from the CLI without executing platform actions:

```bash
python smart_agent.py platform capabilities
python smart_agent.py platform matrix
python smart_agent.py platform explain macos.calendar.read
```

These commands route through SAFE `platform.*` ToolBroker tools and AuditLogger. They only return static metadata, setup hints, risk/trust labels, approval metadata, default-enabled state, and docs links. Unknown capability IDs return structured `not_found` / `unsupported` metadata instead of crashing. The commands do not import platform bridge modules, access personal data, request permissions, or make planned/stubbed capabilities executable.

## Platform Capability Registry v1

`agent.platforms` now provides a portable static registry for the first 27 planned/stubbed platform capability records:

- macOS: `macos.calendar.read`, `macos.calendar.write`, `macos.contacts.search`, `macos.contacts.update`, `macos.file_picker`, `macos.security_scoped_bookmark`, `macos.messages.probe`, `macos.notifications`
- iOS companion: `ios.message_compose_handoff`, `ios.mobile_approval`, `ios.notification`, `ios.quick_action`, `ios.pairing`
- Windows / Microsoft Graph: `windows.platform_doctor`, `windows.file_picker`, `windows.notifications`, `windows.ui_automation`, `microsoft_graph.mail`, `microsoft_graph.calendar`, `microsoft_graph.contacts`, `windows.outlook_bridge`, `windows.teams_bridge`
- Generic app/web bridge: `app_bridge.status`, `app_bridge.pending_actions`, `app_bridge.submit_approval`, `app_bridge.audit_summary`, `app_bridge.connector_status`

Registry v1 is metadata-only. It does not import macOS, iOS, Windows, Microsoft Graph, UI Automation, EventKit, Contacts, Messages, Mail, or native app modules. It does not execute actions, request permissions, access personal data, or enable capabilities. Unknown platforms and unknown capability IDs return structured `unknown` / `unsupported` metadata records.

All planned personal-data capabilities have `default_enabled=false`. All CRITICAL capability records use `approval_required=per_action` to preserve the future ApprovalManager no-reuse boundary. Future execution still requires capability manifest declaration, ToolBroker mapping, PolicyEngine evaluation, PermissionManager checks where applicable, ApprovalManager approval for HIGH/CRITICAL actions, AuditLogger evidence, and release-gate tests.

## Bridge Stubs

The current stub milestone adds lazy-loadable packages for macOS, iOS companion, Windows, and generic app/web bridge families. These stubs subclass `PlatformBridge` through the fail-closed `NullPlatformBridge`, declare the capability records above, and return structured `blocked` for direct `execute_action()` calls or `requires_setup` for broker-context calls. They import no native OS frameworks, perform no personal-data reads, request no permissions, start no app bridge server, and execute no platform actions.
