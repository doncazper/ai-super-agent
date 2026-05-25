from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.dogfood.suites import list_suite_summaries
from agent.session_logs.store import SessionLogStore


DAILY_SAFE_SMOKE = [
    {
        "order": 1,
        "title": "Start session",
        "command": 'python smart_agent.py session start --name "daily-dogfood"',
        "expected": "Creates a redacted session log before any dogfood command runs.",
    },
    {
        "order": 2,
        "title": "Run core suite",
        "command": "python smart_agent.py dogfood run core --session",
        "expected": "Exercises no-tool chat, runtime doctor/status, tools list, config, and preflight.",
        "skip_if": "Skip live LM Studio commands when LMSTUDIO_MODEL is not configured.",
    },
    {
        "order": 3,
        "title": "Run weather suite if configured",
        "command": "python smart_agent.py dogfood run weather --session",
        "expected": "Exercises weather doctor/current/forecast/error handling through existing weather tools.",
        "skip_if": "Skip live provider calls when weather provider/network prerequisites are unavailable.",
    },
    {
        "order": 4,
        "title": "Run web suite if configured",
        "command": "python smart_agent.py dogfood run web --session",
        "expected": "Exercises source-grounded public web workflows when web/search providers are configured.",
        "skip_if": "Skip provider-dependent commands when web access/search provider is unavailable.",
    },
    {
        "order": 5,
        "title": "Run workspace suite",
        "command": "python smart_agent.py dogfood run workspace_files --session",
        "expected": "Exercises workspace-bounded read/write/search/patch denials with synthetic files.",
    },
    {
        "order": 6,
        "title": "Run memory suite",
        "command": "python smart_agent.py dogfood run memory --session",
        "expected": "Exercises safe synthetic memory add/search/delete/export and secret refusal.",
    },
    {
        "order": 7,
        "title": "Add feedback",
        "command": 'python smart_agent.py feedback rate --last --score 4',
        "expected": "Records at least one redacted feedback item while the session is fresh.",
    },
    {
        "order": 8,
        "title": "End session",
        "command": "python smart_agent.py session end",
        "expected": "Closes the active session before review.",
    },
    {
        "order": 9,
        "title": "Review session",
        "command": "python smart_agent.py session review --last",
        "expected": "Produces a redacted review of failures, feedback, UX friction, and suspected bugs.",
    },
    {
        "order": 10,
        "title": "Generate bugs",
        "command": "python smart_agent.py session review --last --create-bugs",
        "expected": "Creates local redacted bug records only after reviewing the session.",
    },
    {
        "order": 11,
        "title": "Pick top bug",
        "command": "python smart_agent.py bugs list",
        "expected": "Selects the highest-priority bug for regression-test generation or fix planning.",
    },
]


WEEKLY_DEEPER_CHECK = [
    {
        "order": 1,
        "title": "Run all_safe suite",
        "command": "python smart_agent.py dogfood run all_safe --session",
        "expected": "Exercises the safe cross-feature subset in one pass.",
    },
    {
        "order": 2,
        "title": "Run approval suite",
        "command": "python smart_agent.py dogfood run approvals --session",
        "expected": "Exercises preflight, denial, and approval-preview ergonomics without risky execution.",
    },
    {
        "order": 3,
        "title": "Run native skills suite",
        "command": "python smart_agent.py dogfood run native_skills --session",
        "expected": "Exercises local manifest/finder/vetter flows with synthetic fixtures only.",
    },
    {
        "order": 4,
        "title": "Run personal dry-run suite",
        "command": "python smart_agent.py dogfood run personal_dry_run --session",
        "expected": "Runs preflight-only personal connector checks without reading real personal data.",
    },
    {
        "order": 5,
        "title": "Run safe eval suite",
        "command": "python smart_agent.py eval run --safe",
        "expected": "Runs safe evals with personal-data evals skipped by default.",
    },
    {
        "order": 6,
        "title": "Review feature maturity",
        "command": "python smart_agent.py files read docs/FEATURE_MATURITY.md",
        "expected": "Reviews conservative maturity and live-validation gaps.",
    },
    {
        "order": 7,
        "title": "Update roadmap",
        "command": "manual",
        "expected": "Update roadmap/tracking docs after reviewing weekly evidence.",
    },
]


