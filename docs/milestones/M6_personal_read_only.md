# M6 Read-Only Personal Modules

## Scope

Add selected-scope personal-data access, read-only and draft-only.

## Non-Goals

No sending, deleting, calendar/contact writes, bulk export, full inbox ingestion, full message history reading, or unsafe database scraping.

## Requirements

- `contacts.search`
- `contacts.read_selected`
- `calendar.read_date_range`
- `calendar.find_availability`
- `email.list_metadata`
- `email.read_selected_thread`
- `email.summarize_thread`
- `email.draft_reply`
- `messages.read_selected_thread`
- `messages.summarize_thread`
- `messages.draft_reply`
- `browser.read_selected_tab`

## Risks

- Overbroad private-data access.
- Prompt injection from personal content.
- Accidental long-term storage.
- Pressure to request broad Full Disk Access.

## Tests

- Disabled modules denied.
- Selected contact read requires permission.
- Calendar date range read requires permission.
- Email body read requires approval.
- Draft generated without sending.
- Email/message prompt injection ignored.
- Body text not stored by default.
- Personal access audited.

## Approval Gate

Explicit user approval required before implementation.
