from service.layers.domain.mange_ta_main import DataPacket, PacketTypes
from service.main import struct_logger


def test_root_endpoint(test_client):
    url = "/mange_ta_main/"
    struct_logger.info(f"Testing route: {url}")
    response = test_client.get(url)
    assert response.status_code == 200
    assert (
        response.json()
        == DataPacket(type=PacketTypes.RESPONSE, payload="Hi, my name is mange_ta_main!").to_json()
    )
