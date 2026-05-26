from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from agent.media.licenses import provider_license_records
from agent.media.models import MediaSafetyReview
from agent.media.redaction import prompt_hash, redact_media_prompt


class MediaSafetyCategory(StrEnum):
    SAFE_GENERAL = "safe_general"
    COMMERCIAL_USE_UNCLEAR = "commercial_use_unclear"
    COPYRIGHTED_CHARACTER_OR_BRAND = "copyrighted_character_or_brand"
    LIVING_PERSON_LIKENESS = "living_person_likeness"
    PRIVATE_PERSON_LIKENESS = "private_person_likeness"
    CELEBRITY_LIKENESS = "celebrity_likeness"
    VOICE_CLONE = "voice_clone"
    IMPERSONATION = "impersonation"
    SEXUAL_CONTENT = "sexual_content"
    GRAPHIC_VIOLENCE = "graphic_violence"
    EXTREMIST_OR_HATE = "extremist_or_hate"
    ILLEGAL_INSTRUCTIONAL_CONTENT = "illegal_instructional_content"
    MEDICAL_LEGAL_FINANCIAL_CLAIM_RISK = "medical/legal/financial claim risk"
    POLITICAL_PERSUASION_RISK = "political persuasion risk"
    PRIVACY_SENSITIVE_INPUT = "privacy_sensitive_input"
    UNKNOWN_RISK = "unknown_risk"


class MediaSafetyOutcome(StrEnum):
    ALLOW = "allow"
    WARN = "warn"
    REQUIRE_LICENSE_REVIEW = "require_license_review"
    REQUIRE_CONSENT = "require_consent"
    REQUIRE_HUMAN_REVIEW = "require_human_review"
    DENY = "deny"


@dataclass(frozen=True)
class MediaSafetyFinding:
    category: MediaSafetyCategory
    outcome: MediaSafetyOutcome
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "category": self.category.value,
            "outcome": self.outcome.value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class MediaPromptSafetyResult:
    status: str
    outcome: MediaSafetyOutcome
    categories: tuple[MediaSafetyCategory, ...]
    findings: tuple[MediaSafetyFinding, ...]
    prompt_hash: str
    prompt_redacted: str
    deterministic: bool
    external_calls: bool
    generation_allowed: bool
    safety_review: MediaSafetyReview
    license_review_required: bool
    consent_required: bool
    human_review_required: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "outcome": self.outcome.value,
            "categories": [category.value for category in self.categories],
            "findings": [finding.to_dict() for finding in self.findings],
            "prompt_hash": self.prompt_hash,
            "prompt_redacted": self.prompt_redacted,
            "deterministic": self.deterministic,
            "external_calls": self.external_calls,
            "generation_allowed": self.generation_allowed,
            "safety_review": self.safety_review.to_dict(),
            "license_review_required": self.license_review_required,
            "consent_required": self.consent_required,
            "human_review_required": self.human_review_required,
        }


DENY_KEYWORDS = {
    MediaSafetyCategory.SEXUAL_CONTENT: ("explicit sexual", "porn", "nude minor", "sexualized child"),
    MediaSafetyCategory.GRAPHIC_VIOLENCE: ("gore", "graphic violence", "dismember", "bloody corpse"),
    MediaSafetyCategory.EXTREMIST_OR_HATE: ("nazi propaganda", "terrorist propaganda", "racial hatred", "ethnic cleansing"),
    MediaSafetyCategory.ILLEGAL_INSTRUCTIONAL_CONTENT: ("make a bomb", "counterfeit money", "forge passport", "bypass security"),
}
COPYRIGHT_MARKERS = ("mickey mouse", "pikachu", "marvel", "disney", "star wars", "pokemon", "batman")
CELEBRITY_MARKERS = ("taylor swift", "beyonce", "elon musk", "donald trump", "joe biden", "zendaya")
PRIVATE_PERSON_MARKERS = ("my coworker", "my boss", "my ex", "my neighbor", "a private person")
VOICE_MARKERS = ("clone voice", "voice clone", "sound exactly like", "imitate the voice", "deepfake voice")
IMPERSONATION_MARKERS = ("make it look like they said", "fake endorsement", "impersonate", "deepfake")
PRIVACY_INPUT_MARKERS = ("from my private photo", "from my camera roll", "from this private video", "without their permission")
COMMERCIAL_MARKERS = ("commercial use", "for an ad", "brand ad", "advertisement", "sell this", "client campaign")
MEDICAL_LEGAL_FINANCIAL_MARKERS = ("medical claim", "legal claim", "financial advice", "investment return", "cure")
POLITICAL_MARKERS = ("persuade voters", "political ad", "campaign propaganda", "target voters")


