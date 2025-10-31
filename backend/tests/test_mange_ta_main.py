import importlib
import io
import logging
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from dependency_injector import providers
from fastapi import Request
from fastapi.testclient import TestClient

import service.main as service_main
from service.container import Container
from service.layers import logger as backend_logger
from service.layers.api import mange_ta_main as api_module
from service.layers.application import mange_ta_main as mtm
from service.layers.application.data_cleaning import (
    clean_data,
    normalize_ids,
    remove_outliers,
)
from service.layers.application.exceptions import (
    DataNormalizationError,
    UnsupportedAnalysisError,
)
from service.layers.application.interfaces.interface import IDataAdapter
from service.layers.application.mange_ta_main import AnalysisType, DataAnylizer
from service.layers.domain.mange_ta_main import SERVICE_PREFIX
from service.layers.infrastructure.csv_adapter import CSVAdapter
from service.layers.infrastructure.types import DataType
from service.layers.logger import struct_logger
from service.main import app, lifespan

# --------------------------------------------------------------------------------------
# Tests for review analytics (existing ones extended)
# --------------------------------------------------------------------------------------


def test_review_overview_metrics(sample_recipes: pd.DataFrame, sample_interactions: pd.DataFrame):
    overview = mtm.review_overview(sample_recipes, sample_interactions)
    metrics = {row["metric"]: row["value"] for _, row in overview.iterrows()}

    assert metrics["total_reviews"] == 3
    assert metrics["recipes_with_reviews"] == 2
    assert metrics["total_recipes"] == 3
    assert metrics["share_recipes_reviewed_pct"] == pytest.approx(66.67, rel=1e-3)
    assert metrics["unique_reviewers"] == 3
    assert metrics["avg_reviews_per_recipe"] == pytest.approx(1.5)
    assert metrics["median_reviews_per_recipe"] == pytest.approx(1.5)
    assert metrics["empty_review_ratio_pct"] == pytest.approx(40.0)
    assert metrics["avg_review_length_words"] == pytest.approx(1.7, rel=1e-2)
    assert metrics["median_review_length_words"] == pytest.approx(2.0)
    assert metrics["avg_rating_given"] == pytest.approx(4.33, rel=1e-3)


def test_review_distribution_per_recipe(
    sample_recipes: pd.DataFrame, sample_interactions: pd.DataFrame
):
    distribution = mtm.review_distribution_per_recipe(sample_recipes, sample_interactions)
    assert distribution["recipe_count"].sum() == len(sample_recipes)

    bins_to_counts = dict(zip(distribution["reviews_bin"], distribution["recipe_count"]))

    assert bins_to_counts.get("0", 0) == 1
    assert bins_to_counts.get("1", 0) == 1
    assert bins_to_counts.get("2", 0) == 1


def test_reviewer_reviews_vs_recipes(
    sample_recipes: pd.DataFrame, sample_interactions: pd.DataFrame
):
    df = mtm.reviewer_reviews_vs_recipes(sample_recipes, sample_interactions)

    row_u1 = df[df["user_id"] == "u1"].iloc[0]
    assert row_u1["reviews_count"] == 1
    assert row_u1["recipes_published"] == 2
    assert row_u1["avg_rating_given"] == pytest.approx(3.5)

    row_u2 = df[df["user_id"] == "u2"].iloc[0]
    assert row_u2["reviews_count"] == 1
    assert row_u2["recipes_published"] == 1
    assert row_u2["avg_rating_given"] == pytest.approx(5.0)

    row_u3 = df[df["user_id"] == "u3"].iloc[0]
    assert row_u3["reviews_count"] == 1
    assert row_u3["recipes_published"] == 0
    assert row_u3["avg_rating_given"] == pytest.approx(4.0)


def test_review_overview_missing_columns(sample_interactions: pd.DataFrame):
    assert mtm.review_overview(pd.DataFrame(), sample_interactions).empty
    assert mtm.review_overview(pd.DataFrame({"name": ["A"]}), pd.DataFrame()).empty
    assert mtm.review_overview(pd.DataFrame({"foo": [1]}), sample_interactions).empty

    recipes = pd.DataFrame({"id": [1], "contributor_id": ["u1"]})
    interactions = pd.DataFrame({"recipe_id": [1], "review": ["Great"]})
    result = mtm.review_overview(recipes, interactions)
    assert "avg_rating_given" not in result["metric"].values


