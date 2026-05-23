from __future__ import annotations


class ConnectorError(ValueError):
    """Base error for connector metadata and status failures."""


class UnknownConnectorError(ConnectorError):
    def __init__(self, connector: str) -> None:
        super().__init__(f"unknown connector: {connector}")
        self.connector = connector
