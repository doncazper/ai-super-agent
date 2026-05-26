# Autonomy Risk Model

Autonomy risk is determined by action authority, data sensitivity, persistence, user presence, reversibility, and exposure to untrusted inputs.

## Risk Levels

| Area | Baseline Risk | Notes |
|---|---:|---|
| Status/doctor metadata | SAFE | Must not access personal data, start services, or call providers unexpectedly. |
| Local proposal generation | LOW | Proposals must not execute actions or enable skills automatically. |
| Scheduler previews and dry runs | LOW/MEDIUM | Safe only when manual-run and non-persistent. |
| Public web/source discovery | LOW/MEDIUM | Web content remains `UNTRUSTED_WEB`; no bypass behavior. |
| Personal-data reads | HIGH | Disabled by default and selected-scope approval required. |
| Sends/writes/mutations | CRITICAL | Per-action exact preview, no approval reuse, no unattended execution. |
| Background persistence | HIGH/CRITICAL | Requires separate decision, visibility, lifecycle control, and audit. |
| Cloud/server execution with private data | HIGH/CRITICAL | Deferred until explicit authorization, sandboxing, retention, and audit exist. |
| Anti-bot/CAPTCHA/login/paywall bypass | FORBIDDEN | Third-party bypass and impersonation are not allowed. |

## Trust Labels

- `TRUSTED_USER`: explicit user-provided instructions or configuration.
- `MODEL_OUTPUT`: generated proposals, summaries, and explanations.
- `UNTRUSTED_WEB`: public web, news, forum, and browser content.
- `UNTRUSTED_DOCUMENT`: imported files, generated exports, external docs.
- `UNTRUSTED_MESSAGE`: inbound message or channel text.
- `LOCAL_PRIVATE_DATA`: selected personal data from approved connectors.

## Default Behavior

- Autonomy features default to disabled, dry-run, metadata-only, or proposal-only.
- No prompt, channel message, webpage, forum post, email, document, or model output can approve actions, alter policy, reveal secrets, call tools, or create persistence.
- Personal content is not written to memory by default.
- Subagents receive no write permissions by default.
- Channels cannot expose tools directly; they submit requests into the existing control plane.

## Risk Escalators

Escalate to HIGH or CRITICAL when a workflow includes:

- Personal-data access.
- External communication or sending.
- File writes outside approved workspace paths.
- Provider credentials or tokens.
- Background execution.
- Browser automation.
- Cloud execution.
- Non-reversible side effects.
- Subagent delegation with tool access.

## Required Evidence

Every future autonomy milestone must record:

- Scope and non-goals.
- Risk and threat-model notes.
- ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger behavior.
- Tests for denial, approval, audit, redaction, and no-memory defaults.
- Command registry entries for user-visible commands.
- Conservative maturity classification.
