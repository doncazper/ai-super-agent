from __future__ import annotations

import pytest

from agent.core.router import Router


@pytest.fixture(autouse=True)
def isolate_weather_preferences(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_PREFERENCES_PATH", str(tmp_path / "weather_preferences.json"))


def test_router_preserves_normal_chat_without_tools() -> None:
    route = Router().route("Explain RCS vs iMessage")

    assert route.name == "chat.default"
    assert route.use_tools is False
    assert route.tool_names == set()


def test_router_selects_time_tool_for_time_query() -> None:
    route = Router().route("What time is it?")

    assert route.name == "tool.time"
    assert route.use_tools is True
    assert route.tool_names == {"time.get_current_time"}


def test_router_no_tools_override_wins() -> None:
    route = Router().route("What time is it?", force_no_tools=True)

    assert route.name == "chat.no_tools"
    assert route.use_tools is False


def test_router_selects_web_search_for_search_query() -> None:
    route = Router().route("Look up current Swift release notes")

    assert route.name == "tool.web_search"
    assert route.use_tools is True
    assert route.tool_names == {"web.search"}


def test_router_selects_web_fetch_for_url_query() -> None:
    route = Router().route("https://example.com")

    assert route.name == "tool.web_fetch"
    assert route.use_tools is True
    assert route.tool_names == {"web.fetch_url"}


def test_router_selects_memory_tools_for_memory_query() -> None:
    route = Router().route("Remember that I prefer short answers")

    assert route.name == "tool.memory"
    assert route.use_tools is True
    assert "memory.store" in route.tool_names


def test_router_detects_weather_intent_with_location() -> None:
    route = Router().route("What's the weather in Phoenix?")

    assert route.name == "tool.weather"
    assert route.use_tools is True
    assert route.tool_names == {"weather.current", "weather.forecast"}
    assert route.metadata["location"] == "Phoenix"


def test_router_weather_impact_routes_to_weather_and_web() -> None:
    route = Router().route("Are flights delayed due to weather at LAX?")

    assert route.name == "tool.weather_research"
    assert route.use_tools is True
    assert {"weather.current", "weather.forecast", "web.search"}.issubset(route.tool_names)
    assert route.metadata["web_context_needed"] is True
    assert route.metadata["location"] == "LAX"


def test_router_latest_hurricane_routes_to_alerts_and_web_without_location_inference() -> None:
    route = Router().route("What is the latest hurricane update?")

    assert route.name == "tool.weather_research"
    assert route.use_tools is True
    assert route.tool_names == {"weather.alerts", "web.search"}
    assert route.metadata["missing_location"] is True
    assert route.metadata["location_detected"] is False


def test_router_detects_weather_rain_tomorrow_with_location() -> None:
    route = Router().route("Is it going to rain tomorrow in LA?")

    assert route.name == "tool.weather"
    assert route.use_tools is True
    assert route.metadata["requested_period"] == "tomorrow"
    assert route.metadata["location"] == "LA"


def test_router_detects_weather_wear_today_with_location() -> None:
    route = Router().route("What should I wear in Seattle today?")

    assert route.name == "tool.weather"
    assert route.use_tools is True
    assert route.metadata["requested_period"] == "today"
    assert route.metadata["location"] == "Seattle"


def test_router_does_not_route_educational_weather_topic() -> None:
    route = Router().route("Explain how weather forecasting works.")

    assert route.name == "chat.default"
    assert route.use_tools is False


def test_router_does_not_route_climate_comparison() -> None:
    route = Router().route("What is the difference between climate and weather?")

    assert route.name == "chat.default"
    assert route.use_tools is False


def test_router_does_not_route_creative_rain_prompt() -> None:
    route = Router().route("Write a poem about rain.")

    assert route.name == "chat.default"
    assert route.use_tools is False


def test_router_does_not_route_weather_app_architecture() -> None:
    route = Router().route("Build a weather app architecture.")

    assert route.name == "chat.default"
    assert route.use_tools is False


def test_router_handles_missing_weather_location_without_inference(monkeypatch) -> None:
    monkeypatch.delenv("WEATHER_DEFAULT_LOCATION", raising=False)

    route = Router().route("Do I need an umbrella today?")

    assert route.name == "chat.weather_missing_location"
    assert route.use_tools is False
    assert route.metadata["missing_location"] is True
    assert route.metadata["location_detected"] is False


def test_router_does_not_infer_personal_location(monkeypatch) -> None:
    monkeypatch.delenv("WEATHER_DEFAULT_LOCATION", raising=False)

    route = Router().route("Any weather alerts near me?")

    assert route.name == "chat.weather_missing_location"
    assert route.use_tools is False
    assert route.metadata["missing_location"] is True


def test_router_uses_default_weather_location_only_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_DEFAULT_LOCATION", "Phoenix, AZ")

    route = Router().route("How hot will it be this weekend?")

    assert route.name == "tool.weather"
    assert route.use_tools is True
    assert route.metadata["default_location_used"] is True
    assert route.metadata["location_detected"] is False
    assert route.metadata["location"] == "Phoenix, AZ"
    assert route.metadata["requested_period"] == "weekend"


def test_router_no_tools_override_wins_for_weather() -> None:
    route = Router().route("What's the weather in Phoenix?", force_no_tools=True)

    assert route.name == "chat.no_tools"
    assert route.use_tools is False
    assert route.tool_names == set()
