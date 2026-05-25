# Test Plan

## Unit Tests

- Policy decisions.
- Tool broker execution and denial.
- LM Studio request payload construction.
- Audit entry redaction and hash chaining.
- Tool argument validation.

## Integration Tests

- No-tool chat sends no tools.
- Cross-platform architecture docs tests verify required platform docs exist, the Python core is documented as platform-neutral, bridges cannot bypass ToolBroker/PolicyEngine/ApprovalManager/AuditLogger, the capability matrix tracks planned non-executable capabilities, planned platform commands are tracked, and startup overhead policy forbids native imports, network calls, subprocesses, personal file scans, and app bridge server startup.
- Platform capability registry tests verify the portable `agent.platforms` registry loads on any OS, unknown platforms and capabilities return structured unsupported records, platform and capability ID lookup work, all records have risk/trust/approval/default/setup metadata, planned personal-data capabilities default disabled, CRITICAL capabilities require per-action approval metadata, registry imports do not import native macOS/iOS/Windows modules, and safe platform detection does not access personal data.
- Platform bridge interface tests verify `NullPlatformBridge` fails closed, `PlatformBridgeRegistry` lazy-loads only requested loaders, `prepare_action()` performs no side effects, direct `execute_action()` is blocked outside ToolBroker-approved context, broker-context null actions still return `requires_setup`, capability lists map to registry records, health checks access no personal data, and bridge interface imports require no native platform modules.
- Platform config/path/detection tests verify mocked macOS/Windows/Linux/unknown detection, runtime mode defaults and test forcing, brief cache behavior, detection failure setup guidance, project-local path computation without `Path.home()` or directory creation, Windows policy metadata warnings, disabled/lazy bridge config defaults, invalid config safe fallback, secret env omission from config metadata, and no native platform imports.
- Platform doctor command tests verify brokered read-only `platform doctor`, `platform status`, `platform capabilities`, `platform matrix`, and `platform explain <capability_id>` behavior for mocked macOS/Windows/unknown platforms, capability listing, web matrix planning rows, known/unknown capability explanations, no personal-data access flags, no native imports, startup policy validation, and command registry validation.
- Platform bridge stub tests verify macOS, iOS companion, Windows, and generic app/web stubs lazy-load only when requested, declare registry-backed capability records, return side-effect-free previews, block direct `execute_action()` calls, return `requires_setup` for broker-context execution, expose setup hints, import no native platform modules, access no personal data, perform no side effects, appear in platform doctor metadata, and keep default registry import overhead low.
- App Bridge contract tests verify schema validation, invalid payload rejection, unpaired sensitive request denial, ApprovalManager bypass denial, explicit user-interaction requirements, CRITICAL exact-preview/per-action/no-reuse rules, no personal data in status payloads, disabled safe config defaults, forced remote-off config, audit correlation requirements, no server startup during import, and secret-field redaction.
- Cross-platform release-gate docs tests verify `CROSS_PLATFORM_RELEASE_GATE.md` plus future macOS/iOS companion/Windows/app frontend guides exist and require ToolBroker, PolicyEngine, ApprovalManager, AuditLogger, command registry updates, startup-overhead rules, unsupported behavior handling, and explicit future approval for forbidden platform behavior.
- Native skill docs generator tests verify dry-run writes no files, explicit generation writes `docs/native_skills/SKILL_CATALOG.md` from fixture manifests, manual notes are preserved, missing docs are reported, deprecated skills remain cataloged, maturity is copied conservatively from manifests, catalog/docs-check CLI commands work, and command registry entries exist.
- Release generated artifact hygiene tests verify narrow `.gitignore` coverage for local eval, lead, messaging, iOS compose, and Reddit thread export artifacts while keeping source fixtures such as `workspace/dogfood/` and `workspace/skills/` reviewable.
- Tracker hygiene docs tests verify the dashboard, index, maintenance guide, archive policy, and consistency report exist and that README, AGENTS, Project State, Feature Maturity, and Command Registry link or enforce the new tracker navigation rules.
- Release hardening regression tests cover the `smart_agent.py setup` first-run guidance path and ensure it exits successfully without leaking secret-looking output.
- Tool-call loop appends matching tool results.
- CLI modes construct expected orchestration options.
- Golden Eval Suite tests load data-backed cases from `eval_cases/`, run router/policy/ToolBroker/workflow/prompt-injection checks, write scorecard reports, and keep personal-data cases skipped by default.
- Model-router benchmark and prompt-quality tests load reviewed fixture prompts, compare expected vs actual routes, attached tools, and policy decisions, verify no-tool prompts attach no tools, verify personal-data/send requests do not auto-execute, verify prompt-injection wrappers, and write prompt-quality reports.
- Prompt tracking CLI lists, advances, shows, adds, marks, audits, and reports missing prompt records without executing agent tools.
- Prompt tracker maturity tests cover embedded delimiter preservation, prompt search/evidence commands, one-active enforcement, failed-reason requirements, conservative recovery plans, prompt tracker evals, PTM release-gate docs, and prompt dogfood suite validation.
- Session logging tests cover start/status/end/list/show/replay/export behavior, `session run -- ...` stdout/stderr/exit-code capture, secret/email/phone and command-line redaction, visible audit-id linking, large-output truncation/storage, malformed session files, and gitignore protection for raw reports.
- Session review tests cover clean session summaries, failed command detection, user feedback flags, optional bug creation, stable incrementing bug ids, secret/personal-data redaction, P0 safety classification for policy-bypass signals, and `bugs list/show/export`.
- Live dogfood workflow tests cover `dogfood plan`, `dogfood next`, `dogfood checklist`, feature-maturity/latest-session recommendation logic, runbook document existence, and daily checklist references to session logging and review.
- Product Quality Dashboard tests cover `quality status`, session metadata display, open bug counts, P0/P1 next-bug prioritization, feedback secret redaction, read-only behavior without artifact directory creation, features lacking live validation, regression-test gaps, and JSON subcommands.
- Smoke harness tests use mocks for LM Studio, web search/fetch, and personal connector policy checks.
- Pytest markers identify `unit`, `integration`, `live_lmstudio`, `live_web`, `live_calendar`, `live_contacts`, `requires_approval`, and `personal_data`.
- Tests marked `personal_data` are skipped by default and must be explicitly selected.

