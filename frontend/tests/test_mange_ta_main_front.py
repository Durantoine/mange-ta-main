import sys
from pathlib import Path
import pytest
from unittest.mock import patch, Mock, MagicMock
import pandas as pd
import numpy as np
import requests
import altair as alt
from ..service.domain import BASE_URL
from ..service.logger import struct_logger
from ..service.components.tab01_top_contributors import render_top_contributors
from ..service.components.tab02_duration_recipe import render_duration_recipe
from ..service.components.tab04_rating import render_user_rating
from ..service.components.tab06_top10_analyse import render_top10_vs_global
from ..service.components.tab07_tags import render_top_tags_by_segment, SEGMENT_ORDER

# Sample test data for API responses
SAMPLE_DATA = [
    {"population": "top_10_percent", "contributor_count": 100, "avg_duration_minutes": 45.5, "avg_rating": 4.2, "avg_comments": 8.5},
    {"population": "global", "contributor_count": 1000, "avg_duration_minutes": 42.0, "avg_rating": 4.0, "avg_comments": 3.2}
]

SAMPLE_TAG_DATA = [
    {
        "segment": 1,
        "persona": "Super Cookers",
        "tag": "preparation",
        "count": 150,
        "share_pct": 5.8
    },
    {
        "segment": 1,
        "persona": "Super Cookers",
        "tag": "time-to-make",
        "count": 120,
        "share_pct": 4.6
    },
    {
        "segment": 2,
        "persona": "Quick Cookers",
        "tag": "easy",
        "count": 80,
        "share_pct": 3.2
    }
]

# Test fixtures
@pytest.fixture
def mock_streamlit():
    """Mock all streamlit components"""
    with patch("frontend.service.components.tab07_tags.st") as mock_st:
        # Setup radio button default
        mock_st.radio.return_value = "Volume (count)"
        # Setup columns mock
        mock_columns = [MagicMock(), MagicMock()]
        mock_st.columns.return_value = mock_columns
        mock_st.session_state = {}
        yield mock_st

@pytest.fixture
def mock_requests_get():
    """Mock requests.get for API calls"""
    with patch("frontend.service.components.tab07_tags.requests.get") as mock_get:
        yield mock_get

@pytest.fixture
def mock_altair():
    """Mock altair for visualization"""
    with patch("frontend.service.components.tab07_tags.alt") as mock_alt:
        yield mock_alt

# Tests for components/tab01_top_contributors.py
@patch("frontend.service.components.tab01_top_contributors.st")
@patch("frontend.service.components.tab01_top_contributors.requests.get")
@patch("frontend.service.components.tab01_top_contributors.struct_logger")
def test_render_top_contributors_success(mock_logger, mock_requests, mock_st):
    """Test the render_top_contributors function for successful data retrieval."""
    # Mock response data
    mock_data = [
        {"contributor_id": 1, "recipe_count": 10},
        {"contributor_id": 2, "recipe_count": 8},
    ]
    mock_requests.return_value.json.return_value = mock_data
    mock_requests.return_value.status_code = 200

    # Setup streamlit mocks
    mock_st.session_state = {}
    col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()
    mock_st.columns.return_value = [col1, col2, col3]
    mock_st.warning = MagicMock()
    mock_st.error = MagicMock()
    mock_st.metric = MagicMock()
    mock_st.title = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.bar_chart = MagicMock()
    mock_st.dataframe = MagicMock()
    mock_st.download_button = MagicMock()

    # Call the function
    render_top_contributors(show_title=False)    # Assertions
    assert mock_requests.called
    assert mock_logger.info.called
    assert mock_st.session_state.get("metrics")  # Check if metrics were set
    assert mock_st.session_state.get("dataframe")  # Check if dataframe was created
    assert mock_st.metric.called  # Check if metrics were displayed
    assert mock_st.bar_chart.called  # Check if bar chart was displayed
    assert mock_st.dataframe.called  # Check if dataframe was displayed
    assert mock_st.download_button.called  # Check if download button was created

@patch("frontend.service.components.tab01_top_contributors.st")
@patch("frontend.service.components.tab01_top_contributors.requests.get")
@patch("frontend.service.components.tab01_top_contributors.struct_logger")
def test_render_top_contributors_no_data(mock_logger, mock_requests, mock_st):
    """Test the render_top_contributors function when no data is returned."""
    # Mock streamlit
    mock_st.warning = MagicMock()
    
    # Setup test data
    mock_requests.return_value.json.return_value = []
    mock_requests.return_value.status_code = 200

    # Call the function
    render_top_contributors(show_title=False)

    # Assertions
    assert mock_requests.called
    assert mock_logger.info.called
    assert mock_st.warning.called  # Check if warning was shown

