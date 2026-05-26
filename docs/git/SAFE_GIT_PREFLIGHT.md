# Safe Git Preflight

Status: local redacted preflight.

Run Git preflight before committing or pushing:

```bash
python smart_agent.py git preflight
python smart_agent.py git preflight --staged
```

The preflight command combines a redacted secret leak scan with a short Git status summary. It does not commit, push, rewrite history, stage files, install scanners, or print raw secret values.

## Pass Criteria

- No likely real secret in tracked files or staged diffs.
- No tracked `.env`.
- No tracked private key or credential file.
- Findings, if present, are redacted and classified.

If preflight fails, do not push. Remove or redact the file, update `.gitignore` where needed, rotate any exposed credential, and rerun preflight.
