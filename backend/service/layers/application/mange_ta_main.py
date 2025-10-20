from enum import StrEnum

import pandas as pd

from service.layers.application.interfaces.interface import IDataAdapter
from service.layers.infrastructure.types import DataType


class AnalysisType(StrEnum):
    NO_ANALYSIS = "no_analysis"
    NUMBER_RECIPES = "number_recipes"
    BEST_RECIPES = "best_recipes"
    NUMBER_COMMENTS = "number_comments"


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

            case _:
                raise ValueError(f"Analyse non supportée : {analysis_type}")