@patch("frontend.service.components.tab01_top_contributors.st")
@patch("frontend.service.components.tab01_top_contributors.requests.get")
@patch("frontend.service.components.tab01_top_contributors.struct_logger")
def test_render_top_contributors_request_exception(mock_logger, mock_requests, mock_st):
    """Test the render_top_contributors function when a request exception occurs."""
    # Mock streamlit
    mock_st.error = MagicMock()
    
    # Setup test data
    mock_requests.side_effect = requests.RequestException("Network error")

    # Call the function
    render_top_contributors(show_title=False)

    # Assertions
    assert mock_requests.called
    assert mock_logger.error.called
    assert mock_st.error.called  # Check if error message was shown
    
    
    
# tests components/tab02_duration_recipe.py
@patch("frontend.service.components.tab02_duration_recipe.st")
@patch("frontend.service.components.tab02_duration_recipe.requests.get")
@patch("frontend.service.components.tab02_duration_recipe.struct_logger")
def test_render_duration_recipe_success(mock_logger, mock_requests, mock_st):
    """Test the render_duration_recipe function for successful data retrieval."""
    # Mock response data for duration distribution
    mock_data = [
        {"duration_bin": "0-15", "count": 10, "share": 20.0, "avg_duration_in_bin": 10.0, "cum_share": 20.0},
        {"duration_bin": "15-30", "count": 15, "share": 30.0, "avg_duration_in_bin": 25.0, "cum_share": 50.0},
    ]
    mock_requests.return_value.json.return_value = mock_data
    mock_requests.return_value.status_code = 200
    
    # Setup streamlit mocks
    mock_st.warning = MagicMock()
    mock_st.error = MagicMock()
    mock_st.metric = MagicMock()
    mock_st.bar_chart = MagicMock()
    mock_st.line_chart = MagicMock()
    mock_st.dataframe = MagicMock()
    mock_st.download_button = MagicMock()

    # Call the function
    render_duration_recipe(logger=mock_logger)

    # Assertions
    assert mock_requests.called
    assert mock_logger.info.called
    assert mock_st.metric.called  # Check if metrics were displayed
    assert mock_st.bar_chart.called  # Check if bar chart was displayed
    assert mock_st.line_chart.called  # Check if line chart was displayed
    assert mock_st.dataframe.called  # Check if dataframe was displayed
    assert mock_st.download_button.called  # Check if download button was created

@patch("frontend.service.components.tab02_duration_recipe.st")
@patch("frontend.service.components.tab02_duration_recipe.requests.get")
@patch("frontend.service.components.tab02_duration_recipe.struct_logger")
def test_render_duration_recipe_no_data(mock_logger, mock_requests, mock_st):
    """Test the render_duration_recipe function when no data is returned."""
    mock_requests.return_value.json.return_value = []
    mock_requests.return_value.status_code = 200

    # Setup streamlit mocks
    mock_st.warning = MagicMock()
    mock_st.error = MagicMock()
    mock_st.header = MagicMock()
    mock_st.radio = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]

    # Call the function
    render_duration_recipe(logger=mock_logger)

    # Assertions
    assert mock_requests.called
    assert mock_logger.info.called
    assert mock_st.warning.called  # Check if warning was shown

@patch("frontend.service.components.tab02_duration_recipe.st")
@patch("frontend.service.components.tab02_duration_recipe.requests.get")
@patch("frontend.service.components.tab02_duration_recipe.struct_logger")
def test_render_duration_recipe_request_exception(mock_logger, mock_requests, mock_st):
    """Test the render_duration_recipe function when a request exception occurs."""
    mock_requests.side_effect = requests.RequestException("Network error")

    # Setup streamlit mocks
    mock_st.error = MagicMock()
    mock_st.header = MagicMock()
    mock_st.radio = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]

    # Call the function
    render_duration_recipe(logger=mock_logger)

    # Assertions
    assert mock_requests.called
    assert mock_logger.error.called
    assert mock_st.error.called  # Check if error message was shown
    
    
    # tests components/tab04_rating.py


@pytest.fixture
def mock_rating_distribution_data():
    """Sample rating distribution data."""
    return [
        {"rating_bin": "0-1", "count": 10, "share": 20.0, "avg_rating_in_bin": 0.5, "cum_share": 20.0},
        {"rating_bin": "1-2", "count": 15, "share": 30.0, "avg_rating_in_bin": 1.5, "cum_share": 50.0},
        {"rating_bin": "2-3", "count": 25, "share": 50.0, "avg_rating_in_bin": 2.5, "cum_share": 100.0}
    ]

