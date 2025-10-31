"""FastAPI routes exposing the analytics computed by the application layer."""

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from service.layers.application.data_cleaning import clean_data
from service.layers.application.exceptions import DataNormalizationError
from service.layers.application.mange_ta_main import AnalysisType, DataAnylizer
from service.layers.domain.mange_ta_main import SERVICE_PREFIX
from service.layers.infrastructure.csv_adapter import CSVAdapter
from service.layers.infrastructure.types import DataType
from service.layers.logger import struct_logger

router: APIRouter = APIRouter(prefix="/" + SERVICE_PREFIX)


def get_data_analyzer(request: Request) -> DataAnylizer:
    """Retrieve a lazily-instantiated :class:`DataAnylizer` from the container."""
    return request.app.state.container.data_analyzer()


@router.get("/health")
async def health():
    """Simple health check used by monitoring and CI."""
    return {"status": "ok"}


@router.get("/load-data")
def get_data(
    data_type: DataType = Query(DataType.RECIPES),
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return either the raw recipes or interactions as JSON serialisable rows."""
    df_recipes: pd.DataFrame
    df_interactions: pd.DataFrame
    df_recipes, df_interactions = data_analyzer.get_raw_data()

    if data_type == DataType.RECIPES:
        return df_recipes.to_dict(orient="records")
    if data_type == DataType.INTERACTIONS:
        return df_interactions.to_dict(orient="records")
    raise HTTPException(
        status_code=400,
        detail=f"Unknown data_type: {data_type}. Must be 'recipes' or 'interactions'.",
    )


@router.get("/most-recipes-contributors")
def get_number_recipes(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Expose the ``most_recipes_contributors`` analysis as JSON."""
    df_result = data_analyzer.process_data(AnalysisType.NUMBER_RECIPES)
    return df_result.to_dict(orient="records")


@router.get("/best-ratings-contributors")
def get_best_contributors(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return contributors ranked by their average rating."""
    df_best = data_analyzer.process_data(AnalysisType.BEST_RECIPES)
    struct_logger.info(df_best)
    return df_best.to_dict(orient="records")


@router.post("/clean-raw-data")
def clean_raw_data_endpoint(data_type: DataType) -> dict[str, str | int]:
    """Trigger the cleaning pipeline and persist the cleaned dataset."""
    csv_adapter = CSVAdapter()
    try:
        df_cleaned = clean_data(csv_adapter, data_type)
    except DataNormalizationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success", "rows": len(df_cleaned)}


@router.get("/duration-distribution")
def get_duration_distribution(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return histogram bins describing recipe durations."""
    df_result = data_analyzer.process_data(AnalysisType.DURATION_DISTRIBUTION)
    struct_logger.info(df_result)
    return df_result.to_dict(orient="records")


@router.get("/duration-vs-recipe-count")
def get_duration_vs_recipe_count(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Expose the correlation between duration and publication volume."""
    df_result = data_analyzer.process_data(AnalysisType.DURATION_VS_RECIPE_COUNT)
    struct_logger.info(df_result)
    return df_result.to_dict(orient="records")


@router.get("/top-10-percent-contributors")
def get_top_10_percent_contributors(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return aggregated metrics for the top 10 % of contributors."""
    df_result = data_analyzer.process_data(AnalysisType.TOP_10_PERCENT_CONTRIBUTORS)
    struct_logger.info("top_10_percent_contributors", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/user-segments")
def get_user_segments(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return persona assignments for each contributor."""
    df_result = data_analyzer.process_data(AnalysisType.USER_SEGMENTS)
    struct_logger.info("user_segments", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/top-tags-by-segment")
def get_top_tags_by_segment(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return the most frequent tags for each persona."""
    df_result = data_analyzer.process_data(AnalysisType.TOP_TAGS_BY_SEGMENT)
    struct_logger.info("top_tags_by_segment", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/rating-distribution")
def get_rating_distribution(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Expose contributors grouped by their mean rating."""
    df_result = data_analyzer.process_data(AnalysisType.RATING_DISTRIBUTION)
    struct_logger.info("rating_distribution", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/rating-vs-recipes")
def get_rating_vs_recipes(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Expose the relation between publication volume and rating."""
    df_result = data_analyzer.process_data(AnalysisType.RATING_VS_RECIPES)
    struct_logger.info("rating_vs_recipes")
    return df_result.to_dict(orient="records")


@router.get("/review-overview")
def get_review_overview(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return global KPIs describing the review ecosystem."""
    df_result = data_analyzer.process_data(AnalysisType.REVIEW_OVERVIEW)
    struct_logger.info("review_overview", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/review-distribution")
def get_review_distribution(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return how many reviews each recipe gathers."""
    df_result = data_analyzer.process_data(AnalysisType.REVIEW_DISTRIBUTION)
    struct_logger.info("review_distribution", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/top-reviewers")
def get_top_reviewers(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return the most active reviewers."""
    df_result = data_analyzer.process_data(AnalysisType.REVIEWER_ACTIVITY)
    struct_logger.info("top_reviewers", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/review-trend")
def get_review_trend(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Expose the monthly volume of reviews and reviewer count."""
    df_result = data_analyzer.process_data(AnalysisType.REVIEW_TEMPORAL_TREND)
    struct_logger.info("review_trend", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/reviews-vs-rating")
def get_reviews_vs_rating(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return review counts and ratings per recipe."""
    df_result = data_analyzer.process_data(AnalysisType.REVIEWS_VS_RATING)
    struct_logger.info("reviews_vs_rating", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/reviewer-vs-recipes")
def get_reviewer_vs_recipes(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    """Return the balance between reviews written and recipes published."""
    df_result = data_analyzer.process_data(AnalysisType.REVIEWER_VS_RECIPES)
    struct_logger.info("reviewer_vs_recipes", rows=len(df_result))
    return df_result.to_dict(orient="records")
