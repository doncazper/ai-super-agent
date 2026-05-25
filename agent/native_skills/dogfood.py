from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.native_skills.registry import NativeSkillRegistry


def native_skill_dogfood_plan(project_root: str | Path = ".", skill_id: str | None = None) -> dict[str, Any]:
    registry = NativeSkillRegistry(project_root)
    manifests = registry.manifests()
    target = None
    if skill_id:
        target = next((manifest for manifest in manifests if manifest.skill_id == skill_id), None)
        if target is None:
            return {
                "status": "error",
                "error": "native skill not found",
                "skill_id": skill_id,
                "execution_model": _execution_model(),
            }
    selected_id = skill_id or (manifests[0].skill_id if manifests else "")
    if not selected_id:
        return {"status": "requires_setup", "error": "no native skill manifests found", "execution_model": _execution_model()}

    commands = [
        f"python smart_agent.py skills test {selected_id}",
        f"python smart_agent.py skills validate {selected_id}",
        f"python smart_agent.py skills doctor {selected_id}",
        f"python smart_agent.py skills compatibility {selected_id}",
        "python smart_agent.py skills conflicts",
        f"python smart_agent.py skills provenance {selected_id}",
        f"python smart_agent.py skills trust {selected_id}",
        "python smart_agent.py dogfood run native_skills_core --dry-run",
        "python smart_agent.py eval run --native-skills --json",
    ]
    return {
        "status": "ok",
        "skill_id": selected_id,
        "commands": commands,
        "manual_qa_notes": [
            "Run only safe/default checks unless an explicit future approval covers high/critical or personal-data behavior.",
            "Do not execute candidate skill scripts, package installers, plugin runtimes, or marketplace code.",
            "Use dogfood sessions for redacted evidence, then update FEATURE_MATURITY conservatively.",
        ],
        "failure_signals": [
            "manifest validation failure",
            "blocking conflict",
            "prompt-injection fixture not caught",
            "secret fixture not caught",
            "high/critical or personal-data skill not skipped by default",
            "dogfood command attempts external script or plugin execution",
        ],
        "execution_model": _execution_model(),
    }


def _execution_model() -> str:
    return "plan_only; dogfood planning never executes untrusted skills, scripts, package installers, providers, plugin runtimes, high/critical skills, or personal-data skills by default"
