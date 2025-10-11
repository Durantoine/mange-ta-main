from fastapi import APIRouter, Depends, HTTPException, Query, Request

from service.layers.application.data_cleaning import DataType, clean_data
from service.layers.application.mange_ta_main import AnalysisType, DataAnylizer
from service.layers.domain.mange_ta_main import SERVICE_PREFIX, DataPacket, PacketTypes
from service.layers.infrastructure.csv_adapter import CSVAdapter
from service.layers.logger import struct_logger

router = APIRouter(prefix="/" + SERVICE_PREFIX)

demo_data_packet = DataPacket(
    type=PacketTypes.RESPONSE, payload="Hi, my name is mange_ta_main!")


def get_data_analyzer(request: Request) -> DataAnylizer:
    return request.app.state.container.data_analyzer()


@router.get("/")
async def root() -> dict:
    return demo_data_packet.to_json()


@router.get("/load-data")
def get_data(
    data_type: DataType = Query(DataType.RECIPES),
    data_analyzer: DataAnylizer = Depends(get_data_analyzer),
):
    df_recipes, df_interactions = data_analyzer.process_data(
        AnalysisType.NO_ANALYSIS)
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
def get_numbeer_recipes(data_analyzer: DataAnylizer = Depends(get_data_analyzer)):
    return data_analyzer.process_data(AnalysisType.NUMBER_RECIPES).to_dict(orient="records")


@router.get("/best-ratings-contributors")
def get_best_contributors(data_analyzer: DataAnylizer = Depends(get_data_analyzer)):
    df_best = data_analyzer.process_data(AnalysisType.BEST_RECIPES)
    struct_logger.info(df_best)
    return df_best.to_dict(orient="records")


@router.post("/clean-raw-data")
def clean_raw_data_endpoint(data_type: DataType):
    csv_adapter = CSVAdapter()
    df_cleaned = clean_data(csv_adapter, data_type)
    return {"status": "success", "rows": len(df_cleaned)}
