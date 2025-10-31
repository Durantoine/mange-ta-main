"""Custom exceptions used across the application layer."""


class DataNormalizationError(Exception):
    """Raised when the raw datasets cannot be normalised safely."""


class UnsupportedAnalysisError(Exception):
    """Raised when an unsupported analysis is requested from the orchestrator."""
