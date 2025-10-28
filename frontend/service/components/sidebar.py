import streamlit as st


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

    with st.sidebar:
        st.header("Navigation")
        st.page_link("/app/service/app.py", label="Exploration")
        st.page_link("/app/service/pages/tab01_data.py", label="Données")
        st.page_link("/app/service/pages/tab02_analyse.py", label="Analyse")
        st.page_link("/app/service/pages/tab03_conclusions.py", label="Conclusions")
