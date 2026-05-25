# Model Migration Guide

This guide covers moving from Qwopus through LM Studio to another local model, hosted model, or model-router setup.

## Invariants

- The model never receives authority to execute tools directly.
- No-tools chat stays available.
- Tool requests remain structured, brokered, bounded, and audited.
- Prompt-injection text remains data, not instruction.
- Personal-data tools stay disabled by default.
- Send/write actions stay approval-gated.

## Migration Steps

1. Add a model adapter behind the existing client/router boundary.
2. Keep `--no-tools` mode working before enabling tool-call mode.
3. Run no-tool quality evals against fixture prompts.
4. Run router intent classification evals.
5. Run tool schema and argument validation evals.
6. Run policy denial and approval evals.
7. Run prompt-injection refusal evals.
8. Compare answer quality with the previous model.
9. Document model-specific limitations.
10. Keep rollback to the previous model available.

## Tool-Call Protocol Checks

- Normal chat must attach no tools unless routing requires tools.
- Tool calls must include known names and validated args.
- Unknown tools and malformed args are denied before execution.
- Tool results are passed back as data with matching call IDs.

## Prompt Contamination Checks

Test that untrusted emails, messages, web pages, documents, PDFs, lead text, and imported prompts cannot:

- approve actions
- request sends
- change risk levels
- disable audit
- grant permissions
- override system policy

## Regression Suite

Run safe evals, router evals, prompt quality evals, command registry validation, startup policy validation, capability manifest validation, and focused workflow tests for any model prompt changes.

## Rollback

Keep the old model config and prompt templates available until the new model passes release gates and a manual smoke test.
