# M10 UX and Packaging

## Scope

Make the agent usable, inspectable, and configurable.

## Non-Goals

No hidden privacy controls or buried approvals.

## Requirements

- Interactive CLI.
- Approval prompt UI.
- Audit viewer.
- Permission dashboard.
- Config viewer.
- Memory viewer.
- Tool list command.
- Setup wizard.
- Optional local web dashboard.
- Packaging docs.

## Risks

- Users misunderstand risk.
- Approvals become too easy to click through.
- Configuration hides dangerous defaults.

## Tests

- CLI commands work.
- Approval prompt blocks critical action until approved.
- Audit viewer displays entries.
- Permission grant/revoke works.
- Config validator rejects dangerous config.

## Approval Gate

None beyond included tools.
