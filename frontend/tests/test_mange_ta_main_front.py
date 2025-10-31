import importlib
import io
import logging
import sys
import types
from unittest.mock import MagicMock, Mock, patch

import altair as alt
import numpy as np
import pandas as pd
import pytest
import requests

from ..service.components.tab01_top_contributors import render_top_contributors
from ..service.components.tab02_duration_recipe import render_duration_recipe
from ..service.components.tab03_reviews import _format_metric
from ..service.components.tab04_rating import render_user_rating
from ..service.components.tab06_top10_analyse import render_top10_vs_global
from ..service.components.tab07_tags import SEGMENT_ORDER, render_top_tags_by_segment
from ..service.domain import BASE_URL
from ..service.logger import struct_logger
from ..service.src.http_client import BackendAPIError


def test_base_url_is_non_empty_string():
    assert isinstance(BASE_URL, str)
    assert BASE_URL.strip() != ""


def test_altair_chart_smoke():
    df = pd.DataFrame({"x": [1], "y": [1]})
    chart = alt.Chart(df).mark_point().encode(x="x", y="y")
    assert chart is not None
    assert hasattr(chart, "to_dict")


def test_numpy_pandas_basic_ops():
    arr = np.array([1, 2, 3])
    assert arr.sum() == 6
    df = pd.DataFrame({"a": [1, 2, 3]})
    assert df["a"].mean() == 2


def test_logger_available():
    # struct_logger can be a logger or factory; ensure it's usable
    assert struct_logger is not None


def test_component_symbols_are_callable():
    funcs = [
        render_top_contributors,
        render_duration_recipe,
        render_user_rating,
        render_top10_vs_global,
        render_top_tags_by_segment,
    ]
    for fn in funcs:
        assert callable(fn)


def test_segment_order_type():
    assert isinstance(SEGMENT_ORDER, (list, tuple))


def test_requests_can_be_mocked_without_calls():
    with patch.object(requests, "get", MagicMock(return_value=Mock(status_code=200))) as mocked_get:
        # Do not invoke; just ensure mocking wiring works and no accidental I/O happens.
        mocked_get.assert_not_called()


def test_format_metric_various_types():
    assert _format_metric("total_reviews", 1250) == "1 250"
    assert _format_metric("share_pct", 87.345) == "87.3%"
    assert _format_metric("avg_reviews_per_recipe", 3.50) == "3.5"
    assert _format_metric("median_review_length_words", 12.0) == "12"
    assert _format_metric("custom", 1.23456) == "1.23"
    assert _format_metric("anything", None) == "-"
    assert _format_metric("text", "Hello") == "Hello"


def test_render_top_contributors_with_data(top_contributors_payload, make_response):
    fake_response = make_response(top_contributors_payload)
    module_path = render_top_contributors.__module__
    with (
        patch(f"{module_path}.fetch_backend_json", return_value=fake_response) as mock_fetch,
        patch(f"{module_path}.st") as st_mock,
    ):

        # Make st.columns return three context-manageable columns
        col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()
        st_mock.columns.return_value = (col1, col2, col3)

        # Act
        render_top_contributors(show_title=True)

        # Assert: network called once on expected endpoint
        mock_fetch.assert_called_once()
        assert mock_fetch.call_args.kwargs["ttl"] == 120
        assert mock_fetch.call_args.args[0] == "most-recipes-contributors"

        # Assert: basic Streamlit render pipeline executed
        st_mock.title.assert_called_once()
        st_mock.subheader.assert_called_once()
        assert st_mock.metric.call_count >= 3
        st_mock.bar_chart.assert_called_once()
        st_mock.dataframe.assert_called_once()

        # CSV download button label should be as defined
        args, kwargs = st_mock.download_button.call_args
        assert args[0].startswith("📥 ")
        assert "text/csv" in args or kwargs.get("mime") == "text/csv"

        # No warnings or errors when data is present
        st_mock.warning.assert_not_called()
        st_mock.error.assert_not_called()


def test_render_top_contributors_no_data(make_response):
    fake_response = make_response([])
    module_path = render_top_contributors.__module__
    with (
        patch(f"{module_path}.fetch_backend_json", return_value=fake_response),
        patch(f"{module_path}.st") as st_mock,
    ):
        render_top_contributors(show_title=False)
        st_mock.warning.assert_called_once()
        st_mock.error.assert_not_called()


