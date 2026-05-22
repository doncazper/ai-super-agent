from __future__ import annotations

from agent.core.router import Router


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
