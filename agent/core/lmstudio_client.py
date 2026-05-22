from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

from agent.config.runtime import RuntimeConfig, RuntimeConfigError, validate_base_url


class LMStudioError(RuntimeError):
    pass


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
        runtime = RuntimeConfig.from_env()
        return cls.from_runtime(runtime)

    @classmethod
    def from_runtime(cls, runtime: RuntimeConfig) -> "LMStudioConfig":
        return cls(
            base_url=runtime.lmstudio_base_url,
            model=runtime.lmstudio_model,
            temperature=runtime.temperature,
            top_p=runtime.top_p,
            max_tokens=runtime.max_tokens,
        )


class LMStudioClient:
    def __init__(self, config: LMStudioConfig) -> None:
        if not config.model:
            raise LMStudioError("LMSTUDIO_MODEL is not set. Export LMSTUDIO_MODEL='<model id>'.")
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
        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                response = client.post(f"{self.config.base_url}/chat/completions", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.ConnectError as exc:
            raise LMStudioError(
                f"LM Studio server not reachable at {self.config.base_url}. "
                "Start LM Studio Developer Server and retry."
            ) from exc
        except httpx.TimeoutException as exc:
            raise LMStudioError(
                f"LM Studio request timed out at {self.config.base_url}. "
                "Confirm the model is loaded and retry."
            ) from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            body = exc.response.text[:500]
            raise LMStudioError(
                f"LM Studio returned HTTP {status}. Confirm model '{self.config.model}' is loaded. "
                f"Response: {body}"
            ) from exc
        except ValueError as exc:
            raise LMStudioError("LM Studio returned a malformed non-JSON response.") from exc

        if not isinstance(data, dict) or not data.get("choices"):
            raise LMStudioError("LM Studio returned a malformed response: missing choices.")
        return data
