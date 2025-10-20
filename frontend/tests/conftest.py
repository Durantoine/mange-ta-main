from unittest.mock import Mock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_requests_for_streamlit():
    """Mock automatique de tous les appels requests pour les tests Streamlit"""
    fake_response = Mock()
    fake_response.json.return_value = []
    fake_response.raise_for_status = Mock()

    with patch("requests.get", return_value=fake_response):
        yield
