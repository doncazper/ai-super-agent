from __future__ import annotations


class PerformanceError(Exception):
    """Base error for safe performance report handling."""


class PerformanceReportNotFoundError(PerformanceError):
    """Raised when a requested report does not exist."""


class PerformanceReportValidationError(PerformanceError):
    """Raised when report data cannot be serialized safely."""
