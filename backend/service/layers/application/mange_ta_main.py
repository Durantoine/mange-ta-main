from enum import StrEnum
from typing import List, Optional, Sequence, Union
import pandas as pd
import numpy as np

from service.layers.application.interfaces.interface import IDataAdapter
from service.layers.infrastructure.types import DataType


class AnalysisType(StrEnum):
    NO_ANALYSIS = "no_analysis"
    NUMBER_RECIPES = "number_recipes"
    BEST_RECIPES = "best_recipes"
    NUMBER_COMMENTS = "number_comments"
    DURATION_DISTRIBUTION = "duration_distribution" 
    DURATION_VS_RECIPE_COUNT = "duration_vs_recipe_count"


def most_recipes_contributors(df_recipes: pd.DataFrame) -> pd.DataFrame:

    number_recipes_contributors = (
        df_recipes.groupby('contributor_id').size().sort_values(ascending=False).reset_index()
    )

    return number_recipes_contributors


def best_ratings_contributors(
    df_recipes: pd.DataFrame, df_interactions: pd.DataFrame
) -> pd.DataFrame:

    avg_ratings = (
        df_interactions.groupby("recipe_id")["rating"].mean().reset_index(name="avg_rating")
    )

    df = df_recipes.merge(avg_ratings, how="left", left_on="id", right_on="recipe_id")

    contributor_counts = df.groupby("contributor_id")["id"].count().reset_index(name="num_recipes")

    contributor_avg = df.groupby("contributor_id")["avg_rating"].mean().reset_index()

    contributor_stats = contributor_avg.merge(contributor_counts, on="contributor_id")

    contributor_stats = contributor_stats[contributor_stats["num_recipes"] >= 5]

    contributor_stats = contributor_stats.sort_values(by="avg_rating", ascending=False).reset_index(
        drop=True
    )

    contributor_stats = contributor_stats.where(pd.notna(contributor_stats), None)

    return contributor_stats

def average_duration_distribution(
    df_recipes: pd.DataFrame,
    duration_col: str = "minutes",
    bins: Optional[Union[int, Sequence[float]]] = None,
    labels: Optional[Sequence[str]] = None,
    group_cols: Optional[Sequence[str]] = None,
) -> pd.DataFrame:

    df = df_recipes.copy()
    df[duration_col] = pd.to_numeric(df[duration_col], errors="coerce")
    df = df.dropna(subset=[duration_col])

    # Définition des classes (bins)
    if bins is None:
        bins = [0, 15, 30, 45, 60, 90, 120, np.inf]
        if labels is None:
            labels = ["0–15", "15–30", "30–45", "45–60", "60–90", "90–120", "120+"]

    # Si bins est un entier --> classes d’amplitude égale
    if isinstance(bins, int):
        vmin, vmax = df[duration_col].min(), df[duration_col].max()
        bins = np.linspace(vmin, vmax, bins + 1).tolist()

    # Découpage des durées en classes
    df["duration_bin"] = pd.cut(
        df[duration_col],
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=False
    )

    # Comptage et moyenne par classe
    group_cols_list = list(group_cols) if group_cols else []
    group_keys = group_cols_list + ["duration_bin"]

    agg = (
        df.groupby(group_keys)
          .agg(
              count=(duration_col, "size"),
              avg_duration_in_bin=(duration_col, "mean")
          )
          .reset_index()
    )

    # Calcul des parts par groupe
    if group_cols_list:
        totals = agg.groupby(group_cols_list)["count"].sum().reset_index(name="total_count")
        out = agg.merge(totals, on=group_cols_list, how="left")
    else:
        total_count = agg["count"].sum()
        out = agg.assign(total_count=total_count)

    out["share"] = (out["count"] / out["total_count"] * 100).round(2)

    # Part cumulée (%)
    out = out.sort_values(group_cols_list + ["duration_bin"]).reset_index(drop=True)
    if group_cols_list:
        out["cum_share"] = out.groupby(group_cols_list)["share"].cumsum().round(2)
    else:
        out["cum_share"] = out["share"].cumsum().round(2)

    # Finition
    out = out.drop(columns=["total_count"])
    out["avg_duration_in_bin"] = pd.to_numeric(
        out["avg_duration_in_bin"], errors="coerce"
    ).round(1)

    return out

def duration_vs_recipe_count(
    df_recipes: pd.DataFrame,
    duration_col: str = "minutes",
) -> pd.DataFrame:
    """Aggregate contributor activity and recipe duration metrics for correlation plots."""
    df = df_recipes.copy()
    df = df.dropna(subset=["contributor_id"])
    df[duration_col] = pd.to_numeric(df[duration_col], errors="coerce")
    df = df.dropna(subset=[duration_col])

    agg = (
        df.groupby("contributor_id")
        .agg(
            recipe_count=("id", "size"),
            avg_duration=(duration_col, "mean"),
            median_duration=(duration_col, "median"),
        )
        .reset_index()
    )

    if agg.empty:
        return agg

    agg["avg_duration"] = agg["avg_duration"].round(2)
    agg["median_duration"] = agg["median_duration"].round(2)

    return agg


class DataAnylizer:

    def __init__(self, csv_adapter: IDataAdapter):
        self.df_recipes = csv_adapter.load(DataType.RECIPES)
        self.df_interactions = csv_adapter.load(DataType.INTERACTIONS)

    def get_raw_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        return self.df_recipes, self.df_interactions

    def process_data(self, analysis_type: AnalysisType) -> pd.DataFrame:
        match analysis_type:

            case AnalysisType.NUMBER_RECIPES:
                return most_recipes_contributors(self.df_recipes)

            case AnalysisType.BEST_RECIPES:
                return best_ratings_contributors(self.df_recipes, self.df_interactions)
            
            case AnalysisType.DURATION_DISTRIBUTION: 
                return average_duration_distribution(
                    self.df_recipes,
                    duration_col="minutes",         
                )

            case AnalysisType.DURATION_VS_RECIPE_COUNT:
                return duration_vs_recipe_count(
                    self.df_recipes,
                    duration_col="minutes",
                )

            case _:
                raise ValueError(f"Analyse non supportée : {analysis_type}")
