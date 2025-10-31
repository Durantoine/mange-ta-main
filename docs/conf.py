from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
BACKEND_SERVICE_ROOT = BACKEND_ROOT / "service"
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
FRONTEND_SERVICE_ROOT = FRONTEND_ROOT / "service"

sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(BACKEND_SERVICE_ROOT))
sys.path.insert(0, str(FRONTEND_ROOT))
sys.path.insert(0, str(FRONTEND_SERVICE_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

project = "Mange Ta Main"
author = "Telecom Paris – Intelligence Artificielle Multimodale"
copyright = (
    f"{datetime.now():%Y}, {author}"
)  # noqa: A003  (sphinx reserved name)
release = "0.1.0"

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.extlinks",
    "sphinx.ext.autosectionlabel",
    "sphinx_copybutton",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = ["_build", "Thumbs.db", ".DS_Store"]

language = "fr"

html_theme = "furo"
html_title = project
html_static_path = ["_static"]
html_logo = None
html_favicon = None

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = False

todo_include_todos = True

intersphinx_mapping: dict[str, tuple[str, str]] = {}

extlinks = {
    "issue": ("https://github.com/Durantoine/mange-ta-main/issues/%s", "#%s"),
}

autosectionlabel_prefix_document = True

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "substitution",
]

# Ensure Sphinx can locate environment variables when running outside Docker.
os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT))
