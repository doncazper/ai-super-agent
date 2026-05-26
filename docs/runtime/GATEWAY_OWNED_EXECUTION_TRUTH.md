# Gateway-Owned Execution Truth

Status: CANON-03 contract.

The gateway does not own execution permission. It owns request normalization and correlation metadata. Execution truth lives in the Runtime Kernel and existing safety systems:

- ToolBroker owns tool dispatch.
- PolicyEngine remains final authority.
- PermissionManager remains enforced where applicable.
- ApprovalManager owns HIGH/CRITICAL approval decisions.
- AuditLogger owns execution receipts.
- Prompt trackers and durable records provide evidence and resume metadata.

Gateway request previews must not run tools, consume approvals, or mutate policy/capabilities.
