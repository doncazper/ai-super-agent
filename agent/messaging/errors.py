from __future__ import annotations


class MessagingError(ValueError):
    """Base error for message-channel validation and registry failures."""


class UnknownChannelError(MessagingError):
    pass


class MessageValidationError(MessagingError):
    pass


class DirectSendNotSupportedError(MessagingError):
    pass