## Policy Tests

- Unknown capabilities denied.
- Release hardening gates run startup policy validation, capability manifest validation, command registry validation, safe evals, dogfood dry-runs, and personal/default/CRITICAL approval checks before readiness promotion.
- SAFE actions allowed.
- HIGH actions ask approval.
- CRITICAL actions require per-action approval.
- FORBIDDEN actions denied.
- Capability manifest validation requires normalized capability name, tool name, connector name, risk level, trust level, default state, approval requirement, approval reuse flag, storage flag, rate limit field, memory behavior, audit fields, setup hint, and docs reference.
- Startup validation rejects missing risk levels, missing trust levels, missing approval rules, missing audit rules, invalid memory behavior, and manifest bypass flags.
- Personal-data capabilities must be disabled by default.
- CRITICAL capabilities must require per-action approval and disallow approval reuse.
- Every registered tool must have a matching manifest capability.

## Approval Tests

- Approval required when policy returns `ASK`.
- Denial prevents execution.
- Critical actions do not reuse approvals.
- Interactive approval prompts display previews, allow details review, and execute only after explicit approval.
- Action Center tests verify list/show, HIGH and CRITICAL approval requirements, one-time approval consumption, denial, edit invalidation, non-interactive blocking, no direct execution, required tool metadata, and export/audit minimization of sensitive bodies and drafts.
- Calendar approved write tests verify draft-only Action Center records, create/update/delete approval gates, denial blocking, one-shot approved execution through `ToolBroker`, direct broker write denial without a verified Action Center action id, rollback token capture, notes/body omission unless explicitly allowed, audit lifecycle, and disabled-by-default manifest entries.
- Contacts approved edit tests verify draft-only Action Center records, update/create approval gates, denial blocking, one-shot approved execution through `ToolBroker`, direct broker write denial without a verified Action Center action id, submitted-args matching against the approved preview, exact field diffs, sensitive-field redaction, bulk-edit denial, delete deferral, audit lifecycle, and disabled-by-default manifest entries.
- Email approved send tests verify Action Center reviewed drafts, CRITICAL per-action approval, denial blocking, edit invalidation, one-shot mock send execution through `ToolBroker`, direct broker send denial without a verified Action Center action id, submitted-args matching against the approved reviewed draft, full body preview, missing recipient blocking, attachment blocking, untrusted reply context, audit lifecycle, and disabled-by-default manifest entries.
- Messages safe handoff tests verify Action Center reviewed save/copy drafts, approval blocking, local draft-id handoff action creation, `messages draft` CLI draft creation, mock Lead Inbox draft creation, workspace-only saves, mock clipboard copy, direct broker save/copy denial without a verified Action Center action id, submitted-args matching against the approved reviewed draft, no automatic send capability, no memory writes, and audit lifecycle.
- Message safety Action Center tests verify send actions require local drafts, send action records are CRITICAL with exact previews, approval reuse is denied, draft edits invalidate approval, non-interactive/direct send paths remain unavailable, untrusted content cannot create sends without explicit user request, bulk recipients are rejected, audit lifecycle is logged, and audit/export copies redact message bodies/recipients.
- iOS compose bridge tests verify handoff payloads are created from approved drafts, unapproved drafts are blocked unless compose-only mode is explicitly used, payloads expire, approved Action Center preview mismatches are rejected, sent/cancelled/failed iOS-returned results are recorded, audit logs cover payload/result events, and no silent-send tool exists.
- macOS Messages probe tests verify non-mac unsupported results, macOS mocked metadata probe results, permission-denied setup instructions, no send verb, no `~/Library/Messages` access, result serialization for connector status, brokered audit logging, and LOW-risk capability manifest fields.
- macOS approved iMessage send adapter tests verify disabled-by-default status, CRITICAL exact Action Center preview, approved-action requirement, recipient allowlist, recent live-send probe, one-shot approval consumption, daily rate limit, non-interactive block, unsupported platform errors, probe failure keeping sends blocked, no private Messages database access, no Full Disk Access requirement, bulk/group denial, and redacted audit logs.
- Approved Lead Response Send tests verify CRITICAL exact-preview send-action creation from lead-linked drafts, Action Center approval requirement, approval reuse denial, draft-edit invalidation, unsupported-channel fallback, iOS compose handoff payload creation, manual handoff save/copy Action Center actions, local responded status updates, macOS Messages disabled/probe gate delegation, no bulk recipients, no auto-send, and no memory write.
- Messaging Dogfood Suite tests verify the `messaging_core`, `messaging_handoff`, `messaging_ios_compose`, `messaging_macos_probe`, `messaging_send_dry_run`, and `lead_response` YAML suites validate, remain default-disabled, use fixture/mock/preflight data, exclude `live-send-probe`, avoid direct `send --from-action` execution outside preflight, and keep `all_safe` free of live-send or personal-data commands.

