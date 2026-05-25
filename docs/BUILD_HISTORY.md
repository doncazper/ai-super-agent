# Build History

This is a human-readable reconstruction of the project build arc. It is evidence-oriented, not a claim that every historical prompt is exact.

## Origin And Motivation

The project started as a local Mac AI agent intended to chat naturally through LM Studio/Qwopus while gradually gaining safe local capabilities.

## LM Studio And Qwopus Harness

The earliest stable behavior was no-tool chat with a local OpenAI-compatible LM Studio server. The project preserved a clean no-tool path so ordinary chat does not accidentally attach tools.

## Safety Foundation

The control plane came first: `ToolBroker`, `PolicyEngine`, `PermissionManager`, `ApprovalManager`, `AuditLogger`, redaction, capability manifests, dry-run/preflight, and conservative defaults.

## M0-M11 Baseline

Baseline milestones established chat, routing, tool result plumbing, time tool, audit logging, approval lifecycle, workspace file boundaries, memory, and release-gate tests.

## Weather Connector Pattern

Weather became the pattern for a useful external connector: free-first providers, audit, cache, no system-location inference, no memory writes, and provider fallback docs.

## Web And Internet Access

Web search/fetch/research evolved toward source-grounded, untrusted-content-aware, free-first acquisition with robots/sitemap/feed/direct URL handling and paid providers disabled by default.

## News Intelligence

News-like workflows were planned and partially represented through web/research/eval patterns. Claims should be verified against code, tests, command registry, and completion evidence before reuse.

## Reddit And Forum Intelligence

Forum-style acquisition is a planned or reconstructed track unless concrete commands/tests prove otherwise. It remains subject to untrusted-content and provider-policy rules.

## Native Skills

Native skills were defined as reviewed local workflow metadata mapped to existing ToolBroker capabilities, not unreviewed external scripts. The program added intake, criteria, risk model, marketplace survey, vetter, manifest loader, finder, and PDF workspace skill.

## Prompt Tracker And PromptOps

Prompt ledger, queue, audit, prompt pack import, status CLI, evidence audit, recovery, and workbench flows were added to prevent missed prompts and make large batch runs resumable.

## Command Registry And Manual QA

The command registry and test matrix became the durable CLI source of truth. Manual dogfood suites, session logging, feedback, session review, bug generation, regression stubs, and quality dashboard created a real practice loop.

## Apple Messaging And Lead Response

Apple and lead-response work introduced a docs-first roadmap, message channel abstraction, message safety Action Center integration, iOS user-confirmed compose bridge, and Lead Inbox abstraction. Silent sends, private Messages database scraping, and broad Full Disk Access remain out of scope.

## Cross-Platform App Bridge

Runtime orchestration and bridge planning established a control-plane-first approach for future app shells: metadata, status, event bus, workflow runner, job queue, scheduler policy, and frontend contracts without background persistence.

## User Guide And Docs Automation

Project docs became part of the product: project state, changelog, completion report, feature registry, maturity, command registry, prompt tracking, risk register, threat model, and release checklist are maintained as source-of-truth.

## Release Hardening

Repeated release gates verify tests, startup policy, capability manifest, safe evals, command registry, prompt audit, ToolBroker paths, default personal-data state, and HIGH/CRITICAL approval rules.

## Core DNA

The core DNA is safety-first, local-first, brokered, audited, evidence-tracked, and manually recoverable.

## Still Experimental Or Planned

Real personal-data connectors, approved sends, provider live validation, native app shells, autonomous scheduling, and platform bridges remain conservative and gated unless specific release evidence proves readiness.
