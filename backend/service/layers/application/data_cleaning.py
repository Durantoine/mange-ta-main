"""Module de nettoyage et de préparation des données.

Ce module fournit des fonctions pour nettoyer, normaliser et préparer
les données de recettes et d'interactions avant analyse.

Examples:
    Nettoyer un DataFrame de recettes::

        df_recipes = load_recipes()
        df_clean = remove_outliers(df_recipes, factor=5)
        df_normalized = normalize_ids(df_clean, DataType.RECIPES)
"""

import ast
from enum import StrEnum
from typing import Any, Hashable

import numpy as np
import pandas as pd

from service.layers.application.interfaces.interface import IDataAdapter
from service.layers.infrastructure.types import DataType


class DataTypes(StrEnum):
    """Types de données supportés par l'application.

    Attributes:
        RECIPES: Données de recettes
        INTERACTIONS: Données d'interactions utilisateurs
    """

    RECIPES = "recipes"
    INTERACTIONS = "interactions"


def remove_outliers(df: pd.DataFrame, factor: float = 5) -> pd.DataFrame:
    """Supprime les valeurs aberrantes d'un DataFrame.

    Utilise la méthode IQR (Interquartile Range) pour détecter et supprimer
    les outliers. Pour chaque colonne numérique, les valeurs au-delà de
    Q3 + factor * IQR sont considérées comme des outliers et supprimées.

    Args:
        df: DataFrame à nettoyer
        factor: Facteur multiplicatif pour l'IQR. Plus il est élevé,
            plus la détection des outliers est permissive. Valeur par
            défaut : 5 (détection modérée).

    Returns:
        DataFrame nettoyé sans les lignes contenant des outliers.
        Les valeurs NaN sont remplacées par None.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'a': [1, 2, 3, 100], 'b': [4, 5, 6, 7]})
        >>> df_clean = remove_outliers(df, factor=3)
        >>> print(len(df_clean))  # Moins de 4 lignes
        3

    Note:
        - Les valeurs infinies (inf, -inf) sont traitées comme des NaN
        - Seules les colonnes numériques sont traitées
        - Les lignes complètes contenant des outliers sont supprimées

    Warning:
        Cette fonction modifie le DataFrame en supprimant des lignes.
        Faites une copie si vous devez conserver l'original.
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
    """Normalise les identifiants dans un DataFrame.

    Convertit les identifiants (user_id, contributor_id, id) en entiers
    séquentiels à partir de 0 ou 1, en utilisant pd.factorize().

    Args:
        df: DataFrame contenant les identifiants à normaliser
        data_type: Type de données (RECIPES ou INTERACTIONS) qui détermine
            quels identifiants normaliser

    Returns:
        DataFrame avec les identifiants normalisés en entiers séquentiels

    Raises:
        ValueError: Si le type de données n'est pas reconnu

    Examples:
        Normaliser les IDs de recettes::

            >>> df = pd.DataFrame({
            ...     'id': ['abc', 'def', 'abc'],
            ...     'contributor_id': ['user1', 'user2', 'user1']
            ... })
            >>> df_norm = normalize_ids(df, DataType.RECIPES)
            >>> print(df_norm['id'].tolist())
            [0, 1, 0]
            >>> print(df_norm['contributor_id'].tolist())
            [1, 2, 1]

        Normaliser les IDs d'interactions::

            >>> df = pd.DataFrame({'user_id': ['u1', 'u2', 'u1']})
            >>> df_norm = normalize_ids(df, DataType.INTERACTIONS)
            >>> print(df_norm['user_id'].tolist())
            [1, 2, 1]

    Note:
        - Pour RECIPES: normalise 'contributor_id' (commence à 1) et 'id' (commence à 0)
        - Pour INTERACTIONS: normalise 'user_id' (commence à 1)
        - pd.factorize() assigne des entiers basés sur l'ordre d'apparition
    """

    match data_type:
        case DataTypes.INTERACTIONS:
            df['user_id'] = pd.factorize(df['user_id'])[0] + 1

        case DataTypes.RECIPES:
            df['contributor_id'] = pd.factorize(df['contributor_id'])[0] + 1
            df['id'] = pd.factorize(df['id'])[0]

        case _:
            raise ValueError(f"Unknown data type: {data_type}")

    return df


def clean_data(csv_adapter: IDataAdapter, data_type: DataType) -> list[dict[Hashable, Any]]:
    match data_type:
        case DataType.RECIPES:
            df = csv_adapter.load(DataType.RECIPES, raw=True)
            df.dropna(subset=['name'], inplace=True)
        case DataType.INTERACTIONS:
            df = csv_adapter.load(DataType.INTERACTIONS, raw=True)
        case _:
            raise ValueError(f"Unknown data type: {data_type}")

    for col in df.columns:
        sample_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
        if isinstance(sample_val, str) and sample_val.startswith('[') and sample_val.endswith(']'):
            df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    df = remove_outliers(df)

    df = normalize_ids(df, data_type)

    df = df.astype(object)
    df = df.where(pd.notna(df), None)

    match data_type:
        case DataType.RECIPES:
            csv_adapter.save(df, DataType.RECIPES)
        case DataType.INTERACTIONS:
            csv_adapter.save(df, DataType.INTERACTIONS)

    return df.to_dict(orient="records")
