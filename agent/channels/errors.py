from __future__ import annotations


class ChannelGatewayError(RuntimeError):
    """Base error for safe channel gateway scaffolding."""


class UnknownChannelError(ChannelGatewayError):
    """Raised when a channel id is not registered."""


class ChannelDisabledError(ChannelGatewayError):
    """Raised when a channel is known but disabled."""


class ChannelSecurityError(ChannelGatewayError):
    """Raised when a channel attempts a forbidden control-plane action."""
