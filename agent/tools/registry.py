from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from agent.tools.backup import BACKUP_SCHEMAS, make_backup_tools
from agent.tools.channels import CHANNEL_SCHEMAS, make_channel_tools
from agent.tools.low_risk.git_tools import GIT_SCHEMAS, make_git_tools
from agent.tools.low_risk.test_runner import TEST_RUNNER_SCHEMAS, make_test_tools
from agent.tools.low_risk.time_tool import OPENAI_TOOL_SCHEMA, TOOL_NAME, get_current_time
from agent.tools.low_risk.workspace_files import FILESYSTEM_SCHEMAS, make_filesystem_tools
from agent.tools.documents.pdf import PDF_SCHEMAS, make_pdf_tools
from agent.tools.forums.chinese_discovery import CN_FORUM_SCHEMAS, make_chinese_forum_tools
from agent.tools.forums.provider_registry import FORUM_PROVIDER_SCHEMAS, make_forum_provider_tools
from agent.tools.forums.research import FORUM_RESEARCH_SCHEMAS, make_forum_research_tools
from agent.tools.forums.reddit import REDDIT_SCHEMAS, make_reddit_tools
from agent.tools.forums.v2ex import V2EX_SCHEMAS, make_v2ex_tools
from agent.tools.leads import LEAD_SCHEMAS, make_lead_tools
from agent.tools.language import LANGUAGE_SCHEMAS, make_language_tools
from agent.messaging.channels import MESSAGING_SCHEMAS, make_messaging_tools
from agent.memory.tools import MEMORY_SCHEMAS, make_memory_tools
from agent.tools.media import MEDIA_SCHEMAS, make_media_tools
from agent.tools.native_skills import NATIVE_SKILL_SCHEMAS, make_native_skill_tools
from agent.tools.performance import PERFORMANCE_SCHEMAS, make_performance_tools
from agent.tools.platform import PLATFORM_SCHEMAS, make_platform_tools
from agent.tools.sandbox import SANDBOX_SCHEMAS, make_sandbox_tools
from agent.tools.secrets import SECRETS_SCHEMAS, make_secret_tools
from agent.tools.personal.calendar import CalendarConnector
from agent.tools.personal.contacts import ContactsConnector
from agent.tools.personal.email import EmailConnector
from agent.tools.personal.messages import MessagesConnector
from agent.tools.personal.tasks import TasksConnector
from agent.tools.personal.read_only import PERSONAL_SCHEMAS, make_personal_tools
from agent.tools.personal.write_actions import WRITE_ACTION_SCHEMAS, make_write_action_tools
from agent.tools.web.acquisition import WEB_ACQUISITION_SCHEMAS, make_web_acquisition_tools
from agent.tools.web.cache_index import WEB_CACHE_INDEX_SCHEMAS, make_web_cache_index_tools
from agent.tools.web.fetch import (
    WEB_EXTRACT_METADATA_SCHEMA,
    WEB_EXTRACT_READABLE_SCHEMA,
    WEB_FETCH_SCHEMA,
    DomainRules,
    WebResponse,
    make_extract_tools,
    make_fetch_tool,
)
from agent.tools.web.official_apis import WEB_OFFICIAL_API_SCHEMAS, make_official_api_tools
from agent.tools.web.search import (
    SearchProvider,
    SerpApiSearchProvider,
    WEB_BRAVE_DOCTOR_SCHEMA,
    WEB_PROVIDER_DECISION_SCHEMA,
    WEB_PROVIDER_POLICY_SCHEMA,
    WEB_PROVIDERS_SCHEMA,
    WEB_SEARCH_PROVIDERS_SCHEMA,
    WEB_SEARCH_SCHEMA,
    WEB_SEARXNG_DOCTOR_SCHEMA,
    WEB_SERPAPI_DOCTOR_SCHEMA,
    WEB_SERPAPI_SEARCH_SCHEMA,
    make_brave_doctor_tool,
    make_provider_policy_tools,
    make_search_tool,
    make_searxng_doctor_tool,
    make_serpapi_doctor_tool,
    make_serpapi_search_tool,
)
from agent.tools.weather.provider import WEATHER_SCHEMAS, WeatherProvider, make_weather_tools
from agent.web_acquisition.official_apis import OfficialApiRegistry


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

    def specs(self) -> list[ToolSpec]:
        return list(self._tools.values())

    def schemas(self, names: set[str] | None = None) -> list[dict[str, Any]]:
        if names is None:
            return [tool.schema for tool in self._tools.values()]
        return [tool.schema for name, tool in self._tools.items() if name in names]


