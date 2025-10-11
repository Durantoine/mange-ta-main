from fastapi import APIRouter

# from service.main import struct_logger
from service.layers.domain.mange_ta_main import SERVICE_PREFIX, DataPacket, PacketTypes

router = APIRouter(prefix="/" + SERVICE_PREFIX)

demo_data_packet = DataPacket(
    type=PacketTypes.RESPONSE, payload="Hi, my name is mange_ta_main!")


@router.get("/")
async def root() -> dict:
    # struct_logger.info("Hello")
    return demo_data_packet.to_json()

def add(a, b):
    return a + b