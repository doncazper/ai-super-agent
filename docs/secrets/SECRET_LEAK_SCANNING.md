# Secret Leak Scanning

Status: best-effort local scanner.

The secret leak scanner is a pre-commit/pre-push guardrail for tracked files and staged diffs. It is not a replacement for GitHub secret scanning, provider-side revocation, or dedicated scanners such as gitleaks/trufflehog.

## Commands

```bash
python smart_agent.py secrets scan
python smart_agent.py secrets scan --staged
```

The scanner checks for:

- tracked `.env` files;
- tracked token, credential, client-secret, private-key, and key-like file paths;
- private key block markers;
- common provider token formats;
- key/value assignments such as `API_KEY=...`, `TOKEN=...`, and `CLIENT_SECRET=...`.

## Safety Behavior

- Findings include path, line number when available, type, severity, and a redacted sample.
- Raw values are never printed.
- Obvious placeholders and test fixtures are treated as non-blocking where practical.
- A likely real secret returns structured `status=fail` and a non-zero CLI exit.
- Staged scans inspect added diff lines only.

## Limits

This scanner is intentionally conservative and dependency-free. It can miss provider-specific secrets and can still report false positives. If a likely real secret is found in tracked history, stop and rotate/revoke the secret before committing or pushing.
