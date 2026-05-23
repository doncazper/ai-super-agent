# AI Super Agent User Guide

## Purpose

This guide explains how to use the AI Super Agent as a real product, not just as a collection of scripts and features.

It should be kept in sync with:

- `README.md`
- `CHANGELOG.md`
- `docs/COMMAND_REGISTRY.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_MATURITY.md`
- `docs/FEATURE_ROADMAP.md`
- `docs/PROJECT_STATE.md`
- `docs/COMPLETION_REPORT.md`
- `docs/RISK_REGISTER.md`
- `docs/THREAT_MODEL.md`
- `docs/RELEASE_CHECKLIST.md`

The README is the quick start.
The command registry is the full command catalog.
This user guide is the end-to-end operating manual.

---

## 1. What This Agent Is

AI Super Agent is a local AI assistant that runs through a Python agent core and connects to LM Studio / Qwopus for model responses.

The agent is designed to eventually support:

- local chat
- web research
- weather
- news
- Reddit and forum research
- workspace files
- memory
- calendar
- contacts
- email drafting
- message drafting
- approvals
- audit logs
- native skills
- self-improvement
- future Mac / iOS / Windows app bridges

The agent is safety-first. Tools do not execute directly. Actions must pass through the ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger.

---

## 2. What This Agent Is Not

The agent is not an unrestricted system controller.

It should not:

- silently read email, messages, contacts, calendar, browser history, Keychain, secrets, or private app folders
- scrape private macOS app databases as the first approach
- send emails or texts without explicit per-action approval
- bypass CAPTCHA, paywalls, robots, or anti-bot systems
- weaken its own policy
- disable audit logs
- grant itself permissions
- create persistence without explicit approval
- use personal data by default
- store secrets in memory

---

## 3. Quick Start

### 3.1 Activate your virtual environment

From the repo root:

```bash
source .venv/bin/activate
```

### 3.2 Set your LM Studio model

```bash
export LMSTUDIO_BASE_URL="http://localhost:1234/v1"
export LMSTUDIO_MODEL="qwopus3.6-35b-a3b-v1@q5_k_m"
```

### 3.3 Run doctor

```bash
python smart_agent.py doctor
```

### 3.4 Try clean no-tool chat

```bash
python smart_agent.py --no-tools "Explain RCS vs iMessage in simple terms."
```

### 3.5 Try a debug tool call

```bash
python smart_agent.py --debug "What time is it?"
```

### 3.6 Use interactive mode

```bash
python smart_agent.py --interactive
```

---

## 4. Core Concepts

### ToolBroker

All tools must execute through the ToolBroker.

### PolicyEngine

PolicyEngine decides whether an action is allowed, denied, or requires approval.

### PermissionManager

PermissionManager tracks which capabilities are enabled or disabled.

### ApprovalManager

ApprovalManager handles user approval for risky actions.

### AuditLogger

AuditLogger records important events, including denials, approvals, executions, and failures.

### Trust Levels

Content from web pages, emails, messages, documents, and forums is treated as untrusted data.

### Risk Levels

Actions are classified as SAFE, LOW, MEDIUM, HIGH, CRITICAL, or FORBIDDEN.

---

## 5. Main Command Areas

For the full list, see `docs/COMMAND_REGISTRY.md`.

Common command groups include:

- core runtime
- doctor / status / config
- tools
- connectors
- approvals
- action center
- weather
- web / research
- news
- Reddit / forums
- workspace files
- memory
- calendar
- contacts
- email
- messages
- native skills
- PDF / documents
- session logging
- dogfood
- feedback
- bugs / regressions
- PromptOps / workbench
- evals / quality
- briefing
- meeting workflows
- tasks / reminders
- capture / notes
- privacy
- backup
- scheduler
- self-improvement
- dashboard
- platform bridge

---

## 6. Weather

Weather is intended to be a mature connector pattern.

Example commands:

```bash
python smart_agent.py weather doctor
python smart_agent.py weather current "Phoenix, AZ"
python smart_agent.py weather forecast "Phoenix, AZ" --days 3
python smart_agent.py weather alerts "Los Angeles, CA"
python smart_agent.py briefing daily --weather "Phoenix, AZ"
```

Expected behavior:

