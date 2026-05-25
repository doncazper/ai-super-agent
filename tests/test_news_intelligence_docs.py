from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


NEWS_DOCS = [
    "docs/news/NEWS_INTELLIGENCE_TRACK.md",
    "docs/news/NEWS_SOURCE_POLICY.md",
    "docs/news/NEWS_PROVIDER_STRATEGY.md",
    "docs/news/NEWS_FRESHNESS_POLICY.md",
    "docs/news/NEWS_SOURCE_GROUNDING.md",
    "docs/news/NEWS_RETENTION_POLICY.md",
    "docs/decisions/news_intelligence_architecture.md",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_news_intelligence_docs_exist_and_keep_scope_safe() -> None:
    combined = "\n".join(read(path) for path in NEWS_DOCS)

    for path in NEWS_DOCS:
        assert (ROOT / path).exists(), path

    assert "No provider API calls in this milestone" in combined
    assert "No paid API" in combined
    assert "No search-history, news-history, or full article-body storage by default" in combined
    assert "UNTRUSTED_WEB" in combined
    assert "UNTRUSTED_DOCUMENT" in combined
    assert "No CAPTCHA bypass" in combined
    assert "No login-wall bypass" in combined
    assert "No paywall bypass" in combined
    assert "No fabricated" in combined


def test_news_provider_strategy_order_is_documented() -> None:
    strategy = read("docs/news/NEWS_PROVIDER_STRATEGY.md")
    expected = [
        "1. Local news cache.",
        "2. User-provided URL.",
        "3. Configured RSS/Atom feeds.",
        "4. News sitemaps.",
        "5. GDELT.",
        "6. Media Cloud, optional/configured.",
        "7. SearXNG/Brave/SerpAPI through web provider policy.",
        "8. NewsAPI, optional/fallback only.",
        "9. Graceful unavailable response.",
    ]
    positions = [strategy.index(item) for item in expected]
    assert positions == sorted(positions)


def test_news_risk_model_and_source_grounding_are_explicit() -> None:
    decision = read("docs/decisions/news_intelligence_architecture.md")
    grounding = read("docs/news/NEWS_SOURCE_GROUNDING.md")
    freshness = read("docs/news/NEWS_FRESHNESS_POLICY.md")

    for phrase in [
        "News provider status | SAFE",
        "Public headline search | LOW",
        "Article fetch | MEDIUM",
        "Source comparison/research | MEDIUM",
        "Binary/downloaded article files | HIGH or disabled",
        "Paid provider usage | Config/approval-gated",
        "Login/paywall/CAPTCHA bypass | FORBIDDEN",
    ]:
        assert phrase in decision

    assert "Never cite a fabricated URL" in grounding
    assert "Never cite a failed fetch as supporting evidence" in grounding
    assert "Do not fabricate publication dates" in freshness


def test_news_commands_are_tracked_as_planned_not_active() -> None:
    registry = read("docs/COMMAND_REGISTRY.md")
    expected_commands = [
        "python smart_agent.py news providers",
        "python smart_agent.py news top",
        "python smart_agent.py news search \"query\"",
        "python smart_agent.py news topic \"topic\"",
        "python smart_agent.py news source \"source\"",
        "python smart_agent.py news brief \"topic\"",
        "python smart_agent.py news timeline \"topic\"",
        "python smart_agent.py news compare \"topic\"",
        "python smart_agent.py news multilingual \"topic\"",
        "python smart_agent.py news cache status",
        "python smart_agent.py news dogfood",
    ]
    for command in expected_commands:
        assert f"`{command}`" in registry

    assert "| CMD-NEWS-001 | `python smart_agent.py news providers` | News |" in registry
    assert "| planned | 1 Specified | SAFE |" in registry
    assert "not implemented; planned command" in registry


def test_news_retention_forbids_history_and_article_body_defaults() -> None:
    retention = read("docs/news/NEWS_RETENTION_POLICY.md")
    assert "must not store readable search history, news history, or full article bodies by default" in retention
    assert "Full article body text" in retention
    assert "Readable user search queries" in retention
    assert "News content is not used for model training" in retention

