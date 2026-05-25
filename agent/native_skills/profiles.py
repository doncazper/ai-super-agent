from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SkillProfile:
    profile_id: str
    name: str
    description: str
    allowed_skills: list[str] = field(default_factory=list)
    blocked_skills: list[str] = field(default_factory=list)
    allowed_categories: list[str] = field(default_factory=list)
    blocked_categories: list[str] = field(default_factory=list)
    risk_ceiling: str = "MEDIUM"
    allow_personal_data: bool = False
    allow_network: bool = False
    allow_writes: bool = False
    allow_critical_actions: bool = False
    default_tools: list[str] = field(default_factory=list)
    memory_policy: str = "no_store"
    approval_policy: str = "policy_engine_final"
    docs_path: str = "docs/native_skills/SKILL_PROFILES.md"
    enabled_by_default: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_skill_profiles() -> list[SkillProfile]:
    return [
        SkillProfile(
            profile_id="default",
            name="Default",
            description="Conservative default profile for broadly safe native skills.",
            allowed_categories=["documents", "research", "coding", "testing", "security", "developer tools"],
            risk_ceiling="MEDIUM",
            allow_network=False,
        ),
        SkillProfile(
            profile_id="research",
            name="Research",
            description="Research-oriented profile for web/news/forum/weather/document skills without personal-data writes.",
            allowed_categories=["research", "browser/web", "documents", "weather", "forums", "news", "security"],
            risk_ceiling="MEDIUM",
            allow_network=True,
        ),
        SkillProfile(
            profile_id="coding",
            name="Coding",
            description="Coding profile for workspace/code/test/git/documentation skills without personal-data access.",
            allowed_categories=["coding", "testing", "developer tools", "documents", "security"],
            risk_ceiling="MEDIUM",
            allow_writes=False,
        ),
        SkillProfile(
            profile_id="personal_assistant",
            name="Personal Assistant",
            description="Personal-assistant profile; personal-data skills remain hidden unless separately enabled by profile and policy.",
            allowed_categories=["productivity", "calendar/scheduling", "communications", "documents", "security"],
            risk_ceiling="MEDIUM",
            allow_personal_data=False,
        ),
        SkillProfile(
            profile_id="lead_response",
            name="Lead Response",
            description="Lead response drafting profile; sends and personal-data writes are not visible by default.",
            allowed_categories=["communications", "lead_response", "productivity", "security"],
            risk_ceiling="MEDIUM",
            allow_personal_data=False,
            allow_writes=False,
        ),
        SkillProfile(
            profile_id="locked_down",
            name="Locked Down",
            description="Locked-down profile for no skills or SAFE-only reviewed metadata.",
            allowed_categories=[],
            risk_ceiling="SAFE",
            allow_network=False,
            allow_writes=False,
        ),
        SkillProfile(
            profile_id="experimental",
            name="Experimental",
            description="Disabled-by-default profile for experimental skills under explicit review only.",
            allowed_categories=["experimental"],
            risk_ceiling="LOW",
            enabled_by_default=False,
        ),
    ]


def profile_by_id(profile_id: str) -> SkillProfile | None:
    for profile in default_skill_profiles():
        if profile.profile_id == profile_id:
            return profile
    return None
