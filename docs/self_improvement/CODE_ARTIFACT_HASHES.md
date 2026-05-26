# Code Artifact Hashes

CANON-05 adds deterministic, redacted hash evidence for code-mode and self-heal review. The hash layer is read-only: it does not patch files, run tests, create commits, push branches, install packages, start services, call live providers, or execute queued prompts.

## Hash Coverage

- Git diff hash from the current `git diff --no-ext-diff`, redacted before hashing.
- Touched file hashes from `git status --short`, recorded as path-to-SHA-256 metadata only.
- Test command output hash from caller-provided text, redacted before hashing.
- Generated report hashes for configured local reports and completion evidence.
- Approval preview hash from caller-provided text, redacted before hashing.
- Command registry snapshot hash from `docs/COMMAND_REGISTRY.md`.
- Capability manifest hash from `config/capabilities.yaml`.

## Command

```bash
python smart_agent.py improve artifact-hashes --json
```

The command prints hashes and counts only. It does not print raw diffs, test output, generated report bodies, secrets, credential values, or personal data.

## Safety Boundary

Artifact hashes are evidence, not approval. They can help reviewers confirm that the diff, command registry, capability manifest, generated reports, and approval previews stayed stable between review steps. They do not replace ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, tests, command registry validation, or human review.

