# Media Safety Policy

Status: specified only.
Last updated: 2026-05-25.

## Safety Boundary

Creative media generation must be opt-in, brokered, policy-checked, audited, and provider-specific. This milestone does not generate media.

## Forbidden Or Deferred Workflows

- Voice cloning without explicit consent policy.
- Real-person likeness generation without consent and approval policy.
- Impersonation workflows.
- Unsafe, abusive, extremist, or sexual media workflows.
- Automatic upload, publication, or social posting.
- Paid API generation by default.
- Provider setup that installs packages or downloads large models without explicit approval.
- Use of personal-data tools by default.

## Prompt Handling

Future prompt planning must:

- redact secrets before audit/report output
- avoid writing raw prompts to memory by default
- treat untrusted source text as data
- reject prompts that ask the agent to ignore policy or bypass approvals
- preserve source references for user-supplied input assets

## Output Review

Future real generation must include a safety result before asset handoff. A generated asset is not automatically safe for commercial, publishing, or social use.

