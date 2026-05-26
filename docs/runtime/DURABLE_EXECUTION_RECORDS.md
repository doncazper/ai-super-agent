# Durable Execution Records

Status: CANON-02 implemented as contract/read-only scaffolding.

Durable execution records are future-facing metadata contracts for prompt runs, prompt-pack runs, jobs, workflows, commands, QA runs, self-heal runs, approval-gated resumes, media generation runs, and secret scans.

CANON-02 does not add a worker, scheduler, executor, background service, web server, or prompt runner. It defines record schemas and read-only inspection commands only.

## Record Types

- `PromptRunRecord`
- `PromptPackRunRecord`
- `JobRunRecord`
- `WorkflowRunRecord`
- `CommandRunRecord`
- `ApprovalGatedResumeRecord`
- `QARunRecord`
- `SelfHealRunRecord`
- `MediaGenerationRunRecord` future/stubbed
- `SecretScanRunRecord` future/stubbed

## Statuses

- `queued`
- `active`
- `waiting_for_approval`
- `running`
- `completed`
- `failed`
- `blocked`
- `cancelled`
- `superseded`
- `needs_review`

## Storage Policy

Future writers may store redacted metadata under `reports/runtime/records/`. They must not store raw secrets, personal data, provider payloads, raw prompt bodies, raw command output, or unredacted logs by default.

## Commands

- `python smart_agent.py runtime records list`
- `python smart_agent.py runtime records show <record_id>`
- `python smart_agent.py runtime records latest`
- `python smart_agent.py runtime records validate`

These commands are read-only and tolerate an empty record store.