def test_render_duration_recipe_with_data(
    duration_distribution_payload, duration_vs_recipe_payload, make_response
):
    fake_resp_dist = make_response(duration_distribution_payload)
    fake_resp_corr = make_response(duration_vs_recipe_payload)

    module_path = render_duration_recipe.__module__
    with (
        patch(
            f"{module_path}.fetch_backend_json", side_effect=[fake_resp_dist, fake_resp_corr]
        ) as mock_fetch,
        patch(f"{module_path}.st") as st_mock,
    ):

        # Ensure radio returns a valid option
        st_mock.radio.return_value = "Nombre de recettes"
        # Make st.columns return three context-manageable columns
        col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()
        st_mock.columns.return_value = (col1, col2, col3)

        # Act
        render_duration_recipe()

        # Assert: two endpoints called
        assert mock_fetch.call_count == 2
        endpoints = [call.args[0] for call in mock_fetch.call_args_list]
        assert endpoints == ["duration-distribution", "duration-vs-recipe-count"]

        # Streamlit interactions occur
        st_mock.header.assert_called()
        st_mock.subheader.assert_called()
        assert st_mock.metric.call_count >= 3
        st_mock.bar_chart.assert_called()
        st_mock.line_chart.assert_called()
        st_mock.dataframe.assert_called()
        st_mock.download_button.assert_called()
        # Correlation chart rendered
        st_mock.altair_chart.assert_called()
        # No error on happy path
        st_mock.error.assert_not_called()


def test_render_user_rating_with_data(
    rating_distribution_payload, rating_vs_recipes_payload, make_response
):
    fake_resp_dist = make_response(rating_distribution_payload)
    fake_resp_corr = make_response(rating_vs_recipes_payload)

    module_path = render_user_rating.__module__
    with (
        patch(
            f"{module_path}.fetch_backend_json", side_effect=[fake_resp_dist, fake_resp_corr]
        ) as mock_fetch,
        patch(f"{module_path}.st") as st_mock,
    ):

        st_mock.radio.return_value = "Nombre de contributeurs"
        col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()
        st_mock.columns.return_value = (col1, col2, col3)

        render_user_rating()

        assert mock_fetch.call_count == 2
        endpoints = [call.args[0] for call in mock_fetch.call_args_list]
        assert endpoints == ["rating-distribution", "rating-vs-recipes"]

        st_mock.header.assert_called()
        st_mock.subheader.assert_called()
        assert st_mock.metric.call_count >= 3
        st_mock.bar_chart.assert_called()
        st_mock.dataframe.assert_called()
        st_mock.download_button.assert_called()
        st_mock.altair_chart.assert_called()
        st_mock.error.assert_not_called()


def test_render_top10_vs_global_with_data(top10_vs_global_payload, make_response):
    fake_resp = make_response(top10_vs_global_payload)
    module_path = render_top10_vs_global.__module__
    with (
        patch(f"{module_path}.fetch_backend_json", return_value=fake_resp) as mock_fetch,
        patch(f"{module_path}.st") as st_mock,
    ):

        col1, col2 = MagicMock(), MagicMock()
        st_mock.columns.return_value = (col1, col2)

        render_top10_vs_global()

        mock_fetch.assert_called_once()
        assert mock_fetch.call_args.args[0] == "top-10-percent-contributors"

        assert st_mock.metric.call_count >= 2
        assert st_mock.altair_chart.call_count >= 1
        st_mock.dataframe.assert_called_once()
        st_mock.download_button.assert_called_once()
        st_mock.error.assert_not_called()


def test_render_top_tags_by_segment_with_data(tags_by_segment_payload, make_response):
    fake_resp = make_response(tags_by_segment_payload)
    module_path = render_top_tags_by_segment.__module__
    with (
        patch(f"{module_path}.fetch_backend_json", return_value=fake_resp) as mock_fetch,
        patch(f"{module_path}.st") as st_mock,
    ):

        st_mock.columns.return_value = (MagicMock(), MagicMock())
        st_mock.radio.return_value = "Volume (count)"

        render_top_tags_by_segment()

        mock_fetch.assert_called_once()
        assert mock_fetch.call_args.args[0] == "top-tags-by-segment"

        # Should render charts and table, and offer a CSV download
        assert st_mock.altair_chart.call_count >= 1
        st_mock.dataframe.assert_called()
        st_mock.download_button.assert_called_once()
        st_mock.error.assert_not_called()


