# frontend/frontend/__init__.py
# Make "frontend.*" resolve to modules that live at the project root (/app).
import os
from pathlib import Path

_pkg_dir = Path(__file__).resolve().parent        # /app/frontend
_project_root = _pkg_dir.parent                   # /app

# First search /app (so "frontend.service" -> "/app/service"),
# then fall back to /app/frontend if needed.
__path__ = [str(_project_root), str(_pkg_dir)]