# Skill Allowlists

Skill allowlists decide visibility for a profile. They do not enable execution.

Rules:

- Blocked skill IDs override allowed skill IDs.
- Blocked categories override allowed categories.
- Risk ceilings hide skills above the profile limit.
- Personal-data skills are hidden unless the profile explicitly allows personal data and the capability policy also allows the relevant capability.
- `CRITICAL` skills are hidden unless the profile explicitly allows critical actions and the skill still requires approval.
- Network-facing skills are hidden unless the profile allows network behavior.
- Write-capable skills are hidden unless the profile allows writes.
- The experimental profile is disabled by default.

Visibility output includes both visible and hidden skills with reasons. A visible result means only that the profile may show the skill to the user. It does not grant tools, change capability defaults, bypass approval, or mark a skill safe to run.

Use:

```bash
python smart_agent.py skills profile allowed research
python smart_agent.py skills profile validate locked_down
```

When a profile and policy disagree, report the disagreement and keep execution denied. The policy engine wins.
