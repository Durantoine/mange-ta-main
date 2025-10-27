from service.main import struct_logger


def test_root_endpoint(test_client):
    url = "/mange_ta_main/health"
    struct_logger.info(f"Testing route: {url}")
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
