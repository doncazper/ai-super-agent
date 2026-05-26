"""Provider-neutral brain runtime scaffolding.

BRAIN-02 defines interfaces, models, registry, and mock provider only. The
current LM Studio runtime path remains unchanged until the later refactor.
"""

from agent.brain.base import BrainProvider
from agent.brain.config import BrainRuntimeConfig
from agent.brain.errors import BrainProviderError
from agent.brain.models import (
    BrainChatRequest,
    BrainChatResponse,
    BrainGenerationSettings,
    BrainMessage,
    BrainModelInfo,
    BrainProviderHealth,
    BrainProviderStatus,
    BrainToolCall,
    BrainToolSpec,
)
from agent.brain.registry import BrainProviderRegistration, BrainProviderRegistry, default_registry

__all__ = [
    "BrainChatRequest",
    "BrainChatResponse",
    "BrainGenerationSettings",
    "BrainMessage",
    "BrainModelInfo",
    "BrainProvider",
    "BrainProviderError",
    "BrainProviderHealth",
    "BrainProviderStatus",
    "BrainProviderRegistration",
    "BrainProviderRegistry",
    "BrainToolCall",
    "BrainToolSpec",
    "BrainRuntimeConfig",
    "default_registry",
]
