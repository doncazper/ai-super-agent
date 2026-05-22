from __future__ import annotations

import pytest

from agent.config.runtime import RuntimeConfig, RuntimeConfigError


def test_runtime_config_loads_new_env_names(monkeypatch) -> None:
    monkeypatch.setenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
    monkeypatch.setenv("LMSTUDIO_MODEL", "qwopus")
    monkeypatch.setenv("TEMPERATURE", "0.2")
    monkeypatch.setenv("TOP_P", "0.8")
    monkeypatch.setenv("MAX_TOKENS", "4096")
    monkeypatch.setenv("TOOL_MODE", "no-tools")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("AUDIT_LOG_PATH", "custom/audit.jsonl")

    config = RuntimeConfig.from_env(load_env_file=False)

    assert config.lmstudio_model == "qwopus"
    assert config.temperature == 0.2
    assert config.top_p == 0.8
    assert config.max_tokens == 4096
    assert config.tool_mode == "no-tools"
    assert config.debug is True
    assert config.audit_log_path == "custom/audit.jsonl"


def test_runtime_config_rejects_invalid_base_url(monkeypatch) -> None:
    monkeypatch.setenv("LMSTUDIO_BASE_URL", "not-a-url")

    with pytest.raises(RuntimeConfigError, match="LMSTUDIO_BASE_URL"):
        RuntimeConfig.from_env(load_env_file=False)


def test_runtime_config_rejects_invalid_tool_mode(monkeypatch) -> None:
    monkeypatch.setenv("TOOL_MODE", "everything")

    with pytest.raises(RuntimeConfigError, match="TOOL_MODE"):
        RuntimeConfig.from_env(load_env_file=False)