def test_review_distribution_per_recipe_edge_cases(
    sample_recipes: pd.DataFrame, sample_interactions: pd.DataFrame
):
    assert mtm.review_distribution_per_recipe(None, sample_interactions).empty
    no_cols = mtm.review_distribution_per_recipe(pd.DataFrame({"foo": [1]}), sample_interactions)
    assert no_cols.empty
    too_short = mtm.review_distribution_per_recipe(sample_recipes, sample_interactions, bins=[0])
    assert too_short.empty

    zero_share = mtm.review_distribution_per_recipe(
        sample_recipes,
        sample_interactions,
        bins=[0, 2],
    )
    assert isinstance(zero_share, pd.DataFrame)


def test_reviews_vs_rating(sample_recipes: pd.DataFrame, sample_interactions: pd.DataFrame):
    result = mtm.reviews_vs_rating(sample_recipes, sample_interactions)

    assert set(result["recipe_id"].tolist()) == {1, 3}

    recipe_one = result[result["recipe_id"] == 1].iloc[0]
    assert recipe_one["review_count"] == 2
    assert recipe_one["avg_rating"] == pytest.approx(4.5)
    assert recipe_one["contributor_id"] == "u1"
    assert recipe_one["recipe_name"] == "Recipe A"

    recipe_three = result[result["recipe_id"] == 3].iloc[0]
    assert recipe_three["review_count"] == 1
    assert recipe_three["avg_rating"] == pytest.approx(3.0)
    assert recipe_three["contributor_id"] == "u1"
    assert recipe_three["recipe_name"] == "Recipe C"


def test_reviews_vs_rating_edge_cases():
    empty = mtm.reviews_vs_rating(pd.DataFrame(), pd.DataFrame())
    assert empty.empty

    missing_cols = mtm.reviews_vs_rating(pd.DataFrame({"id": [1]}), pd.DataFrame())
    assert missing_cols.empty


# --------------------------------------------------------------------------------------
# Tests covering the remaining analytics helpers
# --------------------------------------------------------------------------------------


def test_parse_tags_to_list_variants():
    assert mtm._parse_tags_to_list(["A", " B "]) == ["a", "b"]
    assert mtm._parse_tags_to_list("['A','C']") == ["a", "c"]
    assert mtm._parse_tags_to_list("a, b ,c") == ["a", "b", "c"]
    assert mtm._parse_tags_to_list(np.nan) == []
    assert mtm._parse_tags_to_list("not a list]") == ["not a list]"]
    assert mtm._parse_tags_to_list("[broken") == ["[broken"]


def test_find_col_variants(sample_recipes: pd.DataFrame):
    assert mtm._find_col(sample_recipes, ["ID"]) == "id"
    assert mtm._find_col(sample_recipes, ["contributor"]) == "contributor_id"
    assert mtm._find_col(sample_recipes, ["contrib"]) == "contributor_id"
    assert mtm._find_col(sample_recipes, ["minutes"]) == "minutes"
    assert mtm._find_col(sample_recipes, ["unknown"]) is None


def test_non_empty_text_and_word_count(sample_interactions: pd.DataFrame):
    mask = mtm._non_empty_text_mask(sample_interactions["review"])
    assert mask.tolist() == [True, True, True, False, False]
    words = mtm._word_count(sample_interactions["review"])
    assert words.iloc[0] == 1
    assert words.iloc[1] == 2


def test_most_and_best_contributors(rich_recipes: pd.DataFrame, rich_interactions: pd.DataFrame):
    most = mtm.most_recipes_contributors(rich_recipes)
    assert str(most.iloc[0]["contributor_id"]) == "c1"

    best = mtm.best_ratings_contributors(rich_recipes, rich_interactions)
    assert "contributor_id" in best.columns
    assert best.empty or (best["num_recipes"] >= 5).all()


def test_average_duration_distribution_variants(rich_recipes: pd.DataFrame):
    overall = mtm.average_duration_distribution(rich_recipes, duration_col="minutes")
    assert overall["share"].sum() == pytest.approx(100.0)

    default_labels = mtm.average_duration_distribution(rich_recipes, duration_col="minutes")
    assert "120+" in default_labels["duration_bin"].astype(str).tolist()

    grouped = mtm.average_duration_distribution(
        rich_recipes,
        duration_col="minutes",
        group_cols=["contributor_id"],
        bins=[0, 30, 60, np.inf],
        labels=["short", "medium", "long"],
    )
    assert set(grouped["duration_bin"].unique()) <= {"short", "medium", "long"}

    custom = mtm.average_duration_distribution(rich_recipes, duration_col="minutes", bins=3)
    assert custom["duration_bin"].notna().all()


