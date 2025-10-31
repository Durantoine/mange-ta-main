from contextlib import contextmanager

import streamlit as st


@contextmanager
def _sidebar_context():
    sidebar = getattr(st, "sidebar", None)
    if sidebar is None:
        yield st  # fallback for tests where sidebar is not available
        return
    if hasattr(sidebar, "__enter__") and hasattr(sidebar, "__exit__"):
        ctx_obj = sidebar.__enter__()
        try:
            yield ctx_obj if ctx_obj is not None else sidebar
        finally:
            sidebar.__exit__(None, None, None)
        return
    yield sidebar


def render_sidebar() -> None:
    """Render the common sidebar navigation."""
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #5170ff !important;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] a {
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] a:hover {
            opacity: 0.85;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with _sidebar_context() as sidebar:
        target = sidebar if sidebar is not None else st

        header_fn = getattr(target, "header", None)
        if callable(header_fn):
            header_fn("Navigation")

        page_link_fn = getattr(target, "page_link", None)
        if callable(page_link_fn):
            page_link_fn("/app/service/app.py", label="Exploration")
            page_link_fn("/app/service/pages/tab01_data.py", label="Données")
            page_link_fn("/app/service/pages/tab02_analyse.py", label="Analyse")
            page_link_fn("/app/service/pages/tab03_conclusions.py", label="Conclusions")
