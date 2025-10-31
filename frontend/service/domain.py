"""Frontend domain constants shared across Streamlit pages."""

import os

BASE_URL = os.getenv("BASE_URL", "http://mange-ta-main-back:8000")
"""Base URL used by the frontend to reach the FastAPI backend."""