def build_dogfood_plan(*, project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    return {
        "status": "ok",
        "recommended_next": dogfood_next(project_root=root),
        "available_suites": list_suite_summaries(project_root=root),
        "daily_safe_smoke": DAILY_SAFE_SMOKE,
        "weekly_deeper_check": WEEKLY_DEEPER_CHECK,
        "rules": [
            "No real email/text sending in dogfood by default.",
            "No calendar/contact writes in dogfood by default.",
            "Personal-data dogfood must use dry-run or selected mock fixtures unless explicitly approved.",
            "Every dogfood session should create a redacted session log.",
            "Every failure should become feedback or a bug.",
            "Every bug fix should add a regression test when feasible.",
        ],
    }


def dogfood_checklist(*, project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    return {
        "status": "ok",
        "daily": DAILY_SAFE_SMOKE,
        "weekly": WEEKLY_DEEPER_CHECK,
        "docs": [
            "docs/dogfood/LIVE_TEST_RUNBOOK.md",
            "docs/dogfood/DAILY_DOGFOOD_CHECKLIST.md",
            "docs/dogfood/WEEKLY_RELEASE_CHECK.md",
        ],
        "available_suites": [suite["suite_id"] for suite in list_suite_summaries(project_root=root)],
    }


def dogfood_next(*, project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    store = SessionLogStore(project_root=root)
    last_session = store.last_session()
    maturity_notes = _dogfood_maturity_notes(root)

    if last_session is None:
        return {
            "next_type": "start_daily_session",
            "suite": "all_safe",
            "reason": "No session logs were found; start with the safe baseline dogfood session.",
            "commands": [
                'python smart_agent.py session start --name "daily-dogfood"',
                "python smart_agent.py dogfood run all_safe --session",
            ],
            "maturity_notes": maturity_notes,
        }
    if last_session.status == "active":
        return {
            "next_type": "continue_active_session",
            "session_id": last_session.session_id,
            "suite": "all_safe",
            "reason": "An active session exists; keep capturing dogfood output before review.",
            "commands": [
                "python smart_agent.py dogfood run all_safe --session",
                "python smart_agent.py feedback rate --last --score 4",
                "python smart_agent.py session end",
            ],
            "maturity_notes": maturity_notes,
        }
    if last_session.command_count == 0:
        return {
            "next_type": "run_safe_suite",
            "session_id": last_session.session_id,
            "suite": "all_safe",
            "reason": "The latest session has no commands; run the safe suite in a new session.",
            "commands": [
                'python smart_agent.py session start --name "daily-dogfood"',
                "python smart_agent.py dogfood run all_safe --session",
            ],
            "maturity_notes": maturity_notes,
        }
    if last_session.feedback_count == 0:
        return {
            "next_type": "capture_feedback",
            "session_id": last_session.session_id,
            "suite": None,
            "reason": "The latest session has commands but no feedback; add one rating or note before review.",
            "commands": ["python smart_agent.py feedback rate --last --score 4"],
            "maturity_notes": maturity_notes,
        }
    if last_session.failure_count > 0 or last_session.bug_count > 0:
        return {
            "next_type": "review_failures",
            "session_id": last_session.session_id,
            "suite": None,
            "reason": "The latest session has failures or suspected bugs; review it and create redacted bug records.",
            "commands": [
                "python smart_agent.py session review --last",
                "python smart_agent.py session review --last --create-bugs",
                "python smart_agent.py bugs list",
            ],
            "maturity_notes": maturity_notes,
        }
    return {
        "next_type": "weekly_or_targeted_check",
        "session_id": last_session.session_id,
        "suite": "approvals",
        "reason": "The latest session has feedback and no failures; run a deeper weekly suite or target the least-validated area.",
        "commands": [
            'python smart_agent.py session start --name "weekly-dogfood"',
            "python smart_agent.py dogfood run approvals --session",
            "python smart_agent.py dogfood run native_skills --session",
            "python smart_agent.py dogfood run personal_dry_run --session",
        ],
        "maturity_notes": maturity_notes,
    }


def _dogfood_maturity_notes(root: Path) -> list[str]:
    path = root / "docs" / "FEATURE_MATURITY.md"
    if not path.exists():
        return ["FEATURE_MATURITY.md not found; defaulting to all_safe."]
    text = path.read_text(encoding="utf-8")
    notes: list[str] = []
    for phrase in [
        "first real manual dogfood session still pending",
        "first real daily/weekly dogfood session still pending",
        "first real dogfood review session still pending",
        "manual dogfood feedback session still pending",
        "manual QA pending",
    ]:
        if phrase in text:
            notes.append(phrase)
    return notes[:5] or ["No dogfood-specific maturity warnings found."]