def test_render_sidebar_smoke():
    # Import lazily to avoid circulars
    from ..service.components.sidebar import render_sidebar as _render_sidebar

    module_path = _render_sidebar.__module__
    with patch(f"{module_path}.st") as st_mock:
        # Ensure sidebar context manager behaves
        st_mock.sidebar.__enter__.return_value = MagicMock()
        _render_sidebar()
        # Should style and create links
        st_mock.markdown.assert_called()
        sidebar_links = (
            st_mock.sidebar.__enter__.return_value.page_link.call_count
            if hasattr(st_mock.sidebar.__enter__.return_value, "page_link")
            else 0
        )
        assert st_mock.page_link.call_count + sidebar_links >= 4


def test_pages_imports_smoke_without_network():
    # Import pages with streamlit/requests patched so module-level UI runs safely and no network occurs.

    class _FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return []

    fake_requests = types.SimpleNamespace(get=MagicMock(return_value=_FakeResp()))
    fake_st = MagicMock()
    fake_st.sidebar.__enter__.return_value = MagicMock()
    fake_st.tabs.return_value = (MagicMock(), MagicMock(), MagicMock())

    with patch.dict(sys.modules, {"streamlit": fake_st, "requests": fake_requests}):
        mod_app = importlib.import_module("service.app")
        mod_data = importlib.import_module("service.pages.tab01_data")
        mod_analyse = importlib.import_module("service.pages.tab02_analyse")
        mod_conclusions = importlib.import_module("service.pages.tab03_conclusions")

    # Basic sanity that modules loaded
    assert mod_app is not None and mod_data is not None
    assert mod_analyse is not None and mod_conclusions is not None


def test_keyword_friendly_logger_captures_kwargs():
    from ..service import logger as logger_module

    base_logger = logging.getLogger("frontend.test.logger")
    previous_handlers = list(base_logger.handlers)
    previous_level = base_logger.level
    previous_propagate = base_logger.propagate
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    base_logger.handlers = [handler]
    base_logger.setLevel(logging.DEBUG)
    base_logger.propagate = False

    fallback = logger_module._KeywordFriendlyLogger(base_logger)

    fallback.info("Fetched data", count=3, error="none")
    fallback.bind(user="abc").warning("", reason="coverage")
    try:
        raise ValueError("boom")
    except ValueError:
        fallback.exception("Failure")
    fallback.debug("Just message without kwargs")
    assert fallback.bind() is fallback
    handler.flush()

    log_output = stream.getvalue()
    assert "count=3" in log_output
    assert "reason=coverage" in log_output
    assert "Failure" in log_output and "exc_info=True" in log_output
    underlying = getattr(fallback, "_logger", None)
    if isinstance(underlying, logging.LoggerAdapter):
        assert underlying.logger is base_logger

    base_logger.handlers = previous_handlers
    base_logger.setLevel(previous_level)
    base_logger.propagate = previous_propagate


def test_sidebar_without_context_manager(monkeypatch):
    from ..service.components import sidebar as sidebar_module

    fake_sidebar = types.SimpleNamespace(header=MagicMock(), page_link=MagicMock())
    fake_st = types.SimpleNamespace(markdown=MagicMock(), sidebar=fake_sidebar)

    monkeypatch.setattr(sidebar_module, "st", fake_st)

    sidebar_module.render_sidebar()

    fake_st.markdown.assert_called_once()
    assert fake_sidebar.header.call_count == 1
    assert fake_sidebar.page_link.call_count == 4


def test_render_data_page_success(monkeypatch):
    module_name = "service.pages.tab01_data"
    sys.modules.pop(module_name, None)

    class _Spinner:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    fake_st = types.SimpleNamespace(
        header=MagicMock(),
        markdown=MagicMock(),
        selectbox=lambda *a, **k: "recipes",
        button=lambda *a, **k: True,
        spinner=lambda *a, **k: _Spinner(),
        dataframe=MagicMock(),
        error=MagicMock(),
    )
    fake_sidebar = types.SimpleNamespace(render_sidebar=lambda: None)

    monkeypatch.setitem(sys.modules, "streamlit", fake_st)
    monkeypatch.setitem(sys.modules, "components.sidebar", fake_sidebar)

    imported = importlib.import_module(module_name)

    monkeypatch.setattr(imported, "fetch_backend_json", lambda *a, **k: [{"id": 1, "name": "Test"}])

    imported.render_data_page()

    fake_st.dataframe.assert_called_once()
    fake_st.error.assert_not_called()

    sys.modules.pop(module_name, None)


