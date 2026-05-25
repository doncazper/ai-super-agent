# Skill Inspection

`python smart_agent.py skills inspect <path_or_skill_id>` performs read-only static inspection of an approved workspace/project skill candidate or a reviewed native skill manifest id.

Inspection is intentionally non-executing:

- Skill text is treated as `UNTRUSTED_DOCUMENT`.
- Scripts, binaries, dependency manifests, and commands are inventoried only.
- Instructions inside `SKILL.md` are never followed.
- No package install, network access, plugin runtime, external binary, or marketplace operation is performed.
- Full skill content is not written to memory.

Approved inputs are limited to:

- `workspace/...`
- `native_skills/...`
- `docs/native_skills/...`
- a known native `skill_id`

Inspection detects frontmatter, manifest-like fields, requested capabilities, scripts, shell/package-install patterns, network references, environment/secrets references, filesystem escape requests, browser/cookie/session access, personal-data access requests, prompt-injection language, policy/approval bypass language, persistence/background behavior, opaque binaries, missing license/tests/docs, and missing risk/trust metadata.

Example:

```bash
python smart_agent.py skills inspect ./workspace/skills/example/SKILL.md
python smart_agent.py skills inspect native_skill_vetter
```

The output is metadata and findings only. Use `skills vet` to produce a saved risk report under `reports/native_skills/`.
