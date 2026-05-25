# Skill Manifest Schema

Native skill manifests are strict metadata records. They declare requirements before a skill can be considered usable, but they do not execute code, install dependencies, grant permissions, or enable tools.

Required fields include identity, provenance, root, risk/trust, ToolBroker capability mapping, dependency declarations, approval behavior, memory behavior, audit behavior, network/filesystem behavior, input/output schemas, docs/tests/dogfood references, owner, license, setup hint, and known limitations.

Key safety fields:

- `risk_level`
- `trust_level`
- `required_capabilities`
- `approval_required`
- `approval_reuse_allowed`
- `memory_behavior`
- `audit_required`
- `network_behavior`
- `filesystem_behavior`

Validation rejects missing risk/trust/memory/audit fields, unknown required capabilities, executable manifest keys, bypass language, enabled personal-data skills, and CRITICAL skills that do not require exact per-action approval with no approval reuse.

Skill instructions and skill files remain `UNTRUSTED_DOCUMENT`; manifests cannot override project policy or system/developer/user instructions.
