# Skill Precedence

Native skill precedence resolves duplicate `skill_id` records deterministically while making shadowing visible.

Default precedence, highest first:

1. `workspace_skills`
2. `project_skills`
3. `personal_skills`
4. `managed_skills`
5. `bundled_native_skills`
6. `reconstructed_skills`
7. `experimental_skills`

Higher-precedence roots can shadow lower-precedence roots only when the higher root is enabled and explicitly allows shadowing. This prevents unreviewed workspace, personal, reconstructed, or experimental skill text from silently changing trusted native behavior.

## Diagnostics

```bash
python smart_agent.py skills precedence
```

The report includes:

- duplicate skill IDs
- the winning skill candidate
- shadowed candidates
- root trust and source metadata
- diagnostics explaining blocked or visible shadowing

The scan is metadata-only. It reads `SKILL.md` and manifest files as untrusted documents and never executes scripts, shell commands, package installers, or Python modules from a skill folder.

## Why Shadowing Is Dangerous

Skill files can contain untrusted instructions that ask the agent to ignore policy, reveal secrets, use browser sessions, access private data, or execute arbitrary code. Precedence therefore cannot be a plain path-order rule. The resolver must account for trust, root configuration, and explicit shadowing permissions.
