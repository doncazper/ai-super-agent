# Skill Roots And Scopes

Native skill roots define where skill metadata may live. They are source-of-truth records for discovery only; scanning a root must never execute scripts, import code from that root, install packages, or grant tool access.

## Default Roots

| Root ID | Scope | Enabled by default | Trusted | Shadowing allowed | Writable | Purpose |
|---|---|---:|---:|---:|---:|---|
| `workspace_skills` | workspace | yes | no | no | yes | Local candidate skills under `workspace/skills` for review and experiments. |
| `project_skills` | project | yes | yes | yes | yes | Project-owned reviewed native skill manifests under `native_skills/`. |
| `personal_skills` | personal | yes | no | no | yes | User-local candidate skills; cannot override trusted native behavior by default. |
| `managed_skills` | managed | yes | yes | yes | no | Reviewed managed skills, if a future managed distribution path is approved. |
| `bundled_native_skills` | bundled native | yes | yes | no | no | Bundled project-native skills; protected against silent untrusted overrides. |
| `reconstructed_skills` | reconstructed | yes | no | no | no | Historical or reconstructed skill records; not exact originals unless evidence says so. |
| `experimental_skills` | experimental | no | no | no | yes | Disabled-by-default experiments. |

All skill text from roots is treated as `UNTRUSTED_DOCUMENT` until vetted and mapped to project-owned behavior.

## Read-Only Commands

```bash
python smart_agent.py skills roots
python smart_agent.py skills registry
python smart_agent.py skills explain-root workspace_skills
```

These commands return metadata and setup hints only. They do not run skill code, request permissions, read personal app data, or change policy.

## Safe Override Testing

To test a workspace override safely, create a candidate under `workspace/skills`, run `skills precedence`, then vet the candidate. A candidate root must explicitly allow shadowing before it can win over a lower-precedence root, and untrusted roots cannot silently override trusted native skills.
