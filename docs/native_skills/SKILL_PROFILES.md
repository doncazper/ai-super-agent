# Skill Profiles

Native skill profiles describe which reviewed skills should be visible in a given agent mode. Profiles are advisory metadata only: selecting a profile does not enable a skill, grant a capability, change policy, or execute anything.

Default profiles:

| Profile | Default | Purpose |
|---|---:|---|
| `default` | yes | Conservative default for LOW/MEDIUM reviewed skills in broad safe categories. |
| `research` | yes | Web/news/forum/weather/document research visibility without personal-data writes. |
| `coding` | yes | Workspace, coding, testing, developer-tool, and docs skills without personal-data access. |
| `personal_assistant` | yes | Personal-assistant category visibility, with personal-data skills still hidden by default. |
| `lead_response` | yes | Lead drafting visibility, with sends and writes hidden by default. |
| `locked_down` | yes | No skills or SAFE-only reviewed metadata. |
| `experimental` | no | Disabled-by-default experimental profile for explicit review only. |

Profile fields:

- `profile_id`
- `name`
- `description`
- `allowed_skills`
- `blocked_skills`
- `allowed_categories`
- `blocked_categories`
- `risk_ceiling`
- `allow_personal_data`
- `allow_network`
- `allow_writes`
- `allow_critical_actions`
- `default_tools`
- `memory_policy`
- `approval_policy`
- `docs_path`

Commands:

```bash
python smart_agent.py skills profiles
python smart_agent.py skills profile show default
python smart_agent.py skills profile allowed default
python smart_agent.py skills profile validate default
```

Profiles are not a runtime permission mechanism. `ToolBroker`, `PolicyEngine`, `PermissionManager`, `ApprovalManager`, and `AuditLogger` remain the final authority for execution.
