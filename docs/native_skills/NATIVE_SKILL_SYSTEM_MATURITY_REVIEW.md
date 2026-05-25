# Native Skill System Maturity Review

Review date: 2026-05-25

This review uses conservative maturity labels. Local tests and fixture dogfood can support `Tested` or `Hardened`; they do not prove live marketplace readiness or user-ready external skill execution.

| Area | Maturity | Evidence | Limitation / Next Step |
|---|---|---|---|
| Skill roots/scopes/precedence | Hardened | Metadata-only root registry, deterministic precedence, shadowing diagnostics, tests, docs, CLI smokes, release gate | External/personal/experimental roots remain untrusted candidate sources |
| Manifest schema | Hardened | Required risk/trust/memory/audit/approval/dependency fields, manifest tests, validation command, release gate | Future fields may need migration docs as runtime skills expand |
| Dependency gating | Hardened | Detection-only env/config/binary/file/platform/capability checks, tests, redacted outputs | Does not install or repair dependencies automatically |
| Provenance/trust metadata | Hardened | Provenance records, trust status, source/review metadata, tests, docs | External provenance validation remains future work |
| Lockfile/pinning | Tested | Read-only lock status/verify and example lockfile exist; verification reports missing real lockfile records clearly | Real reviewed `native_skills.lock` and write/pin approval flow are deferred |
| Inspection/vetting | Hardened | Static approved-path inspector/vetter detects scripts, shell, secrets, network, filesystem, browser/session, personal-data, and approval-bypass risks; reports audited | Static analysis can miss obfuscated behavior |
| Profile allowlists | Tested | Advisory profiles, visibility checks, risk ceilings, personal-data defaults, tests, docs | Profiles do not yet attach to runtime skill execution modes |
| Compatibility matrix | Tested | Manifest-derived platform/runtime/setup records, CLI, docs, tests | Live platform/app bridge validation remains future work |
| Conflict detector | Tested | Duplicate, overlap, shadowing, dependency, provider, platform, approval, risk, memory, docs/tests checks and CLI | Advisory only; no auto-resolution by design |
| Test/dogfood harness | Tested | Safe harness, fixture evals, dogfood suites, CLI, release-gate dogfood session | Manual external-skill dogfood remains future/approval-gated |
| Docs generator/catalog | Tested | Dry-run default, explicit write, generated catalog, missing-docs check, manual-note preservation, tests | Catalog is evidence/navigation, not a runtime allowlist |
| Release gate | Hardened | Full suite, policy/manifest/command/docs/native skill validation, dogfood, eval, docs-check, maturity review | Needs reviewed lockfile and manual live intake validation before user-ready external skill execution |

## Overall Assessment

Native skill system v1 is safe to rely on for:

- local reviewed manifest discovery
- static vetting and scoring
- provenance/trust diagnostics
- advisory profile visibility
- compatibility and conflict diagnostics
- safe metadata-only test/dogfood/eval evidence
- generated catalog documentation
- release-gate validation

Native skill system v1 is not safe to rely on for:

- installing external skills
- enabling marketplace skills
- running external skill scripts
- executing plugin runtimes
- auto-fixing dependencies
- enabling personal-data skills
- bypassing ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger

## Recommended Next Track

Continue with a clean release-candidate boundary and reviewed lockfile/pinning workflow before adding any external skill import, installation, or runtime execution path.
