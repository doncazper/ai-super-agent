# Skill Marketplace Survey

Date: 2026-05-23

Prompt ID: `SKILL-MARKETPLACE-SURVEY`

## Scope

This survey reviews popular OpenClaw, ClawHub, LobeHub-style, and adjacent agent-skill categories as product and safety signals only. It does not install, import, run, clone, or execute external skills.

External marketplace pages, repository listings, and skill descriptions are treated as `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`. Useful patterns must be reimplemented locally as reviewed native skills that map to existing `ToolBroker` capabilities and obey `PolicyEngine`, `PermissionManager`, `ApprovalManager`, `AuditLogger`, memory rules, and trust labels.

## Sources Reviewed

Sources are used for category and ecosystem signals, not as trusted implementation instructions.

| Source | What It Contributed | Trust |
|---|---|---|
| OpenClaw ecosystem docs: `https://clawdocs.org/reference/ecosystem/` | Marketplace size, category breadth, security warnings, skill collection categories | `UNTRUSTED_WEB` |
| Sundial awesome OpenClaw skills: `https://github.com/sundial-org/awesome-openclaw-skills` | Category examples for developer tools, web/search, notes/knowledge, documents, code review, architecture, productivity, communications | `UNTRUSTED_WEB` |
| LobeHub file upload and knowledge base docs: `https://www.mintlify.com/lobehub/lobehub/features/file-upload` | File/document/knowledge-base demand signals, source-grounded document workflows, privacy caveats | `UNTRUSTED_WEB` |
| TechRadar OpenClaw skills guide: `https://www.techradar.com/pro/what-are-openclaw-skills-a-detailed-guide` | General description of skill mechanics and marketplace safety risks | `UNTRUSTED_WEB` |

## Survey Findings

The marketplace categories cluster around a few repeated user needs:

- Work with documents, PDFs, Office files, and knowledge bases.
- Search, fetch, summarize, and cite public web sources.
- Improve coding workflows through TDD, code review, architecture review, GitHub/PR review, and browser testing.
- Capture notes, project facts, and reusable workflow lessons.
- Manage personal productivity across tasks, calendar, email, and messages.
- Analyze data and spreadsheets.
- Vet skills, scan secrets, and protect agents from supply-chain and prompt-injection attacks.
- Automate increasingly broad workflows, including browser automation, cloud deployment, communications, and self-improvement.

For this project, the most attractive native candidates are not the most powerful marketplace skills. They are the ones that can be implemented locally with bounded workspace inputs, mockable tests, no secrets by default, and clear `ToolBroker` mappings.

## High-Confidence Patterns

| Pattern | Reason It Matters | Safe Native Interpretation |
|---|---|---|
| Skill discovery and vetting | Skill marketplaces are large and uneven; manual review does not scale | Local records, source/license/risk review, no install or execution |
| Document and PDF workflows | Frequent, valuable, workspace-bounded, easy to test with fixtures | Read/summarize/extract/cite approved workspace files only |
| Office document workflows | High user value for reports, spreadsheets, decks | Use existing document/spreadsheet libraries through controlled workflow modules |
| Source-grounded research | Common marketplace category and already partly implemented here | Reusable research workflow over brokered `web.search` and `web.fetch_url` |
| TDD and regression generation | Low personal-data risk and high leverage for this repo | Read approved project files/tests and propose tests; writes only via file policy |
| Code and architecture review | Useful, workspace-bounded, no external credentials needed | Read diffs/files through `ToolBroker`; produce review findings as model output |
| Knowledge capture | Complements Memory v2 and workspace capture | Store captures in approved workspace; memory promotion explicit and audited |

## High-Risk Patterns

| Pattern | Why Deferred |
|---|---|
| Email send | CRITICAL side effect, recipient/body/attachments must be reviewed per action |
| Message send | CRITICAL side effect, platform automation risks, no safe broad macOS path yet |
| Browser automation | Can touch logged-in sessions, cookies, forms, passwords, and private data |
| Cloud deployment | Can mutate paid infrastructure, secrets, DNS, and production resources |
| Self-evolution | Can weaken policy or add persistence unless tightly gated |
| Unrestricted app automation | Often depends on Accessibility, UI scripting, broad file access, or fragile state |

## Category Priorities

Native candidates should be selected in this order:

1. Safety and governance skills that make future skill intake safer.
2. Workspace-bounded document, testing, review, and research skills.
3. Existing workflow-polish skills that reuse already-hardened modules.
4. Selected-scope personal-data skills only after explicit readiness gates.
5. Approved write/send or automation skills only after Action Center and per-action approval gates.

## Non-Goals Preserved

- No external skills installed.
- No external scripts run.
- No untrusted code fetched for execution.
- No runtime capabilities added.
- No personal-data tools enabled by default.
- No policy, approval, audit, or ToolBroker weakening.