## Audit-Log Tests

- Executions are logged.
- Denials are logged.
- Approval results are logged.
- Hash chain links entries.
- Secrets are redacted.
- Action lifecycle audit entries minimize sensitive Action Center previews while preserving lifecycle status, risk, trust, capability, and approval metadata.

## Prompt-Injection Tests

- Webpage instructions are ignored.
- Email/message instructions are ignored.
- Document instructions are ignored.
- Golden eval prompt-injection fixtures verify hostile page text is wrapped as untrusted data and does not become a system/tool instruction.
- Regression phrases include attempts to ignore instructions, reveal secrets, change policy, call tools, send email/text, disable audit logs, and store private data.

## Web Research Tests

- Web search provider missing returns a structured error.
- Brave/provider results normalize to compact untrusted records.
- `WEB_ACCESS_ENABLED=false` denies search/fetch through the broker.
- Fetch validates blocked domains, redirects, content types, and size limits.
- Scripts and event-handler content are stripped from extracted text.
- Fetched content is labeled and wrapped as `UNTRUSTED_WEB`.
- Research workflow does not fabricate sources.
- Research workflow reports fetch failures.
- Research workflow labels snippet-only evidence, reports unavailable fetches, surfaces basic conflicting-source limitations, includes provider/retrieved metadata, and supports `--provider`, `--max-sources`, `--freshness`, and `--no-fetch`.
- Citation/source attribution tests cover stable source IDs, fetched source citation, failed source exclusion from supporting citations, snippet-only labeling, retrieved timestamps, fabricated/unknown source rejection, conflict claim representation, and `research sources/export-sources/verify-sources --last`.
- Web cache/index tests cover cache hit before provider refresh, TTL expiry refresh, content-hash dedupe, local index search, personal/authenticated content denial, cache clear, no sensitive query persistence, audit logs for cache/index operations, command registry entries, and startup policy validation.
- Official API connector framework tests cover registry loading, provider/domain matching, missing setup hints, mocked public result normalization to `SearchResult`-compatible untrusted records, ToolBroker rate limiting, secret redaction, Reddit no-web-scraping-substitute metadata, provider-domain audit logging, and command registry entries.
- Internet dogfood/eval tests cover the new internet dogfood suite YAML files, default-disabled live web suites, recursive `eval_cases/internet` loading, fixture-backed source list and citation validation, `retrieved_at`, fetch-failure reporting, prompt-injection ignoring, free-first provider policy, no paid provider default, no query/web-content persistence, audit network-domain fixtures, CLI `eval run --internet` flag parsing, and command registry entries.
- Forum dogfood/eval tests cover Reddit/V2EX/multilingual/Chinese forum dogfood suite YAML validation, default-disabled live provider suites, `all_safe` exclusion for credential/network-gated forum suites, `eval_cases/forums` fixture sanitation, source ID/permalink preservation, generated translation labels, original snippets, deleted/removed and prompt-injection exclusion, no scraping or paid-provider defaults, no memory write, retention/cache policy evidence, provider-call audit fixtures, CLI `eval run --forums` flag parsing, and command registry entries.
- Forum Intelligence release-gate validation runs full pytest, startup policy validation, capability manifest validation, command registry validation, focused docs/command/forum/prompt tests, forum dogfood dry-runs, fixture-backed `eval run --forums`, safe Reddit/V2EX status checks, Reddit cache/retention/privacy reports, language/provider CLI smokes, and scans for CAPTCHA/login/anti-bot bypass, Chinese forum cookie/session scraping, and Reddit post/comment/vote/DM/moderation/write capability drift.
- Reddit + Multilingual Forum Intelligence planning validation checks the decision record, forum access policy, Reddit access policy, multilingual strategy, Chinese forum strategy, source-grounding policy, and retention policy exist and document no scraping, no CAPTCHA/login/anti-bot bypass, no forum-content training, no permanent forum storage by default, untrusted content labels, source grounding, and future ToolBroker/PolicyEngine/AuditLogger gates.
- Reddit provider policy/compliance tests cover disabled-by-default config, missing OAuth setup hints, no unauthenticated mode, forbidden posting/commenting/voting/DM capability denial, retention defaults, hard-false `REDDIT_USE_FOR_TRAINING`, author metadata disabled by default, web fallback policy denial, and capability manifest validation for disabled read-only placeholders.
- Reddit OAuth/config doctor tests cover missing config setup hints, secret redaction, repo-local token-path warnings, tracked `.env` warnings, generic user-agent warnings, disabled connector status, `connectors status reddit`, mocked auth-check success/failure, auth-check audit logs, no post/comment content fetch, brokered CLI output, and command registry entries.
- Reddit read-only connector tests cover mocked official Data API search/post/comment normalization, nested comments, deleted/removed content handling, rate-limit header parsing and structured 429 errors, author metadata redaction by default, TTL cache behavior, retention sweep deletion, absence of write capabilities, setup-required CLI behavior, sensitive query audit redaction, OAuth-only API base usage, command registry entries, startup policy validation, and capability manifest validation.
- Reddit search workflow tests cover global search, subreddit search, sort/time/limit/language option handling, setup-required behavior when Reddit is disabled or OAuth is missing, sensitive query audit redaction, no readable query persistence, snippet-only evidence labels, rate-limit error normalization, cached source explanation, CLI parsing, command registry entries, startup policy validation, and capability manifest validation.
- Reddit thread workflow tests cover Reddit URL and ID parsing, official API-only thread fetch, comment tree normalization, nested comment flattening, max-comment truncation, deleted/removed comment handling, author metadata redaction, workspace-only `UNTRUSTED_DOCUMENT` export, CLI audit records for fetch/export, command registry entries, startup policy validation, and capability manifest validation.
- Reddit summarization tests cover fetched-thread source use, snippet-only search summaries, source IDs/permalinks, deleted/removed content exclusion, prompt-injection-like comment exclusion, fabricated-source prevention, anecdotal caveats, low-data messaging, no summary memory write, CLI audit/query redaction, command registry entries, startup policy validation, and capability manifest validation.
- Reddit retention/cache compliance tests cover cache entry expiry, expired-entry sweep deletion, author metadata minimization by default, count-only privacy reports, no readable query-history persistence, removed/deleted content non-retention, cache clear behavior, audit logs for sweeps, CLI cache/retention/privacy status commands, command registry entries, startup policy validation, and capability manifest validation.
- Multilingual forum language tests cover English/Spanish/Chinese/Japanese/Korean detection fixtures, simplified/traditional Chinese hints, mocked local-model Chinese translation, generated-translation labeling, chunk source ID preservation, prompt-injection wrapping/ignoring, no memory write, workspace-file reads through brokered `filesystem.read`, command registry entries, startup policy validation, and capability manifest validation.
- Cross-language forum research tests cover English-only mocked research, Chinese fixture translation labeling, multiple-source comparison, unavailable source reporting, prompt-injection exclusion, fabricated-source prevention, no memory write, CLI ToolBroker/audit path, command registry entries, startup policy validation, and capability manifest validation.
- Global forum provider registry tests cover registry loading, Reddit registration, V2EX disabled/default documented-API status, Chinese discovery-only provider site-filter metadata, unknown provider handling, no personal/logged-in/network status reads, CLI provider/capability output, command registry entries, startup policy validation, and capability manifest validation.
- V2EX connector tests cover missing config doctor, token redaction, mocked node-topic/topic/reply normalization, structured rate-limit errors, mocked language/translation integration, absent write endpoints, command registry entries, startup policy validation, and capability manifest validation.
- Chinese forum discovery tests cover site-filter query generation for Zhihu/Tieba/Douban/Xiaohongshu/Weibo/V2EX/NGA, mocked approved search-provider result normalization, blocked/login/CAPTCHA page unavailability, public fixture fetch and summary, language detection triggering, mocked local translation triggering, no login cookies/browser sessions, no memory write/search-history persistence, CLI ToolBroker/audit path, command registry entries, startup policy validation, and capability manifest validation.
- Foreign-language titles/snippets/excerpts pass through without cloud translation.
- Audit logs include search and fetch actions.
- Free-first web acquisition tests cover robots allow/disallow parsing, malformed robots handling, robots-disallowed URL handling, sitemap XML and sitemap-index extraction, malformed sitemap handling, RSS/Atom item extraction with title/URL/date/summary/source fields, RSS/Atom MIME allowlist handling, sitemap/feed binary denial, malformed feed handling, timeout handling, default max limits, blocked-domain denial, TTL cache hits before repeated source fetches, CAPTCHA/block-page unavailability without bypass attempts, untrusted wrapper/document labels, network-domain audit logging, alias capability execution, and paid-provider skip defaults.
- Optional SerpAPI fallback tests cover no automatic selection under `free_first`, explicit provider use with mocked HTTP responses, missing-key and disabled-provider setup hints, paid-API and daily-cap disabled errors, config-only doctor/status output, result normalization, timeout/API/429 handling, secret/query redaction, provider-domain audit logging, and source-grounded research routing through `web.search.serpapi`.
- SearXNG provider tests cover missing base URL setup hints, disabled-by-default behavior, config-only doctor/status output, mocked JSON result normalization, timeout handling, HTTP 403/429 handling, malformed JSON / disabled JSON output errors, configured-domain audit logging, sensitive-query redaction, and no search-history persistence.
- Brave provider tests cover missing key setup hints, disabled-by-default behavior, config-only doctor/status output, key redaction, free-first skip behavior, paid/quota policy denial, mocked web/news result normalization, timeout handling, HTTP/API/429 handling, `api.search.brave.com` audit logging, sensitive-query redaction, and no search-history persistence.
- Internet Access graduation docs validation checks the decision record, web access policy, provider strategy, source-grounding requirements, and blocked-source policy exist and preserve no-bypass/no-paid-default/no-memory-by-default requirements.
- News Intelligence docs validation checks required News track/source/provider/freshness/grounding/retention/decision docs exist, provider strategy preserves the free-first/cache-first ladder, the risk model covers SAFE/LOW/MEDIUM/HIGH/FORBIDDEN news categories, planned `news.*` commands are present in the command registry as non-executable, and retention defaults forbid news/search history plus full article-body storage by default.
- News capability/provider-policy tests validate the 18 disabled/planned `news.*` manifest entries, required provider/status/rate-limit/memory/audit/docs fields, unknown news capability denial, default-disabled PolicyEngine denial for planned entries, no CRITICAL news v1 actions, missing risk/trust manifest rejection, safe `NEWS_*` config defaults, free-first provider choice, paid-provider skip defaults, no-history defaults, and conservative planned command registry rows.
- Native skill compatibility matrix tests cover manifest-derived platform/runtime/setup records, mocked macOS/Windows/Linux compatibility, missing binary setup requirements, personal-data skill flags, native app bridge planned status, no native platform imports, no skill execution, registry methods, CLI commands, command registry entries, startup policy validation, and capability manifest validation.