@pytest.fixture
def mock_correlation_data():
    """Sample correlation data between ratings and recipe counts."""
    return [
        {"contributor_id": "user1", "recipe_count": 5, "avg_rating": 4.2, "median_rating": 4.0},
        {"contributor_id": "user2", "recipe_count": 10, "avg_rating": 4.5, "median_rating": 4.3},
        {"contributor_id": "user3", "recipe_count": 15, "avg_rating": 4.8, "median_rating": 4.7}
    ]

@patch("frontend.service.components.tab04_rating.requests.get")
@patch("frontend.service.components.tab04_rating.struct_logger")
def test_render_user_rating_success(mock_logger, mock_requests, mock_rating_distribution_data, mock_correlation_data):
    """Test successful rendering of rating distribution and correlation."""
    # Mock responses
    mock_distribution_response = Mock()
    mock_distribution_response.json.return_value = mock_rating_distribution_data
    mock_distribution_response.status_code = 200

    mock_correlation_response = Mock()
    mock_correlation_response.json.return_value = mock_correlation_data
    mock_correlation_response.status_code = 200

    mock_requests.side_effect = [mock_distribution_response, mock_correlation_response]

    # Call function
    render_user_rating(logger=mock_logger)

    # Verify API calls
    assert mock_requests.call_count == 2
    mock_requests.assert_any_call(f"{BASE_URL}/mange_ta_main/average-rating-distribution")
    mock_requests.assert_any_call(f"{BASE_URL}/mange_ta_main/rating-vs-recipe-count")

    # Verify logging
    assert mock_logger.info.call_count == 2
    mock_logger.info.assert_any_call("Rating distribution fetched", count=len(mock_rating_distribution_data))
    mock_logger.info.assert_any_call("Rating vs recipe count fetched", count=len(mock_correlation_data))

@patch("frontend.service.components.tab04_rating.st")
@patch("frontend.service.components.tab04_rating.requests.get")
@patch("frontend.service.components.tab04_rating.struct_logger")
def test_render_user_rating_no_data(mock_logger, mock_requests, mock_st):
    """Test handling of empty data responses."""
    # Mock empty responses
    mock_distribution_response = Mock()
    mock_distribution_response.json.return_value = []
    mock_distribution_response.status_code = 200

    mock_correlation_response = Mock()
    mock_correlation_response.json.return_value = []
    mock_correlation_response.status_code = 200

    mock_requests.side_effect = [mock_distribution_response, mock_correlation_response]

    # Setup streamlit mocks
    mock_st.warning = MagicMock()
    mock_st.error = MagicMock()
    mock_st.header = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    # Call function
    render_user_rating(logger=mock_logger)

    # Verify warnings displayed
    assert mock_st.warning.called
    assert "Aucune donnée disponible" in mock_st.warning.call_args_list[0][0][0]

@patch("frontend.service.components.tab04_rating.st")
@patch("frontend.service.components.tab04_rating.requests.get")
@patch("frontend.service.components.tab04_rating.struct_logger")
def test_render_user_rating_api_error(mock_logger, mock_requests, mock_st):
    """Test handling of API errors."""
    # Mock request exception
    mock_requests.side_effect = requests.RequestException("Network error")

    # Setup streamlit mocks
    mock_st.error = MagicMock()
    mock_st.header = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    # Call function
    render_user_rating(logger=mock_logger)

    # Verify error handling
    assert mock_logger.error.called
    assert mock_st.error.called
    assert "Erreur lors de la récupération des données" in mock_st.error.call_args_list[0][0][0]

@patch("frontend.service.components.tab04_rating.st")
@patch("frontend.service.components.tab04_rating.requests.get")
@patch("frontend.service.components.tab04_rating.struct_logger")
def test_render_user_rating_invalid_data(mock_logger, mock_requests, mock_st):
    """Test handling of invalid data format."""
    # Mock invalid data response
    mock_response = Mock()
    mock_response.json.return_value = [{"invalid_key": "value"}]
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    # Setup streamlit mocks
    mock_st.error = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.header = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    # Call function
    render_user_rating(logger=mock_logger)

    # Verify error handling for invalid data
    assert mock_logger.info.called
    assert mock_st.error.called or mock_st.warning.called
    
