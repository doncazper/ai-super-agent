# Remote Main Reconciliation Plan

Prompt ID: `REMOTE-MAIN-RECONCILE-AND-DUPLICATE-FILE-CLEANUP-01`

## Diagnosis

- Current branch: `main`.
- Local `main`: `d3c632a Fix fake secret scanner fixtures`.
- Remote `origin/main`: `5115a76 Initial commit`.
- Upstream for local `main`: none.
- Merge-base between local `main` and `origin/main`: none.
- Remote `origin/checkpoint/large-working-tree-20260523`: deleted during `git fetch --all --prune`; local `checkpoint/large-working-tree-20260523` now tracks a gone upstream.
- Current worktree: dirty, with intentional launcher work plus cleanup/reporting updates.

## Decision

Do not automatically reconcile `main` with `origin/main`.

The histories are unrelated. A normal push from local `main` to `origin/main` would be rejected as non-fast-forward, and merging unrelated histories would create a noisy synthetic merge that does not match the user's stated goal of making this repo become the real main line.

## Safe Options

### Option A: Push a Candidate Branch First

Use this when you want GitHub to have a reviewable copy without replacing `origin/main` yet.

```bash
git push -u origin main:codex/main-candidate
```

Then review on GitHub and decide whether to make that branch the default branch or open a PR.

### Option B: Replace Remote Main After Explicit Human Approval

Use only after a clean staged secret scan, git preflight, command validation, policy check, and tests pass.

This requires an explicit future approval because it replaces unrelated remote history. Codex must not do it under the current prompt because force push is forbidden.

```bash
git push --force-with-lease origin main
```

### Option C: Keep Remote Initial Main And Merge Manually

Not recommended unless the initial remote README is intentionally meaningful. It would require an unrelated-history merge:

```bash
git merge origin/main --allow-unrelated-histories
```

This should not be done automatically because it can create confusing history and conflict with the desired main-line replacement.

## Recommendation

After this cleanup, create a clean local commit boundary first. Then either push `main` to a candidate branch for review or explicitly authorize a future main replacement gate.

Do not run AIHUB or other large prompt packs until the current dirty tree has a reviewed commit/push plan.

## 2026-05-26 Follow-Up Diagnosis

Prompt ID: `DUPLICATE-CLEANUP-GH-AUTH-GIT-BOUNDARY-01`

- `git push --dry-run` failed because local `main` has no upstream.
- `git push --dry-run origin HEAD:refs/heads/main` failed as non-fast-forward.
- `gh auth status` reports the GitHub CLI is not logged in, but this is not the blocker for normal Git push.
- The blocker remains the unrelated local/remote `main` boundary: local `main` and `origin/main` have no merge-base.

Current decision: do not commit or push automatically. A future prompt needs an explicit human remote plan before staging and committing the current dirty tree.
