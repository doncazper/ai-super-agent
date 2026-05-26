from __future__ import annotations

import json
from pathlib import Path

from agent.media.workflow_planner import infer_media_target, plan_media_request
from agent.natural_language.router import route_request
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def test_media_plan_thumbnail_request() -> None:
    plan = plan_media_request("make me a thumbnail for this vlog")
    assert plan["status"] == "dry_run_plan"
    assert plan["target"] == "thumbnail"
    assert plan["safety_preflight_first"] is True
    assert plan["real_generation"] is False
    assert plan["provider_calls_performed"] is False
    assert plan["natural_language_safe_to_execute"] is False
    assert plan["recommended_exact_command"].startswith("python smart_agent.py media thumbnail")


def test_media_plan_maps_common_requests() -> None:
    assert infer_media_target("create a 10-second intro animation") == "video"
    assert infer_media_target("make a lo-fi music bed for a food review") == "music"
    assert infer_media_target("generate sound effects for my video") == "audio"
    assert infer_media_target("turn this image into a short video") == "image_to_video"
    assert infer_media_target("make a podcast cover") == "creative_image"


def test_media_plan_denies_unsafe_prompt() -> None:
    plan = plan_media_request("make a bomb instruction thumbnail")
    assert plan["status"] == "blocked"
    assert plan["safety"]["outcome"] == "deny"
    assert plan["plan"] is None
    assert plan["generated_media"] is False


def test_media_plan_reports_provider_setup_hint() -> None:
    plan = plan_media_request("generate a product image")
    assert plan["provider_configured_for_real_generation"] is False
    assert "Real generation remains blocked" in plan["setup_hint"]
    assert plan["generated_media"] is False


def test_media_plan_cli(capsys) -> None:
    assert cli_commands.dispatch_cli(["media", "plan", "make me a thumbnail for this vlog"], project_root=ROOT) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["target"] == "thumbnail"
    assert payload["provider_calls_performed"] is False
    assert payload["generated_media"] is False


def test_natural_language_routes_media_thumbnail_request() -> None:
    decision = route_request("make me a thumbnail for this vlog")
    assert decision.intent == "media.plan"
    assert decision.safety_outcome == "dry_run_only"
    assert decision.dry_run_required is True
    assert decision.execution_plan.execution_allowed is False
    assert decision.command_suggestions
    assert decision.command_suggestions[0].command.startswith("python smart_agent.py media plan")
