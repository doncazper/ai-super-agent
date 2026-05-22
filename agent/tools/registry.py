from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from agent.tools.low_risk.git_tools import GIT_SCHEMAS, make_git_tools
from agent.tools.low_risk.test_runner import TEST_RUNNER_SCHEMAS, make_test_tools
from agent.tools.low_risk.time_tool import OPENAI_TOOL_SCHEMA, TOOL_NAME, get_current_time
from agent.tools.low_risk.workspace_files import FILESYSTEM_SCHEMAS, make_filesystem_tools
from agent.memory.tools import MEMORY_SCHEMAS, make_memory_tools
from agent.tools.personal.calendar import CalendarConnector
from agent.tools.personal.contacts import ContactsConnector
from agent.tools.personal.email import EmailConnector
from agent.tools.personal.messages import MessagesConnector
from agent.tools.personal.read_only import PERSONAL_SCHEMAS, make_personal_tools
from agent.tools.personal.write_actions import WRITE_ACTION_SCHEMAS, make_write_action_tools
from agent.tools.web.fetch import WEB_FETCH_SCHEMA, DomainRules, WebResponse, make_fetch_tool
from agent.tools.web.search import SearchProvider, WEB_SEARCH_SCHEMA, make_search_tool
from agent.tools.weather.provider import WEATHER_SCHEMAS, WeatherProvider, make_weather_tools


@dataclass(frozen=True)
class ToolSpec:
    name: str
    capability: str
    schema: dict[str, Any]
    handler: Callable[..., Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def schemas(self, names: set[str] | None = None) -> list[dict[str, Any]]:
        if names is None:
            return [tool.schema for tool in self._tools.values()]
        return [tool.schema for name, tool in self._tools.items() if name in names]


def default_registry(
    project_root: str | Path | None = None,
    python_executable: str | None = None,
    web_search_provider: SearchProvider | None = None,
    web_fetcher: Callable[[str, int], WebResponse] | None = None,
    web_domain_rules: DomainRules | None = None,
    weather_provider: WeatherProvider | None = None,
    memory_path: str | Path | None = None,
    calendar_connector: CalendarConnector | None = None,
    contacts_connector: ContactsConnector | None = None,
    email_connector: EmailConnector | None = None,
    messages_connector: MessagesConnector | None = None,
) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name=TOOL_NAME,
            capability=TOOL_NAME,
            schema=OPENAI_TOOL_SCHEMA,
            handler=get_current_time,
        )
    )
    root = Path(project_root or ".").resolve()
    for name, handler in make_filesystem_tools(root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=FILESYSTEM_SCHEMAS[name], handler=handler))
    for name, handler in make_git_tools(root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=GIT_SCHEMAS[name], handler=handler))
    for name, handler in make_test_tools(root, python_executable).items():
        registry.register(ToolSpec(name=name, capability=name, schema=TEST_RUNNER_SCHEMAS[name], handler=handler))
    registry.register(
        ToolSpec(
            name="web.search",
            capability="web.search",
            schema=WEB_SEARCH_SCHEMA,
            handler=make_search_tool(web_search_provider),
        )
    )
    registry.register(
        ToolSpec(
            name="web.fetch_url",
            capability="web.fetch_url",
            schema=WEB_FETCH_SCHEMA,
            handler=make_fetch_tool(fetcher=web_fetcher, domain_rules=web_domain_rules),
        )
    )
    for name, handler in make_weather_tools(weather_provider).items():
        registry.register(ToolSpec(name=name, capability=name, schema=WEATHER_SCHEMAS[name], handler=handler))
    for name, handler in make_memory_tools(memory_path).items():
        registry.register(ToolSpec(name=name, capability=name, schema=MEMORY_SCHEMAS[name], handler=handler))
    for name, handler in make_personal_tools(
        project_root=root,
        calendar_connector=calendar_connector,
        contacts_connector=contacts_connector,
        email_connector=email_connector,
        messages_connector=messages_connector,
    ).items():
        registry.register(ToolSpec(name=name, capability=name, schema=PERSONAL_SCHEMAS[name], handler=handler))
    for name, handler in make_write_action_tools().items():
        registry.register(ToolSpec(name=name, capability=name, schema=WRITE_ACTION_SCHEMAS[name], handler=handler))
    return registry
