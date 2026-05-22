from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class LMStudioConfig:
    base_url: str = "http://localhost:1234/v1"
    model: str = ""
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 2048
    timeout_seconds: float = 120.0

    @classmethod
    def from_env(cls) -> "LMStudioConfig":
        return cls(
            base_url=os.getenv("LMSTUDIO_BASE_URL", cls.base_url).rstrip("/"),
            model=os.getenv("LMSTUDIO_MODEL", ""),
            temperature=float(os.getenv("LMSTUDIO_TEMPERATURE", cls.temperature)),
            top_p=float(os.getenv("LMSTUDIO_TOP_P", cls.top_p)),
            max_tokens=int(os.getenv("LMSTUDIO_MAX_TOKENS", cls.max_tokens)),
        )


class LMStudioClient:
    def __init__(self, config: LMStudioConfig) -> None:
        if not config.model:
            raise ValueError("LMSTUDIO_MODEL is required")
        self.config = config

    def build_payload(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_tokens": self.config.max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        return payload

    def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload = self.build_payload(messages, tools=tools)
        with httpx.Client(timeout=self.config.timeout_seconds) as client:
            response = client.post(f"{self.config.base_url}/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()
