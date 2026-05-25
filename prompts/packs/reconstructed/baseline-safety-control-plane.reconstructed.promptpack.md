# Baseline Safety Control Plane Reconstructed Prompt Pack

```yaml
pack_id: baseline-safety-control-plane.reconstructed
title: Baseline Safety Control Plane
status: reconstructed
exact_original: false
reconstruction_sources:
  - SPEC.md
  - docs/FEATURE_REGISTRY.md
  - docs/FEATURE_MATURITY.md
  - docs/RELEASE_CHECKLIST.md
related_features:
  - SAFETY-BROKER
  - SAFETY-POLICY
  - SAFETY-PERMISSIONS
  - SAFETY-APPROVALS
  - SAFETY-AUDIT
related_docs:
  - SPEC.md
  - docs/THREAT_MODEL.md
related_commits:
  - unknown
confidence: medium
caveats:
  - Original prompt text is unavailable.
prompt_ids:
  - BASELINE-SAFETY-01
```

## Prompt Records

### BASELINE-SAFETY-01

type: reconstructed_summary

Build the safety control plane before adding risky capabilities: ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, redaction, capability manifest validation, default disabled personal-data capabilities, HIGH approval requirements, and CRITICAL per-action approvals.
