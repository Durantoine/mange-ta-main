from typing import Iterator
from unittest.mock import MagicMock

import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import service.main as service_main
from service.layers.api import mange_ta_main as api_module
from service.layers.application.mange_ta_main import AnalysisType
from service.main import app


@pytest.fixture
def test_client() -> Iterator[TestClient]:
    """Minimal FastAPI router exposure for lightweight endpoint checks."""
    app_instance = FastAPI()
    app_instance.include_router(api_module.router)
    with TestClient(app_instance) as client:
        yield client


@pytest.fixture
def sample_recipes() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"id": 1, "contributor_id": "u1", "minutes": 30, "name": "Recipe A"},
            {"id": 2, "contributor_id": "u2", "minutes": 20, "name": "Recipe B"},
            {"id": 3, "contributor_id": "u1", "minutes": 45, "name": "Recipe C"},
        ]
    )


@pytest.fixture
def sample_interactions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "user_id": "u1",
                "recipe_id": 1,
                "rating": 4.0,
                "review": "Delicious",
                "date": "2024-01-05",
            },
            {
                "user_id": "u2",
                "recipe_id": 1,
                "rating": 5.0,
                "review": "Must try",
                "date": "2024-01-06",
            },
            {
                "user_id": "u3",
                "recipe_id": 3,
                "rating": 4.0,
                "review": "Very good",
                "date": "2024-02-10",
            },
            {
                "user_id": "u1",
                "recipe_id": 2,
                "rating": 3.0,
                "review": "",
                "date": "2024-02-11",
            },
            {
                "user_id": "u4",
                "recipe_id": 3,
                "rating": 2.0,
                "review": None,
                "date": "2024-02-12",
            },
        ]
    )


@pytest.fixture
def rich_recipes() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": 1,
                "contributor_id": "c1",
                "minutes": 10,
                "tags": "['sweet','quick']",
                "name": "A",
            },
            {
                "id": 2,
                "contributor_id": "c1",
                "minutes": 20,
                "tags": "['savory','quick']",
                "name": "B",
            },
            {
                "id": 3,
                "contributor_id": "c1",
                "minutes": 30,
                "tags": "['sweet','family']",
                "name": "C",
            },
            {"id": 4, "contributor_id": "c1", "minutes": 40, "tags": "['snack']", "name": "D"},
            {"id": 5, "contributor_id": "c1", "minutes": 50, "tags": "['dessert']", "name": "E"},
            {"id": 6, "contributor_id": "c2", "minutes": 15, "tags": "['quick']", "name": "F"},
            {"id": 7, "contributor_id": "c3", "minutes": 70, "tags": "['slow']", "name": "G"},
            {
                "id": 8,
                "contributor_id": "c4",
                "minutes": 25,
                "tags": "['quick','veggie']",
                "name": "H",
            },
            {"id": 9, "contributor_id": "c5", "minutes": 45, "tags": "['sweet']", "name": "I"},
            {"id": 10, "contributor_id": "c6", "minutes": 35, "tags": "['family']", "name": "J"},
        ]
    )


@pytest.fixture
def rich_interactions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "user_id": "u1",
                "recipe_id": 1,
                "rating": 4.0,
                "review": "Nice",
                "date": "2024-01-01",
            },
            {
                "user_id": "u2",
                "recipe_id": 1,
                "rating": 5.0,
                "review": "Great",
                "date": "2024-01-02",
            },
            {
                "user_id": "u3",
                "recipe_id": 2,
                "rating": 3.0,
                "review": "Okay",
                "date": "2024-02-01",
            },
            {
                "user_id": "u4",
                "recipe_id": 3,
                "rating": 4.5,
                "review": "Loved",
                "date": "2024-02-15",
            },
            {
                "user_id": "u5",
                "recipe_id": 4,
                "rating": 4.0,
                "review": "Tasty",
                "date": "2024-03-03",
            },
            {"user_id": "u6", "recipe_id": 5, "rating": 5.0, "review": "Yum", "date": "2024-03-10"},
            {
                "user_id": "u1",
                "recipe_id": 6,
                "rating": 4.0,
                "review": "Fast",
                "date": "2024-03-15",
            },
            {
                "user_id": "u2",
                "recipe_id": 7,
                "rating": 2.0,
                "review": "Too long",
                "date": "2024-04-01",
            },
            {
                "user_id": "u3",
                "recipe_id": 8,
                "rating": 4.0,
                "review": "Green",
                "date": "2024-04-10",
            },
            {
                "user_id": "u3",
                "recipe_id": 9,
                "rating": 5.0,
                "review": "Sweet treat",
                "date": "2024-05-12",
            },
            {
                "user_id": "u4",
                "recipe_id": 10,
                "rating": 3.5,
                "review": "Family meal",
                "date": "2024-06-20",
            },
            {
                "user_id": "u5",
                "recipe_id": 1,
                "rating": 4.5,
                "review": "Repeat",
                "date": "2024-06-25",
            },
            {
                "user_id": "u6",
                "recipe_id": 3,
                "rating": 4.8,
                "review": "Again",
                "date": "2024-07-01",
            },
        ]
    )


@pytest.fixture
def api_stub_analyzer():
    class StubAnalyzer:
        def __init__(self):
            self.raw = (
                pd.DataFrame([{"id": 1, "value": "recipes"}]),
                pd.DataFrame([{"id": 2, "value": "interactions"}]),
            )

        def get_raw_data(self):
            return self.raw

        def process_data(self, analysis_type: AnalysisType) -> pd.DataFrame:
            return pd.DataFrame([{"analysis": analysis_type.value}])

    return StubAnalyzer()


@pytest.fixture
def stub_container(api_stub_analyzer):
    container = MagicMock()
    container.data_analyzer.return_value = api_stub_analyzer
    return container


@pytest.fixture
def api_client(api_stub_analyzer, stub_container, monkeypatch) -> Iterator[TestClient]:
    monkeypatch.setattr(service_main, "Container", lambda: stub_container)
    app.dependency_overrides[api_module.get_data_analyzer] = lambda: api_stub_analyzer
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
