# Approval UI Contract

Runtime orchestration does not own approval semantics.

Future approval UI surfaces must show exact previews from Action Center and must preserve:

- HIGH approval requirements;
- CRITICAL per-action approval;
- no CRITICAL approval reuse;
- approval invalidation after draft/action edits;
- audit logging of request, approval, denial, execution, and failure.

Runtime events or frontend messages cannot approve actions.