## Memory Tests

- Preference, project fact, and workflow lesson memories can be stored through `ToolBroker`.
- Secrets are rejected and redacted from audit logs.
- Email/message/contact/calendar content is not stored by default.
- Personal-data memory requires approval.
- Search respects scope and category filters.
- Export/delete/clear lifecycle operations are audited and document best-effort deletion limits.
- Context injection obeys record and character limits, excludes personal memory by default, and audits injected memory IDs.
- Knowledge Capture tests cover workspace-only note captures, URL captures through `web.fetch_url`, file captures through `filesystem.read`, explicit `--trusted-user` file labeling, secret rejection before capture writes, prompt-injection filtering, personal-data default memory-promotion blocks, and `promote-to-memory` routing through `memory.store`.
- Privacy Center tests cover status, metadata-only inventory, disabled connector visibility, memory counts without contents, redacted export previews, delete-memory confirmation denial, brokered `memory.clear` execution, audit summary, permissions summary, CLI dispatch, and no personal connector reads.

## Weather Tests

- Weather provider missing returns a structured error.
- `WEB_ACCESS_ENABLED=false` denies weather calls through the broker.
- Weather capabilities are LOW risk, rate-limited, audited, and labeled `UNTRUSTED_WEB`.
- Configured mock providers return normalized current weather and forecast data.
- Open-Meteo provider tests mock geocoding and forecast endpoints; live internet is not required for unit tests.
- Open-Meteo tests cover current normalization, forecast normalization, malformed responses, timeouts, geocoding failures, and audit domains.
- NWS provider tests mock geocoding, points/grid, forecast, hourly, and alerts endpoints; live internet is not required for unit tests.
- NWS tests cover U.S.-only location enforcement, forecast normalization, alert normalization, retryable timeouts, missing grid data, CLI alerts, and audit domains.
- WeatherKit stub tests cover not-configured errors, env presence checks, no secret values in output/audit logs, and provider selection only when explicitly configured.
- Forecast days are capped by `WEATHER_MAX_FORECAST_DAYS`.
- Location arguments are redacted from audit logs and are not persisted as history by default.
- Weather preferences tests cover no default location by default, explicit default-location use, default-location audit source, units preference, cache disabling, config show/set/clear, and no automatic memory writes.
- Weather-aware web research tests cover simple weather staying weather-only, delay/closure/latest-storm queries attaching web when needed, provider errors becoming limitations, web-disabled limitations, untrusted web instruction filtering, separated weather/web sections, and audit logs for both weather and web calls.
- Provider timeouts/errors return structured error payloads.
- Unknown weather tools are denied.

