from service.layers.application.data_cleaning import RawDataTypes, clean_data
from service.layers.infrastructure.data_loader import CSVDataLoader
from fastapi import APIRouter, Query
from service.layers.logger import struct_logger
import numpy as np


from service.layers.domain.mange_ta_main import SERVICE_PREFIX, DataPacket, PacketTypes

router = APIRouter(prefix="/" + SERVICE_PREFIX)

demo_data_packet = DataPacket(
    type=PacketTypes.RESPONSE, payload="Hi, my name is mange_ta_main!")


@router.get("/")
async def root() -> dict:
    return demo_data_packet.to_json()


@router.get("/raw-data")
def get_raw_data(data_type: RawDataTypes = Query(RawDataTypes.RECIPES)):
    loader = CSVDataLoader()
    df = clean_data(loader, data_type)
    #struct_logger.info("DataFrame preview", data=df.head().to_dict())
    df = df.replace({np.nan: None})
    return df.to_dict(orient="records")