# Skill Intake Process

## Scope

The intake process reviews skill ideas and public skill examples. It does not install or run third-party code.

## Intake Steps

1. Create a candidate record from `docs/templates/native_skill_record_template.md`.
2. Record the source URL, repository, marketplace, or user-provided description.
3. Identify the skill category.
4. Run the local static vetter on copied workspace-only files, when available.
5. Summarize intended user value.
6. Record data accessed and actions possible.
7. Check license and attribution requirements.
8. Identify opaque binaries, install scripts, package managers, or hidden network calls.
9. Map intended behavior to existing brokered capabilities.
10. Identify missing capabilities and approval gates.
11. Apply disqualification criteria.
12. Write a recommended decision: accept for specification, defer, reject, or needs more research.

## Static Vetter v1

The local vetter helps intake reviewers inspect candidate skills before any native port or installation.

```bash
python smart_agent.py skills inspect ./workspace/skills/example/SKILL.md
python smart_agent.py skills vet ./workspace/skills/example/SKILL.md
python smart_agent.py skills vet-folder ./workspace/skills/example
python smart_agent.py skills score ./workspace/skills/example/SKILL.md
python smart_agent.py skills report --last
```

Vetter rules:

- Reads only files under approved workspace/project skill paths or known native skill ids.
- Treats every skill file as `UNTRUSTED_DOCUMENT`.
- Parses `SKILL.md` frontmatter when present.
- Never executes scripts, shell commands, binaries, package managers, or imported code.
- Never installs dependencies, grants permissions, or stores skill content in memory by default.
- Executes through `ToolBroker`, `PolicyEngine`, and `AuditLogger`.
- Produces a risk report with risk level, trust level, required capabilities, approval gates, reasons, `safe_to_import`, `safe_to_enable`, recommended native implementation path, and findings.
- Saves vetting reports under `reports/native_skills/` for review evidence.

The v1 vetter is heuristic static analysis. A low-risk report is not permission to install or run an external skill; it is evidence for the next human-reviewed native specification step.

## Required Review Fields

- name
- category
- source
- license
- user value
- expected frequency
- data accessed
- actions possible
- external dependencies
- network behavior
- filesystem behavior
- personal-data behavior
- secret handling
- ToolBroker mapping
- PolicyEngine behavior
- ApprovalManager behavior
- AuditLogger behavior
- memory behavior
- trust levels
- risks
- tests required
- docs required
- decision

## Intake Decisions

- accept for specification: safe enough to write local requirements
- defer: useful but blocked by missing capability, unclear design, or lower priority
- reject: violates safety model or has unacceptable risk
- needs more research: not enough evidence to decide

## Safety Defaults

- Do not run `install.sh`, package scripts, browser extensions, or binaries.
- Do not copy unreviewed source into runtime paths.
- Do not grant permissions based on a skill manifest.
- Do not add credentials during intake.
- Do not enable personal-data modules.
- Do not add persistence, launch agents, cron jobs, or daemons.

## Output

Each intake produces either:

- a completed candidate record in `docs/native_skills/NATIVE_SKILL_CANDIDATES.md`
- a decision record under `docs/decisions/`
- or a rejection/defer note with reasons
