# Native Skill Risk Model

## Risk Factors

Native skill review must consider:

- data sensitivity
- action side effects
- filesystem scope
- network scope
- credential needs
- personal-data access
- persistence/background behavior
- opaque binaries or generated code
- prompt-injection exposure
- memory behavior
- auditability
- testability
- rollback feasibility

## Risk Levels

Use the existing `RiskLevel` model.

| RiskLevel | Native skill meaning |
|---|---|
| SAFE | Metadata-only or docs-only workflow; no tool execution. |
| LOW | Workspace-bounded read-only or public web research through brokered tools. |
| MEDIUM | Broader public web, document parsing, or draft generation with meaningful failure modes. |
| HIGH | Selected-scope personal-data reads or destructive local actions requiring approval. |
| CRITICAL | Sends, irreversible writes, cloud mutations, or high-impact actions requiring per-action approval. |
| FORBIDDEN | Keychain/password reads, private database scraping, approval bypass, policy weakening, hidden persistence, or unrestricted access. |

## Trust Labels

Skill inputs and outputs must use existing `TrustLevel` labels:

- `TRUSTED_USER` for explicit user instructions and local reviewed records
- `MODEL_OUTPUT` for generated plans, drafts, and proposals
- `LOCAL_PRIVATE_DATA` for approved personal connector results
- `UNTRUSTED_WEB` for marketplace pages, fetched docs, public content
- `UNTRUSTED_EMAIL` for email-derived context
- `UNTRUSTED_MESSAGE` for message-derived context
- `UNTRUSTED_DOCUMENT` for external skill text, imported prompts, PDFs, and workspace documents of unknown provenance

## Supply-Chain Risks

External skill ecosystems can contain:

- prompt-injection text
- hidden setup instructions
- package-install commands
- shell scripts
- broad filesystem expectations
- browser-session assumptions
- credentials in examples
- incompatible licenses
- stale APIs
- opaque binaries

Mitigation:

- inspect as data only
- never run during intake
- record license and source
- translate useful behavior into local code
- route all local actions through existing tool/policy/audit layers

## Approval Gates

- SAFE/LOW docs-only research can proceed without user approval.
- MEDIUM skill specs require documented risks and tests.
- HIGH skill behavior requires ApprovalManager integration and non-interactive denial behavior.
- CRITICAL skill behavior requires Action Center and per-action approval.
- FORBIDDEN behavior is rejected.

## Memory Rules

Native skills may not store external skill content, personal data, secrets, or generated assumptions in long-term memory by default.

Only safe project facts or workflow lessons may be stored, and memory writes must go through memory policy and audit logging.