def check_media_prompt_safety(
    prompt: str,
    *,
    provider_id: str = "mock",
    commercial_use: bool = False,
) -> MediaPromptSafetyResult:
    text = prompt.lower()
    findings: list[MediaSafetyFinding] = []

    for category, keywords in DENY_KEYWORDS.items():
        if _contains_any(text, keywords):
            findings.append(MediaSafetyFinding(category, MediaSafetyOutcome.DENY, f"Prompt matched {category.value} deny markers."))

    if _contains_any(text, VOICE_MARKERS):
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.VOICE_CLONE,
                MediaSafetyOutcome.DENY,
                "Voice cloning is denied/deferred until an explicit consent workflow exists.",
            )
        )
    if _contains_any(text, IMPERSONATION_MARKERS):
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.IMPERSONATION,
                MediaSafetyOutcome.DENY,
                "Impersonation or fake endorsement workflows are denied.",
            )
        )
    if _contains_any(text, CELEBRITY_MARKERS):
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.CELEBRITY_LIKENESS,
                MediaSafetyOutcome.REQUIRE_CONSENT,
                "Celebrity/living-person likeness requires consent and human review.",
            )
        )
    if _contains_any(text, PRIVATE_PERSON_MARKERS):
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.PRIVATE_PERSON_LIKENESS,
                MediaSafetyOutcome.REQUIRE_CONSENT,
                "Private-person likeness requires explicit consent and human review.",
            )
        )
    if "real person" in text or "living person" in text:
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.LIVING_PERSON_LIKENESS,
                MediaSafetyOutcome.REQUIRE_CONSENT,
                "Living-person likeness requires consent and review.",
            )
        )
    if _contains_any(text, COPYRIGHT_MARKERS):
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.COPYRIGHTED_CHARACTER_OR_BRAND,
                MediaSafetyOutcome.REQUIRE_LICENSE_REVIEW,
                "Copyrighted character, franchise, or brand reference requires license review.",
            )
        )
    if commercial_use or _contains_any(text, COMMERCIAL_MARKERS) or _provider_license_unclear(provider_id):
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.COMMERCIAL_USE_UNCLEAR,
                MediaSafetyOutcome.REQUIRE_LICENSE_REVIEW,
                "Commercial/provider license status is unclear and requires review.",
            )
        )
    if _contains_any(text, PRIVACY_INPUT_MARKERS):
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.PRIVACY_SENSITIVE_INPUT,
                MediaSafetyOutcome.REQUIRE_HUMAN_REVIEW,
                "Private or personal input media requires explicit tagging and later approval.",
            )
        )
    if _contains_any(text, MEDICAL_LEGAL_FINANCIAL_MARKERS):
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.MEDICAL_LEGAL_FINANCIAL_CLAIM_RISK,
                MediaSafetyOutcome.WARN,
                "Medical, legal, or financial claims need caveats and cannot be represented as authoritative.",
            )
        )
    if _contains_any(text, POLITICAL_MARKERS):
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.POLITICAL_PERSUASION_RISK,
                MediaSafetyOutcome.REQUIRE_HUMAN_REVIEW,
                "Political persuasion or targeted campaign material requires human review.",
            )
        )

    if not findings:
        findings.append(
            MediaSafetyFinding(
                MediaSafetyCategory.SAFE_GENERAL,
                MediaSafetyOutcome.ALLOW,
                "No deterministic safety, consent, or license risk markers matched.",
            )
        )

    outcome = _highest_outcome(finding.outcome for finding in findings)
    categories = tuple(dict.fromkeys(finding.category for finding in findings))
    blocked = outcome is MediaSafetyOutcome.DENY
    return MediaPromptSafetyResult(
        status="ok",
        outcome=outcome,
        categories=categories,
        findings=tuple(findings),
        prompt_hash=prompt_hash(prompt),
        prompt_redacted=redact_media_prompt(prompt),
        deterministic=True,
        external_calls=False,
        generation_allowed=outcome is MediaSafetyOutcome.ALLOW,
        safety_review=MediaSafetyReview(
            status=outcome.value,
            blocked=blocked,
            reasons=tuple(finding.reason for finding in findings if finding.outcome is not MediaSafetyOutcome.ALLOW),
            warnings=tuple(finding.reason for finding in findings if finding.outcome is MediaSafetyOutcome.WARN),
            reviewer="deterministic_media_safety_v1",
        ),
        license_review_required=any(finding.outcome is MediaSafetyOutcome.REQUIRE_LICENSE_REVIEW for finding in findings),
        consent_required=any(finding.outcome is MediaSafetyOutcome.REQUIRE_CONSENT for finding in findings),
        human_review_required=any(finding.outcome is MediaSafetyOutcome.REQUIRE_HUMAN_REVIEW for finding in findings),
    )


def build_consent_policy() -> dict[str, Any]:
    return {
        "status": "ok",
        "consent_workflow_implemented": False,
        "voice_cloning_allowed": False,
        "real_person_likeness_allowed_by_default": False,
        "private_person_likeness_allowed_by_default": False,
        "requires_human_review": True,
        "rules": [
            "Voice cloning is denied/deferred until an explicit consent workflow exists.",
            "Living-person and private-person likeness requests require consent and human review.",
            "The agent must not infer consent from a prompt alone.",
            "Consent evidence must be recorded in future asset metadata before generation is allowed.",
            "This policy is operational safety guidance, not legal advice.",
        ],
    }


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def _provider_license_unclear(provider_id: str) -> bool:
    for record in provider_license_records():
        if record.provider_id == provider_id:
            return record.status in {"requires_review", "blocked"}
    return True


def _highest_outcome(outcomes: object) -> MediaSafetyOutcome:
    order = {
        MediaSafetyOutcome.ALLOW: 0,
        MediaSafetyOutcome.WARN: 1,
        MediaSafetyOutcome.REQUIRE_LICENSE_REVIEW: 2,
        MediaSafetyOutcome.REQUIRE_CONSENT: 3,
        MediaSafetyOutcome.REQUIRE_HUMAN_REVIEW: 4,
        MediaSafetyOutcome.DENY: 5,
    }
    return max(tuple(outcomes), key=lambda outcome: order[outcome])
