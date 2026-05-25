from __future__ import annotations

from dataclasses import dataclass


DEFAULT_ROBOTS_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class RobotsRule:
    directive: str
    path: str


@dataclass(frozen=True)
class RobotsPolicy:
    source_url: str
    sitemaps: list[str]
    rules: list[RobotsRule]
    status: str = "ok"
    error: str = ""

    def allowed(self, path: str) -> bool:
        normalized = path or "/"
        matches = [rule for rule in self.rules if rule.path and normalized.startswith(rule.path)]
        if not matches:
            return True
        strongest = max(matches, key=lambda rule: (len(rule.path), 1 if rule.directive == "allow" else 0))
        return strongest.directive == "allow"

    def to_dict(self, *, checked_path: str | None = None) -> dict[str, object]:
        payload: dict[str, object] = {
            "status": self.status,
            "source_url": self.source_url,
            "sitemaps": self.sitemaps,
            "rules": [{"directive": rule.directive, "path": rule.path} for rule in self.rules],
        }
        if checked_path is not None:
            payload["checked_path"] = checked_path or "/"
            payload["allowed"] = self.allowed(checked_path)
        if self.error:
            payload["error"] = self.error
        return payload


def parse_robots_txt(text: str, *, user_agent: str = "LocalMacAIAgent") -> tuple[list[RobotsRule], list[str]]:
    active_applies = False
    current_agents: list[str] = []
    rules: list[RobotsRule] = []
    sitemaps: list[str] = []
    normalized_agent = user_agent.casefold()
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().casefold()
        value = value.strip()
        if key == "user-agent":
            if not current_agents or rules:
                current_agents = []
            current_agents.append(value.casefold())
            active_applies = "*" in current_agents or normalized_agent in current_agents
            continue
        if key == "sitemap" and value:
            sitemaps.append(value)
            continue
        if key in {"allow", "disallow"} and active_applies:
            if key == "disallow" and value == "":
                continue
            rules.append(RobotsRule("allow" if key == "allow" else "disallow", value or "/"))
    return rules, sitemaps