- free-first provider selection where possible
- provider shown in output
- retrieved time shown
- cache and rate limits respected
- no system location inference unless explicitly configured
- no memory write by default

---

## 7. Web Research

Web research is for source-grounded answers using public web data.

Example commands:

```bash
python smart_agent.py research "latest LM Studio MCP documentation"
python smart_agent.py web fetch "https://example.com"
python smart_agent.py web providers
python smart_agent.py router explain "latest AI coding agent news"
```

Expected behavior:

- web content is untrusted
- sources are shown
- blocked/fetch-failed sources are reported
- paid providers are not used by default
- search history is not stored by default

---

## 8. News

News should become a dedicated module built on top of web acquisition.

Example future commands:

```bash
python smart_agent.py news top
python smart_agent.py news search "OpenAI Codex"
python smart_agent.py news brief "AI agents"
python smart_agent.py news timeline "Reddit API changes"
python smart_agent.py news compare "OpenAI and Anthropic agents"
```

Expected behavior:

- freshness is clear
- source list is shown
- snippet-only sources are labeled
- conflicting coverage is caveated
- no fabricated citations
- blocked/paywalled pages are reported

---

## 9. Reddit and Forums

Reddit/forum intelligence should use official APIs or compliant public fetches.

Example future commands:

```bash
python smart_agent.py reddit doctor
python smart_agent.py reddit search "best local LLM tools"
python smart_agent.py reddit thread "<post_url_or_id>"
python smart_agent.py reddit summarize-thread "<post_url_or_id>"
python smart_agent.py forums research "topic" --languages en,zh
```

Expected behavior:

- official Reddit API first
- no CAPTCHA or anti-bot bypass
- no logged-in scraping
- no AI training use
- retention/cache policy enforced
- forum content treated as untrusted
- multilingual summaries label translations as generated

---

## 10. Workspace Files

Workspace file access is bounded to approved roots.

Example commands:

```bash
python smart_agent.py files list ./workspace
python smart_agent.py files read ./workspace/notes.md
python smart_agent.py files summarize ./workspace/notes.md
python smart_agent.py files patch ./workspace/file.py
```

Expected behavior:

- path traversal blocked
- private folders denied
- backups before overwrite
- deletes require approval
- file content is treated as untrusted unless explicitly trusted

---

## 11. Memory

Memory stores safe preferences, project facts, and workflow lessons.

Example commands:

```bash
python smart_agent.py memory list
python smart_agent.py memory add
python smart_agent.py memory search "project uses pytest"
python smart_agent.py memory delete <memory_id>
python smart_agent.py memory export
```

Expected behavior:

- secrets are rejected or redacted
- personal data requires approval
- email/message/contact/calendar bodies are not stored by default
- memory reads and writes are audited

---

## 12. Personal Data Modules

Personal modules are disabled by default and selected-scope first.

Planned or active areas:

- calendar read-only
- contacts read-only
- email draft-only
- messages draft-only
- tasks / reminders
- approved writes later

Rules:

- no bulk ingestion
- no sends without explicit approval
- no writes without approval
- no long-term storage of personal content by default
- every access audited

---

## 13. Approvals and Action Center

Risky actions should create reviewable actions before execution.

Example commands:

```bash
python smart_agent.py approvals list
python smart_agent.py approvals show <request_id>
python smart_agent.py actions list
python smart_agent.py actions show <action_id>
python smart_agent.py actions approve <action_id>
python smart_agent.py actions deny <action_id>
```

Expected behavior:

- HIGH actions require approval
- CRITICAL actions require explicit per-action approval
- approval reuse is denied for CRITICAL actions
- editing an action invalidates prior approval
- all approval lifecycle events are audited

---

## 14. Session Logging and Dogfooding

Use dogfood sessions to test real behavior.

Example workflow:

```bash
python smart_agent.py session start --name "daily-smoke"
python smart_agent.py dogfood run core --session
python smart_agent.py dogfood run weather --session
python smart_agent.py dogfood run web --session
python smart_agent.py session end
python smart_agent.py session review --last --create-bugs
python smart_agent.py quality status
```

Expected behavior:

- commands are logged
- outputs are redacted
- feedback can be attached
- bugs can be generated
- regression tests can be created from bugs

