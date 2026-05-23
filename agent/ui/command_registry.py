from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


STATUS_VALUES = {"active", "experimental", "stubbed", "deprecated", "legacy", "removed", "blocked", "planned"}
RISK_VALUES = {"SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL", "FORBIDDEN"}


@dataclass(frozen=True)
class CommandRecord:
    command_id: str
    command: str
    group: str
    description: str
    example: str
    status: str
    maturity_level: str
    risk_level: str
    trust_level: str
    requires_approval: str
    requires_connector: str
    requires_provider: str
    side_effects: str
    toolbroker_path: str
    audit_behavior: str
    memory_behavior: str
    test_coverage: str
    manual_qa_status: str
    docs_link: str
    introduced: str = "2026-05-22"
    deprecated: str = "n/a"
    replacement: str = "n/a"
    last_verified: str = "2026-05-23 automated"
    known_bugs: str = "none known"
    notes: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _r(command_id: str, command: str, group: str, description: str, example: str, status: str, maturity: str, risk: str, trust: str, approval: str, connector: str, provider: str, side_effects: str, broker: str, audit: str, memory: str, tests: str, qa: str, docs: str, notes: str = "", introduced: str = "2026-05-22", replacement: str = "n/a") -> CommandRecord:
    return CommandRecord(
        command_id=command_id,
        command=command,
        group=group,
        description=description,
        example=example,
        status=status,
        maturity_level=maturity,
        risk_level=risk,
        trust_level=trust,
        requires_approval=approval,
        requires_connector=connector,
        requires_provider=provider,
        side_effects=side_effects,
        toolbroker_path=broker,
        audit_behavior=audit,
        memory_behavior=memory,
        test_coverage=tests,
        manual_qa_status=qa,
        docs_link=docs,
        notes=notes,
        introduced=introduced,
        replacement=replacement,
    )