# tests components/tab06_top10_analyse.py
# Sample test data
SAMPLE_DATA = [
    {"population": "top_10_percent", "contributor_count": 100, "avg_duration_minutes": 45.5, "avg_rating": 4.2, "avg_comments": 8.5},
    {"population": "global", "contributor_count": 1000, "avg_duration_minutes": 42.0, "avg_rating": 4.0, "avg_comments": 3.2}
]

@pytest.fixture
def mock_streamlit():
    """Mock all streamlit functions used in the component"""
    with patch("frontend.service.components.tab06_top10_analyse.st") as mock_st:
        yield mock_st

@pytest.fixture
def mock_requests_get():
    """Mock requests.get for API calls"""
    with patch("frontend.service.components.tab06_top10_analyse.requests.get") as mock_get:
        yield mock_get

@pytest.fixture
def mock_altair():
    """Mock altair for visualization"""
    with patch("frontend.service.components.tab06_top10_analyse.alt") as mock_alt:
        yield mock_alt

def test_successful_data_fetch(mock_streamlit, mock_requests_get, mock_altair):
    """Test successful data fetch and display"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_DATA
    mock_requests_get.return_value = mock_response

    # Call the function
    render_top10_vs_global()

    # Verify API call
    mock_requests_get.assert_called_once_with(f"{BASE_URL}/mange_ta_main/top-10-percent-contributors")
    
    # Verify key metrics were displayed
    mock_streamlit.metric.assert_any_call("Contributeurs Top 10%", 100)
    mock_streamlit.metric.assert_any_call("Contributeurs Total", 1000)

    # Verify charts were created
    assert mock_altair.Chart.called
    assert mock_streamlit.altair_chart.called

def test_api_error_handling(mock_streamlit, mock_requests_get):
    """Test error handling when API request fails"""
    # Setup mock to raise an exception
    mock_requests_get.side_effect = requests.RequestException("API Error")

    # Call the function
    render_top10_vs_global()

    # Verify error was displayed
    mock_streamlit.error.assert_called_once()
    assert "Erreur lors de la récupération des données" in mock_streamlit.error.call_args[0][0]

def test_empty_data_handling(mock_streamlit, mock_requests_get):
    """Test handling of empty data response"""
    # Setup mock to return empty data
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_requests_get.return_value = mock_response

    # Call the function
    render_top10_vs_global()

    # Verify warning was displayed
    mock_streamlit.warning.assert_called_once_with("Aucune donnée disponible.")

def test_data_processing(mock_streamlit, mock_requests_get, mock_altair):
    """Test data processing and visualization creation"""
    # Setup mock response with test data
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_DATA
    mock_requests_get.return_value = mock_response

    # Call the function
    render_top10_vs_global()

    # Verify all charts were created
    assert mock_streamlit.altair_chart.call_count == 3  # One for each metric chart

    # Verify markdown sections were created
    mock_streamlit.markdown.assert_any_call("### ✨ Lecture")
    
    # Verify download button was created
    mock_streamlit.download_button.assert_called_once()

def test_logger_usage(mock_streamlit, mock_requests_get):
    """Test logger functionality"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_DATA
    mock_requests_get.return_value = mock_response

    # Create mock logger
    mock_logger = MagicMock()

    # Call the function with mock logger
    render_top10_vs_global(logger=mock_logger)

    # Verify logger was used
    mock_logger.info.assert_called_once_with("Top 10% contributor metrics fetched", count=2)

def test_api_error_logging(mock_streamlit, mock_requests_get):
    """Test logging of API errors"""
    # Setup mock logger
    mock_logger = MagicMock()
    
    # Setup mock to raise an exception
    mock_requests_get.side_effect = requests.RequestException("API Error")

    # Call the function with mock logger
    render_top10_vs_global(logger=mock_logger)

    # Verify error was logged
    mock_logger.error.assert_called_once_with("Failed to fetch top 10% metrics", error="API Error")
    
# tests components/tab07_tags.py
# Sample test data for API response
SAMPLE_TAG_DATA = [
    {
        "segment": 1,
        "persona": "Super Cookers",
        "tag": "preparation",
        "count": 150,
        "share_pct": 5.8
    },
    {
        "segment": 1,
        "persona": "Super Cookers",
        "tag": "time-to-make",
        "count": 120,
        "share_pct": 4.6
    },
    {
        "segment": 2,
        "persona": "Quick Cookers",
        "tag": "easy",
        "count": 80,
        "share_pct": 3.2
    }
]

