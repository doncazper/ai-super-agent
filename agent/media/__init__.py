"""Creative media scaffolding.

This package is provider-neutral and safe-by-default. It does not generate
media, import model runtimes, upload assets, or call external providers.
"""

from agent.media.asset_manager import MediaAssetManager
from agent.media.provider_registry import MediaProviderRegistry, default_media_provider_registry

__all__ = [
    "MediaAssetManager",
    "MediaProviderRegistry",
    "default_media_provider_registry",
]
