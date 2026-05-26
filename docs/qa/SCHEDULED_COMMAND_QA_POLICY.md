# Scheduled Command QA Policy

Scheduled command QA is disabled by default.

Rules:

- `qa daily --dry-run` and `qa weekly --dry-run` generate plans only.
- No background jobs, timers, or recurring automations are created by this track.
- Future scheduled QA must create a reviewed Action Center item or TODO before being enabled.
- HIGH and CRITICAL command tiers are never automatic.
- Personal-data connector checks remain manual/dry-run and disabled by default.
- Maturity evidence updates only after actual reviewed runs, not after planned schedules.

