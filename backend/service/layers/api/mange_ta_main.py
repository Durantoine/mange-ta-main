import pandas as pd
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


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/load-data")
def get_data(
    data_type: DataType = Query(DataType.RECIPES),
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    df_recipes: pd.DataFrame
    df_interactions: pd.DataFrame
    df_recipes, df_interactions = data_analyzer.get_raw_data()

    match data_type:
        case DataType.RECIPES:
            return df_recipes.to_dict(orient="records")
        case DataType.INTERACTIONS:
            return df_interactions.to_dict(orient="records")
        case _:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown data_type: {data_type}. Must be 'recipes' or 'interactions'.",
            )


@router.get("/most-recipes-contributors")
def get_number_recipes(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    df_result = data_analyzer.process_data(AnalysisType.NUMBER_RECIPES)
    return df_result.to_dict(orient="records")


@router.get("/best-ratings-contributors")
def get_best_contributors(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    df_best = data_analyzer.process_data(AnalysisType.BEST_RECIPES)
    struct_logger.info(df_best)
    return df_best.to_dict(orient="records")


@router.post("/clean-raw-data")
def clean_raw_data_endpoint(data_type: DataType) -> dict[str, str | int]:
    csv_adapter = CSVAdapter()
    df_cleaned = clean_data(csv_adapter, data_type)
    return {"status": "success", "rows": len(df_cleaned)}


@router.get("/duration-distribution")
def get_duration_distribution(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    df_result = data_analyzer.process_data(AnalysisType.DURATION_DISTRIBUTION)
    struct_logger.info(df_result)
    return df_result.to_dict(orient="records")


@router.get("/duration-vs-recipe-count")
def get_duration_vs_recipe_count(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    df_result = data_analyzer.process_data(AnalysisType.DURATION_VS_RECIPE_COUNT)
    struct_logger.info(df_result)
    return df_result.to_dict(orient="records")

@router.get("/top-10-percent-contributors")
def get_top_10_percent_contributors(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    df_result = data_analyzer.process_data(AnalysisType.TOP_10_PERCENT_CONTRIBUTORS)
    struct_logger.info("top_10_percent_contributors", rows=len(df_result))
    return df_result.to_dict(orient="records")

@router.get("/user-segments")
def get_user_segments(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    df_result = data_analyzer.process_data(AnalysisType.USER_SEGMENTS)
    struct_logger.info("user_segments", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/top-tags-by-segment")
def get_top_tags_by_segment(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    df_result = data_analyzer.process_data(AnalysisType.TOP_TAGS_BY_SEGMENT)
    struct_logger.info("top_tags_by_segment", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/rating-distribution")
def get_rating_distribution(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    df_result = data_analyzer.process_data(AnalysisType.RATING_DISTRIBUTION)
    struct_logger.info("rating_distribution", rows=len(df_result))
    return df_result.to_dict(orient="records")


@router.get("/rating-vs-recipes")
def get_rating_vs_recipes(
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
) -> list[dict]:
    df_result = data_analyzer.process_data(AnalysisType.RATING_VS_RECIPES)
    struct_logger.info("rating_vs_recipes")
    return df_result.to_dict(orient="records")
