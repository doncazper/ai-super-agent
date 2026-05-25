# Skill Dogfood Runbook

Native skill dogfood is manual QA evidence for reviewed metadata and safe fixtures. It must not execute untrusted skill packages or marketplace/plugin runtime code.

## Commands

```bash
python smart_agent.py skills dogfood native_skill_vetter
python smart_agent.py dogfood run native_skills_core --session
python smart_agent.py dogfood run native_skill_vetting --session
python smart_agent.py eval run --native-skills
```

Use `skills dogfood <skill_id>` first to print a safe plan. Use a redacted session when running dogfood suites:

```bash
python smart_agent.py session start --name native-skills-dogfood
python smart_agent.py dogfood run native_skills_core --session
python smart_agent.py dogfood run native_skill_vetting --session
```

## What To Verify

- manifest validation passes or fails clearly
- dependency gaps report `requires_setup`
- provenance/trust/lockfile diagnostics are present
- conflicts are visible and not auto-resolved
- profile visibility remains advisory
- compatibility remains metadata-only
- prompt-injection and secret fixtures are caught
- risky fixture vetting reports high/forbidden findings
- high/critical and personal-data skills are skipped by default

## Forbidden During Dogfood

- running external skill scripts
- installing dependencies
- enabling marketplace skills
- executing plugin runtimes
- accessing personal data
- approving high/critical skill behavior automatically
- treating dogfood output as permission to use a skill

## Maturity Updates

Dogfood results can support moving a skill toward `Tested` only when tests, docs, command registry, policy/audit behavior, and release-gate evidence agree. Live/manual dogfood evidence is still required before `User-Ready`.