COMMANDS: tuple[CommandRecord, ...] = (
    _r("CMD-CORE-001", "python smart_agent.py --no-tools \"<message>\"", "Core runtime", "Run clean LM Studio/Qwopus chat with no tools attached.", "python smart_agent.py --no-tools \"Explain RCS vs iMessage\"", "active", "5 Hardened", "SAFE", "TRUSTED_USER / MODEL_OUTPUT", "no", "LM Studio", "local OpenAI-compatible API", "model call", "n/a", "no tool audit for pure chat", "no memory write", "unit/runtime tests", "pending manual live LM Studio smoke", "README.md", "Must preserve the original user text."),
    _r("CMD-CORE-002", "python smart_agent.py --interactive", "Core runtime", "Start the interactive local chat shell.", "python smart_agent.py --interactive", "active", "4 Tested", "SAFE", "TRUSTED_USER / MODEL_OUTPUT", "no", "LM Studio", "local OpenAI-compatible API", "model call", "ToolBroker for tools only", "tool calls audited when used", "no memory write by default", "CLI tests", "pending manual interactive smoke", "README.md"),
    _r("CMD-CORE-003", "python smart_agent.py --debug \"<message>\"", "Core runtime", "Run a message with redacted debug diagnostics.", "python smart_agent.py --debug \"What time is it?\"", "active", "4 Tested", "LOW", "TRUSTED_USER / MODEL_OUTPUT", "per tool", "LM Studio", "local OpenAI-compatible API", "model/tool call", "yes for tool calls", "tool calls and denials audited", "no memory write by default", "debug/no-secret tests", "pending manual debug smoke", "README.md"),
    _r("CMD-CORE-004", "python smart_agent.py --dry-run \"<message>\"", "Core runtime", "Evaluate routed tool policy without executing tools.", "python smart_agent.py --dry-run \"What time is it?\"", "active", "4 Tested", "SAFE", "MODEL_OUTPUT", "reports required approvals", "none", "none", "dry-run audit", "yes dry-run", "dry-run event may be audited", "no memory write", "preflight/dry-run tests", "manual safe smoke recommended", "README.md"),
    _r("CMD-CORE-005", "python smart_agent.py setup", "Doctor/status/config", "Print minimal local setup guidance.", "python smart_agent.py setup", "active", "3 Implemented", "SAFE", "TRUSTED_USER", "no", "none", "none", "prints guidance", "n/a", "none", "none", "CLI dispatch tests", "manual verified by help output", "README.md"),
    _r("CMD-DOCTOR-001", "python smart_agent.py doctor", "Doctor/status/config", "Check Python, config, LM Studio reachability, policy, audit, and connector readiness.", "python smart_agent.py doctor", "active", "5 Hardened", "SAFE", "LOCAL_PRIVATE_DATA metadata", "no", "LM Studio optional", "none", "read metadata/status", "n/a", "status-only; no model prompts", "no memory write", "doctor tests", "manual live runtime smoke recommended", "README.md"),
    _r("CMD-DASHBOARD-001", "python smart_agent.py dashboard", "Dashboard", "Show read-only agent dashboard.", "python smart_agent.py dashboard", "active", "5 Hardened", "SAFE", "Tool-specific metadata", "no", "none", "none", "read metadata", "n/a", "reads audit metadata only", "memory counts only", "dashboard tests", "manual QA pending", "README.md"),
    _r("CMD-DASHBOARD-002", "python smart_agent.py status", "Dashboard", "Alias for read-only dashboard status.", "python smart_agent.py status", "active", "5 Hardened", "SAFE", "Tool-specific metadata", "no", "none", "none", "read metadata", "n/a", "reads audit metadata only", "memory counts only", "dashboard tests", "manual QA pending", "README.md"),
    _r("CMD-TOOLS-001", "python smart_agent.py tools list", "Tools", "List registered tool schemas.", "python smart_agent.py tools list", "active", "4 Tested", "SAFE", "Tool metadata", "no", "none", "none", "read metadata", "n/a", "none", "none", "CLI tests", "manual QA pending", "README.md"),
    _r("CMD-CONFIG-001", "python smart_agent.py config show", "Doctor/status/config", "Show redacted runtime config.", "python smart_agent.py config show", "active", "4 Tested", "SAFE", "LOCAL_PRIVATE_DATA metadata", "no", "none", "none", "read config", "n/a", "none", "none", "config tests", "manual QA pending", "README.md"),
    _r("CMD-CONFIG-002", "python smart_agent.py config diff", "Doctor/status/config", "Show current capability config summary.", "python smart_agent.py config diff", "active", "3 Implemented", "SAFE", "LOCAL_PRIVATE_DATA metadata", "no", "none", "none", "read config", "n/a", "none", "none", "CLI tests", "manual QA pending", "README.md"),
    _r("CMD-CONN-001", "python smart_agent.py connectors list", "Connectors", "List connector metadata without personal reads.", "python smart_agent.py connectors list", "active", "4 Tested", "SAFE", "Tool-specific metadata", "no", "none", "none", "read metadata", "n/a", "status checks avoid personal data", "no memory write", "connector tests", "manual QA pending", "README.md"),
    _r("CMD-CONN-002", "python smart_agent.py connectors doctor", "Connectors", "Run connector status checks without personal data reads.", "python smart_agent.py connectors doctor", "active", "4 Tested", "SAFE", "Tool-specific metadata", "no", "none", "none", "read metadata", "n/a", "status checks avoid personal data", "no memory write", "connector tests", "manual QA pending", "README.md"),
    _r("CMD-CONN-003", "python smart_agent.py connectors status <connector>", "Connectors", "Show one connector status.", "python smart_agent.py connectors status weather", "active", "4 Tested", "SAFE", "Tool-specific metadata", "no", "connector-specific", "provider optional", "read metadata", "n/a", "status checks avoid personal data", "no memory write", "connector tests", "manual QA pending", "README.md"),
    _r("CMD-PERM-001", "python smart_agent.py permissions show", "Approvals", "Show persisted permission grants.", "python smart_agent.py permissions show", "active", "4 Tested", "SAFE", "LOCAL_PRIVATE_DATA metadata", "no", "none", "none", "read permission metadata", "n/a", "permission changes audited in tool flows", "no memory write", "permission tests", "manual QA pending", "README.md"),
    _r("CMD-PERM-002", "python smart_agent.py permissions grant <capability>", "Approvals", "Grant a capability permission entry.", "python smart_agent.py permissions grant web.search", "experimental", "3 Implemented", "MEDIUM", "TRUSTED_USER", "user action", "none", "none", "permission write", "n/a", "permission changes affect future policy checks", "no memory write", "permission tests", "manual QA with caution", "README.md"),
    _r("CMD-PERM-003", "python smart_agent.py permissions revoke <capability>", "Approvals", "Revoke a capability permission entry.", "python smart_agent.py permissions revoke web.search", "experimental", "3 Implemented", "MEDIUM", "TRUSTED_USER", "user action", "none", "none", "permission write", "n/a", "permission changes affect future policy checks", "no memory write", "permission tests", "manual QA with caution", "README.md"),
    _r("CMD-APPROVAL-001", "python smart_agent.py approvals list", "Approvals", "List pending approval requests.", "python smart_agent.py approvals list", "active", "4 Tested", "SAFE", "LOCAL_PRIVATE_DATA metadata", "no", "none", "none", "read approval queue", "n/a", "approval lifecycle audited", "no memory write", "approval tests", "manual QA pending", "README.md"),
    _r("CMD-APPROVAL-002", "python smart_agent.py approvals show <request_id>", "Approvals", "Show one approval request.", "python smart_agent.py approvals show apr_123", "active", "4 Tested", "MEDIUM", "LOCAL_PRIVATE_DATA metadata", "no", "none", "none", "read redacted preview", "n/a", "approval lifecycle audited", "no memory write", "approval tests", "manual QA pending", "README.md"),
    _r("CMD-APPROVAL-003", "python smart_agent.py approvals approve <request_id>", "Approvals", "Approve a pending request.", "python smart_agent.py approvals approve apr_123", "active", "4 Tested", "HIGH", "TRUSTED_USER", "yes", "none", "none", "approval state write", "n/a", "approval decision audited", "no memory write", "approval tests", "manual QA with test request", "README.md"),
    _r("CMD-APPROVAL-004", "python smart_agent.py approvals deny <request_id>", "Approvals", "Deny a pending request.", "python smart_agent.py approvals deny apr_123", "active", "4 Tested", "SAFE", "TRUSTED_USER", "no", "none", "none", "approval state write", "n/a", "denial audited", "no memory write", "approval tests", "manual QA with test request", "README.md"),
    _r("CMD-ACTION-001", "python smart_agent.py actions list", "Action Center", "List pending and historical Action Center records.", "python smart_agent.py actions list", "active", "4 Tested", "SAFE", "MODEL_OUTPUT / LOCAL_PRIVATE_DATA metadata", "no", "none", "none", "read action queue", "n/a", "action lifecycle audited", "no memory write", "action tests", "manual QA pending", "README.md"),
    _r("CMD-ACTION-002", "python smart_agent.py actions show <action_id>", "Action Center", "Show exact action preview.", "python smart_agent.py actions show act_123", "active", "4 Tested", "MEDIUM", "MODEL_OUTPUT / LOCAL_PRIVATE_DATA metadata", "no", "none", "none", "read redacted preview", "n/a", "action lifecycle audited", "no memory write", "action tests", "manual QA pending", "README.md"),
    _r("CMD-ACTION-003", "python smart_agent.py actions approve <action_id>", "Action Center", "Approve one pending action.", "python smart_agent.py actions approve act_123", "active", "4 Tested", "HIGH", "TRUSTED_USER", "yes/per-action", "connector-specific", "provider optional", "approval state write", "n/a", "action approval audited", "no memory write", "action tests", "manual QA with mock action", "README.md"),
    _r("CMD-ACTION-004", "python smart_agent.py actions deny <action_id>", "Action Center", "Deny one pending action.", "python smart_agent.py actions deny act_123", "active", "4 Tested", "SAFE", "TRUSTED_USER", "no", "none", "none", "approval state write", "n/a", "action denial audited", "no memory write", "action tests", "manual QA with mock action", "README.md"),
    _r("CMD-ACTION-005", "python smart_agent.py actions edit <action_id> key=value", "Action Center", "Edit action preview args and invalidate prior approval.", "python smart_agent.py actions edit act_123 subject=\"New subject\"", "active", "4 Tested", "HIGH", "TRUSTED_USER", "yes for later execution", "connector-specific", "provider optional", "action state write", "n/a", "edit lifecycle audited", "no memory write", "action edit tests", "manual QA pending", "README.md"),
    _r("CMD-ACTION-006", "python smart_agent.py actions clear-denied", "Action Center", "Remove denied action records.", "python smart_agent.py actions clear-denied", "active", "3 Implemented", "LOW", "TRUSTED_USER", "no", "none", "none", "action queue cleanup", "n/a", "cleanup audited", "no memory write", "action tests", "manual QA pending", "README.md"),
    _r("CMD-ACTION-007", "python smart_agent.py actions export", "Action Center", "Export action records.", "python smart_agent.py actions export", "active", "3 Implemented", "MEDIUM", "MODEL_OUTPUT / LOCAL_PRIVATE_DATA metadata", "no", "none", "none", "read action queue", "n/a", "export audited", "no memory write", "action tests", "manual QA pending", "README.md"),
    _r("CMD-AUDIT-001", "python smart_agent.py audit tail", "Doctor/status/config", "Show recent audit entries.", "python smart_agent.py audit tail 20", "active", "4 Tested", "MEDIUM", "Tool-specific metadata", "no", "none", "none", "read audit log", "n/a", "audit viewer only", "no memory write", "dashboard/audit tests", "manual QA pending", "README.md"),
    _r("CMD-PREFLIGHT-001", "python smart_agent.py preflight \"<request>\"", "Approvals", "Show dry-run route, risk, and approvals for a request.", "python smart_agent.py preflight \"delete workspace file\"", "active", "4 Tested", "SAFE", "MODEL_OUTPUT", "reports required approvals", "none", "none", "dry-run audit", "yes dry-run", "dry-run audited", "no memory write", "preflight tests", "manual QA pending", "README.md"),
    _r("CMD-SMOKE-001", "python smart_agent.py smoke --all-safe --dry-run", "Quality/evals", "Run controlled smoke checks without personal reads.", "python smart_agent.py smoke --all-safe --dry-run", "active", "4 Tested", "LOW", "Tool-specific", "no for safe checks", "optional", "optional", "tool dry-runs/status checks", "yes where tools run", "brokered calls audited", "no personal memory", "smoke tests", "manual QA pending", "README.md"),
    _r("CMD-EVAL-001", "python smart_agent.py eval list", "Quality/evals", "List eval checks.", "python smart_agent.py eval list", "active", "4 Tested", "SAFE", "Tool metadata", "no", "none", "none", "read metadata", "n/a", "none", "none", "eval tests", "manual QA pending", "README.md"),
    _r("CMD-EVAL-002", "python smart_agent.py eval run --safe", "Quality/evals", "Run safe mocked/live-optional eval checks.", "python smart_agent.py eval run --safe", "active", "4 Tested", "LOW", "Tool-specific", "no for safe checks", "optional", "optional", "brokered safe tool calls", "yes for tools", "tool calls audited", "non-sensitive memory test fact deleted", "eval tests", "manual safe eval recommended", "README.md"),
    _r("CMD-EVAL-003", "python smart_agent.py eval report", "Quality/evals", "Show latest eval report.", "python smart_agent.py eval report", "active", "4 Tested", "SAFE", "Tool metadata", "no", "none", "none", "read docs report", "n/a", "none", "no memory write", "eval tests", "manual QA pending", "README.md"),
    _r("CMD-WEATHER-001", "python smart_agent.py weather doctor", "Weather", "Check weather provider configuration.", "python smart_agent.py weather doctor", "active", "5 Hardened", "SAFE", "UNTRUSTED_WEB metadata", "no", "weather", "open_meteo/nws/weatherkit stub", "read config/status", "yes", "status audited where brokered", "no memory write", "weather tests", "manual live provider smoke recommended", "README.md"),
    _r("CMD-WEATHER-002", "python smart_agent.py weather smoke \"<location>\"", "Weather", "Run current and forecast weather checks for an explicit location.", "python smart_agent.py weather smoke \"Phoenix, AZ\"", "active", "5 Hardened", "LOW", "UNTRUSTED_WEB", "no", "weather", "open_meteo/nws", "network/cache", "yes", "provider calls audited", "weather cache only", "weather tests", "manual live smoke recommended", "README.md"),
    _r("CMD-WEATHER-003", "python smart_agent.py weather current \"<location>\"", "Weather", "Get current weather.", "python smart_agent.py weather current \"Phoenix, AZ\" --provider open_meteo", "active", "5 Hardened", "LOW", "UNTRUSTED_WEB", "no", "weather", "open_meteo/nws", "network/cache", "yes", "provider calls audited", "weather cache only", "weather tests", "manual live smoke recommended", "README.md"),
    _r("CMD-WEATHER-004", "python smart_agent.py weather forecast \"<location>\" --days N", "Weather", "Get forecast for an explicit location.", "python smart_agent.py weather forecast \"Phoenix, AZ\" --days 3", "active", "5 Hardened", "LOW", "UNTRUSTED_WEB", "no", "weather", "open_meteo/nws", "network/cache", "yes", "provider calls audited", "weather cache only", "weather tests", "manual live smoke recommended", "README.md"),
    _r("CMD-WEATHER-005", "python smart_agent.py weather alerts \"<location>\"", "Weather", "Get weather alerts if provider supports alerts.", "python smart_agent.py weather alerts \"Los Angeles, CA\" --provider nws", "active", "5 Hardened", "LOW", "UNTRUSTED_WEB", "no", "weather", "nws", "network/cache", "yes", "provider calls audited", "weather cache only", "weather tests", "manual NWS live smoke recommended", "README.md"),
    _r("CMD-WEATHER-006", "python smart_agent.py weather config show", "Weather", "Show explicit weather preferences.", "python smart_agent.py weather config show", "active", "5 Hardened", "SAFE", "LOCAL_PRIVATE_DATA metadata", "no", "weather", "none", "read config", "n/a", "default location use audited in weather calls", "no memory write", "weather prefs tests", "manual QA pending", "README.md"),
    _r("CMD-WEATHER-007", "python smart_agent.py weather config set-default \"<location>\"", "Weather", "Set opt-in default weather location.", "python smart_agent.py weather config set-default \"Phoenix, AZ\"", "active", "5 Hardened", "MEDIUM", "TRUSTED_USER", "user action", "weather", "none", "writes config", "n/a", "default use audited later", "no memory write", "weather prefs tests", "manual QA pending", "README.md"),
    _r("CMD-WEATHER-008", "python smart_agent.py weather config clear-default", "Weather", "Clear default weather location.", "python smart_agent.py weather config clear-default", "active", "5 Hardened", "LOW", "TRUSTED_USER", "no", "weather", "none", "writes config", "n/a", "none", "no memory write", "weather prefs tests", "manual QA pending", "README.md"),
    _r("CMD-WEATHER-009", "python smart_agent.py weather cache clear", "Weather", "Clear weather cache.", "python smart_agent.py weather cache clear", "active", "5 Hardened", "LOW", "UNTRUSTED_WEB metadata", "no", "weather", "none", "cache delete", "yes", "cache clear audited", "no memory write", "cache tests", "manual QA pending", "README.md"),
    _r("CMD-WEB-001", "python smart_agent.py web \"<query>\"", "Web/research", "Run public web search through configured provider.", "python smart_agent.py web \"LM Studio local API\"", "active", "5 Hardened", "LOW", "UNTRUSTED_WEB", "no", "web", "Brave optional", "network", "yes", "provider/domain audited", "no search history memory", "web tests", "manual provider smoke pending", "README.md"),
    _r("CMD-WEB-002", "python smart_agent.py research \"<query>\"", "Web/research", "Search, fetch selected pages, and summarize with source URLs.", "python smart_agent.py research \"Open-Meteo weather API\"", "active", "5 Hardened", "LOW", "UNTRUSTED_WEB", "no", "web", "search provider optional", "network", "yes", "search/fetch audited", "no memory write", "research tests", "manual provider smoke pending", "README.md"),
    _r("CMD-BROWSER-001", "python smart_agent.py browser read-url \"<url>\"", "Web/research", "Fetch an explicit public URL without browser history access.", "python smart_agent.py browser read-url \"https://example.com\"", "active", "4 Tested", "LOW", "UNTRUSTED_WEB", "no", "web", "none", "network", "yes via web.fetch_url", "fetch audited", "no memory write", "browser clip tests", "manual web smoke pending", "README.md"),
    _r("CMD-BROWSER-002", "python smart_agent.py browser summarize-url \"<url>\"", "Web/research", "Summarize an explicit public URL.", "python smart_agent.py browser summarize-url \"https://example.com\"", "active", "4 Tested", "LOW", "UNTRUSTED_WEB", "no", "web", "none", "network", "yes via web.fetch_url", "fetch audited", "no memory write", "browser clip tests", "manual web smoke pending", "README.md"),
    _r("CMD-BROWSER-003", "python smart_agent.py browser clip-url \"<url>\" --to workspace", "Web/research", "Clip explicit URL content into approved workspace.", "python smart_agent.py browser clip-url \"https://example.com\" --to workspace", "active", "4 Tested", "MEDIUM", "UNTRUSTED_WEB / UNTRUSTED_DOCUMENT", "no", "web/files", "none", "network and workspace write", "yes", "fetch/write audited", "no memory write", "browser clip tests", "manual QA pending", "README.md"),
    _r("CMD-BROWSER-004", "python smart_agent.py browser selected-tab", "Web/research", "Show selected-tab unavailable/setup notes.", "python smart_agent.py browser selected-tab", "stubbed", "2 Scaffolded", "HIGH", "LOCAL_PRIVATE_DATA", "yes if future native read", "browser", "none", "prints unsupported status", "yes for stub denial", "stub denial audited", "no memory write", "browser stub tests", "manual QA pending", "README.md", "No browser history, cookies, or tab automation in v1."),
    _r("CMD-FILES-001", "python smart_agent.py files list [path]", "Workspace files", "List files inside approved roots.", "python smart_agent.py files list ./workspace", "active", "5 Hardened", "LOW", "UNTRUSTED_DOCUMENT metadata", "no", "filesystem", "none", "workspace read", "yes", "files read audited", "no memory write", "files workflow tests", "manual QA pending", "README.md"),
    _r("CMD-FILES-002", "python smart_agent.py files read <path>", "Workspace files", "Read a UTF-8 file inside approved roots.", "python smart_agent.py files read ./workspace/test.md", "active", "5 Hardened", "MEDIUM", "UNTRUSTED_DOCUMENT", "no", "filesystem", "none", "workspace read", "yes", "files read audited", "no memory write", "files workflow tests", "manual QA pending", "README.md"),
    _r("CMD-FILES-003", "python smart_agent.py files summarize <path>", "Workspace files", "Summarize a file as untrusted document data.", "python smart_agent.py files summarize ./workspace/test.md", "active", "5 Hardened", "MEDIUM", "UNTRUSTED_DOCUMENT", "no", "filesystem", "none", "workspace read/model-free summary", "yes", "files read audited", "no memory write", "files workflow tests", "manual QA pending", "README.md"),
    _r("CMD-FILES-004", "python smart_agent.py files search \"<query>\"", "Workspace files", "Search UTF-8 files inside approved roots.", "python smart_agent.py files search \"TODO\" --path ./workspace", "active", "5 Hardened", "LOW", "UNTRUSTED_DOCUMENT", "no", "filesystem", "none", "workspace read", "yes", "files read/search audited", "no memory write", "files workflow tests", "manual QA pending", "README.md"),
    _r("CMD-FILES-005", "python smart_agent.py files write <path> --content \"...\"", "Workspace files", "Write UTF-8 content inside approved roots.", "python smart_agent.py files write ./workspace/new.md --content \"hello\"", "active", "5 Hardened", "MEDIUM", "TRUSTED_USER", "policy-dependent", "filesystem", "none", "workspace write", "yes", "file write audited", "no memory write", "files workflow tests", "manual QA pending", "README.md"),
    _r("CMD-FILES-006", "python smart_agent.py files patch <path> --old-text A --new-text B", "Workspace files", "Patch exact text with backup and diff.", "python smart_agent.py files patch ./workspace/test.md --old-text old --new-text new", "active", "5 Hardened", "MEDIUM", "TRUSTED_USER", "policy-dependent", "filesystem", "none", "workspace write", "yes", "file patch audited", "no memory write", "files workflow tests", "manual QA pending", "README.md"),
    _r("CMD-FILES-007", "python smart_agent.py files diff [path]", "Workspace files", "Show brokered git diff.", "python smart_agent.py files diff --max-chars 20000", "active", "5 Hardened", "LOW", "LOCAL_PRIVATE_DATA metadata", "no", "git", "none", "read diff", "yes", "git diff audited", "no memory write", "files workflow tests", "manual QA pending", "README.md"),
    _r("CMD-MEMORY-001", "python smart_agent.py memory list", "Memory", "List memory records for a scope.", "python smart_agent.py memory list --scope default", "active", "5 Hardened", "LOW", "MODEL_OUTPUT / LOCAL_PRIVATE_DATA metadata", "no for non-personal", "memory", "sqlite", "memory read", "yes", "memory read audited", "reads memory", "memory tests", "manual QA pending", "README.md"),
    _r("CMD-MEMORY-002", "python smart_agent.py memory add --category <category> --content \"...\"", "Memory", "Store safe preference/project/workflow memory.", "python smart_agent.py memory add --category project_fact --content \"Uses pytest\"", "active", "5 Hardened", "LOW/HIGH", "TRUSTED_USER", "yes for personal", "memory", "sqlite", "memory write", "yes", "memory write audited", "writes only if policy allows", "memory tests", "manual QA pending", "README.md"),
    _r("CMD-MEMORY-003", "python smart_agent.py memory search \"<query>\"", "Memory", "Search safe memory by scope/categories.", "python smart_agent.py memory search \"pytest\" --category project_fact", "active", "5 Hardened", "LOW", "MODEL_OUTPUT / LOCAL_PRIVATE_DATA metadata", "no for non-personal", "memory", "sqlite", "memory read", "yes", "memory search audited", "reads memory", "memory tests", "manual QA pending", "README.md"),
    _r("CMD-MEMORY-004", "python smart_agent.py memory delete <id>", "Memory", "Delete a memory record.", "python smart_agent.py memory delete mem_123", "active", "5 Hardened", "MEDIUM", "TRUSTED_USER", "policy-dependent", "memory", "sqlite", "memory delete", "yes", "memory delete audited", "deletes memory", "memory tests", "manual QA pending", "README.md"),
    _r("CMD-MEMORY-005", "python smart_agent.py memory export", "Memory", "Export memory records for a scope.", "python smart_agent.py memory export --scope default", "active", "5 Hardened", "MEDIUM/HIGH", "MODEL_OUTPUT / LOCAL_PRIVATE_DATA metadata", "policy-dependent", "memory", "sqlite", "memory read/export", "yes", "memory export audited", "reads memory", "memory tests", "manual QA pending", "README.md"),
    _r("CMD-MEMORY-006", "python smart_agent.py memory clear", "Memory", "Clear memory records for a scope.", "python smart_agent.py memory clear --scope default", "active", "5 Hardened", "HIGH", "TRUSTED_USER", "yes", "memory", "sqlite", "memory delete", "yes", "memory clear audited", "deletes memory", "memory tests", "manual QA with caution", "README.md"),
    _r("CMD-MEMORY-007", "python smart_agent.py memory context \"<query>\"", "Memory", "Build bounded non-personal memory context.", "python smart_agent.py memory context \"pytest\"", "active", "5 Hardened", "LOW", "MODEL_OUTPUT", "no for non-personal", "memory", "sqlite", "memory read", "yes", "context injection audited", "reads non-personal memory", "memory tests", "manual QA pending", "README.md"),
    _r("CMD-CALENDAR-001", "python smart_agent.py calendar read --start DATE --end DATE", "Calendar", "Read compact selected-range calendar summaries.", "python smart_agent.py calendar read --start 2026-05-23 --end 2026-05-24", "active", "5 Hardened", "HIGH", "LOCAL_PRIVATE_DATA", "yes", "calendar", "optional Calendar.app adapter/mock", "personal read", "yes", "calendar read audited", "no memory write", "calendar tests", "manual live approval pending", "README.md"),
    _r("CMD-CALENDAR-002", "python smart_agent.py calendar availability --start DATE --end DATE --duration N", "Calendar", "Find availability without event detail leakage.", "python smart_agent.py calendar availability --start 2026-05-23 --end 2026-05-24 --duration 30", "active", "5 Hardened", "HIGH", "LOCAL_PRIVATE_DATA", "yes", "calendar", "optional Calendar.app adapter/mock", "personal read", "yes", "calendar access audited", "no memory write", "calendar tests", "manual live approval pending", "README.md"),
    _r("CMD-CALENDAR-003", "python smart_agent.py calendar draft-create --title ...", "Calendar", "Create a pending Action Center calendar-create draft.", "python smart_agent.py calendar draft-create --title Standup --start 2026-05-23T09:00 --end 2026-05-23T09:30", "active", "4 Tested", "CRITICAL", "MODEL_OUTPUT / LOCAL_PRIVATE_DATA", "Action Center", "calendar", "stub/mock", "pending action", "Action Center then ToolBroker on execution", "draft/action lifecycle audited", "no memory write", "calendar write tests", "manual QA with mock action", "README.md"),
    _r("CMD-CALENDAR-004", "python smart_agent.py calendar create --from-action <action_id>", "Calendar", "Execute one approved calendar create action.", "python smart_agent.py calendar create --from-action act_123", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "per-action", "calendar", "stub/mock", "calendar write stub", "yes", "execution audited", "no memory write", "calendar write tests", "manual mock-only QA", "README.md"),
    _r("CMD-CALENDAR-005", "python smart_agent.py calendar draft-update <event_id>", "Calendar", "Draft a calendar update action.", "python smart_agent.py calendar draft-update evt_123 --title New", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "Action Center", "calendar", "stub/mock", "pending action", "Action Center then ToolBroker on execution", "draft/action lifecycle audited", "no memory write", "calendar write tests", "manual mock-only QA", "README.md"),
    _r("CMD-CALENDAR-006", "python smart_agent.py calendar update --from-action <action_id>", "Calendar", "Execute one approved calendar update action.", "python smart_agent.py calendar update --from-action act_123", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "per-action", "calendar", "stub/mock", "calendar write stub", "yes", "execution audited", "no memory write", "calendar write tests", "manual mock-only QA", "README.md"),
    _r("CMD-CALENDAR-007", "python smart_agent.py calendar draft-delete <event_id>", "Calendar", "Draft a calendar delete action.", "python smart_agent.py calendar draft-delete evt_123", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "Action Center", "calendar", "stub/mock", "pending action", "Action Center then ToolBroker on execution", "draft/action lifecycle audited", "no memory write", "calendar write tests", "manual mock-only QA", "README.md"),
    _r("CMD-CALENDAR-008", "python smart_agent.py calendar delete --from-action <action_id>", "Calendar", "Execute one approved calendar delete action.", "python smart_agent.py calendar delete --from-action act_123", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "per-action", "calendar", "stub/mock", "calendar write stub", "yes", "execution audited", "no memory write", "calendar write tests", "manual mock-only QA", "README.md"),
    _r("CMD-CONTACTS-001", "python smart_agent.py contacts search \"<name>\"", "Contacts", "Search compact contact candidates.", "python smart_agent.py contacts search \"Sam\"", "active", "5 Hardened", "HIGH", "LOCAL_PRIVATE_DATA", "yes", "contacts", "optional Contacts.app adapter/mock", "personal read", "yes", "contacts access audited", "no memory write", "contacts tests", "manual live approval pending", "README.md"),
    _r("CMD-CONTACTS-002", "python smart_agent.py contacts read <contact_id>", "Contacts", "Read explicitly selected contact fields.", "python smart_agent.py contacts read contact_123 --field display_name", "active", "5 Hardened", "HIGH", "LOCAL_PRIVATE_DATA", "yes", "contacts", "optional Contacts.app adapter/mock", "personal read", "yes", "contacts access audited", "no memory write", "contacts tests", "manual live approval pending", "README.md"),
    _r("CMD-CONTACTS-003", "python smart_agent.py contacts draft-update <contact_id>", "Contacts", "Draft selected contact update.", "python smart_agent.py contacts draft-update contact_123 --set company=Acme", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "Action Center", "contacts", "stub/mock", "pending action", "Action Center then ToolBroker on execution", "draft/action lifecycle audited", "no memory write", "contact edit tests", "manual mock-only QA", "README.md"),
    _r("CMD-CONTACTS-004", "python smart_agent.py contacts update --from-action <action_id>", "Contacts", "Execute one approved contact update.", "python smart_agent.py contacts update --from-action act_123", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "per-action", "contacts", "stub/mock", "contact write stub", "yes", "execution audited", "no memory write", "contact edit tests", "manual mock-only QA", "README.md"),
    _r("CMD-CONTACTS-005", "python smart_agent.py contacts draft-create --display-name \"Name\"", "Contacts", "Draft contact creation.", "python smart_agent.py contacts draft-create --display-name \"Pat Example\"", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "Action Center", "contacts", "stub/mock", "pending action", "Action Center then ToolBroker on execution", "draft/action lifecycle audited", "no memory write", "contact edit tests", "manual mock-only QA", "README.md"),
    _r("CMD-CONTACTS-006", "python smart_agent.py contacts create --from-action <action_id>", "Contacts", "Execute one approved contact create.", "python smart_agent.py contacts create --from-action act_123", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "per-action", "contacts", "stub/mock", "contact write stub", "yes", "execution audited", "no memory write", "contact edit tests", "manual mock-only QA", "README.md"),
    _r("CMD-EMAIL-001", "python smart_agent.py email metadata", "Email", "List email metadata only.", "python smart_agent.py email metadata --max-results 5", "active", "5 Hardened", "HIGH", "UNTRUSTED_EMAIL", "yes", "email", "IMAP optional/mock", "personal read", "yes", "email metadata audited", "no body memory", "email tests", "manual non-production account pending", "README.md"),
    _r("CMD-EMAIL-002", "python smart_agent.py email read <thread_id>", "Email", "Read one selected email thread.", "python smart_agent.py email read thread_123", "active", "5 Hardened", "HIGH", "UNTRUSTED_EMAIL", "yes", "email", "IMAP optional/mock", "personal read", "yes", "email body read audited/redacted", "no body memory", "email tests", "manual non-production account pending", "README.md"),
    _r("CMD-EMAIL-003", "python smart_agent.py email summarize <thread_id>", "Email", "Summarize one selected email thread.", "python smart_agent.py email summarize thread_123", "active", "5 Hardened", "HIGH", "UNTRUSTED_EMAIL", "yes", "email", "IMAP optional/mock", "personal read/summary", "yes", "email summary audited", "no body memory", "email tests", "manual non-production account pending", "README.md"),
    _r("CMD-EMAIL-004", "python smart_agent.py email draft-reply <thread_id>", "Email", "Draft a reply without sending.", "python smart_agent.py email draft-reply thread_123 --instruction concise", "active", "5 Hardened", "HIGH", "UNTRUSTED_EMAIL", "yes", "email", "IMAP optional/mock", "draft only", "yes", "draft audited", "no body memory", "email tests", "manual QA pending", "README.md"),
    _r("CMD-EMAIL-005", "python smart_agent.py email triage", "Email", "Metadata-only triage with optional selected thread.", "python smart_agent.py email triage --dry-run --json", "active", "5 Hardened", "HIGH", "UNTRUSTED_EMAIL", "yes", "email", "IMAP optional/mock", "personal read", "yes", "triage steps audited", "no body memory", "email triage tests", "manual QA pending", "README.md"),
    _r("CMD-EMAIL-006", "python smart_agent.py email draft-new --to ...", "Email", "Create reviewed new-email send action.", "python smart_agent.py email draft-new --to a@example.com --subject Hi --body Hello", "active", "4 Tested", "CRITICAL", "MODEL_OUTPUT", "Action Center", "email", "mock only", "pending send action", "Action Center then ToolBroker on execution", "draft/action audited", "no memory write", "email send tests", "manual mock-only QA", "README.md"),
    _r("CMD-EMAIL-007", "python smart_agent.py email send --from-action <action_id>", "Email", "Execute one approved email send action.", "python smart_agent.py email send --from-action act_123", "active", "4 Tested", "CRITICAL", "MODEL_OUTPUT / UNTRUSTED_EMAIL", "per-action", "email", "mock only", "mock send", "yes", "send execution audited", "no memory write", "email send tests", "manual mock-only QA", "README.md"),
    _r("CMD-MSG-001", "python smart_agent.py messages read <thread_id>", "Messages", "Read one selected message thread if safe connector configured.", "python smart_agent.py messages read thread_123", "stubbed", "4 Tested", "HIGH", "UNTRUSTED_MESSAGE", "yes", "messages", "none safe configured", "unsupported/personal read", "yes", "denial/stub audited", "no body memory", "messages tests", "manual QA pending", "README.md", "No Messages database scraping."),
    _r("CMD-MSG-002", "python smart_agent.py messages summarize <thread_id>", "Messages", "Summarize selected message thread if connector configured.", "python smart_agent.py messages summarize thread_123", "stubbed", "4 Tested", "HIGH", "UNTRUSTED_MESSAGE", "yes", "messages", "none safe configured", "unsupported/personal read", "yes", "denial/stub audited", "no body memory", "messages tests", "manual QA pending", "README.md"),
    _r("CMD-MSG-003", "python smart_agent.py messages draft-reply <thread_id>", "Messages", "Draft reply to selected message thread if connector configured.", "python smart_agent.py messages draft-reply thread_123 --to Sam", "stubbed", "4 Tested", "HIGH", "UNTRUSTED_MESSAGE", "yes", "messages", "none safe configured", "draft only", "yes", "draft audited", "no body memory", "messages tests", "manual QA pending", "README.md"),
    _r("CMD-MSG-004", "python smart_agent.py messages draft-from-text --to \"Name\" --context-file ./workspace/thread.txt", "Messages", "Draft from manually provided workspace text.", "python smart_agent.py messages draft-from-text --to Sam --context-file ./workspace/thread.txt", "active", "5 Hardened", "HIGH", "UNTRUSTED_MESSAGE", "yes", "messages/files", "none", "workspace read and pending handoff actions", "yes", "draft/handoff audited", "no body memory", "messages tests", "manual QA pending", "README.md"),
    _r("CMD-MSG-005", "python smart_agent.py messages save-draft --from-action <action_id>", "Messages", "Save approved message draft inside workspace.", "python smart_agent.py messages save-draft --from-action act_123", "active", "4 Tested", "HIGH", "UNTRUSTED_MESSAGE", "Action Center", "messages/files", "none", "workspace write", "yes", "handoff audited", "no memory write", "handoff tests", "manual QA pending", "README.md"),
    _r("CMD-MSG-006", "python smart_agent.py messages copy-draft --from-action <action_id>", "Messages", "Copy approved message draft to clipboard without sending.", "python smart_agent.py messages copy-draft --from-action act_123", "active", "4 Tested", "HIGH", "UNTRUSTED_MESSAGE", "Action Center", "messages", "none", "clipboard write", "yes", "handoff audited", "no memory write", "handoff tests", "manual QA pending", "README.md"),
    _r("CMD-MSG-007", "python smart_agent.py messages send --from-action <action_id>", "Messages", "Automatic text/message sending.", "python smart_agent.py messages send --from-action act_123", "blocked", "0 Idea", "CRITICAL", "UNTRUSTED_MESSAGE", "per-action future", "messages", "none approved", "send", "not implemented", "n/a", "n/a", "no send tests because blocked", "blocked", "docs/decisions/messages_send_path.md", "Automatic message sending remains deferred.", replacement="messages save-draft/copy-draft"),
    _r("CMD-TASKS-001", "python smart_agent.py tasks list", "Tasks/reminders", "List selected-scope tasks/reminders.", "python smart_agent.py tasks list --max-results 5", "active", "4 Tested", "HIGH", "LOCAL_PRIVATE_DATA", "yes", "tasks", "mock/stub", "personal read", "yes", "task access audited", "no task memory", "tasks tests", "manual mock QA pending", "README.md"),
    _r("CMD-TASKS-002", "python smart_agent.py tasks draft-create \"task\"", "Tasks/reminders", "Create pending task-create action.", "python smart_agent.py tasks draft-create \"Follow up\" --due 2026-05-24", "active", "4 Tested", "CRITICAL", "MODEL_OUTPUT", "Action Center", "tasks", "mock/stub", "pending action", "Action Center then ToolBroker on execution", "draft audited", "no memory write", "tasks tests", "manual mock QA pending", "README.md"),
    _r("CMD-TASKS-003", "python smart_agent.py tasks create --from-action <action_id>", "Tasks/reminders", "Execute approved task creation.", "python smart_agent.py tasks create --from-action act_123", "active", "4 Tested", "CRITICAL", "MODEL_OUTPUT", "per-action", "tasks", "mock/stub", "task write stub", "yes", "execution audited", "no memory write", "tasks tests", "manual mock QA pending", "README.md"),
    _r("CMD-TASKS-004", "python smart_agent.py tasks update <task_id>", "Tasks/reminders", "Update selected task after approval.", "python smart_agent.py tasks update task_123 --title \"New title\"", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "yes/per-action", "tasks", "mock/stub", "task write stub", "yes", "execution audited", "no memory write", "tasks tests", "manual mock QA pending", "README.md"),
    _r("CMD-TASKS-005", "python smart_agent.py tasks complete <task_id>", "Tasks/reminders", "Complete selected task after approval.", "python smart_agent.py tasks complete task_123", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "yes/per-action", "tasks", "mock/stub", "task write stub", "yes", "execution audited", "no memory write", "tasks tests", "manual mock QA pending", "README.md"),
    _r("CMD-TASKS-006", "python smart_agent.py tasks delete <task_id>", "Tasks/reminders", "Delete selected task after approval.", "python smart_agent.py tasks delete task_123", "active", "4 Tested", "CRITICAL", "LOCAL_PRIVATE_DATA", "yes/per-action", "tasks", "mock/stub", "task delete stub", "yes", "execution audited", "no memory write", "tasks tests", "manual mock QA pending", "README.md"),
    _r("CMD-TASKS-007", "python smart_agent.py tasks extract --from-notes ./workspace/notes.md", "Tasks/reminders", "Extract candidate tasks into Action Center drafts.", "python smart_agent.py tasks extract --from-notes ./workspace/notes.md --dry-run", "active", "4 Tested", "LOW/HIGH", "UNTRUSTED_DOCUMENT / LOCAL_PRIVATE_DATA", "yes for personal sources", "files/email/calendar/web", "optional", "source read and pending actions", "yes", "source/action audited", "no memory write", "task extraction tests", "manual notes-only QA pending", "README.md"),
    _r("CMD-CAPTURE-001", "python smart_agent.py capture note \"text\"", "Capture/notes", "Save explicit note to workspace capture inbox.", "python smart_agent.py capture note \"Research idea\" --title Idea", "active", "4 Tested", "LOW", "TRUSTED_USER", "no", "filesystem", "none", "workspace write", "yes", "capture write audited", "no memory write", "capture tests", "manual QA pending", "README.md"),
    _r("CMD-CAPTURE-002", "python smart_agent.py capture from-file <path>", "Capture/notes", "Capture a workspace file.", "python smart_agent.py capture from-file ./workspace/notes.md", "active", "4 Tested", "MEDIUM", "UNTRUSTED_DOCUMENT", "no", "filesystem", "none", "workspace read/write", "yes", "read/write audited", "no memory write", "capture tests", "manual QA pending", "README.md"),
    _r("CMD-CAPTURE-003", "python smart_agent.py capture from-url <url>", "Capture/notes", "Capture explicit URL through web.fetch_url.", "python smart_agent.py capture from-url https://example.com", "active", "4 Tested", "MEDIUM", "UNTRUSTED_WEB", "no", "web/files", "optional", "network and workspace write", "yes", "fetch/write audited", "no memory write", "capture tests", "manual web QA pending", "README.md"),
    _r("CMD-CAPTURE-004", "python smart_agent.py capture list", "Capture/notes", "List workspace captures.", "python smart_agent.py capture list", "active", "4 Tested", "SAFE", "UNTRUSTED_DOCUMENT metadata", "no", "filesystem", "none", "workspace read", "yes", "read audited", "no memory write", "capture tests", "manual QA pending", "README.md"),
    _r("CMD-CAPTURE-005", "python smart_agent.py capture summarize", "Capture/notes", "Summarize workspace capture inbox.", "python smart_agent.py capture summarize --limit 10", "active", "4 Tested", "LOW", "UNTRUSTED_DOCUMENT", "no", "filesystem", "none", "workspace read", "yes", "read audited", "no memory write", "capture tests", "manual QA pending", "README.md"),
    _r("CMD-CAPTURE-006", "python smart_agent.py capture promote-to-memory <capture_id>", "Capture/notes", "Promote capture through Memory v2 policy.", "python smart_agent.py capture promote-to-memory cap_123 --category project_fact", "active", "4 Tested", "MEDIUM/HIGH", "UNTRUSTED_DOCUMENT", "policy-dependent", "memory/files", "sqlite", "memory write if allowed", "yes", "memory promotion audited", "writes only through memory policy", "capture/memory tests", "manual QA pending", "README.md"),
    _r("CMD-BRIEF-001", "python smart_agent.py briefing daily", "Briefing", "Run configurable daily briefing.", "python smart_agent.py briefing daily --sections weather --weather \"Phoenix, AZ\"", "active", "5 Hardened", "LOW/HIGH", "Tool-specific", "yes for personal sections", "weather/calendar/tasks/email/web/memory", "optional", "selected reads and pending actions", "yes", "each section audited", "no memory write", "briefing tests", "manual weather-only QA pending", "README.md"),
    _r("CMD-BRIEF-002", "python smart_agent.py briefing daily --dry-run", "Briefing", "Preview daily briefing sections/tools/approvals.", "python smart_agent.py briefing daily --sections calendar,email --dry-run", "active", "5 Hardened", "SAFE", "Tool-specific metadata", "reports required approvals", "optional", "optional", "dry-run only", "yes dry-run", "dry-run audited", "no memory write", "briefing tests", "manual QA pending", "README.md"),
    _r("CMD-BRIEF-003", "python smart_agent.py briefing config show", "Briefing", "Show Daily Briefing v2 config.", "python smart_agent.py briefing config show", "active", "4 Tested", "SAFE", "LOCAL_PRIVATE_DATA metadata", "no", "none", "none", "read config", "n/a", "none", "no memory write", "briefing tests", "manual QA pending", "README.md"),
    _r("CMD-BRIEF-004", "python smart_agent.py briefing config set key=value", "Briefing", "Set Daily Briefing v2 config.", "python smart_agent.py briefing config set sections=weather web_topics=ai", "active", "4 Tested", "MEDIUM", "TRUSTED_USER", "user action", "none", "none", "writes config", "n/a", "none", "no memory write", "briefing tests", "manual QA pending", "README.md"),
    _r("CMD-MEET-001", "python smart_agent.py meeting prep --event-id <event_id>", "Meeting", "Prepare for selected calendar meeting.", "python smart_agent.py meeting prep --event-id evt_123 --dry-run", "active", "5 Hardened", "HIGH", "LOCAL_PRIVATE_DATA / UNTRUSTED_WEB", "yes for personal reads", "calendar/contacts/web", "optional", "selected reads", "yes", "steps audited", "no memory write", "meeting tests", "manual live approval pending", "README.md"),
    _r("CMD-MEET-002", "python smart_agent.py meeting prep --date DATE --title \"title\"", "Meeting", "Prepare for meeting by selected date/title.", "python smart_agent.py meeting prep --date 2026-05-23 --title Standup --dry-run", "active", "5 Hardened", "HIGH", "LOCAL_PRIVATE_DATA / UNTRUSTED_WEB", "yes for personal reads", "calendar/contacts/web", "optional", "selected reads", "yes", "steps audited", "no memory write", "meeting tests", "manual live approval pending", "README.md"),
    _r("CMD-MEET-003", "python smart_agent.py meeting follow-up --notes-file ./workspace/notes.md", "Meeting", "Generate follow-up summary and pending actions from workspace notes.", "python smart_agent.py meeting follow-up --notes-file ./workspace/notes.md --dry-run", "active", "4 Tested", "LOW/HIGH", "UNTRUSTED_DOCUMENT / LOCAL_PRIVATE_DATA", "yes for personal reads", "files/calendar/contacts", "optional", "source reads and pending actions", "yes", "steps/actions audited", "no memory write", "meeting follow-up tests", "manual notes-only QA pending", "README.md"),
    _r("CMD-MEET-004", "python smart_agent.py meeting follow-up --event-id <event_id>", "Meeting", "Generate follow-up from selected calendar event.", "python smart_agent.py meeting follow-up --event-id evt_123 --dry-run", "active", "4 Tested", "HIGH", "LOCAL_PRIVATE_DATA", "yes", "calendar/contacts", "optional", "selected reads and pending actions", "yes", "steps/actions audited", "no memory write", "meeting follow-up tests", "manual live approval pending", "README.md"),
    _r("CMD-IMPROVE-001", "python smart_agent.py improve backlog", "Self-improvement", "Generate read-only improvement backlog.", "python smart_agent.py improve backlog --dry-run --json", "active", "5 Hardened", "LOW", "UNTRUSTED_DOCUMENT", "no", "filesystem", "none", "brokered project reads", "yes", "file reads audited", "no memory write", "self-improvement tests", "manual QA pending", "README.md"),
    _r("CMD-IMPROVE-002", "python smart_agent.py improve propose", "Self-improvement", "Return top safe improvement proposal.", "python smart_agent.py improve propose --json", "active", "5 Hardened", "LOW", "UNTRUSTED_DOCUMENT", "no", "filesystem", "none", "brokered project reads", "yes", "file reads audited", "no memory write", "self-improvement tests", "manual QA pending", "README.md"),
    _r("CMD-IMPROVE-003", "python smart_agent.py improve implement <proposal_id>", "Self-improvement", "Implement approved proposal on codex branch.", "python smart_agent.py improve implement PROP-001 --json", "active", "5 Hardened", "HIGH", "UNTRUSTED_DOCUMENT / MODEL_OUTPUT", "approved proposal required", "filesystem/git/tests", "none", "branch/write/tests/diff/pending commit", "yes where architecture allows", "steps audited", "no memory write", "self-improvement loop tests", "manual docs-only proposal pending", "README.md"),
    _r("CMD-IMPROVE-004", "python smart_agent.py improve run-tests", "Self-improvement", "Run brokered self-improvement tests.", "python smart_agent.py improve run-tests --test-path tests", "active", "5 Hardened", "LOW", "LOCAL_PRIVATE_DATA metadata", "no", "tests", "pytest", "command execution limited to tests", "yes", "test command audited", "no memory write", "self-improvement tests", "manual QA pending", "README.md"),
    _r("CMD-IMPROVE-005", "python smart_agent.py improve show-diff", "Self-improvement", "Show brokered diff for current implementation.", "python smart_agent.py improve show-diff", "active", "5 Hardened", "LOW", "LOCAL_PRIVATE_DATA metadata", "no", "git", "none", "read diff", "yes", "diff audited", "no memory write", "self-improvement tests", "manual QA pending", "README.md"),
    _r("CMD-IMPROVE-006", "python smart_agent.py improve commit --from-action <action_id>", "Self-improvement", "Execute approved self-improvement commit action.", "python smart_agent.py improve commit --from-action act_123", "active", "5 Hardened", "HIGH", "TRUSTED_USER", "Action Center", "git", "none", "git commit", "yes", "commit audited", "no memory write", "self-improvement tests", "manual QA with caution", "README.md"),
    _r("CMD-PROMPTS-001", "python smart_agent.py prompts list", "PromptOps/workbench", "List prompt records.", "python smart_agent.py prompts list", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read docs", "n/a", "none", "no memory write", "prompt tests", "manual QA pending", "README.md"),
    _r("CMD-PROMPTS-002", "python smart_agent.py prompts next", "PromptOps/workbench", "Show next queued prompt.", "python smart_agent.py prompts next", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read docs", "n/a", "none", "no memory write", "prompt tests", "manual QA pending", "README.md"),
    _r("CMD-PROMPTS-003", "python smart_agent.py prompts show <prompt_id>", "PromptOps/workbench", "Show prompt record/body.", "python smart_agent.py prompts show NATIVE-SKILLS-FOUNDATION", "active", "4 Tested", "LOW", "UNTRUSTED_DOCUMENT metadata", "no", "none", "none", "read docs", "n/a", "none", "no memory write", "prompt tests", "manual QA pending", "README.md"),
    _r("CMD-PROMPTS-004", "python smart_agent.py prompts import <pack_file>", "PromptOps/workbench", "Validate, store, split, and queue prompt pack.", "python smart_agent.py prompts import prompts/packs/pack.md", "active", "4 Tested", "LOW", "UNTRUSTED_DOCUMENT", "no", "none", "none", "write prompt docs", "n/a", "prompt audit doc updated", "no memory write", "prompt pack tests", "manual QA pending", "README.md"),
    _r("CMD-PROMPTS-005", "python smart_agent.py prompts validate-pack <pack_file>", "PromptOps/workbench", "Validate prompt pack without writes.", "python smart_agent.py prompts validate-pack prompts/packs/pack.md", "active", "4 Tested", "SAFE", "UNTRUSTED_DOCUMENT", "no", "none", "none", "read file", "n/a", "none", "no memory write", "prompt pack tests", "manual QA pending", "README.md"),
    _r("CMD-WORK-001", "python smart_agent.py work import --stdin", "PromptOps/workbench", "Import prompt pack or raw prompt from stdin.", "pbpaste | python smart_agent.py work import --stdin --pack-id tonight", "active", "4 Tested", "LOW", "UNTRUSTED_DOCUMENT", "no", "none", "none", "write prompt docs", "n/a", "prompt audit/report docs updated", "no memory write", "PromptOps tests", "manual clipboard/stdin QA pending", "docs/PROMPTOPS_WORKBENCH.md"),
    _r("CMD-WORK-002", "python smart_agent.py work import-clipboard", "PromptOps/workbench", "Import prompt text from macOS clipboard.", "python smart_agent.py work import-clipboard --pack-id tonight", "active", "4 Tested", "LOW", "UNTRUSTED_DOCUMENT", "no", "none", "none", "clipboard read and prompt doc writes", "n/a", "prompt audit/report docs updated", "no memory write", "PromptOps tests with mock clipboard", "manual macOS clipboard QA pending", "docs/PROMPTOPS_WORKBENCH.md"),
    _r("CMD-WORK-003", "python smart_agent.py work next", "PromptOps/workbench", "Show next safe queued prompt.", "python smart_agent.py work next", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read docs", "n/a", "none", "no memory write", "PromptOps tests", "manual QA passed in prior run", "docs/PROMPTOPS_WORKBENCH.md"),
    _r("CMD-WORK-004", "python smart_agent.py work copy-next", "PromptOps/workbench", "Copy next prompt body to clipboard.", "python smart_agent.py work copy-next", "active", "4 Tested", "LOW", "UNTRUSTED_DOCUMENT", "no", "none", "none", "clipboard write", "n/a", "none", "no memory write", "PromptOps tests with mock clipboard", "manual macOS clipboard QA pending", "docs/PROMPTOPS_WORKBENCH.md"),
    _r("CMD-WORK-005", "python smart_agent.py work run-next", "PromptOps/workbench", "Run next prompt only when runner is explicitly enabled.", "python smart_agent.py work run-next", "experimental", "4 Tested", "MEDIUM", "UNTRUSTED_DOCUMENT", "runner disabled by default", "Codex CLI optional", "CODEX_RUNNER_ENABLED", "report write; possible code changes only if enabled", "n/a for disabled default", "PromptOps report written", "no memory write", "PromptOps disabled-runner tests", "manual disabled behavior verified", "docs/PROMPTOPS_WORKBENCH.md"),
    _r("CMD-WORK-006", "python smart_agent.py work autopilot --safe-only --max-prompts N", "PromptOps/workbench", "Attempt multiple safe prompts only with explicit runner config.", "python smart_agent.py work autopilot --safe-only --max-prompts 3", "experimental", "4 Tested", "MEDIUM", "UNTRUSTED_DOCUMENT", "stops at gates", "Codex CLI optional", "CODEX_RUNNER_ENABLED", "report write; possible code changes only if enabled", "n/a for disabled default", "PromptOps report written", "no memory write", "PromptOps safety tests", "manual disabled behavior pending", "docs/PROMPTOPS_WORKBENCH.md"),
    _r("CMD-WORK-007", "python smart_agent.py work status", "PromptOps/workbench", "Show PromptOps queue status.", "python smart_agent.py work status", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read docs", "n/a", "none", "no memory write", "PromptOps tests", "manual QA pending", "docs/PROMPTOPS_WORKBENCH.md"),
    _r("CMD-WORK-008", "python smart_agent.py work review", "PromptOps/workbench", "Review prompt queue/audit state.", "python smart_agent.py work review", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read docs", "n/a", "none", "no memory write", "PromptOps tests", "manual QA pending", "docs/PROMPTOPS_WORKBENCH.md"),
    _r("CMD-COMMANDS-001", "python smart_agent.py commands list", "Quality/evals", "List command registry records.", "python smart_agent.py commands list", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read command registry", "n/a", "none", "no memory write", "command registry tests", "manual QA pending", "docs/COMMAND_REGISTRY.md", introduced="2026-05-23"),
    _r("CMD-COMMANDS-002", "python smart_agent.py commands show <command_id>", "Quality/evals", "Show one command record.", "python smart_agent.py commands show CMD-WEATHER-003", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read command registry", "n/a", "none", "no memory write", "command registry tests", "manual QA pending", "docs/COMMAND_REGISTRY.md", introduced="2026-05-23"),
    _r("CMD-COMMANDS-003", "python smart_agent.py commands search \"<query>\"", "Quality/evals", "Search command descriptions/groups/examples.", "python smart_agent.py commands search weather", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read command registry", "n/a", "none", "no memory write", "command registry tests", "manual QA pending", "docs/COMMAND_REGISTRY.md", introduced="2026-05-23"),
    _r("CMD-COMMANDS-004", "python smart_agent.py commands legacy", "Quality/evals", "List legacy/deprecated/removed commands.", "python smart_agent.py commands legacy", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read command registry", "n/a", "none", "no memory write", "command registry tests", "manual QA pending", "docs/COMMAND_LEGACY.md", introduced="2026-05-23"),
    _r("CMD-COMMANDS-005", "python smart_agent.py commands validate", "Quality/evals", "Validate command registry docs.", "python smart_agent.py commands validate", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read docs", "n/a", "none", "no memory write", "command registry tests", "manual QA pending", "docs/COMMAND_QA_RUNBOOK.md", introduced="2026-05-23"),
    _r("CMD-COMMANDS-006", "python smart_agent.py commands qa-plan", "Quality/evals", "Suggest commands needing manual QA.", "python smart_agent.py commands qa-plan", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "read command registry", "n/a", "none", "no memory write", "command registry tests", "manual QA pending", "docs/COMMAND_QA_RUNBOOK.md", introduced="2026-05-23"),
    _r("CMD-COMMANDS-007", "python smart_agent.py commands qa-run <group>", "Quality/evals", "Print safe manual QA commands for a group.", "python smart_agent.py commands qa-run Weather", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "none", "none", "prints runbook commands only", "n/a", "none", "no memory write", "command registry tests", "manual QA pending", "docs/COMMAND_QA_RUNBOOK.md", introduced="2026-05-23"),
    _r("CMD-SCHEDULE-001", "python smart_agent.py schedule list", "Scheduler", "List explicit local manual-run schedules.", "python smart_agent.py schedule list", "active", "4 Tested", "SAFE", "TRUSTED_USER metadata", "no", "scheduler", "none", "read local schedule JSON", "n/a", "schedule lifecycle audited on changes/runs", "no memory write", "scheduler tests", "manual QA pending", "docs/SCHEDULER.md", introduced="2026-05-23"),
    _r("CMD-SCHEDULE-002", "python smart_agent.py schedule create", "Scheduler", "Create an opt-in local manual-run schedule record.", "python smart_agent.py schedule create --workflow connector_doctor --schedule daily@08:00", "active", "4 Tested", "LOW", "TRUSTED_USER", "user action", "scheduler", "none", "writes local schedule JSON", "n/a", "schedule create audited", "no memory write", "scheduler tests", "manual QA pending", "docs/SCHEDULER.md", introduced="2026-05-23"),
    _r("CMD-SCHEDULE-003", "python smart_agent.py schedule run <schedule_id>", "Scheduler", "Manually run one schedule now; v1 has no background runner.", "python smart_agent.py schedule run sch_123", "active", "4 Tested", "LOW/HIGH", "Tool-specific", "workflow-dependent", "workflow-dependent", "optional", "manual workflow run", "yes for scheduled tool workflows", "scheduled run audited", "no memory write by scheduler", "scheduler tests", "manual QA pending", "docs/SCHEDULER.md", introduced="2026-05-23"),
    _r("CMD-SCHEDULE-004", "python smart_agent.py schedule pause <schedule_id>", "Scheduler", "Pause a local schedule record.", "python smart_agent.py schedule pause sch_123", "active", "4 Tested", "LOW", "TRUSTED_USER", "no", "scheduler", "none", "writes local schedule JSON", "n/a", "schedule pause audited", "no memory write", "scheduler tests", "manual QA pending", "docs/SCHEDULER.md", introduced="2026-05-23"),
    _r("CMD-SCHEDULE-005", "python smart_agent.py schedule delete <schedule_id>", "Scheduler", "Delete a local schedule record.", "python smart_agent.py schedule delete sch_123", "active", "4 Tested", "LOW", "TRUSTED_USER", "no", "scheduler", "none", "writes local schedule JSON", "n/a", "schedule delete audited", "no memory write", "scheduler tests", "manual QA pending", "docs/SCHEDULER.md", introduced="2026-05-23"),
    _r("CMD-LEGACY-001", "python smart_agent.py web fetch <url>", "Web/research", "Legacy planned fetch shortcut that is not implemented.", "python smart_agent.py browser read-url https://example.com", "legacy", "1 Specified", "LOW", "UNTRUSTED_WEB", "no", "web", "none", "n/a", "not implemented", "n/a", "n/a", "legacy docs validation", "not runnable", "docs/COMMAND_LEGACY.md", "Use browser read-url or research.", replacement="browser read-url"),
    _r("CMD-LEGACY-002", "python smart_agent.py weather providers", "Weather", "Legacy provider listing idea not implemented as a command.", "python smart_agent.py weather doctor", "legacy", "1 Specified", "SAFE", "UNTRUSTED_WEB metadata", "no", "weather", "none", "n/a", "not implemented", "n/a", "n/a", "legacy docs validation", "not runnable", "docs/COMMAND_LEGACY.md", "Use weather doctor.", replacement="weather doctor"),
    _r("CMD-PLAN-LEADS-001", "python smart_agent.py leads list", "Leads", "Planned lead inbox listing.", "python smart_agent.py leads list", "planned", "0 Idea", "HIGH", "LOCAL_PRIVATE_DATA", "yes", "lead inbox", "none", "personal/customer read", "not implemented", "n/a", "n/a", "planned only", "not runnable", "docs/FEATURE_ROADMAP.md"),
    _r("CMD-PLAN-SKILLS-001", "python smart_agent.py skills list", "Native skills", "Planned native skill listing.", "python smart_agent.py skills list", "planned", "0 Idea", "SAFE", "Skill metadata", "no", "skills", "none", "read metadata", "not implemented", "n/a", "n/a", "planned only", "not runnable", "docs/FEATURE_ROADMAP.md"),
    _r("CMD-PLAN-PDF-001", "python smart_agent.py pdf summarize <path>", "PDF/documents", "Planned workspace PDF summary command.", "python smart_agent.py pdf summarize ./workspace/file.pdf", "planned", "0 Idea", "MEDIUM", "UNTRUSTED_DOCUMENT", "no", "pdf/files", "none", "workspace read", "not implemented", "n/a", "n/a", "planned only", "not runnable", "docs/FEATURE_ROADMAP.md"),
    _r("CMD-PLAN-SESSION-001", "python smart_agent.py session start --name \"<name>\"", "Session logging", "Planned dogfood session logging.", "python smart_agent.py session start --name daily-smoke", "planned", "0 Idea", "LOW", "TRUSTED_USER", "no", "session logging", "none", "workspace/log write", "not implemented", "n/a", "n/a", "planned only", "not runnable", "docs/PROMPT_QUEUE.md"),
    _r("CMD-PLAN-DOGFOOD-001", "python smart_agent.py dogfood run <suite>", "Dogfood", "Planned dogfood suite runner.", "python smart_agent.py dogfood run core", "planned", "0 Idea", "LOW/MEDIUM", "Tool-specific", "suite-dependent", "dogfood", "none", "multiple command checks", "not implemented", "n/a", "n/a", "planned only", "not runnable", "docs/PROMPT_QUEUE.md"),
    _r("CMD-PLAN-FEEDBACK-001", "python smart_agent.py feedback bad --last --reason \"...\"", "Feedback", "Planned feedback capture.", "python smart_agent.py feedback bad --last --reason \"too vague\"", "planned", "0 Idea", "LOW", "TRUSTED_USER", "no", "feedback", "none", "workspace/log write", "not implemented", "n/a", "n/a", "planned only", "not runnable", "docs/PROMPT_QUEUE.md"),
    _r("CMD-PLAN-BUGS-001", "python smart_agent.py bugs create-regression <bug_id>", "Bugs/regressions", "Planned regression test generator from bugs.", "python smart_agent.py bugs create-regression BUG-001", "planned", "0 Idea", "MEDIUM", "UNTRUSTED_DOCUMENT", "review required", "bugs/tests", "none", "test file write", "not implemented", "n/a", "n/a", "planned only", "not runnable", "docs/PROMPT_QUEUE.md"),
    _r("CMD-PLAN-PRIVACY-001", "python smart_agent.py privacy status", "Privacy", "Planned privacy/data inventory view.", "python smart_agent.py privacy status", "planned", "0 Idea", "SAFE", "Metadata", "no", "privacy", "none", "read metadata", "not implemented", "n/a", "n/a", "planned only", "not runnable", "docs/FEATURE_ROADMAP.md"),
    _r("CMD-PLAN-BACKUP-001", "python smart_agent.py backup create", "Backup", "Planned redacted backup command.", "python smart_agent.py backup create", "planned", "0 Idea", "MEDIUM/HIGH", "LOCAL_PRIVATE_DATA", "yes", "backup", "none", "archive write", "not implemented", "n/a", "n/a", "planned only", "not runnable", "docs/FEATURE_ROADMAP.md"),
)


def list_commands(*, status: str | None = None, group: str | None = None) -> list[CommandRecord]:
    records = list(COMMANDS)
    if status:
        records = [record for record in records if record.status == status]
    if group:
        normalized = group.lower()
        records = [record for record in records if normalized in record.group.lower()]
    return records


def get_command(command_id: str) -> CommandRecord | None:
    return next((record for record in COMMANDS if record.command_id == command_id), None)


def search_commands(query: str) -> list[CommandRecord]:
    needle = query.lower()
    return [
        record
        for record in COMMANDS
        if needle in " ".join(
            [
                record.command_id,
                record.command,
                record.group,
                record.description,
                record.example,
                record.status,
                record.risk_level,
                record.notes,
            ]
        ).lower()
    ]


def legacy_commands() -> list[CommandRecord]:
    return [record for record in COMMANDS if record.status in {"legacy", "deprecated", "removed"}]


def deprecated_commands() -> list[CommandRecord]:
    return [record for record in COMMANDS if record.status == "deprecated"]


def qa_plan() -> list[CommandRecord]:
    return [
        record
        for record in COMMANDS
        if record.status in {"active", "experimental", "stubbed"} and "manual QA pending" in record.manual_qa_status
    ]


def qa_run(group: str) -> list[dict[str, str]]:
    runnable = []
    for record in list_commands(group=group):
        if record.risk_level in {"SAFE", "LOW"} and record.status == "active":
            runnable.append(
                {
                    "command_id": record.command_id,
                    "command": record.example,
                    "expected_behavior": record.description,
                    "note": "Manual QA should inspect output; this command is not executed by qa-run v1.",
                }
            )
    return runnable


def validate_command_registry_docs(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    required = [
        root / "docs/COMMAND_REGISTRY.md",
        root / "docs/COMMAND_TEST_MATRIX.md",
        root / "docs/COMMAND_LEGACY.md",
        root / "docs/COMMAND_QA_RUNBOOK.md",
        root / "docs/templates/command_record_template.md",
        root / "docs/templates/command_test_record_template.md",
    ]
    missing = [path.relative_to(root).as_posix() for path in required if not path.exists()]
    registry_text = (root / "docs/COMMAND_REGISTRY.md").read_text(encoding="utf-8") if (root / "docs/COMMAND_REGISTRY.md").exists() else ""
    matrix_text = (root / "docs/COMMAND_TEST_MATRIX.md").read_text(encoding="utf-8") if (root / "docs/COMMAND_TEST_MATRIX.md").exists() else ""
    missing_registry_ids = [record.command_id for record in COMMANDS if f"| {record.command_id} |" not in registry_text]
    missing_matrix_ids = [record.command_id for record in COMMANDS if f"| {record.command_id} |" not in matrix_text]
    invalid_records = [
        record.command_id
        for record in COMMANDS
        if record.status not in STATUS_VALUES or not any(part in RISK_VALUES for part in record.risk_level.split("/")) or not record.example
    ]
    agents_text = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").exists() else ""
    readme_text = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    problems = missing + missing_registry_ids + missing_matrix_ids + invalid_records
    if "COMMAND_REGISTRY.md" not in agents_text:
        problems.append("AGENTS.md missing COMMAND_REGISTRY.md rule")
    if "COMMAND_REGISTRY.md" not in readme_text:
        problems.append("README.md missing COMMAND_REGISTRY.md link")
    return {
        "status": "ok" if not problems else "error",
        "command_count": len(COMMANDS),
        "missing_files": missing,
        "missing_registry_ids": missing_registry_ids,
        "missing_matrix_ids": missing_matrix_ids,
        "invalid_records": invalid_records,
        "problems": problems,
    }


def format_command_list(records: list[CommandRecord]) -> str:
    return json.dumps(
        {
            "commands": [
                {
                    "command_id": record.command_id,
                    "command": record.command,
                    "group": record.group,
                    "status": record.status,
                    "risk_level": record.risk_level,
                }
                for record in records
            ]
        },
        indent=2,
        sort_keys=True,
    )


def format_command_detail(record: CommandRecord | None) -> str:
    if record is None:
        return json.dumps({"status": "not_found"}, indent=2, sort_keys=True)
    return json.dumps(record.to_dict(), indent=2, sort_keys=True)


def render_registry_markdown() -> str:
    lines = [
        "# Command Registry",
        "",
        "This is the durable catalog of implemented, experimental, stubbed, planned, blocked, legacy, deprecated, and removed CLI commands.",
        "",
        "Update this file whenever a command is added, renamed, changed, deprecated, removed, or superseded.",
        "",
        "## Status Values",
        "",
        "`active`, `experimental`, `stubbed`, `deprecated`, `legacy`, `removed`, `blocked`, `planned`.",
        "",
        "## Command Catalog",
        "",
        _registry_header(),
    ]
    lines.extend(_registry_row(record) for record in COMMANDS)
    return "\n".join(lines) + "\n"


def render_test_matrix_markdown() -> str:
    lines = [
        "# Command Test Matrix",
        "",
        "This matrix maps command records to automated coverage and manual QA expectations.",
        "",
        _matrix_header(),
    ]
    lines.extend(_matrix_row(record) for record in COMMANDS)
    return "\n".join(lines) + "\n"


def render_legacy_markdown() -> str:
    lines = [
        "# Command Legacy Tracker",
        "",
        "Deprecated, legacy, removed, and intentionally unavailable commands remain listed so users know the replacement path.",
        "",
        "| Command ID | Command | Status | Replacement command | Removal target | Reason for deprecation | Compatibility notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in COMMANDS:
        if record.status in {"deprecated", "legacy", "removed", "blocked"}:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(record.command_id),
                        f"`{_cell(record.command)}`",
                        record.status,
                        _cell(record.replacement),
                        "not scheduled" if record.status != "removed" else record.deprecated,
                        _cell(record.notes or "Policy/platform/support boundary."),
                        _cell(record.description),
                    ]
                )
                + " |"
            )
    return "\n".join(lines) + "\n"


def render_qa_runbook_markdown() -> str:
    return """# Command QA Runbook

Use this runbook to keep command behavior, docs, and tests aligned.

## Daily Command Smoke Test

1. Run `python smart_agent.py commands validate`.
2. Run `python smart_agent.py commands qa-plan`.
3. Run SAFE/LOW examples from the groups changed in the current run.
4. Run `python smart_agent.py doctor`.
5. Run `python smart_agent.py tools list`.
6. Run focused tests for touched command groups.

## Weekly Full Command Review

1. Run the full test suite.
2. Run startup policy validation.
3. Run capability manifest validation.
4. Run `python smart_agent.py commands validate`.
5. Review `docs/COMMAND_TEST_MATRIX.md` for stale manual QA status.
6. Review `docs/COMMAND_LEGACY.md` for obsolete or confusing command paths.

## Logging Failures

- Add a bug ID to the `Linked bug IDs` column in `docs/COMMAND_TEST_MATRIX.md`.
- Record the failing command, environment, expected behavior, actual behavior, and relevant audit/report path.
- Do not paste secrets or private personal data into bug reports.

## Adding Regression Tests

- Add a focused test under `tests/` for the command group.
- Mock live providers and personal-data connectors by default.
- Use live tests only when explicitly opted in.

## Marking Commands Verified

- Update `Last manual test result` in `docs/COMMAND_TEST_MATRIX.md`.
- Update `Manual QA status` and `Last verified` in `docs/COMMAND_REGISTRY.md`.
- Update `docs/FEATURE_MATURITY.md` if manual QA changes maturity.

## Updating Feature Maturity

Manual QA can raise UX/docs readiness, but it does not replace automated tests, policy checks, approval checks, or audit coverage.
"""


def render_record_template() -> str:
    return """# Command Record Template

- Command ID:
- Command:
- Group:
- Description:
- Example:
- Status:
- Maturity level:
- Risk level:
- Trust level:
- Requires approval:
- Requires connector:
- Requires provider:
- Side effects:
- ToolBroker path:
- Audit behavior:
- Memory behavior:
- Test coverage:
- Manual QA status:
- Docs link:
- Introduced date/commit:
- Deprecated date/commit:
- Replacement command:
- Last verified:
- Known bugs:
- Notes:
"""


def render_test_record_template() -> str:
    return """# Command Test Record Template

- Command ID:
- Command:
- Test suite:
- Manual test steps:
- Expected behavior:
- Failure signals:
- Required environment:
- Required provider/API key:
- Requires live LM Studio:
- Requires web:
- Requires personal data:
- Safe for all_safe suite:
- Last manual test result:
- Last automated test result:
- Linked bug IDs:
- Regression test path:
"""


def write_command_docs(project_root: str | Path = ".") -> None:
    root = Path(project_root)
    docs = root / "docs"
    templates = docs / "templates"
    docs.mkdir(exist_ok=True)
    templates.mkdir(exist_ok=True)
    (docs / "COMMAND_REGISTRY.md").write_text(render_registry_markdown(), encoding="utf-8")
    (docs / "COMMAND_TEST_MATRIX.md").write_text(render_test_matrix_markdown(), encoding="utf-8")
    (docs / "COMMAND_LEGACY.md").write_text(render_legacy_markdown(), encoding="utf-8")
    (docs / "COMMAND_QA_RUNBOOK.md").write_text(render_qa_runbook_markdown(), encoding="utf-8")
    (templates / "command_record_template.md").write_text(render_record_template(), encoding="utf-8")
    (templates / "command_test_record_template.md").write_text(render_test_record_template(), encoding="utf-8")


def _registry_header() -> str:
    return (
        "| Command ID | Command | Group | Description | Example | Status | Maturity level | Risk level | Trust level | Requires approval | Requires connector | Requires provider | Side effects | ToolBroker path | Audit behavior | Memory behavior | Test coverage | Manual QA status | Docs link | Introduced date/commit | Deprecated date/commit | Replacement command | Last verified | Known bugs | Notes |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
    )


def _registry_row(record: CommandRecord) -> str:
    values = [
        record.command_id,
        f"`{record.command}`",
        record.group,
        record.description,
        f"`{record.example}`",
        record.status,
        record.maturity_level,
        record.risk_level,
        record.trust_level,
        record.requires_approval,
        record.requires_connector,
        record.requires_provider,
        record.side_effects,
        record.toolbroker_path,
        record.audit_behavior,
        record.memory_behavior,
        record.test_coverage,
        record.manual_qa_status,
        record.docs_link,
        record.introduced,
        record.deprecated,
        record.replacement,
        record.last_verified,
        record.known_bugs,
        record.notes or "n/a",
    ]
    return "| " + " | ".join(_cell(value) for value in values) + " |"


def _matrix_header() -> str:
    return (
        "| Command ID | Command | Test suite | Manual test steps | Expected behavior | Failure signals | Required environment | Required provider/API key | Requires live LM Studio | Requires web | Requires personal data | Safe for all_safe suite | Last manual test result | Last automated test result | Linked bug IDs | Regression test path |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
    )


def _matrix_row(record: CommandRecord) -> str:
    requires_web = "yes" if "network" in record.side_effects or "web" in record.requires_connector.lower() else "no"
    requires_personal = "yes" if "personal" in record.side_effects or record.trust_level in {"LOCAL_PRIVATE_DATA", "UNTRUSTED_EMAIL", "UNTRUSTED_MESSAGE"} else "no"
    live_lmstudio = "yes" if "LM Studio" in record.requires_connector else "no"
    safe_suite = "yes" if record.status == "active" and record.risk_level in {"SAFE", "LOW"} and requires_personal == "no" else "no"
    env = "local repo"
    if live_lmstudio == "yes":
        env = "LM Studio configured"
    elif requires_web == "yes":
        env = "network/provider optional"
    elif requires_personal == "yes":
        env = "explicit approval and configured connector"
    values = [
        record.command_id,
        f"`{record.command}`",
        record.test_coverage,
        f"Run `{record.example}` or dry-run/mock equivalent; inspect output and audit where relevant.",
        record.description,
        "non-zero exit, unredacted secret, policy bypass, missing audit, or unexpected side effect",
        env,
        record.requires_provider,
        live_lmstudio,
        requires_web,
        requires_personal,
        safe_suite,
        record.manual_qa_status,
        record.last_verified,
        "none",
        _regression_path(record),
    ]
    return "| " + " | ".join(_cell(value) for value in values) + " |"


def _regression_path(record: CommandRecord) -> str:
    group = record.group.lower()
    if "weather" in group:
        return "tests/test_web.py / tests/test_workflows.py"
    if "memory" in group:
        return "tests/test_memory.py"
    if "calendar" in group or "contacts" in group or "email" in group or "messages" in group or "tasks" in group:
        return "tests/test_personal_modules.py / tests/test_workflows.py"
    if "prompt" in group:
        return "tests/test_prompt_tracking.py / tests/test_promptops_workbench.py"
    if "command" in group or "eval" in group or "quality" in group:
        return "tests/test_command_registry.py"
    if "file" in group:
        return "tests/test_files_workflow.py"
    return "tests/test_ux_packaging.py"


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()
