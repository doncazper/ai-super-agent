# M3 Low-Risk Project Tools

## Scope

Add workspace-bounded file access, git status/diff/branch, and test runner.

## Non-Goals

No arbitrary shell, git push, personal-data access, or broad home-directory access.

## Requirements

- `filesystem.list`
- `filesystem.read`
- `filesystem.write`
- `filesystem.patch`
- `filesystem.delete` with approval.
- `git.status`
- `git.diff`
- `git.branch`
- `git.commit` with approval.
- `code.run_tests`.

## Risks

- Path traversal.
- Writes outside approved roots.
- Reading secrets or private macOS app folders.
- Unintended destructive operations.

## Tests

- Path traversal blocked.
- Denied paths blocked.
- Write inside workspace allowed.
- Write outside workspace denied or approval-required.
- Delete requires approval.
- Git status allowed.
- Git commit requires approval.
- Pytest command allowed with timeout.
- File writes audited.

## Approval Gate

Delete and commit actions require approval.
