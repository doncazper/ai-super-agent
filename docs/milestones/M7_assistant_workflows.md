# M7 Assistant Workflows

## Scope

Combine existing safe tools into useful workflows without new write/send capabilities.

## Non-Goals

No email/text sending, calendar/contact writes, hidden data access, or unapproved memory writes.

## Requirements

- Daily briefing.
- Email summary.
- Email draft reply.
- Text draft reply.
- Calendar availability.
- Contact lookup.
- Multilingual web research.
- Action reports for each workflow.

## Risks

- Workflow hides risky steps.
- Personal data leaks into memory.
- Untrusted content instructs actions.

## Tests

- Workflow denied when permission missing.
- Workflow asks approval for personal-data read.
- Workflow performs no writes.
- Workflow logs each step.
- Multilingual web research works on foreign-language content.

## Approval Gate

Per workflow, based on included personal-data reads.