def test_duration_vs_recipe_count_empty_branch():
    df = pd.DataFrame({"id": [1], "contributor_id": [np.nan], "minutes": [np.nan]})
    result = mtm.duration_vs_recipe_count(df, duration_col="minutes")
    assert result.empty


def test_duration_vs_recipe_count(rich_recipes: pd.DataFrame):
    result = mtm.duration_vs_recipe_count(rich_recipes, duration_col="minutes")
    assert "avg_duration" in result.columns
    assert "median_duration" in result.columns


def test_top_10_percent_contributors(rich_recipes: pd.DataFrame, rich_interactions: pd.DataFrame):
    result = mtm.top_10_percent_contributors(
        rich_recipes, rich_interactions, duration_col="minutes"
    )
    assert set(result["population"]) == {"top_10_percent", "global"}


def test_compute_user_segments_and_tags(
    rich_recipes: pd.DataFrame, rich_interactions: pd.DataFrame
):
    segments = mtm.compute_user_segments(rich_recipes, rich_interactions, duration_col="minutes")
    if not segments.empty:
        assert {"contributor_id", "segment", "persona"}.issubset(segments.columns)
        top_tags = mtm.top_tags_by_segment_from_users(
            rich_recipes, segments, tags_col="tags", top_k=3
        )
    if not top_tags.empty:
        assert {"segment", "persona", "tag"}.issubset(top_tags.columns)

    empty_segments = mtm.compute_user_segments(
        pd.DataFrame({"id": [], "contributor_id": [], "minutes": []}),
        pd.DataFrame({"recipe_id": [], "rating": []}),
        duration_col="minutes",
    )
    assert empty_segments.empty
    assert mtm.top_tags_by_segment_from_users(rich_recipes, empty_segments).empty


def test_rating_distribution_branches(rich_recipes: pd.DataFrame, rich_interactions: pd.DataFrame):
    dist = mtm.rating_distribution(rich_recipes, rich_interactions)
    assert "rating_bin" in dist.columns

    custom = mtm.rating_distribution(
        rich_recipes,
        rich_interactions,
        bins=[0, 3, 5],
        labels=["low", "high"],
    )
    assert set(custom["rating_bin"]) <= {"low", "high"}

    no_contrib = mtm.rating_distribution(
        pd.DataFrame({"id": [1], "name": ["A"], "contributor_id": [np.nan]}),
        rich_interactions,
    )
    assert no_contrib.empty or no_contrib["count"].eq(0).all()

    zero_bins = mtm.rating_distribution(rich_recipes, rich_interactions, bins=[0])
    assert zero_bins.empty

    alt_contrib = mtm.rating_distribution(
        pd.DataFrame({"recipe_id": [1, 2], "author": ["x", "y"]}),
        pd.DataFrame({"recipe_id": [1, 2], "rating": [4, 5]}),
    )
    assert not alt_contrib.empty
    assert alt_contrib["count"].sum() == 1

    empty = mtm.rating_distribution(None, rich_interactions)
    assert empty.empty


def test_rating_vs_recipe_count_branches(
    rich_recipes: pd.DataFrame, rich_interactions: pd.DataFrame
):
    result = mtm.rating_vs_recipe_count(rich_recipes, rich_interactions)
    assert {"contributor_id", "avg_rating"}.issubset(result.columns)

    fallback = mtm.rating_vs_recipe_count(rich_recipes, pd.DataFrame())
    assert fallback["avg_rating"].isna().all()

    assert mtm.rating_vs_recipe_count(pd.DataFrame(), rich_interactions).empty

    missing_cols = mtm.rating_vs_recipe_count(
        pd.DataFrame({"name": ["foo"]}),
        rich_interactions,
    )
    assert missing_cols.empty


