# Natural-Language Intent Taxonomy

Status: specified.

Intent IDs are stable labels used by the natural-language parser and eval fixtures. They are descriptive metadata, not authorization. Future execution remains bounded by ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger.

| Intent ID | Meaning | Typical handling |
|---|---|---|
| `chat.no_tools` | User wants clean model discussion without tools. | `answer_directly` or no-tools chat. |
| `chat.general` | General explanation or creative/helpful response. | `answer_directly` unless current/source-required. |
| `doctor.status` | User asks whether the agent, runtime, provider, or connector is healthy. | `route_to_command` or `show_command_suggestion`. |
| `command.help` | User asks what commands exist or how to use them. | `route_to_command` / help search. |
| `command.search` | User asks to find a command by topic. | Suggest command search. |
| `weather.current` | Current weather for an explicit location. | Safe weather command or preflight. |
| `weather.forecast` | Forecast request for explicit location/date range. | Safe weather forecast command or clarification. |
| `web.research` | Source-grounded web lookup, verification, citations, latest/current info. | Research/search preflight; provider setup if missing. |
| `news.brief` | Current headlines or news topic brief. | Planned news command suggestion or web/research fallback only when policy allows. |
| `reddit.search` | Reddit/forum discussion search. | Suggest configured Reddit/forum command; setup hint if disabled. |
| `file.read` | Read or inspect a workspace file. | Workspace-bounded read suggestion/preflight. |
| `file.summarize` | Summarize a workspace file. | Workspace-bounded summarize suggestion/preflight. |
| `memory.search` | Search existing memory. | Memory search/context-preview suggestion; no personal by default. |
| `memory.add` | Store a memory/preference. | Preflight; personal/secret/untrusted content remains blocked or approval-gated. |
| `prompt.queue` | Prompt tracker queue, next prompt, prompt pack status. | Prompt tracker command suggestion. |
| `git.status` | Repo branch/status/diff question. | Suggest safe git/status command or local CLI status where supported. |
| `test.run` | Run targeted/full tests. | Test command suggestion; no package install. |
| `docs.lookup` | Find docs or explain tracker docs. | Command/docs search suggestion. |
| `bug.report` | File or inspect bug/regression reports. | Bug/session command suggestion. |
| `session.review` | Review latest dogfood/session results. | Session review suggestion; redacted only. |
| `action.preflight` | User asks "what would happen" or "dry run this." | Natural-language preflight. |
| `personal_data.request` | User asks to read personal email/calendar/contacts/messages/tasks. | Require setup/approval/selected scope; no execution by default. |
| `send_or_write.request` | User asks to send, write, delete, mutate, or commit. | Approval/preflight/Action Center only; no silent execution. |
| `unknown` | No reliable intent. | Help handoff or chat fallback. |
| `ambiguous` | More than one plausible intent or missing required parameter. | Ask clarification. |

## Confidence Bands

- High: exact command phrase, explicit known object, and required parameters present.
- Medium: clear domain but missing provider/setup or optional parameters.
- Low: broad phrase, short command, or multiple plausible command groups.

Low confidence should not execute anything. Medium confidence may suggest commands or preflight. High confidence still cannot bypass policy.
