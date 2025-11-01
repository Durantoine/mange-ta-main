import os

import numpy as np
import pandas as pd
import psutil
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from service.layers.application.data_cleaning import clean_data
from service.layers.application.mange_ta_main import AnalysisType, DataAnylizer
from service.layers.domain.mange_ta_main import SERVICE_PREFIX
from service.layers.infrastructure.csv_adapter import CSVAdapter
from service.layers.infrastructure.types import DataType
from service.layers.logger import struct_logger

router: APIRouter = APIRouter(prefix="/" + SERVICE_PREFIX)


def get_data_analyzer(request: Request) -> DataAnylizer:
    return request.app.state.container.data_analyzer()


def df_to_response(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []

    df = df.replace([np.inf, -np.inf], np.nan)

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        elif pd.api.types.is_categorical_dtype(df[col]):  # type: ignore[attr-defined]
            df[col] = df[col].cat.add_categories([""]).fillna("")
        else:
            df[col] = df[col].fillna("")

    result = df.to_dict(orient="records")
    return result


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/debug/memory")
def get_memory_info(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    df_recipes, df_interactions = data_analyzer.get_raw_data()

    return {
        "process_memory_mb": round(memory_info.rss / 1024 / 1024, 2),
        "process_memory_percent": round(process.memory_percent(), 2),
        "df_recipes_memory_mb": round(df_recipes.memory_usage(deep=True).sum() / 1024**2, 2),
        "df_interactions_memory_mb": round(
            df_interactions.memory_usage(deep=True).sum() / 1024**2, 2
        ),
        "df_recipes_shape": df_recipes.shape,
        "df_interactions_shape": df_interactions.shape,
    }


@router.get("/load-data")
def get_data(
    data_type: DataType = Query(DataType.RECIPES),
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_recipes, df_interactions = data_analyzer.get_raw_data()

    match data_type:
        case DataType.RECIPES:
            return df_to_response(df_recipes)
        case DataType.INTERACTIONS:
            return df_to_response(df_interactions)
        case _:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown data_type: {data_type}. Must be 'recipes' or 'interactions'.",
            )


@router.get("/most-recipes-contributors")
def get_number_recipes(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.NUMBER_RECIPES)
    return df_to_response(df_result)


@router.get("/best-ratings-contributors")
def get_best_contributors(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_best = data_analyzer.process_data(AnalysisType.BEST_RECIPES)
    struct_logger.info("best_ratings_contributors", rows=len(df_best))
    return df_to_response(df_best)


@router.post("/clean-raw-data")
def clean_raw_data_endpoint(data_type: DataType) -> dict[str, str | int]:
    csv_adapter = CSVAdapter()
    df_cleaned = clean_data(csv_adapter, data_type)
    return {"status": "success", "rows": len(df_cleaned)}


@router.get("/duration-distribution")
def get_duration_distribution(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.DURATION_DISTRIBUTION)
    struct_logger.info("duration_distribution", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/duration-vs-recipe-count")
def get_duration_vs_recipe_count(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.DURATION_VS_RECIPE_COUNT)
    struct_logger.info("duration_vs_recipe_count", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/top-10-percent-contributors")
def get_top_10_percent_contributors(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.TOP_10_PERCENT_CONTRIBUTORS)
    struct_logger.info("top_10_percent_contributors", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/user-segments")
def get_user_segments(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.USER_SEGMENTS)
    struct_logger.info("user_segments", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/top-tags-by-segment")
def get_top_tags_by_segment(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.TOP_TAGS_BY_SEGMENT)
    struct_logger.info("top_tags_by_segment", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/rating-distribution")
def get_rating_distribution(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.RATING_DISTRIBUTION)
    struct_logger.info("rating_distribution", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/rating-vs-recipes")
def get_rating_vs_recipes(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.RATING_VS_RECIPES)
    struct_logger.info("rating_vs_recipes", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/review-overview")
def get_review_overview(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.REVIEW_OVERVIEW)
    struct_logger.info("review_overview", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/review-distribution")
def get_review_distribution(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.REVIEW_DISTRIBUTION)
    struct_logger.info("review_distribution", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/top-reviewers")
def get_top_reviewers(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.REVIEWER_ACTIVITY)
    struct_logger.info("top_reviewers", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/review-trend")
def get_review_trend(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.REVIEW_TEMPORAL_TREND)
    struct_logger.info("review_trend", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/reviews-vs-rating")
def get_reviews_vs_rating(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.REVIEWS_VS_RATING)
    struct_logger.info("reviews_vs_rating", rows=len(df_result))
    return df_to_response(df_result)


@router.get("/reviewer-vs-recipes")
def get_reviewer_vs_recipes(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_result = data_analyzer.process_data(AnalysisType.REVIEWER_VS_RECIPES)
    struct_logger.info("reviewer_vs_recipes", rows=len(df_result))
    return df_to_response(df_result)
