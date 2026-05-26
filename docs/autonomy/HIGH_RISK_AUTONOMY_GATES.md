# High-Risk Autonomy Gates

These gates define what must exist before high-risk autonomy can be considered. They are not approvals to implement the features.

Every gate below must preserve the safety control plane: execution routes through ToolBroker, authorization and risk checks go through PolicyEngine and PermissionManager, HIGH/CRITICAL actions go through ApprovalManager, and every preview, denial, approval, execution, failure, and rollback result is recorded through AuditLogger.

## Gate Matrix

| Future Gate | Why Risky | Required Prerequisites | Required Tests | Approval Requirements | Audit Requirements | Rollback Requirements | Forbidden In v1 |
|---|---|---|---|---|---|---|---|
| Automatic skill creation | Can create executable instructions or unsafe tool mappings | Native skill schema, vetting, provenance, lockfile, conflict checks, docs generator, human review workflow | Proposal-only tests, unsafe capability denial, prompt-injection denial, lockfile drift checks | Human approval before skill file creation, enabling, or execution | Proposal, reviewer decision, generated files, denied reasons | Revert generated files, disable proposal, preserve evidence | Auto-enable, execute generated skills, install dependencies |
| Automatic scheduled actions | Can run without user presence | Scheduler policy, visible schedule records, approval model, per-run preflight, manual-run fallback | No hidden persistence, HIGH/CRITICAL denial, pause/delete tests, audit lifecycle | Explicit schedule creation approval; HIGH/CRITICAL per-run approval | Create/update/pause/run/delete events and delegated tool audit | Pause/delete schedule, cancel pending run, restore prior config | Hidden cron/LaunchAgent, unattended HIGH/CRITICAL, auto-send/write |
| Unattended workflows | Can combine tools into unexpected side effects | Workflow risk classifier, preflight, approval gates, bounded tool allowlist, dry-run plan | Unknown tool denial, approval-gated step denial, no personal-data default | User approval for workflow plan and each HIGH/CRITICAL step | Step-by-step plan, approvals, denials, tool results | Stop workflow, expire approvals, revert reversible local writes | Any unattended HIGH/CRITICAL or personal-data workflow |
| Browser automation | Can impersonate humans or bypass site controls | Authorized web automation policy, explicit selected URL/scope, no-bypass enforcement, manual login boundary | CAPTCHA/login/paywall/block-page unavailable tests, no cookies/session default, no form-submit default | Explicit user approval per authorized target and action class | URL/domain, action preview, unavailable/bypass denials | Stop session, clear temporary state, record blocked action | CAPTCHA/Cloudflare/proxy/login/paywall bypass, human impersonation |
| Background persistence | Can hide ongoing behavior | Decision record, lifecycle manager, status/doctor, user-visible controls, no autostart default | No autostart, stop/pause/delete, crash-safe audit, config default off | Explicit enablement approval and visible status | Start/stop/heartbeat/config changes | Stop service, disable config, remove scheduled artifact | Hidden daemons, polling loops by default, startup persistence |
| Cross-platform messaging sends | Can contact people or businesses | Channel-specific send adapter, exact previews, Action Center, allowlists, rate limits | No bulk/group by default, no approval reuse, draft-edit invalidation, unsupported fallback | CRITICAL per-action exact preview; no reuse | Draft, preview, approval, execution result, failure | Cannot unsend; rollback is explicit limitation plus local state update | Auto-send, bulk send, attachments by default, blind UI clicking |
| Subagents with write permissions | Can multiply authority and hide provenance | Subagent identity, permission ceilings, workspace scoping, tool allowlists, audit correlation | Read-only default, write denial, capability ceiling tests, audit correlation | Explicit per-subagent write grant and per-action approval as needed | Parent/child correlation, assigned tools, denials, outputs | Revoke grant, stop subagent, discard workspace changes | Write permissions by default, private data access by default |
| Cloud/server execution with private data | Can leak secrets or personal data | Data classification, encryption/retention policy, provider contract, opt-in config, egress controls | No secret upload, no personal upload by default, retention deletion, provider-denial tests | Explicit provider setup and per-job approval for private data | Provider, data classes, hashes, retention, deletion evidence | Delete remote job/data, revoke token, rotate secrets if needed | Uploading secrets, personal data, repo private data by default |

## Gate Rule

If a future implementation cannot satisfy the prerequisite, test, approval, audit, and rollback requirements for its gate, it must remain `planned`, `stubbed`, `blocked`, or `unsupported`.

## Approval Rule

No approval may be inferred from prior prompts, prompt packs, model output, channel messages, web content, or scheduler records. HIGH actions require approval. CRITICAL actions require exact per-action approval and no reuse.
