# Blocked Source Policy

Blocked sources are handled by stopping and explaining the limitation. The agent must not try to work around access controls.

## Blocked Conditions

| Condition | Required response |
|---|---|
| robots.txt disallows fetch | Return blocked or flagged according to the command semantics; do not fetch disallowed content. |
| CAPTCHA or anti-bot page | Return unavailable with `bypass_attempted=false`. |
| Cloudflare or similar challenge | Return unavailable; do not evade. |
| Login wall or private account page | Return unavailable unless the user provides accessible exported text inside the workspace. |
| HTTP 401/403 | Return unavailable/denied with status metadata. |
| Paywall | Return unavailable or cite only accessible metadata; do not bypass. |
| Binary file | Treat as HIGH risk or disabled by default unless a future binary policy approves it. |
| Private/local network target | Deny unless a future explicit local-network policy approves it. |

## Forbidden Workarounds

- CAPTCHA solving.
- Browser-profile cookie use.
- Session-token reuse.
- Proxy rotation.
- User-agent impersonation for access evasion.
- Login automation.
- Screenshot or OCR extraction to bypass access controls.
- Asking the user to disable security controls as a normal path.

## User-Provided Alternatives

The user may provide exported text, a public URL, a document inside the approved workspace, or a citation. That supplied content is still treated as `UNTRUSTED_DOCUMENT` or `UNTRUSTED_WEB` unless clearly authored by the user.

## Audit Expectations

Blocked-source events should record:

- Domain or normalized URL.
- Block reason.
- Provider path attempted.
- Whether any network request occurred.
- `bypass_attempted=false`.
- Redacted query/source metadata.
