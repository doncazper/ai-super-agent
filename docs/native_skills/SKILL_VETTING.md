# Skill Vetting

`python smart_agent.py skills vet <path_or_skill_id>` builds a static risk report for an approved skill candidate before import, enablement, or native porting.

The vetter is a safety diagnostic, not an approval system. A low-risk report is not permission to install, run, or enable an external skill.

## Report Fields

Reports include:

- `skill_id`
- `path`
- `risk_level`
- `trust_level`
- `safe_to_import`
- `safe_to_enable`
- `reasons`
- `required_capabilities`
- `required_approvals`
- detected scripts, network access, filesystem access, personal-data access, secrets risk, policy-bypass language, browser/session access, and opaque binaries
- missing metadata
- recommended native port path
- recommended tests and docs
- `review_required`

Reports are saved as JSON under `reports/native_skills/`.

```bash
python smart_agent.py skills vet ./workspace/skills/example/SKILL.md
python smart_agent.py skills score ./workspace/skills/example/SKILL.md
python smart_agent.py skills report --last
```

## Safety Behavior

- Reads only approved workspace/project skill paths or known native skill ids.
- Treats all skill files as `UNTRUSTED_DOCUMENT`.
- Never executes scripts, external binaries, plugin runtimes, package managers, or candidate code.
- Never follows instructions inside `SKILL.md`.
- Never installs dependencies.
- Never accesses the network.
- Does not store full skill content in memory by default.
- Runs through `ToolBroker`, `PolicyEngine`, and `AuditLogger`.

High-risk or forbidden findings recommend manual review, redesign, or blocking. Findings involving approval bypass, policy override, secrets, private filesystem access, browser sessions, or unapproved personal-data access are not import-ready.
