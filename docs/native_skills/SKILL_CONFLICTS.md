# Skill Conflicts

Native skill conflict detection is a metadata-only release hardening check. It compares reviewed manifests, root precedence diagnostics, dependency declarations, provider flags, platform requirements, docs/tests references, approval behavior, and memory behavior. It does not execute skills, run scripts, install packages, call providers, import plugin runtimes, enable skills, or resolve conflicts automatically.

## Commands

```bash
python smart_agent.py skills conflicts
python smart_agent.py skills conflicts --json
python smart_agent.py skills explain-conflict <conflict_id>
```

The commands return JSON. A conflict report is advisory evidence for human review and release gates; it is not an allowlist and does not grant execution permission. Executable native skill behavior must still route through `ToolBroker`, `PolicyEngine`, `PermissionManager`, `ApprovalManager`, and `AuditLogger`.

## Conflict Types

| Type | Meaning | Default posture |
|---|---|---|
| `duplicate_skill_id` | More than one candidate or manifest declares the same skill id. | Stop promotion until reviewed. |
| `same_command` | Two skills claim the same CLI surface. | Review and rename or scope commands. |
| `same_capability_claim` | More than one skill maps to the same capability. | Confirm intentional overlap and ToolBroker routing. |
| `unsafe_shadowing` | A candidate would shadow another candidate in a risky way. | Human review required. |
| `experimental_overrides_native` | An experimental root would override native behavior. | Block without explicit future approval. |
| `unreviewed_overrides_reviewed` | An unreviewed candidate would override a reviewed skill. | Block without human review and provenance evidence. |
| `dependency_missing` | Required env vars, binaries, or setup dependencies are missing. | Return setup hints; do not auto-install. |
| `provider_disabled` | A required provider is disabled by config/default policy. | Return setup hints; do not call disabled providers. |
| `platform_incompatible` | The skill is not compatible with the current platform. | Return unsupported/requires_setup. |
| `risk_policy_mismatch` | Risk metadata conflicts with approval policy, such as CRITICAL reuse. | Block until corrected. |
| `approval_policy_mismatch` | HIGH/CRITICAL behavior lacks required approval. | Block until ApprovalManager behavior is explicit. |
| `memory_policy_mismatch` | Personal-data behavior is paired with unsafe memory retention. | Block or force no-store/redacted-only. |
| `docs_missing` | The manifest lacks a docs reference. | Not user-ready. |
| `tests_missing` | The manifest lacks test evidence. | Not tested or user-ready. |

## Conflict Record

Each conflict includes:

- `conflict_id`
- `conflict_type`
- `severity`
- `affected_skills`
- `winning_skill`
- `shadowed_skills`
- `risk_level`
- `reason`
- `suggested_resolution`
- `requires_human_review`
- `safe_to_continue`

`safe_to_continue=false` means the batch should not promote or rely on the affected skill behavior until the conflict is reviewed and fixed. The detector still does not mutate files or resolve the conflict.

## Safety Boundaries

- Skill text remains `UNTRUSTED_DOCUMENT`.
- Conflict detection never runs `SKILL.md` instructions or package scripts.
- Missing dependencies are reported; they are never installed.
- Provider-disabled findings do not call providers.
- Shadowing findings do not enable or disable roots.
- Docs/tests findings do not create maturity claims.
- Conflict reports are not permission grants.

## Release-Gate Use

Run conflict detection after manifest validation, precedence checks, compatibility checks, and profile validation. Treat high-severity shadowing, approval, risk, memory, or duplicate-id findings as release blockers unless the release gate explicitly scopes them as non-executable planned/stubbed records.
