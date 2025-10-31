from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
FRONTEND_ROOT = PROJECT_ROOT / "frontend"

sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(FRONTEND_ROOT))

project = "Mange Ta Main"
author = "Telecom Paris – Intelligence Artificielle Multimodale"
copyright = (
    f"{datetime.now():%Y}, {author}"
)  # noqa: A003  (sphinx reserved name)
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
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

autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "exclude-members": "__weakref__",
}
autodoc_mock_imports = [
    "altair",
    "dependency_injector",
    "fastapi",
    "httpx",
    "numpy",
    "pandas",
    "requests",
    "streamlit",
]

autosummary_generate = True
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = False

todo_include_todos = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", {}),
    "pandas": ("https://pandas.pydata.org/docs/", {}),
    "numpy": ("https://numpy.org/doc/stable/", {}),
}

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
