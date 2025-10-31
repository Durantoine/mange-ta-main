"""Utility helpers to clean and normalise the raw CSV datasets."""

import ast
from enum import StrEnum
from typing import Any, Hashable

import numpy as np
import pandas as pd

from service.layers.application.exceptions import DataNormalizationError
from service.layers.application.interfaces.interface import IDataAdapter
from service.layers.infrastructure.types import DataType


class DataTypes(StrEnum):
    RECIPES = "recipes"
    INTERACTIONS = "interactions"


def remove_outliers(df: pd.DataFrame, factor: float = 5) -> pd.DataFrame:
    """Remove extreme rows based on an interquartile band.

    Args:
        df: DataFrame containing the dataset to clean.
        factor: Multiplicative factor applied to the IQR to form upper bounds.

    Returns:
        The filtered dataframe with outliers removed and ``NaN`` converted to
        ``None`` for JSON serialisation.
    """

    df = df.replace([np.inf, -np.inf], np.nan)

    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        high = Q3 + factor * IQR
        df = df.drop(df[df[col] > high].index)

    df = df.where(pd.notna(df), None)

    return df


def normalize_ids(df: pd.DataFrame, data_type: DataType) -> pd.DataFrame:
    """Ensure identifiers follow a consistent pattern across datasets.

    Args:
        df: Raw dataframe loaded from CSV.
        data_type: Dataset kind used to decide which columns to normalise.

    Returns:
        The dataframe with deterministic integer identifiers.
    """

    if data_type == DataType.INTERACTIONS:
        df["user_id"] = pd.factorize(df["user_id"])[0] + 1
    elif data_type == DataType.RECIPES:
        df["contributor_id"] = pd.factorize(df["contributor_id"])[0] + 1
        df["id"] = pd.factorize(df["id"])[0]
    else:
        raise DataNormalizationError(f"Unknown data type: {data_type}")

    return df


def clean_data(csv_adapter: IDataAdapter, data_type: DataType) -> list[dict[Hashable, Any]]:
    """Load, clean and serialise the requested dataset.

    Args:
        csv_adapter: Adapter responsible for reading/writing CSV data.
        data_type: Which dataset to process (recipes or interactions).

    Returns:
        A JSON-ready list of rows persisted back through the adapter.
    """
    if data_type == DataType.RECIPES:
        df = csv_adapter.load(DataType.RECIPES, raw=True)
        df.dropna(subset=["name"], inplace=True)
    elif data_type == DataType.INTERACTIONS:
        df = csv_adapter.load(DataType.INTERACTIONS, raw=True)
    else:
        raise DataNormalizationError(f"Unknown data type: {data_type}")

    for col in df.columns:
        sample_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
        if isinstance(sample_val, str) and sample_val.startswith('[') and sample_val.endswith(']'):
            df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    df = remove_outliers(df)

    df = normalize_ids(df, data_type)

    df = df.astype(object)
    df = df.where(pd.notna(df), None)

    if data_type == DataType.RECIPES:
        csv_adapter.save(df, DataType.RECIPES)
    elif data_type == DataType.INTERACTIONS:
        csv_adapter.save(df, DataType.INTERACTIONS)

    return df.to_dict(orient="records")