def test_reviewer_activity_and_trend(rich_interactions: pd.DataFrame):
    activity = mtm.reviewer_activity(rich_interactions)
    assert {"reviewer_id", "reviews_count"}.issubset(activity.columns)

    assert mtm.reviewer_activity(pd.DataFrame()).empty

    assert mtm.reviewer_activity(pd.DataFrame({"review": ["test"]})).empty

    no_reviews = mtm.reviewer_activity(pd.DataFrame({"user_id": [1], "review": [" "]}))
    assert no_reviews.empty

    missing_user = mtm.reviewer_activity(pd.DataFrame({"review": ["ok"], "rating": [5]}))
    assert missing_user.empty

    without_rating = mtm.reviewer_activity(pd.DataFrame({"user_id": ["u"], "review": ["ok"]}))
    assert (
        "avg_rating_given" not in without_rating.columns
        or without_rating["avg_rating_given"].isna().all()
    )

    trend = mtm.review_temporal_trend(rich_interactions)
    assert "period" in trend.columns

    empty_trend = mtm.review_temporal_trend(pd.DataFrame())
    assert empty_trend.empty

    missing = mtm.review_temporal_trend(pd.DataFrame({"comment": ["hello"]}))
    assert missing.empty

    no_reviews = mtm.review_temporal_trend(pd.DataFrame({"date": ["2024-01-01"], "review": [None]}))
    assert no_reviews.empty

    trend_no_date = mtm.review_temporal_trend(pd.DataFrame({"review": ["ok"]}))
    assert trend_no_date.empty


def test_reviewer_reviews_vs_recipes_empty():
    result = mtm.reviewer_reviews_vs_recipes(pd.DataFrame(), pd.DataFrame())
    assert result.empty

    missing_users = mtm.reviewer_reviews_vs_recipes(pd.DataFrame({"id": [1]}), pd.DataFrame())
    assert missing_users.empty

    no_user_col = mtm.reviewer_reviews_vs_recipes(
        pd.DataFrame({"id": [1], "contributor_id": ["c1"]}),
        pd.DataFrame({"recipe_id": [1], "rating": [5], "review": ["OK"]}),
    )
    assert no_user_col.empty


# --------------------------------------------------------------------------------------
# Tests for orchestration (DataAnylizer) and enum coverage
# --------------------------------------------------------------------------------------


class StubAdapter(IDataAdapter):
    def __init__(self, recipes: pd.DataFrame, interactions: pd.DataFrame):
        self._recipes = recipes
        self._interactions = interactions
        self.saved = {}

    def load(self, data_type: DataType, raw: bool = False) -> pd.DataFrame:
        return self._recipes if data_type == DataType.RECIPES else self._interactions

    def save(self, df: pd.DataFrame, data_type: DataType) -> None:
        self.saved[data_type] = df.copy()


def test_data_analyzer_process_all_types(
    rich_recipes: pd.DataFrame, rich_interactions: pd.DataFrame
):
    adapter = StubAdapter(rich_recipes, rich_interactions)
    analyzer = DataAnylizer(adapter)

    for analysis in [
        AnalysisType.NUMBER_RECIPES,
        AnalysisType.BEST_RECIPES,
        AnalysisType.DURATION_DISTRIBUTION,
        AnalysisType.DURATION_VS_RECIPE_COUNT,
        AnalysisType.TOP_10_PERCENT_CONTRIBUTORS,
        AnalysisType.USER_SEGMENTS,
        AnalysisType.TOP_TAGS_BY_SEGMENT,
        AnalysisType.RATING_DISTRIBUTION,
        AnalysisType.RATING_VS_RECIPES,
        AnalysisType.REVIEW_OVERVIEW,
        AnalysisType.REVIEW_DISTRIBUTION,
        AnalysisType.REVIEWER_ACTIVITY,
        AnalysisType.REVIEW_TEMPORAL_TREND,
        AnalysisType.REVIEWS_VS_RATING,
        AnalysisType.REVIEWER_VS_RECIPES,
    ]:
        df = analyzer.process_data(analysis)
        assert isinstance(df, pd.DataFrame)


def test_data_analyzer_invalid_analysis(
    rich_recipes: pd.DataFrame, rich_interactions: pd.DataFrame
):
    analyzer = DataAnylizer(StubAdapter(rich_recipes, rich_interactions))
    with pytest.raises(UnsupportedAnalysisError):
        analyzer.process_data(AnalysisType.NO_ANALYSIS)


# --------------------------------------------------------------------------------------
# Data cleaning and infrastructure helpers
# --------------------------------------------------------------------------------------


def test_remove_outliers():
    df = pd.DataFrame({"value": [1, 2, 3, 1000]})
    cleaned = remove_outliers(df, factor=1)
    assert 1000 not in cleaned["value"].values


