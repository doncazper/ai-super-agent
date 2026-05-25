from __future__ import annotations

from enum import StrEnum


class SkillRootType(StrEnum):
    WORKSPACE = "workspace_skills"
    PROJECT = "project_skills"
    PERSONAL = "personal_skills"
    MANAGED = "managed_skills"
    BUNDLED_NATIVE = "bundled_native_skills"
    EXPERIMENTAL = "experimental_skills"
    RECONSTRUCTED = "reconstructed_skills"


class SkillTextTrust(StrEnum):
    UNTRUSTED_DOCUMENT = "UNTRUSTED_DOCUMENT"
    REVIEWED_METADATA = "REVIEWED_METADATA"
