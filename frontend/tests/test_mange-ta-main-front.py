from frontend.app import struct_logger


def test_root_endpoint(test_client):
    url = "/mange-ta-main-front/"
    struct_logger.info(f"Testing route: {url}")
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.text == "My name is mange-ta-main-front!"