def test_normalize_ids_for_recipes_and_interactions():
    recipes = pd.DataFrame({"id": [10, 20], "contributor_id": ["A", "B"]})
    normalized_recipes = normalize_ids(recipes.copy(), DataType.RECIPES)
    assert normalized_recipes["id"].tolist() == [0, 1]

    interactions = pd.DataFrame({"user_id": ["x", "y"]})
    normalized_interactions = normalize_ids(interactions.copy(), DataType.INTERACTIONS)
    assert normalized_interactions["user_id"].tolist() == [1, 2]

    with pytest.raises(DataNormalizationError):
        normalize_ids(recipes, cast(DataType, "weird"))  # type: ignore[arg-type]


class InterfaceConcrete(IDataAdapter):
    def load(self, data_type: DataType, raw: bool = False) -> pd.DataFrame:
        super().load(data_type, raw)
        return pd.DataFrame()

    def save(self, df: pd.DataFrame, data_type: DataType) -> None:
        super().save(df, data_type)


def test_interface_concrete_invocation():
    concrete = InterfaceConcrete()
    assert isinstance(concrete.load(DataType.RECIPES), pd.DataFrame)
    concrete.save(pd.DataFrame(), DataType.RECIPES)


def test_clean_data_with_dummy_adapter(tmp_path):
    raw_recipes = pd.DataFrame({"name": ["Cake"], "id": [1], "contributor_id": ["user"]})
    raw_interactions = pd.DataFrame({"user_id": ["x"], "rating": [5], "review": ["Nice"]})

    class DummyAdapter(IDataAdapter):
        def __init__(self):
            self.saved = {}

        def load(self, data_type: DataType, raw: bool = False) -> pd.DataFrame:
            if data_type == DataType.RECIPES:
                return raw_recipes.copy()
            return raw_interactions.copy()

        def save(self, df: pd.DataFrame, data_type: DataType) -> None:
            self.saved[data_type] = df

    adapter = DummyAdapter()
    cleaned_recipes = clean_data(adapter, DataType.RECIPES)
    cleaned_interactions = clean_data(adapter, DataType.INTERACTIONS)

    assert cleaned_recipes and cleaned_interactions
    assert DataType.RECIPES in adapter.saved and DataType.INTERACTIONS in adapter.saved

    with pytest.raises(DataNormalizationError):
        clean_data(adapter, cast(DataType, "strange"))  # type: ignore[arg-type]


def test_csv_adapter_load_and_save(tmp_path: Path):
    adapter = CSVAdapter(data_dir=tmp_path)

    # load missing file -> empty dataframe
    df_missing = adapter.load(DataType.RECIPES)
    assert df_missing.empty
    assert adapter.load(DataType.RECIPES, raw=True).empty

    df = pd.DataFrame({"id": [1], "name": ["Test"]})
    adapter.save(df, DataType.RECIPES)
    loaded = adapter.load(DataType.RECIPES)
    assert loaded.equals(df.astype(object))


# --------------------------------------------------------------------------------------
# Container, domain, logger, and app lifespan
# --------------------------------------------------------------------------------------


def test_container_provides_singleton(rich_recipes: pd.DataFrame, rich_interactions: pd.DataFrame):
    adapter = StubAdapter(rich_recipes, rich_interactions)
    container = Container()
    container.csv_adapter.override(providers.Object(adapter))

    analyzer_one = container.data_analyzer()
    analyzer_two = container.data_analyzer()
    assert analyzer_one is analyzer_two


def test_domain_and_logger_usage(caplog):
    struct_logger.info("Testing logger output")
    assert SERVICE_PREFIX == "mange_ta_main"


def test_keyword_friendly_logger_backend(tmp_path: Path):
    base_logger = logging.getLogger("backend.test.logger")
    previous_handlers = list(base_logger.handlers)
    previous_level = base_logger.level
    previous_propagate = base_logger.propagate

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    base_logger.handlers = [handler]
    base_logger.setLevel(logging.DEBUG)
    base_logger.propagate = False

    fallback = backend_logger._KeywordFriendlyLogger(base_logger)

    fallback.info("Loaded data", count=3, status="ok")
    fallback.warning("Slow query", duration=1.2)
    fallback.error("Failed", reason="timeout")
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        fallback.exception("Processing failure")
    fallback.debug("Raw event")
    fallback.setLevel(logging.INFO)  # exercise __getattr__

    handler.flush()
    log_output = stream.getvalue()
    assert "count=3" in log_output
    assert "reason=timeout" in log_output
    assert "Processing failure" in log_output and "exc_info=True" in log_output

    base_logger.handlers = previous_handlers
    base_logger.setLevel(previous_level)
    base_logger.propagate = previous_propagate


