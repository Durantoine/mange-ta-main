# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Ajouter le chemin vers les modules backend et frontend
sys.path.insert(0, os.path.abspath('../../backend'))
sys.path.insert(0, os.path.abspath('../../frontend'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Mange Ta Main'
copyright = '2025, Équipe Mange Ta Main'
author = 'Équipe Mange Ta Main'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',        # Génération automatique de la doc depuis les docstrings
    'sphinx.ext.napoleon',       # Support pour Google et NumPy style docstrings
    'sphinx.ext.viewcode',       # Ajoute des liens vers le code source
    'sphinx.ext.intersphinx',    # Liens vers d'autres documentations
    'sphinx.ext.todo',           # Support pour les TODOs
    'sphinx.ext.coverage',       # Vérification de la couverture de la documentation
    'sphinx_autodoc_typehints',  # Meilleur support des type hints
    'myst_parser',               # Support pour Markdown
]

templates_path = ['_templates']
exclude_patterns = []

language = 'fr'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Configuration pour autodoc
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Configuration pour napoleon (Google/NumPy docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Configuration pour intersphinx (liens vers autres docs)
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
    'streamlit': ('https://docs.streamlit.io/', None),
}

# Configuration pour TODOs
todo_include_todos = True

# Support pour Markdown
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