## Connector Dashboard Tests

- Weather configured status reports provider and enabled state without network calls.
- Web missing-provider status reports setup hints without hallucinating configuration.
- Browser status reports explicit URL workflow setup and does not require browser profile access.
- Personal connectors remain disabled by default.
- Connector status output does not reveal API keys, passwords, or tokens.
- Connector doctor does not access personal data or audit noisy personal checks.
- Connector status includes normalized capability summaries, risk, approval, rate-limit, cache, last-success/error, and setup-hint fields.
- Runtime doctor checks normalized manifest validation, ToolBroker initialization, connector registry loading, personal connector defaults, and CRITICAL action defaults without sending prompts or attaching tools.

## Provider Cost Policy Tests

- Free-first provider selection chooses no-key providers before paid or quota-limited providers.
- Paid providers are skipped when `ALLOW_PAID_APIS=false`.
- SerpAPI is selected only when explicitly requested, configured, and paid APIs are allowed; default/free-first paths skip it even when a key exists.
- Weather auto-selection chooses Open-Meteo for global current/forecast weather and NOAA/NWS for U.S. alerts where supported.
- WeatherAPI is selected only when configured and either explicitly requested or allowed as a default by paid-provider config.
- Provider decisions can be audited without executing provider calls.
- Provider decision payloads and audit logs redact secret-looking fields.
- `web providers`, `web provider-policy`, and `web provider-decision` run through ToolBroker, do not execute provider API calls, include selected/skipped providers, skip reasons, paid API/cache flags, and redact sensitive queries in audit logs.
- `web search-providers` lists metadata-only search provider registry entries through ToolBroker without provider calls.
- Search Provider Registry tests cover unknown provider denial, missing-provider setup hints, ToolBroker-only provider search, normalized result/response schema, normalized provider errors, query redaction, and no search-history persistence.
- Missing or unsupported providers return clear setup hints.
- Runtime acquisition tools integrate the provider ladder for local cache, feed, sitemap, direct URL, and unavailable query cases without defaulting to paid providers.
- Web Acquisition Layer core tests validate `AcquisitionRequest`, unknown-provider denial, cache-first planning, blocked URL source status, `UNTRUSTED_WEB` / `UNTRUSTED_DOCUMENT` labels, no query-history storage, and brokered `web.source_status` audit records.
- Safe web fetch/extraction tests validate invalid URL and non-http scheme rejection, domain blocklist denial, timeout handling, redirect-limit error propagation, binary content blocking, script/event-handler stripping, prompt-injection wrapping, metadata extraction, CAPTCHA/block-page unavailable results, brokered extraction/metadata tools, audited network domains, and command registry entries.
- Internet routing policy tests validate current/latest/source-required questions route to internet-capable tools, stable and local-repo questions do not route to internet by default, explicit URLs route to fetch, citation requests route to research-shaped search/fetch, no-tools mode disables internet, prompt-injection-like text cannot force routing, `preflight` includes internet-routing metadata, and `router explain` works without provider calls.

