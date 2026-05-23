# Browser Selected-Tab / Web Clipping Connector Decision

Date: 2026-05-22

## Connector

Browser selected-tab and web clipping v1.

## User Value

The user can intentionally pass a webpage URL into the agent, summarize it, or save a clipped copy into the project workspace without granting broad browser access.

## Data Accessed

- Explicit URLs typed by the user.
- Public page content fetched through the existing `web.fetch_url` tool.
- Workspace draft files written through `filesystem.write` when clipping.

The connector does not access browser history, cookies, sessions, password managers, autofill data, bookmarks, private browser profile databases, screenshots, tabs, or form contents.

## Actions Possible

- Read an explicit URL as `UNTRUSTED_WEB`.
- Summarize an explicit URL as source-grounded untrusted data.
- Clip an explicit URL to `./workspace` as `UNTRUSTED_DOCUMENT`.
- Return setup notes for selected-tab integration.

## Read Capabilities

- `browser.read_selected_url`
- `browser.summarize_selected_url`
- `browser.read_selected_tab`, stubbed and disabled by default.

## Write Capabilities

- `browser.clip_url_to_workspace`, workspace-only.

No browser writes, form submissions, downloads, profile edits, or browser automation are implemented.

## Risk Level

- Explicit URL read/summarize: `MEDIUM`, because network content is untrusted and current.
- URL clipping: `MEDIUM`, because it writes untrusted document content into the approved workspace.
- Native selected-tab read: `HIGH`, disabled by default, because it could expose local private browsing context.

## Trust Level

- Fetched page content: `UNTRUSTED_WEB`.
- Stored clips: `UNTRUSTED_DOCUMENT`.
- Future selected-tab content: `LOCAL_PRIVATE_DATA` until the selected scope and source are proven safe.

## Permissions Required

V1 URL workflows require no browser permissions. They require only existing web access and workspace write permissions.

Future selected-tab support would require selected-scope approval and a narrowly permissioned integration that does not expose history, cookies, profiles, or passwords.

## Credentials / Secrets Needed

None.

## Storage Behavior

No search or URL history is stored in memory by default. Clips are saved only under `./workspace` through `filesystem.write`.

## Memory Behavior

No memory writes by default. Clipped content remains a workspace document and is labeled `UNTRUSTED_DOCUMENT`.

## Audit Requirements

- `web.fetch_url` audits network domains.
- `filesystem.write` audits files written.
- The selected-tab stub audits a denied/disabled `browser.read_selected_tab` attempt.

## Approval Requirements

V1 explicit URL read/summarize uses the existing `web.fetch_url` policy. Workspace clipping uses the existing `filesystem.write` policy and approved workspace guard.

Native selected-tab reading remains disabled by default and would require HIGH-risk selected-scope approval.

## Failure Modes

- Web access disabled.
- Blocked or private domain.
- Timeout or malformed page.
- Binary download rejected.
- Workspace write denied.
- Selected-tab integration unavailable.

## Rollback Options

Workspace clips can be removed manually or by future approved file deletion. No browser state is changed in v1.

## Implementation Options

1. URL-only workflow using `web.fetch_url` and `filesystem.write`.
2. Native selected-tab bridge with selected-scope permission.
3. Browser automation through Accessibility or profile scraping.

## Recommended Option

Use option 1 for v1. It gives useful clipping and summarization without browser profile access or automation risk.

## Alternatives Rejected

- Browser history import: overbroad and unnecessary.
- Cookie/session scraping: unsafe and likely privacy-invasive.
- Password manager access: forbidden.
- Browser profile database scraping: unsafe and unnecessary.
- Automatic form submission: out of scope and high risk.
- Accessibility automation to inspect tabs: deferred until there is a reviewed permission model.

## Tests Required

- URL summarize uses `web.fetch_url` through `ToolBroker`.
- Blocked domains are denied.
- Prompt injection is ignored in summaries.
- Clips write only inside `./workspace`.
- Browser history and cookies are not accessed.
- Selected-tab stub returns clear setup notes.
- Audit logs fetch and clip operations.
