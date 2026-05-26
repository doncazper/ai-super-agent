from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from agent.config.runtime import env_bool, parse_float, parse_int


DEFAULT_PROVIDER_ORDER = ("lmstudio", "llama_cpp_server", "ollama", "llama_cpp_inprocess", "mlx")


@dataclass(frozen=True)
class BrainRuntimeConfig:
    default_provider: str = "lmstudio"
    provider_order: tuple[str, ...] = DEFAULT_PROVIDER_ORDER
    task_provider_map: Mapping[str, str] | None = None
    fallback_enabled: bool = False
    require_tool_call_support_for_tools: bool = True
    auto_switch_on_failure: bool = False
    max_fallback_attempts: int = 1
    allow_cloud_fallback: bool = False
    provider_health_timeout_seconds: float = 5.0
    mock_provider_enabled: bool = False
    llama_cpp_server_enabled: bool = False
    llama_cpp_server_base_url: str = "http://localhost:8080/v1"
    llama_cpp_server_model: str = ""
    llama_cpp_server_timeout_seconds: float = 60.0
    llama_cpp_server_supports_tool_calls: bool = False
    llama_cpp_server_supports_streaming: bool = False
    ollama_enabled: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = ""
    ollama_openai_compat_base_url: str = "http://localhost:11434/v1"
    ollama_timeout_seconds: float = 60.0
    ollama_supports_tool_calls: bool = False
    ollama_supports_streaming: bool = False
    llama_cpp_inprocess_enabled: bool = False
    llama_cpp_inprocess_model_path: str = ""
    llama_cpp_inprocess_n_ctx: int = 8192
    llama_cpp_inprocess_n_gpu_layers: int = -1
    llama_cpp_inprocess_threads: str = "auto"
    llama_cpp_inprocess_supports_tool_calls: bool = False
    llama_cpp_inprocess_load_on_startup: bool = False
    llama_cpp_inprocess_max_loaded_models: int = 1
    mlx_provider_enabled: bool = False
    mlx_provider_mode: str = "server"
    mlx_server_base_url: str = "http://localhost:8081/v1"
    mlx_model: str = ""
    mlx_supports_tool_calls: bool = False
    mlx_load_on_startup: bool = False

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "BrainRuntimeConfig":
        source = env

        def get(name: str, default: str = "") -> str:
            if source is not None:
                return source.get(name, default)
            import os

            return os.getenv(name, default)

        order = tuple(
            item.strip().casefold()
            for item in get("BRAIN_PROVIDER_ORDER", ",".join(DEFAULT_PROVIDER_ORDER)).split(",")
            if item.strip()
        )
        task_provider_map = _parse_task_provider_map(get("BRAIN_TASK_PROVIDER_MAP", ""))
        timeout = parse_float(
            "BRAIN_PROVIDER_HEALTH_TIMEOUT_SECONDS",
            get("BRAIN_PROVIDER_HEALTH_TIMEOUT_SECONDS", str(cls.provider_health_timeout_seconds)),
            minimum=0.1,
            maximum=120,
        )
        if source is None:
            mock_enabled = env_bool("BRAIN_MOCK_PROVIDER_ENABLED", default=cls.mock_provider_enabled)
            fallback_enabled = env_bool("BRAIN_FALLBACK_ENABLED", default=cls.fallback_enabled)
            require_tools = env_bool(
                "BRAIN_REQUIRE_TOOL_CALL_SUPPORT_FOR_TOOLS",
                default=cls.require_tool_call_support_for_tools,
            )
            auto_switch = env_bool("BRAIN_AUTO_SWITCH_ON_FAILURE", default=cls.auto_switch_on_failure)
            allow_cloud = env_bool("BRAIN_ALLOW_CLOUD_FALLBACK", default=cls.allow_cloud_fallback)
            llama_enabled = env_bool("LLAMA_CPP_SERVER_ENABLED", default=cls.llama_cpp_server_enabled)
            llama_tools = env_bool(
                "LLAMA_CPP_SERVER_SUPPORTS_TOOL_CALLS",
                default=cls.llama_cpp_server_supports_tool_calls,
            )
            llama_streaming = env_bool(
                "LLAMA_CPP_SERVER_SUPPORTS_STREAMING",
                default=cls.llama_cpp_server_supports_streaming,
            )
            ollama_enabled = env_bool("OLLAMA_ENABLED", default=cls.ollama_enabled)
            ollama_tools = env_bool("OLLAMA_SUPPORTS_TOOL_CALLS", default=cls.ollama_supports_tool_calls)
            ollama_streaming = env_bool("OLLAMA_SUPPORTS_STREAMING", default=cls.ollama_supports_streaming)
            inprocess_enabled = env_bool("LLAMA_CPP_INPROCESS_ENABLED", default=cls.llama_cpp_inprocess_enabled)
            inprocess_tools = env_bool(
                "LLAMA_CPP_INPROCESS_SUPPORTS_TOOL_CALLS",
                default=cls.llama_cpp_inprocess_supports_tool_calls,
            )
            inprocess_load_startup = env_bool(
                "LLAMA_CPP_INPROCESS_LOAD_ON_STARTUP",
                default=cls.llama_cpp_inprocess_load_on_startup,
            )
            mlx_enabled = env_bool("MLX_PROVIDER_ENABLED", default=cls.mlx_provider_enabled)
            mlx_tools = env_bool("MLX_SUPPORTS_TOOL_CALLS", default=cls.mlx_supports_tool_calls)
            mlx_load_startup = env_bool("MLX_LOAD_ON_STARTUP", default=cls.mlx_load_on_startup)
        else:
            mock_enabled = get("BRAIN_MOCK_PROVIDER_ENABLED", "").strip().casefold() in {"1", "true", "yes", "on"}
            fallback_enabled = get("BRAIN_FALLBACK_ENABLED", "").strip().casefold() in {"1", "true", "yes", "on"}
            require_tools = get("BRAIN_REQUIRE_TOOL_CALL_SUPPORT_FOR_TOOLS", "true").strip().casefold() not in {
                "0",
                "false",
                "no",
                "off",
            }
            auto_switch = get("BRAIN_AUTO_SWITCH_ON_FAILURE", "").strip().casefold() in {"1", "true", "yes", "on"}
            allow_cloud = get("BRAIN_ALLOW_CLOUD_FALLBACK", "").strip().casefold() in {"1", "true", "yes", "on"}
            llama_enabled = get("LLAMA_CPP_SERVER_ENABLED", "").strip().casefold() in {"1", "true", "yes", "on"}
            llama_tools = get("LLAMA_CPP_SERVER_SUPPORTS_TOOL_CALLS", "").strip().casefold() in {"1", "true", "yes", "on"}
            llama_streaming = get("LLAMA_CPP_SERVER_SUPPORTS_STREAMING", "").strip().casefold() in {"1", "true", "yes", "on"}
            ollama_enabled = get("OLLAMA_ENABLED", "").strip().casefold() in {"1", "true", "yes", "on"}
            ollama_tools = get("OLLAMA_SUPPORTS_TOOL_CALLS", "").strip().casefold() in {"1", "true", "yes", "on"}
            ollama_streaming = get("OLLAMA_SUPPORTS_STREAMING", "").strip().casefold() in {"1", "true", "yes", "on"}
            inprocess_enabled = get("LLAMA_CPP_INPROCESS_ENABLED", "").strip().casefold() in {"1", "true", "yes", "on"}
            inprocess_tools = get("LLAMA_CPP_INPROCESS_SUPPORTS_TOOL_CALLS", "").strip().casefold() in {"1", "true", "yes", "on"}
            inprocess_load_startup = get("LLAMA_CPP_INPROCESS_LOAD_ON_STARTUP", "").strip().casefold() in {
                "1",
                "true",
                "yes",
                "on",
            }
            mlx_enabled = get("MLX_PROVIDER_ENABLED", "").strip().casefold() in {"1", "true", "yes", "on"}
            mlx_tools = get("MLX_SUPPORTS_TOOL_CALLS", "").strip().casefold() in {"1", "true", "yes", "on"}
            mlx_load_startup = get("MLX_LOAD_ON_STARTUP", "").strip().casefold() in {"1", "true", "yes", "on"}
        llama_timeout = parse_float(
            "LLAMA_CPP_SERVER_TIMEOUT_SECONDS",
            get("LLAMA_CPP_SERVER_TIMEOUT_SECONDS", str(cls.llama_cpp_server_timeout_seconds)),
            minimum=0.1,
            maximum=600,
        )
        ollama_timeout = parse_float(
            "OLLAMA_TIMEOUT_SECONDS",
            get("OLLAMA_TIMEOUT_SECONDS", str(cls.ollama_timeout_seconds)),
            minimum=0.1,
            maximum=600,
        )
        inprocess_n_ctx = parse_int(
            "LLAMA_CPP_INPROCESS_N_CTX",
            get("LLAMA_CPP_INPROCESS_N_CTX", str(cls.llama_cpp_inprocess_n_ctx)),
            minimum=512,
            maximum=1048576,
        )
        inprocess_n_gpu_layers = parse_int(
            "LLAMA_CPP_INPROCESS_N_GPU_LAYERS",
            get("LLAMA_CPP_INPROCESS_N_GPU_LAYERS", str(cls.llama_cpp_inprocess_n_gpu_layers)),
            minimum=-1,
            maximum=4096,
        )
        inprocess_max_loaded = parse_int(
            "LLAMA_CPP_INPROCESS_MAX_LOADED_MODELS",
            get("LLAMA_CPP_INPROCESS_MAX_LOADED_MODELS", str(cls.llama_cpp_inprocess_max_loaded_models)),
            minimum=0,
            maximum=8,
        )
        max_fallback_attempts = parse_int(
            "BRAIN_MAX_FALLBACK_ATTEMPTS",
            get("BRAIN_MAX_FALLBACK_ATTEMPTS", str(cls.max_fallback_attempts)),
            minimum=0,
            maximum=10,
        )
        return cls(
            default_provider=(get("BRAIN_DEFAULT_PROVIDER", cls.default_provider).strip().casefold() or cls.default_provider),
            provider_order=order or DEFAULT_PROVIDER_ORDER,
            task_provider_map=task_provider_map,
            fallback_enabled=fallback_enabled,
            require_tool_call_support_for_tools=require_tools,
            auto_switch_on_failure=auto_switch,
            max_fallback_attempts=max_fallback_attempts,
            allow_cloud_fallback=allow_cloud,
            provider_health_timeout_seconds=timeout,
            mock_provider_enabled=mock_enabled,
            llama_cpp_server_enabled=llama_enabled,
            llama_cpp_server_base_url=get("LLAMA_CPP_SERVER_BASE_URL", cls.llama_cpp_server_base_url).strip()
            or cls.llama_cpp_server_base_url,
            llama_cpp_server_model=get("LLAMA_CPP_SERVER_MODEL", cls.llama_cpp_server_model).strip(),
            llama_cpp_server_timeout_seconds=llama_timeout,
            llama_cpp_server_supports_tool_calls=llama_tools,
            llama_cpp_server_supports_streaming=llama_streaming,
            ollama_enabled=ollama_enabled,
            ollama_base_url=get("OLLAMA_BASE_URL", cls.ollama_base_url).strip() or cls.ollama_base_url,
            ollama_model=get("OLLAMA_MODEL", cls.ollama_model).strip(),
            ollama_openai_compat_base_url=get(
                "OLLAMA_OPENAI_COMPAT_BASE_URL",
                cls.ollama_openai_compat_base_url,
            ).strip()
            or cls.ollama_openai_compat_base_url,
            ollama_timeout_seconds=ollama_timeout,
            ollama_supports_tool_calls=ollama_tools,
            ollama_supports_streaming=ollama_streaming,
            llama_cpp_inprocess_enabled=inprocess_enabled,
            llama_cpp_inprocess_model_path=get(
                "LLAMA_CPP_INPROCESS_MODEL_PATH",
                cls.llama_cpp_inprocess_model_path,
            ).strip(),
            llama_cpp_inprocess_n_ctx=inprocess_n_ctx,
            llama_cpp_inprocess_n_gpu_layers=inprocess_n_gpu_layers,
            llama_cpp_inprocess_threads=get(
                "LLAMA_CPP_INPROCESS_THREADS",
                cls.llama_cpp_inprocess_threads,
            ).strip()
            or cls.llama_cpp_inprocess_threads,
            llama_cpp_inprocess_supports_tool_calls=inprocess_tools,
            llama_cpp_inprocess_load_on_startup=inprocess_load_startup,
            llama_cpp_inprocess_max_loaded_models=inprocess_max_loaded,
            mlx_provider_enabled=mlx_enabled,
            mlx_provider_mode=get("MLX_PROVIDER_MODE", cls.mlx_provider_mode).strip().casefold()
            or cls.mlx_provider_mode,
            mlx_server_base_url=get("MLX_SERVER_BASE_URL", cls.mlx_server_base_url).strip()
            or cls.mlx_server_base_url,
            mlx_model=get("MLX_MODEL", cls.mlx_model).strip(),
            mlx_supports_tool_calls=mlx_tools,
            mlx_load_on_startup=mlx_load_startup,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "default_provider": self.default_provider,
            "provider_order": list(self.provider_order),
            "task_provider_map": dict(self.task_provider_map or {}),
            "fallback_enabled": self.fallback_enabled,
            "require_tool_call_support_for_tools": self.require_tool_call_support_for_tools,
            "auto_switch_on_failure": self.auto_switch_on_failure,
            "max_fallback_attempts": self.max_fallback_attempts,
            "allow_cloud_fallback": self.allow_cloud_fallback,
            "provider_health_timeout_seconds": self.provider_health_timeout_seconds,
            "mock_provider_enabled": self.mock_provider_enabled,
            "llama_cpp_server_enabled": self.llama_cpp_server_enabled,
            "llama_cpp_server_base_url": self.llama_cpp_server_base_url,
            "llama_cpp_server_model": self.llama_cpp_server_model,
            "llama_cpp_server_timeout_seconds": self.llama_cpp_server_timeout_seconds,
            "llama_cpp_server_supports_tool_calls": self.llama_cpp_server_supports_tool_calls,
            "llama_cpp_server_supports_streaming": self.llama_cpp_server_supports_streaming,
            "ollama_enabled": self.ollama_enabled,
            "ollama_base_url": self.ollama_base_url,
            "ollama_model": self.ollama_model,
            "ollama_openai_compat_base_url": self.ollama_openai_compat_base_url,
            "ollama_timeout_seconds": self.ollama_timeout_seconds,
            "ollama_supports_tool_calls": self.ollama_supports_tool_calls,
            "ollama_supports_streaming": self.ollama_supports_streaming,
            "llama_cpp_inprocess_enabled": self.llama_cpp_inprocess_enabled,
            "llama_cpp_inprocess_model_path": self.llama_cpp_inprocess_model_path,
            "llama_cpp_inprocess_n_ctx": self.llama_cpp_inprocess_n_ctx,
            "llama_cpp_inprocess_n_gpu_layers": self.llama_cpp_inprocess_n_gpu_layers,
            "llama_cpp_inprocess_threads": self.llama_cpp_inprocess_threads,
            "llama_cpp_inprocess_supports_tool_calls": self.llama_cpp_inprocess_supports_tool_calls,
            "llama_cpp_inprocess_load_on_startup": self.llama_cpp_inprocess_load_on_startup,
            "llama_cpp_inprocess_max_loaded_models": self.llama_cpp_inprocess_max_loaded_models,
            "mlx_provider_enabled": self.mlx_provider_enabled,
            "mlx_provider_mode": self.mlx_provider_mode,
            "mlx_server_base_url": self.mlx_server_base_url,
            "mlx_model": self.mlx_model,
            "mlx_supports_tool_calls": self.mlx_supports_tool_calls,
            "mlx_load_on_startup": self.mlx_load_on_startup,
        }


def _parse_task_provider_map(raw: str) -> dict[str, str]:
    value = raw.strip()
    if not value:
        return {}
    if value.startswith("{"):
        import json

        try:
            payload = json.loads(value)
        except json.JSONDecodeError:
            return {}
        if not isinstance(payload, dict):
            return {}
        return {str(key).strip().casefold(): str(provider).strip().casefold() for key, provider in payload.items() if str(key).strip() and str(provider).strip()}
    mapping: dict[str, str] = {}
    for part in value.split(","):
        if ":" not in part:
            continue
        task, provider = part.split(":", 1)
        task_id = task.strip().casefold()
        provider_id = provider.strip().casefold()
        if task_id and provider_id:
            mapping[task_id] = provider_id
    return mapping