def test_structlog_configuration_branch_backend(monkeypatch):
    module_name = "service.layers.logger"
    original_module = sys.modules.pop(module_name, None)

    fake_stream = io.StringIO()

    class DummyFileHandler(logging.StreamHandler):
        def __init__(self, filename, mode="a", encoding=None, delay=False):
            super().__init__(fake_stream)

    fake_configure = MagicMock()
    fake_get_logger = MagicMock(return_value="fake_struct_logger")

    fake_structlog = types.SimpleNamespace(
        contextvars=types.SimpleNamespace(merge_contextvars="merge"),
        processors=types.SimpleNamespace(
            add_log_level="add",
            TimeStamper=lambda **kwargs: "timestamp",
            StackInfoRenderer=lambda: "stack",
            format_exc_info="format",
        ),
        stdlib=types.SimpleNamespace(LoggerFactory=lambda: "factory"),
        make_filtering_bound_logger=lambda *args, **kwargs: "wrapper",
        configure=fake_configure,
        get_logger=fake_get_logger,
    )
    fake_structlog_dev = types.SimpleNamespace(ConsoleRenderer=lambda: "console")

    monkeypatch.setitem(sys.modules, "structlog", fake_structlog)
    monkeypatch.setitem(sys.modules, "structlog.dev", fake_structlog_dev)
    monkeypatch.setattr(logging, "FileHandler", DummyFileHandler)

    imported = importlib.import_module(module_name)
    assert imported.struct_logger == "fake_struct_logger"
    fake_configure.assert_called_once()
    fake_get_logger.assert_called_once()

    sys.modules.pop(module_name, None)
    sys.modules.pop("structlog", None)
    sys.modules.pop("structlog.dev", None)
    if original_module is not None:
        sys.modules[module_name] = original_module
    else:
        importlib.import_module(module_name)


def test_lifespan_context(monkeypatch):
    import asyncio

    dummy_container = MagicMock()
    dummy_container.data_analyzer.return_value = MagicMock()
    monkeypatch.setattr(service_main, "Container", lambda: dummy_container)

    async def _run():
        async with lifespan(app):
            pass

    asyncio.run(_run())
    assert dummy_container.data_analyzer.called


# --------------------------------------------------------------------------------------
# API route coverage
# --------------------------------------------------------------------------------------


def test_health_endpoint(api_client: TestClient):
    response = api_client.get(f"/{SERVICE_PREFIX}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_load_data_recipes_and_interactions(api_client: TestClient):
    recipes = api_client.get(f"/{SERVICE_PREFIX}/load-data")
    assert recipes.status_code == 200

    interactions = api_client.get(
        f"/{SERVICE_PREFIX}/load-data", params={"data_type": DataType.INTERACTIONS.value}
    )
    assert interactions.status_code == 200


def test_load_data_invalid_branch(api_stub_analyzer):
    with pytest.raises(api_module.HTTPException):
        api_module.get_data(data_type=cast(DataType, "invalid"), data_analyzer=api_stub_analyzer)


@pytest.mark.parametrize(
    "endpoint",
    [
        "most-recipes-contributors",
        "best-ratings-contributors",
        "duration-distribution",
        "duration-vs-recipe-count",
        "top-10-percent-contributors",
        "user-segments",
        "top-tags-by-segment",
        "rating-distribution",
        "rating-vs-recipes",
        "review-overview",
        "review-distribution",
        "top-reviewers",
        "review-trend",
        "reviews-vs-rating",
        "reviewer-vs-recipes",
    ],
)
def test_analysis_endpoints(api_client: TestClient, endpoint: str):
    response = api_client.get(f"/{SERVICE_PREFIX}/{endpoint}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_clean_raw_data_endpoint(api_client: TestClient, monkeypatch):
    monkeypatch.setattr(api_module, "clean_data", lambda adapter, data_type: [{"ok": True}])
    response = api_client.post(
        f"/{SERVICE_PREFIX}/clean-raw-data",
        params={"data_type": DataType.RECIPES.value},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_get_data_analyzer_direct():
    container = MagicMock()
    analyzer = MagicMock()
    container.data_analyzer.return_value = analyzer
    request = cast(
        Request, SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(container=container)))
    )
    assert api_module.get_data_analyzer(request) is analyzer