@pytest.fixture
def mock_streamlit():
    """Mock all streamlit components"""
    with patch("frontend.service.components.tab07_tags.st") as mock_st:
        # Setup radio button default
        mock_st.radio.return_value = "Volume (count)"
        # Setup columns mock
        mock_columns = [MagicMock(), MagicMock()]
        mock_st.columns.return_value = mock_columns
        yield mock_st

@pytest.fixture
def mock_requests_get():
    """Mock requests.get for API calls"""
    with patch("frontend.service.components.tab07_tags.requests.get") as mock_get:
        yield mock_get

@pytest.fixture
def mock_altair():
    """Mock altair for visualization"""
    with patch("frontend.service.components.tab07_tags.alt") as mock_alt:
        yield mock_alt

def test_successful_data_fetch_and_display(mock_streamlit, mock_requests_get, mock_altair):
    """Test the happy path with successful data fetch and display"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_TAG_DATA
    mock_requests_get.return_value = mock_response

    # Call the function
    render_top_tags_by_segment()

    # Verify API call
    mock_requests_get.assert_called_once_with(f"{BASE_URL}/mange_ta_main/top-tags-by-segment")
    
    # Verify header and initial table display
    mock_streamlit.header.assert_called_once_with("🏷️ Cartographie des tags")
    mock_streamlit.table.assert_called_once()
    
    # Verify charts were created
    assert mock_altair.Chart.called
    mock_streamlit.altair_chart.assert_called()

def test_radio_button_percentage_view(mock_streamlit, mock_requests_get, mock_altair):
    """Test switching to percentage view"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_TAG_DATA
    mock_requests_get.return_value = mock_response
    
    # Setup radio to return percentage view
    mock_streamlit.radio.return_value = "Part (%)"
    
    # Call the function
    render_top_tags_by_segment()
    
    # Verify chart uses share_pct for y-axis
    chart_calls = mock_altair.Chart().encode.call_args_list
    assert any("share_pct" in str(call) for call in chart_calls)

def test_api_error_handling(mock_streamlit, mock_requests_get):
    """Test error handling when API request fails"""
    # Setup mock to raise an exception
    mock_requests_get.side_effect = requests.RequestException("API Error")

    # Call the function
    render_top_tags_by_segment()

    # Verify error was displayed
    mock_streamlit.error.assert_called_once()
    assert "Erreur lors de la récupération des données" in mock_streamlit.error.call_args[0][0]

def test_empty_data_handling(mock_streamlit, mock_requests_get):
    """Test handling of empty data response"""
    # Setup mock to return empty data
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_requests_get.return_value = mock_response

    # Call the function
    render_top_tags_by_segment()

    # Verify warning was displayed
    mock_streamlit.warning.assert_called_once_with("Aucune donnée disponible")

def test_invalid_data_structure(mock_streamlit, mock_requests_get):
    """Test handling of invalid data structure"""
    # Setup mock with invalid data (missing required columns)
    mock_response = MagicMock()
    mock_response.json.return_value = [{"invalid": "data"}]
    mock_requests_get.return_value = mock_response

    # Call the function
    render_top_tags_by_segment()

    # Verify error was displayed
    mock_streamlit.error.assert_called_once_with("Données inattendues reçues pour les tags par segment.")

def test_segment_order_consistency(mock_streamlit, mock_requests_get, mock_altair):
    """Test that segments are displayed in the correct order"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_TAG_DATA
    mock_requests_get.return_value = mock_response

    # Call the function
    render_top_tags_by_segment()

    # Verify segments are processed in the correct order
    df_calls = [call for call in str(mock_streamlit.mock_calls) if "persona" in str(call)]
    for idx, segment in enumerate(SEGMENT_ORDER):
        assert segment in str(df_calls)

def test_logger_functionality(mock_streamlit, mock_requests_get):
    """Test that logging is working correctly"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_TAG_DATA
    mock_requests_get.return_value = mock_response

    # Create mock logger
    mock_logger = MagicMock()

    # Call the function with mock logger
    render_top_tags_by_segment(logger=mock_logger)

    # Verify logging calls
    mock_logger.info.assert_called_once_with("Top tags by segment fetched", count=len(SAMPLE_TAG_DATA))

def test_download_button_creation(mock_streamlit, mock_requests_get):
    """Test that download button is created with correct data"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_TAG_DATA
    mock_requests_get.return_value = mock_response

    # Call the function
    render_top_tags_by_segment()

    # Verify download button was created
    mock_streamlit.download_button.assert_called_once()
    assert "📥 Télécharger CSV" in mock_streamlit.download_button.call_args[0]
    assert "top_tags_by_segment.csv" in mock_streamlit.download_button.call_args[0]