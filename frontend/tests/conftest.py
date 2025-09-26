import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from service.layers.api.mange-ta-main-front import router


@pytest.fixture
def test_client():
    """Create a reusable TestClient fixture for the FastAPI app."""
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as c:
        yield c
