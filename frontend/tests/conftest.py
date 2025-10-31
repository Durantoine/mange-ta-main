from typing import Any, Callable, Iterable, List
from unittest.mock import Mock, patch

import pytest

from ..service.components.tab07_tags import SEGMENT_ORDER

# ---------------------------------------------------------------------------
# Global safety net: block unexpected outbound HTTP calls during Streamlit imports
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def mock_requests_for_streamlit() -> Iterable[None]:
    """Prevent real HTTP calls when modules are imported at test time."""
    fake_response = Mock()
    fake_response.json.return_value = []
    fake_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=fake_response):
        yield


# ---------------------------------------------------------------------------
# Utility fixtures shared across Streamlit component tests
# ---------------------------------------------------------------------------


@pytest.fixture
def make_response() -> Callable[[Any], Mock]:
    """Factory returning a Mock response with the provided payload."""

    def _factory(payload: Any) -> Mock:
        fake_response = Mock()
        fake_response.json.return_value = payload
        fake_response.raise_for_status.return_value = None
        return fake_response

    return _factory


@pytest.fixture
def top_contributors_payload() -> List[List[int]]:
    return [[i, 20 - i] for i in range(101, 111)]


@pytest.fixture
def duration_distribution_payload() -> list[dict[str, Any]]:
    return [
        {
            "duration_bin": "0-15",
            "count": 100,
            "share": 50.0,
            "avg_duration_in_bin": 10.0,
            "cum_share": 50.0,
        },
        {
            "duration_bin": "15-30",
            "count": 60,
            "share": 30.0,
            "avg_duration_in_bin": 20.0,
            "cum_share": 80.0,
        },
        {
            "duration_bin": "30+",
            "count": 40,
            "share": 20.0,
            "avg_duration_in_bin": 45.0,
            "cum_share": 100.0,
        },
    ]


@pytest.fixture
def duration_vs_recipe_payload() -> list[dict[str, Any]]:
    return [
        {"contributor_id": 1, "recipe_count": 5, "avg_duration": 25.0, "median_duration": 20.0},
        {"contributor_id": 2, "recipe_count": 10, "avg_duration": 27.0, "median_duration": 25.0},
        {"contributor_id": 3, "recipe_count": 15, "avg_duration": 26.0, "median_duration": 24.0},
    ]


@pytest.fixture
def rating_distribution_payload() -> list[dict[str, Any]]:
    return [
        {
            "rating_bin": "0-1",
            "count": 5,
            "share": 10.0,
            "avg_rating_in_bin": 0.5,
            "cum_share": 10.0,
        },
        {
            "rating_bin": "1-2",
            "count": 10,
            "share": 20.0,
            "avg_rating_in_bin": 1.5,
            "cum_share": 30.0,
        },
        {
            "rating_bin": "4-5",
            "count": 30,
            "share": 70.0,
            "avg_rating_in_bin": 4.5,
            "cum_share": 100.0,
        },
    ]


@pytest.fixture
def rating_vs_recipes_payload() -> list[dict[str, Any]]:
    return [
        {"contributor_id": 1, "recipe_count": 5, "avg_rating": 3.8, "median_rating": 3.7},
        {"contributor_id": 2, "recipe_count": 12, "avg_rating": 4.0, "median_rating": 4.0},
        {"contributor_id": 3, "recipe_count": 20, "avg_rating": 4.2, "median_rating": 4.1},
    ]


@pytest.fixture
def top10_vs_global_payload() -> list[dict[str, Any]]:
    return [
        {
            "population": "top_10_percent",
            "contributor_count": 100,
            "avg_duration_minutes": 30,
            "avg_rating": 4.1,
            "avg_comments": 8,
        },
        {
            "population": "global",
            "contributor_count": 1000,
            "avg_duration_minutes": 28,
            "avg_rating": 4.0,
            "avg_comments": 3,
        },
    ]


@pytest.fixture
def tags_by_segment_payload() -> list[dict[str, Any]]:
    return [
        {
            "segment": 0,
            "persona": SEGMENT_ORDER[0],
            "tag": "preparation",
            "count": 50,
            "share_pct": 5.0,
        },
        {
            "segment": 0,
            "persona": SEGMENT_ORDER[0],
            "tag": "main-ingredient",
            "count": 30,
            "share_pct": 3.0,
        },
        {
            "segment": 1,
            "persona": SEGMENT_ORDER[1],
            "tag": "time-to-make",
            "count": 70,
            "share_pct": 7.0,
        },
        {
            "segment": 1,
            "persona": SEGMENT_ORDER[1],
            "tag": "dietary",
            "count": 20,
            "share_pct": 2.0,
        },
    ]
