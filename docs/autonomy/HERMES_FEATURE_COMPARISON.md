# Hermes Feature Comparison

This comparison translates useful Hermes-like ideas into safe project-specific milestones.

Every safe interpretation remains subordinate to ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger. A Hermes-like product idea does not become an authority surface merely because it is useful.

| Hermes-like Idea | Safe Interpretation In This Repo | Current Status | Unsafe Interpretation Rejected |
|---|---|---|---|
| Always-available assistant gateway | Channel-neutral request/status model that still enters the control plane | Planned after HERMES-01 | Remote server or channel that can call tools directly |
| Telegram/mobile access | Disabled-by-default setup scaffolding and diagnostics | Planned | Bot polling/webhook listener or message send by default |
| Repeated-task learning | Local proposal records for user-reviewed native skills | Planned | Automatic skill creation, install, enablement, or execution |
| Skill improvement from experience | Evidence-backed patch/proposal workflow | Planned | Self-modifying skills or unreviewed marketplace updates |
| Scheduler UX | Visible dry-run previews and manual-run ergonomics | Planned | Hidden background persistence or unattended high-risk actions |
| Subagents | Isolated read-only helpers with explicit ceilings | Planned | Subagents with write tools or personal-data access by default |
| Sandboxed execution | Backend abstraction and policy docs | Planned | Arbitrary code/plugin execution or cloud private-data jobs |
| Model switching | Dry-run routing and session continuity metadata | Partly available through Brain Runtime scaffolds | Silent paid/cloud fallback or automatic provider switching |
| Long-term memory search | Policy-aware search over approved local memory | Planned | Personal memory injection or private data storage by default |
| Cross-session continuity | Redacted handoff summaries and prompt tracking | Planned | Hidden persistent background agent or raw log replay |
| Browser automation | Authorized selected-scope policy boundary | Planned | CAPTCHA/Cloudflare/proxy/login/paywall bypass or impersonation |

## Adoption Rule

The project adopts a feature only when it can be expressed as a safe, testable, auditable, disabled-by-default capability. If an idea requires hidden authority, unclear consent, bypass behavior, or unbounded data access, it is rejected or deferred.
