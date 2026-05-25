# Release Blockers

Date: 2026-05-25

Prompt: `RELEASE-HARDENING-LOOP-V2`

## P0 Security / Safety

None confirmed in this hardening pass.

Notes:

- Startup policy validation passed.
- Capability manifest validation passed.
- CRITICAL capabilities require per-action approval and no approval reuse.
- Personal-data connectors remain disabled by default.
- No confirmed enabled CAPTCHA, anti-bot, login-wall, private database, send/write, or audit/policy bypass was found.

## P1 Broken Core Flow

None confirmed after hardening.

Notes:

- Full pytest passed.
- Command registry validation passed.
- Safe eval passed.
- Synthetic setup command bug records are fixed with concrete regressions.

## P2 Broken Feature / Release Boundary

| Blocker | Evidence | Required Fix |
|---|---|---|
| Large dirty working tree prevents a clean release boundary | `git status --short` shows broad modified/untracked code, docs, tests, prompts, dogfood, eval, and workspace files. Generated workspace artifact hygiene is now documented in `docs/release/GENERATED_ARTIFACT_HYGIENE.md` and covered by narrow `.gitignore` rules, but the source/diff boundary still needs human review. | Create a release candidate branch or reviewed commit series; review source changes separately from ignored generated/local artifacts |
| Live/manual validation is incomplete for the breadth of implemented capabilities | Quality dashboard still lists live-validation gaps for LM Studio, provider policy, search providers, web fetch/research/cache, and other configured providers | Run opt-in live provider checks and a full safe dogfood session before release |
| Direct network/subprocess primitives require continued broker-path review | Static scan found expected provider/tool/test primitives | Add a documented static guard or allowlist so future changes cannot introduce hidden bypasses |

## P3 UX / Docs Issue

| Issue | Evidence | Required Fix |
|---|---|---|
| Manual QA evidence is thinner than the command surface | Registry validates 382 commands, but live/manual QA remains uneven | Prioritize command QA by risk and mark manual QA status conservatively |
| Release docs were missing before this pass | `docs/release/` did not contain readiness/blocker/plan artifacts | Keep release docs updated for each future hardening loop |
| First-run diagnostics should keep improving | Setup command is now tested, but provider setup paths remain broad | Continue provider-specific setup smoke tests |

## P4 Polish

| Issue | Evidence | Required Fix |
|---|---|---|
| `commands list | head` can surface `BrokenPipeError` when stdout closes early | Observed during command inspection | Catch `BrokenPipeError` or avoid noisy traceback on closed stdout |
| Generated workspace artifact hygiene needs ongoing verification | `workspace/eval/`, local lead records, messaging drafts, iOS compose payloads/results, and Reddit thread exports are generated local data. Narrow ignore rules and `docs/release/GENERATED_ARTIFACT_HYGIENE.md` now classify them. | Keep `tests/test_release_artifact_hygiene.py` green; review ignored generated outputs before release candidate packaging |
| Large docs need navigation help | Changelog and command registry are comprehensive but hard to scan | Add indexes or split generated views when practical |
