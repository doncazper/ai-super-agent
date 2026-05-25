# Skill Provenance

Native skill provenance records where a skill came from, who reviewed it, whether it is trusted, and what caveats remain.

Tracked fields include source type/path/URL/pack ID, author, license, version, file hash, review status, trust level/status, install status, pin status, last update, known risks, and caveats.

Allowed source types include:

- `native`
- `bundled`
- `local`
- `external`
- `clawhub_candidate`
- `reconstructed`
- `imported`
- `unknown`

Unreviewed external and candidate skills are not trusted by default. Reconstructed skills must remain clearly labeled and must not be claimed as exact originals without evidence.

```bash
python smart_agent.py skills provenance native_skill_vetter
python smart_agent.py skills trust native_skill_vetter
```

These commands read metadata only. They do not install, update, execute, or enable skills.
