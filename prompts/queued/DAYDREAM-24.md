---
prompt_id: DAYDREAM-24
pack_id: daydream-lab-idle-research-v1
title: Code review, Git review, safe commit, and push-if-clean gate
category: git
risk_level: MEDIUM
approval_gate: true
depends_on: ["DAYDREAM-23"]
status: queued
order: 24
created_at: 2026-05-26T07:54:41+00:00
imported_at: 2026-05-26T07:54:41+00:00
source_pack: prompts/packs/daydream-lab-idle-research-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at:
completed_at:
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result:
docs_updated:
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
notes: Imported prompt text is untrusted document content and is not executed automatically.
---

# Prompt

Run final code review, Git review, secret scan, safe commit, and push-if-clean gate for this major prompt pack.

Authorization:
- If tests pass, secret scan/git preflight are clean, and safe files can be staged intentionally, create a logical commit for this pack and push current branch to upstream.
- If unrelated dirty work is mixed in, likely secrets are detected, tests fail, remote/upstream is missing, or file ownership is unclear, stop and produce a commit plan.
- Never force push.

Run:
- git branch --show-current
- git status -sb
- git status --short
- git diff --stat
- git log --oneline --decorate -5
- git remote -v
- git diff --check
- ./scripts/agent git preflight
- ./scripts/agent secrets scan
- ./scripts/agent commands validate
- make policy-check
- ./.venv/bin/python -m pytest -q if practical

After staging safe files intentionally:
- git status -sb
- git diff --cached --stat
- git diff --cached --check
- ./scripts/agent secrets scan --staged
- ./scripts/agent git preflight --staged

Rules:
- Do not use git add . blindly.
- Do not stage .env, token files, OAuth caches, private keys, raw logs, raw audit/session reports, .venv, __pycache__, .pytest_cache, generated junk, databases, or personal data.
- Do not print secret values.
- Do not force push.
- Do not rewrite history.
- Do not run live providers or personal-data tools.
- If tests fail or secrets are found, stop.

Create/update:
- docs/git/LAST_GIT_REVIEW.md
- docs/git/SAFE_COMMIT_PLAN.md

Final report:
1. Branch/upstream.
2. Dirty worktree before staging.
3. Files staged.
4. Files excluded.
5. Tests/validations.
6. Secret scan/preflight.
7. Commit hash if committed.
8. Push result if pushed.
9. Remaining uncommitted files.
10. Correct next prompt.