## Secret/Config Doctor Tests

- `secrets doctor` and `secrets status` never print raw SerpAPI, WeatherAPI, Gmail, or Telegram credential values.
- Missing credentials report setup hints.
- Tracked `.env` files and repo-local token paths produce warnings.
- Gmail-focused doctor tests cover broad/send-capable scope warnings, repo-local token path warnings, no inbox reads, no sends, and CRITICAL disabled send policy.
- Telegram-focused doctor tests cover bot-token redaction, missing default chat warnings, allowed chat-id config, no chat reads, no sends, and CRITICAL disabled send policy.
- Secret-looking docs/tests/config values produce redacted warnings.
- SerpAPI and WeatherAPI remain disabled under `free_first` unless paid APIs and limits are explicitly configured.
- `connectors status serpapi/weatherapi/gmail/telegram` returns redacted metadata only and makes no provider calls.

## Live Smoke Tests

- `python smart_agent.py smoke --lmstudio` verifies no-tool chat, debug events, and the safe time-tool path when `LMSTUDIO_MODEL` and LM Studio are available.
- `python smart_agent.py smoke --web` verifies configured search, safe public fetch, and source-grounded research behavior without fabricating sources.
- `python smart_agent.py smoke --calendar --contacts` performs dry-run connector and policy checks only; it does not read personal data by default.
- Unconfigured live services are reported as skipped instead of faked as passing.

## Personal-Data Tests