---

## 15. Command Registry

The command registry is the authoritative CLI catalog.

Use it to answer:

- What commands exist?
- What do they do?
- Are they active, experimental, stubbed, deprecated, legacy, removed, or blocked?
- What risk level do they have?
- What examples can I run?
- What commands need manual QA?

Example future commands:

```bash
python smart_agent.py commands list
python smart_agent.py commands search "weather"
python smart_agent.py commands show CMD-WEATHER-001
python smart_agent.py commands validate
python smart_agent.py commands qa-plan
```

---

## 16. Troubleshooting

### Python version error

If you see an error about `StrEnum`, you are probably using Python 3.9.

Use Python 3.11+ or 3.12.

```bash
python --version
```

### LMSTUDIO_MODEL is not set

Set:

```bash
export LMSTUDIO_BASE_URL="http://localhost:1234/v1"
export LMSTUDIO_MODEL="qwopus3.6-35b-a3b-v1@q5_k_m"
```

Then run:

```bash
python smart_agent.py doctor
```

### LM Studio server not reachable

Start the LM Studio local server, then test:

```bash
curl http://localhost:1234/v1/models
```

### Provider not configured

Run connector doctor commands:

```bash
python smart_agent.py connectors doctor
python smart_agent.py weather doctor
python smart_agent.py web providers
```

### Personal-data command is denied

This is usually correct. Personal-data tools are disabled by default and must be enabled through permissions and approvals.

---

## 17. Manual QA Checklist

Use this weekly:

```bash
python smart_agent.py doctor
python smart_agent.py commands validate
python smart_agent.py eval run --safe
python smart_agent.py dogfood run all_safe --session
python smart_agent.py quality status
```

Check:

- Did any command fail?
- Did any output look confusing?
- Did a command call the wrong tool?
- Did no-tools mode attach tools?
- Did a risky action fail to ask approval?
- Did any source-grounded answer lack sources?
- Did any provider use a paid API unexpectedly?
- Did any log reveal secrets?

---

## 18. Weekly Documentation Review

A weekly docs review should:

1. Read `CHANGELOG.md`.
2. Read `docs/COMPLETION_REPORT.md`.
3. Read `docs/FEATURE_REGISTRY.md`.
4. Read `docs/FEATURE_MATURITY.md`.
5. Read `docs/COMMAND_REGISTRY.md`.
6. Read recent bug/session/eval reports.
7. Update this user guide.
8. Update the README quick start if needed.
9. Update command examples.
10. Add missing troubleshooting notes.
11. Mark stale sections.
12. Create a documentation review report.

Recommended command later:

```bash
python smart_agent.py docs weekly-review
```

---

## 19. Release Readiness

A feature is not production-ready unless:

- command is documented
- command has examples
- tests pass
- policy behavior is validated
- audit behavior is validated
- manual QA has been run
- dogfood/eval exists
- feature maturity is accurate
- setup/troubleshooting docs exist
- known limitations are listed

---

## 20. Known Limitations

Update this section as the project evolves.

Current likely limitations:

- Some commands may be planned or stubbed.
- Some providers require API keys.
- Personal-data tools are disabled by default.
- iMessage/Messages send paths require special Apple bridge work.
- Live validation may lag behind unit tests.
- News, Reddit, and web may be less mature than Weather until their release gates complete.

---

## 21. Where to Look Next

| Need | File |
|---|---|
| Quick start | `README.md` |
| Full user guide | `docs/USER_GUIDE.md` |
| All commands | `docs/COMMAND_REGISTRY.md` |
| Manual command tests | `docs/COMMAND_TEST_MATRIX.md` |
| Current status | `docs/PROJECT_STATE.md` |
| Feature list | `docs/FEATURE_REGISTRY.md` |
| Feature maturity | `docs/FEATURE_MATURITY.md` |
| Roadmap | `docs/FEATURE_ROADMAP.md` |
| Changelog | `CHANGELOG.md` |
| Completion history | `docs/COMPLETION_REPORT.md` |
| Risks | `docs/RISK_REGISTER.md` |
| Threat model | `docs/THREAT_MODEL.md` |
| Release checklist | `docs/RELEASE_CHECKLIST.md` |