def test_logger_fallback_branch(monkeypatch):
    module_name = "service.logger"
    original = sys.modules.pop(module_name, None)

    fake_structlog = types.ModuleType("structlog")
    monkeypatch.setitem(sys.modules, "structlog", fake_structlog)
    monkeypatch.delitem(sys.modules, "structlog.dev", raising=False)

    import importlib

    module = importlib.import_module(module_name)
    fallback_logger = module.struct_logger
    assert isinstance(fallback_logger, module._KeywordFriendlyLogger)
    fallback_logger.bind(user="abc").error("fallback error", count=5)
    fallback_logger.debug("fallback debug")

    if original is not None:
        sys.modules[module_name] = original


def test_tab01_data_logs_request_exception(monkeypatch, caplog):
    module_name = "service.pages.tab01_data"
    sys.modules.pop(module_name, None)

    class _Spinner:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    fake_st = types.SimpleNamespace(
        header=lambda *a, **k: None,
        markdown=lambda *a, **k: None,
        selectbox=lambda *a, **k: "recipes",
        button=lambda *a, **k: True,
        spinner=lambda *a, **k: _Spinner(),
        dataframe=lambda *a, **k: None,
        error=MagicMock(),
    )
    fake_sidebar = types.SimpleNamespace(render_sidebar=lambda: None)

    monkeypatch.setitem(sys.modules, "streamlit", fake_st)
    monkeypatch.setitem(sys.modules, "components.sidebar", fake_sidebar)

    def _raise_backend(*args, **kwargs):
        raise BackendAPIError(endpoint="http://fake", details="boom")

    with caplog.at_level(logging.ERROR, logger="mange-ta-main.frontend"):
        imported = importlib.import_module(module_name)
        monkeypatch.setattr(imported, "fetch_backend_json", _raise_backend, raising=False)
        imported.render_data_page()

    sys.modules.pop(module_name, None)

    assert imported is not None
    fake_st.error.assert_called_once()
    assert "boom" in fake_st.error.call_args.args[0]


def test_fetch_backend_json_raises_backend_error(monkeypatch):
    from ..service.src import http_client as http_client_module

    class DummyResponse:
        def raise_for_status(self):
            raise requests.HTTPError("boom")

    monkeypatch.setattr(http_client_module.requests, "get", lambda *a, **k: DummyResponse())

    with pytest.raises(http_client_module.BackendAPIError):
        http_client_module.fetch_backend_json("endpoint")


def test_fetch_backend_json_uses_cache_wrapper(monkeypatch):
    from ..service.src import http_client as http_client_module

    class DummyCache:
        __module__ = "dummy_cache_module"

        def __call__(self, **cache_kwargs):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

                return wrapper

            return decorator

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "ok"}

    monkeypatch.setattr(http_client_module.requests, "get", lambda *a, **k: DummyResponse())

    original_st = http_client_module.st
    http_client_module.st = types.SimpleNamespace(cache_data=DummyCache())
    try:
        result = http_client_module.fetch_backend_json("endpoint", params={"a": 1})
    finally:
        http_client_module.st = original_st

    assert result == {"status": "ok"}


def test_structlog_configuration_branch(monkeypatch):
    module_name = "service.logger"
    original_module = sys.modules.pop(module_name, None)

    fake_configure = MagicMock()
    fake_get_logger = MagicMock(return_value="fake_struct_logger")

    fake_structlog = types.SimpleNamespace(
        contextvars=types.SimpleNamespace(merge_contextvars="merge"),
        processors=types.SimpleNamespace(
            add_log_level="add",
            TimeStamper=lambda **kwargs: "ts",
            StackInfoRenderer=lambda: "stack",
            format_exc_info="fmt",
        ),
        stdlib=types.SimpleNamespace(LoggerFactory=lambda: "factory"),
        make_filtering_bound_logger=lambda *args, **kwargs: "wrapper",
        configure=fake_configure,
        get_logger=fake_get_logger,
    )
    fake_structlog_dev = types.SimpleNamespace(ConsoleRenderer=lambda: "console")

    monkeypatch.setitem(sys.modules, "structlog", fake_structlog)
    monkeypatch.setitem(sys.modules, "structlog.dev", fake_structlog_dev)

    logger_module = importlib.import_module(module_name)

    assert logger_module.struct_logger == "fake_struct_logger"
    fake_configure.assert_called_once()
    fake_get_logger.assert_called_once()

    sys.modules.pop(module_name, None)
    sys.modules.pop("structlog", None)
    sys.modules.pop("structlog.dev", None)

    if original_module is not None:
        sys.modules[module_name] = original_module
    else:
        importlib.import_module(module_name)
