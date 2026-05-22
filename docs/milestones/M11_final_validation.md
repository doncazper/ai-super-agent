# M11 Final Validation

## Scope

Test the system like it will be attacked or make mistakes.

## Non-Goals

No new feature development except fixes needed to pass release gates.

## Requirements

- Unit tests.
- Integration tests.
- Policy bypass tests.
- Prompt-injection tests.
- Personal-data access tests.
- Web-content trust tests.
- Write-action approval tests.
- Self-improvement safety tests.
- Performance tests.
- Recovery/rollback tests.

## Required Checks

- Normal chat attaches no tools.
- Unknown tool denied.
- Tool cannot bypass broker.
- Path traversal blocked.
- Denied paths blocked.
- Webpage instructions not followed.
- Email send requires approval.
- Text send requires approval.
- Calendar write requires approval.
- Contact edit requires approval.
- Memory refuses secrets.
- Self-improvement cannot edit policy to reduce restrictions.
- Audit log records denials and executions.

## Approval Gate

Release approval.