def default_registry(
    project_root: str | Path | None = None,
    python_executable: str | None = None,
    web_search_provider: SearchProvider | None = None,
    serpapi_search_provider: SerpApiSearchProvider | None = None,
    web_fetcher: Callable[[str, int], WebResponse] | None = None,
    web_domain_rules: DomainRules | None = None,
    weather_provider: WeatherProvider | None = None,
    official_api_registry: OfficialApiRegistry | None = None,
    memory_path: str | Path | None = None,
    calendar_connector: CalendarConnector | None = None,
    contacts_connector: ContactsConnector | None = None,
    email_connector: EmailConnector | None = None,
    messages_connector: MessagesConnector | None = None,
    tasks_connector: TasksConnector | None = None,
    action_center: Any | None = None,
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
    for name, handler in make_pdf_tools(root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=PDF_SCHEMAS[name], handler=handler))
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
            name="web.search.serpapi",
            capability="web.search.serpapi",
            schema=WEB_SERPAPI_SEARCH_SCHEMA,
            handler=make_serpapi_search_tool(serpapi_search_provider),
        )
    )
    registry.register(
        ToolSpec(
            name="web.serpapi.doctor",
            capability="web.serpapi.doctor",
            schema=WEB_SERPAPI_DOCTOR_SCHEMA,
            handler=make_serpapi_doctor_tool(),
        )
    )
    registry.register(
        ToolSpec(
            name="web.searxng.doctor",
            capability="web.searxng.doctor",
            schema=WEB_SEARXNG_DOCTOR_SCHEMA,
            handler=make_searxng_doctor_tool(),
        )
    )
    registry.register(
        ToolSpec(
            name="web.brave.doctor",
            capability="web.brave.doctor",
            schema=WEB_BRAVE_DOCTOR_SCHEMA,
            handler=make_brave_doctor_tool(),
        )
    )
    web_policy_schemas = {
        "web.providers": WEB_PROVIDERS_SCHEMA,
        "web.provider_policy": WEB_PROVIDER_POLICY_SCHEMA,
        "web.provider_decision": WEB_PROVIDER_DECISION_SCHEMA,
        "web.search_providers": WEB_SEARCH_PROVIDERS_SCHEMA,
    }
    for name, handler in make_provider_policy_tools().items():
        registry.register(ToolSpec(name=name, capability=name, schema=web_policy_schemas[name], handler=handler))
    registry.register(
        ToolSpec(
            name="web.fetch_url",
            capability="web.fetch_url",
            schema=WEB_FETCH_SCHEMA,
            handler=make_fetch_tool(fetcher=web_fetcher, domain_rules=web_domain_rules),
        )
    )
    for name, handler in make_extract_tools(fetcher=web_fetcher, domain_rules=web_domain_rules).items():
        schema = WEB_EXTRACT_READABLE_SCHEMA if name == "web.extract_readable_text" else WEB_EXTRACT_METADATA_SCHEMA
        registry.register(ToolSpec(name=name, capability=name, schema=schema, handler=handler))
    for name, handler in make_web_acquisition_tools(
        project_root=root,
        fetcher=web_fetcher,
        domain_rules=web_domain_rules,
    ).items():
        registry.register(ToolSpec(name=name, capability=name, schema=WEB_ACQUISITION_SCHEMAS[name], handler=handler))
    for name, handler in make_web_cache_index_tools(project_root=root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=WEB_CACHE_INDEX_SCHEMAS[name], handler=handler))
    for name, handler in make_official_api_tools(registry=official_api_registry).items():
        registry.register(ToolSpec(name=name, capability=name, schema=WEB_OFFICIAL_API_SCHEMAS[name], handler=handler))
    for name, handler in make_reddit_tools(project_root=root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=REDDIT_SCHEMAS[name], handler=handler))
    for name, handler in make_v2ex_tools(project_root=root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=V2EX_SCHEMAS[name], handler=handler))
    for name, handler in make_forum_provider_tools(project_root=root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=FORUM_PROVIDER_SCHEMAS[name], handler=handler))
    for name, handler in make_forum_research_tools(project_root=root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=FORUM_RESEARCH_SCHEMAS[name], handler=handler))
    for name, handler in make_chinese_forum_tools().items():
        registry.register(ToolSpec(name=name, capability=name, schema=CN_FORUM_SCHEMAS[name], handler=handler))
    for name, handler in make_language_tools().items():
        registry.register(ToolSpec(name=name, capability=name, schema=LANGUAGE_SCHEMAS[name], handler=handler))
    for name, handler in make_platform_tools().items():
        registry.register(ToolSpec(name=name, capability=name, schema=PLATFORM_SCHEMAS[name], handler=handler))
    for name, handler in make_channel_tools().items():
        registry.register(ToolSpec(name=name, capability=name, schema=CHANNEL_SCHEMAS[name], handler=handler))
    for name, handler in make_media_tools(project_root=str(root)).items():
        registry.register(ToolSpec(name=name, capability=name, schema=MEDIA_SCHEMAS[name], handler=handler))
    for name, handler in make_performance_tools(project_root=root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=PERFORMANCE_SCHEMAS[name], handler=handler))
    for name, handler in make_sandbox_tools().items():
        registry.register(ToolSpec(name=name, capability=name, schema=SANDBOX_SCHEMAS[name], handler=handler))
    for name, handler in make_secret_tools(project_root=root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=SECRETS_SCHEMAS[name], handler=handler))
    for name, handler in make_weather_tools(weather_provider).items():
        registry.register(ToolSpec(name=name, capability=name, schema=WEATHER_SCHEMAS[name], handler=handler))
    for name, handler in make_memory_tools(memory_path).items():
        registry.register(ToolSpec(name=name, capability=name, schema=MEMORY_SCHEMAS[name], handler=handler))
    for name, handler in make_native_skill_tools(root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=NATIVE_SKILL_SCHEMAS[name], handler=handler))
    for name, handler in make_backup_tools(root).items():
        registry.register(ToolSpec(name=name, capability=name, schema=BACKUP_SCHEMAS[name], handler=handler))
    for name, handler in make_messaging_tools(root, action_center=action_center).items():
        registry.register(ToolSpec(name=name, capability=name, schema=MESSAGING_SCHEMAS[name], handler=handler))
    for name, handler in make_lead_tools(root, action_center=action_center).items():
        registry.register(ToolSpec(name=name, capability=name, schema=LEAD_SCHEMAS[name], handler=handler))
    for name, handler in make_personal_tools(
        project_root=root,
        calendar_connector=calendar_connector,
        contacts_connector=contacts_connector,
        email_connector=email_connector,
        messages_connector=messages_connector,
        tasks_connector=tasks_connector,
        action_center=action_center,
    ).items():
        registry.register(ToolSpec(name=name, capability=name, schema=PERSONAL_SCHEMAS[name], handler=handler))
    for name, handler in make_write_action_tools(action_center=action_center).items():
        registry.register(ToolSpec(name=name, capability=name, schema=WRITE_ACTION_SCHEMAS[name], handler=handler))
    return registry
