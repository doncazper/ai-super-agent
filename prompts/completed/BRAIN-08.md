---
prompt_id: BRAIN-08
pack_id: brain-runtime-independence-v1
title: Model health, benchmark, and quality evals
category: tests
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-07"]
status: completed
order: 8
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T16:52:13+00:00
completed_at: 2026-05-25T17:01:09+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused BRAIN-08 tests 12 passed; eval-loader regression tests 33 passed; broader brain/docs/feature-maturity/command tests 80 passed; full suite 1268 passed, 1 skipped; policy-check ok; command registry ok with 438 commands
docs_updated: docs/brain/BRAIN_EVALS.md, docs/brain/BRAIN_BENCHMARKS.md, README, CHANGELOG, command registry/test matrix, feature/project/prompt trackers
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
command_registry_updated:
completion_report_updated:
evidence_links:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes: Mock-first safe benchmark/eval/report scaffolding complete. Live provider evals remain opt-in; no paid/cloud default, model download/install/start, personal data, memory write, high-risk tool execution, default provider change, MCP enablement, listener startup, or safety bypass.
---

# Prompt

You are Codex working in this repo.

Task:
Build model health, benchmark, and quality evals.

Goal:
Compare brain providers safely using repeatable no-tool chat, tool-call compatibility, latency, error handling, and answer-quality evals.

Scope:
- Eval cases.
- Benchmark commands.
- Reports.
- Mock-first tests.
- Live provider evals opt-in.

Non-goals:
- Do not call paid/cloud providers by default.
- Do not access personal data.
- Do not run high-risk tools.
- Do not download models.
- Do not require every provider to be installed.

Create:
- agent/brain/health.py
- agent/brain/benchmark.py
- agent/brain/evals.py
- tests/brain/test_brain_health_benchmark_eval.py
- eval_cases/brain/
- reports/brain/.gitkeep
- docs/brain/BRAIN_EVALS.md
- docs/brain/BRAIN_BENCHMARKS.md

Commands:
- python smart_agent.py brain health
- python smart_agent.py brain health --provider <provider>
- python smart_agent.py brain benchmark --safe
- python smart_agent.py brain benchmark --provider <provider>
- python smart_agent.py brain eval --safe
- python smart_agent.py brain eval --provider <provider>
- python smart_agent.py brain report --last

Eval categories:
1. no-tool chat
2. no-tools mode attaches no tools
3. tool-call compatibility with mock safe tool
4. malformed tool-call handling
5. router prompt quality
6. refusal/approval-gate behavior
7. untrusted content handling
8. latency/timeouts
9. provider error handling
10. final answer quality rubric

Requirements:
1. Safe evals use mocks or no-risk prompts.
2. Live evals opt-in.
3. Personal data not used.
4. Tool calls use safe mock/time tool only.
5. Results include provider, model, latency, success/fail/skip.
6. Quality rubrics are conservative.
7. Reports saved under reports/brain.
8. Command registry updated.
9. Feature maturity updated based on evidence.

Tests:
- health report with mock providers.
- benchmark with mock provider.
- eval report generated.
- unavailable provider skipped.
- no-tools eval checks no tools.
- tool-call eval uses mock safe tool.
- no personal data.
- command registry updated.

Update docs/tracking.

Run tests/validations.

Final report:
- evals/benchmarks added
- tests run/results
- next recommended prompt
