from service.layers.application.data_loading import load_data
from service.layers.infrastructure import csv_adapter
from service.layers.application.data_cleaning import DataType, clean_data
from service.layers.infrastructure.csv_adapter import CSVAdapter
from fastapi import APIRouter, Query
from service.layers.logger import struct_logger
import numpy as np
import pandas as pd


from service.layers.domain.mange_ta_main import SERVICE_PREFIX, DataPacket, PacketTypes

router = APIRouter(prefix="/" + SERVICE_PREFIX)

demo_data_packet = DataPacket(
    type=PacketTypes.RESPONSE, payload="Hi, my name is mange_ta_main!")


@router.get("/")
async def root() -> dict:
    return demo_data_packet.to_json()

@router.get("/load-data")
def get_data(data_type: DataType = Query(DataType.RECIPES)):
    csv_adapter = CSVAdapter()
    df = load_data(csv_adapter, data_type)   
    return df.to_dict(orient="records")


@router.post("/clean-raw-data")
def clean_raw_data_endpoint(data_type: DataType):
    csv_adapter = CSVAdapter()
    df_cleaned = clean_data(csv_adapter, data_type)
    return {"status": "success", "rows": len(df_cleaned)}