- Personal modules disabled by default.
- Selected-scope reads require approval.
- Body text is not stored in long-term memory by default.
- Calendar selected-range reads require approval, enforce max date ranges, omit notes/body by default, redact locations by default, and audit accesses as `LOCAL_PRIVATE_DATA`.
- Calendar availability returns slots without leaking event details.
- Contacts search/read require approval, keep tools disabled by default, return compact search candidates, require a selected-scope token and explicit requested fields for selected reads, omit notes, redact email/phone/address values by default, deny bulk export attempts, and audit accesses as `LOCAL_PRIVATE_DATA`.
- Email metadata/read/summarize/draft require approval when enabled, keep tools disabled by default, return no body in metadata, wrap selected thread bodies as `UNTRUSTED_EMAIL`, ignore prompt injection, never send drafts, refuse bulk thread ids, avoid long-term body storage, and audit access.
- Messages read/summarize/draft require approval when enabled, keep tools disabled by default, do not implement sends or bulk history reads, refuse bulk thread ids, return clear setup errors for unsafe/unconfigured adapters, restrict manual draft context files to `./workspace`, wrap content as `UNTRUSTED_MESSAGE`, ignore prompt injection, avoid long-term body storage, and audit access.
- Messages save/copy handoff requires Action Center approval with verified action ids and approved-preview argument matching before any workspace draft write or clipboard copy.
- macOS `messages.macos.send_approved` is disabled by default and must require `channel=macos_messages`, exact approved Action Center item, allowlisted recipient, recent passing live-send probe, rate-limit availability, no attachments, no bulk/group recipients, and ToolBroker execution.
- Channel-neutral messaging send proposals require local drafts and create Action Center records only; `messaging.send_approved` remains disabled and unregistered as an executable tool, approval reuse is false, draft edits invalidate approvals, bulk recipients and attachments are denied, and no message body is stored in memory by default.
- Incoming message strategy tests cover manual workspace-file import, unsafe path and `~/Library/Messages/chat.db` denial, `UNTRUSTED_MESSAGE` labeling, manual/mock inbox list/show, Lead Inbox candidate metadata, draft-only reply creation, prompt-injection filtering, no send path, no memory write, CLI commands, and audit logs for import/read/draft.
- iOS user-confirmed compose bridge tests cover local payload creation, expiration, approved-preview recipient/body matching, result recording, no message body memory writes, and no silent send path.
- Lead Inbox and Lead Response Drafting tests cover mock lead listing, selected full-message read approval behavior and disabled-by-default manifest state, classification without action creation, summaries with untrusted-source assumptions, draft-response creating editable local `MessageDraft` records without sending or send actions, follow-up task Action Center records without task execution, meeting suggestions without calendar reads or event creation, prompt-injection filtering from untrusted lead previews, no memory writes by default, and broker audit coverage.
- Apple Messages for Business provider tests cover disabled/not-configured setup hints, mock inbound lead creation, `UNTRUSTED_MESSAGE` labeling, local Lead Inbox mapping, draft-response `MessageDraft` creation without sends, future send capability disabled by default, connector status disabled, secret redaction, audit redaction, and CLI commands.
- Browser selected URL and clipping tests cover canonical capabilities `browser.read_url`, `browser.summarize_url`, `browser.clip_url_to_workspace`, and disabled `browser.selected_tab`; explicit URL fetch through `web.fetch_url`; blocked-domain denial; prompt-injection filtering; workspace-only clipping through `filesystem.write`; `UNTRUSTED_WEB`/`UNTRUSTED_DOCUMENT` labeling; selected-tab stub setup notes; no browser history/cookie/session/password/profile access; and audit logs for fetch/write/stub paths.
- Tasks/reminders tests cover disabled provider access, approval-required listing, brokered `tasks.draft_create` Action Center queuing, create/complete/delete approval gates, one-shot approved create execution, no memory writes, audit lifecycle, setup errors, and mock provider list/create/update/complete/delete paths.

## Self-Improvement Tests

- Proposal mode does not edit files.
- Implementation creates a branch.
- Policy weakening and audit disabling are blocked.
- Tests and diffs are produced before commit.
- `improve create-action-for-commit` runs brokered tests and brokered diff, creates only a pending Action Center `self_improvement.commit` record when tests pass and a diff exists, and does not commit.
- Failed self-improvement tests prevent commit action creation.
- `improve overnight-plan` excludes HIGH/CRITICAL and personal-data work, ranks docs/tests/hardening candidates first, reads tracking docs through `ToolBroker`, and creates no branch, schedule, memory write, commit, or file edit.
- Overnight runbook and report template existence tests verify safe-mode constraints and review fields are documented.

## Release-Gate Tests

- All selected milestone tests pass or failures are documented.
- Forbidden capabilities are absent.
- Audit and policy checks pass.
- Full release-gate maturity reviews run the full suite, startup policy validation, capability manifest validation, safe eval suite, command registry validation, native skill validation, unknown-tool denial, ToolBroker path scans, personal-data default checks, HIGH approval checks, and CRITICAL per-action/no-reuse checks.

## Prompt Tracking Tests

