"""Shared enums and type aliases for the infrastructure layer."""

from enum import StrEnum


class DataType(StrEnum):
    """Datasets available throughout the application."""

    INTERACTIONS = "interactions"
    RECIPES = "recipes"