- `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, `docs/PROMPT_AUDIT.md`, and `docs/templates/prompt_record_template.md` exist.
- `docs/PROMPT_PACK_FORMAT.md` and `docs/templates/prompt_pack_template.md` exist.
- Every queued prompt has a `prompt_id`.
- At most one prompt is active at a time.
- `docs/PROJECT_STATE.md` references `active_prompt_id`, `next_prompt_id`, `prompt_queue_status`, and `last_prompt_audit_result`.
- `AGENTS.md` requires prompt ledger/queue updates.
- `prompts mark-complete` requires test/docs status fields or `--unknown`.
- Prompt pack parser tests cover valid packs, duplicate ids, duplicate order, missing end markers, missing metadata, invalid risk levels, missing dependencies, circular dependencies, execute-all rejection, validate-without-write behavior, import file writes, queue updates, dependency-aware next prompt selection, approval-gate blocking, body preservation, and missing completion evidence.
- PromptOps Workbench tests cover import from stdin/file/clipboard, raw single prompt import, invalid metadata/risk rejection, dependency-aware next prompt selection, copy-next clipboard behavior, disabled-by-default run-next, safe-only autopilot rejection of HIGH/approval-gated prompts, secret redaction in reports, and mark-complete evidence requirements.

## Command Registry Tests

- `docs/COMMAND_REGISTRY.md`, `docs/COMMAND_TEST_MATRIX.md`, `docs/COMMAND_LEGACY.md`, `docs/COMMAND_QA_RUNBOOK.md`, and command templates exist.
- Every registered command has an id, command string, group, status, maturity level, risk level, approval requirement, description, example, docs link, and test/manual QA status.
- Command registry validation catches missing docs, missing matrix rows, invalid status values, invalid risk values, missing examples, and missing AGENTS/README references.
- CLI tests cover `commands list`, `commands show`, `commands search`, `commands legacy`, `commands deprecated`, `commands validate`, `commands qa-plan`, and `commands qa-run`.
- `commands qa-run` does not execute command examples in v1 and only prints SAFE/LOW active command examples for the requested group.

## Native Skills Program Tests

- `docs/native_skills/NATIVE_SKILLS_PROGRAM.md` exists.
- `docs/native_skills/SKILL_INTAKE_PROCESS.md` exists.
- `docs/native_skills/NATIVE_SKILL_CRITERIA.md` exists.
- `docs/native_skills/NATIVE_SKILL_CANDIDATES.md` exists.
- `docs/native_skills/SKILL_RISK_MODEL.md` exists.
- `docs/templates/native_skill_record_template.md` exists.
- Program docs define native skills as reviewed local workflows mapped to `ToolBroker`.
- Program docs state native skills are not unreviewed external scripts, direct tool access, hidden network access, automatic installs, or approval bypasses.
- Native skill vetter tests cover safe `SKILL.md` files, shell-command flags, network-call flags, secret references, filesystem escapes, prompt-injection language, approval-bypass language, opaque binaries, missing license warnings, no script execution, workspace-only reads, and audit logging.
- Native skill manifest tests cover valid manifest loading, invalid manifest rejection, unknown capability rejection, missing risk/trust rejection, ToolBroker-bypass language rejection, personal-data disabled-by-default enforcement, and `skills list/show/validate/doctor` command behavior.
- Native skill conflict detector tests cover duplicate skill IDs, same command, same capability claim, CRITICAL approval reuse, HIGH without approval, personal-data memory mismatch, missing docs/tests, missing dependency/provider/platform conflicts, unreviewed shadowing, explain-conflict lookup, JSON CLI output, and metadata-only execution language.
- Native skill test harness tests cover safe skill pass, high-risk skip, personal-data skip, missing dependency setup skip, prompt-injection fixture detection, secret fixture detection, `skills test`, `skills dogfood`, native skill dogfood suite validation, `eval run --native-skills`, and command registry coverage.
- Native skill finder tests cover implemented manifest matches, planned candidate matches, maturity/readiness reporting, approval reporting, no-match candidate creation guidance, no external marketplace search/install, brokered execution, and audit logging of local docs read.
- PDF workspace native skill tests cover path traversal, denied paths, PDF info fixtures, embedded text extraction, no-table extraction behavior, no-memory summaries, file-size limits, malformed PDFs, audit logging, no external binary execution, CLI broker path, and native manifest/docs validation.
- Criteria docs include disqualifiers for unrestricted filesystem access, browser cookies/session tokens, Keychain/password access, private app database scraping, opaque binaries, unclear licenses, and unsandboxable behavior.
- Risk model docs cover external skill supply-chain risk and prohibit running external code during intake.

## Scheduler Tests

- Schedule create/list writes and reads explicit local schedule records.
- Manual `schedule run` executes a safe supported workflow and audits run start/finish.
- Personal scheduled Daily Briefing sections require normal approval and do not read personal data when approval is unavailable.
- Unsupported or CRITICAL workflows are rejected and not executed.
- Pause prevents runs and delete removes the local schedule record.
- Scheduler v1 creates no LaunchAgent, cron, daemon, login item, or hidden persistence.
- CLI tests cover schedule create/list with a test-local `SCHEDULE_PATH`.
- Scheduler backup tests verify `backup_create` runs through brokered `backup.create`, writes a redacted backup, audits the provider call, reads no personal connectors, writes no memory, and rejects unredacted backup args.
