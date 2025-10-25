import sys
from pathlib import Path

import streamlit as st

ROOT_PATH = Path(__file__).resolve().parents[2]
if str(ROOT_PATH) not in sys.path:
    sys.path.append(str(ROOT_PATH))

COMPONENTS_DIR = Path(__file__).resolve().parent / "components"
if COMPONENTS_DIR.exists() and str(COMPONENTS_DIR) not in sys.path:
    sys.path.append(str(COMPONENTS_DIR))

from service.logger import struct_logger  # noqa: E402

try:
    from frontend.service.components.tab02_top_contributors import render_top_contributors  # noqa: E402
except ModuleNotFoundError:
    from tab01_top_contributors import render_top_contributors

try:
    from frontend.service.components.tab02_duration_recipe import render_duration_recipe  # noqa: E402
except ModuleNotFoundError:
    from tab02_duration_recipe import render_duration_recipe

try:
    from frontend.service.components.sidebar import render_sidebar  # noqa: E402
except ModuleNotFoundError:
    from sidebar import render_sidebar

BASE_URL = "http://mange_ta_main:8000/mange_ta_main"

st.set_page_config(page_title="Mangetamain Dashboard", layout="wide")

st.image("images/home_ban_big.png", use_container_width=True)

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    .st-emotion-cache-1lqf7hx {
        background-color: #5170ff !important;
    }
    [style*="rgb(255, 75, 75)"],
    [style*="rgb(255,75,75)"],
    div[style*="color: inherit"][style*="background-color: rgb(255, 75, 75)"],
    span[style*="color: inherit"][style*="background-color: rgb(255, 75, 75)"],
    div[style*="color: inherit; background-color: rgb(255, 75, 75)"],
    span[style*="color: inherit; background-color: rgb(255, 75, 75)"] {
        color: #5170ff !important;
        background-color: #5170ff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💬 Édito")
st.write(
    "Dans l’univers foisonnant des applications de partage de recettes, certains utilisateurs se distinguent par leur régularité et leur influence."
)
st.write(
    "Notre étude décrypte le profil de ces contributeurs les plus actifs, véritables catalyseurs de la communauté culinaire en ligne."
)
st.write(
    "Entre passion du partage, recherche d’efficacité et goût de la transmission, ils façonnent les tendances du “fait maison connecté”."
)
st.write(
    "Identifier ces profils, c’est comprendre ce qui fait vibrer la créativité culinaire d’aujourd’hui — entre inspiration, engagement et simplicité du quotidien."
)

st.divider()
render_top_contributors(base_url=BASE_URL, logger=struct_logger, show_title=False)
st.divider()

st.markdown(
    """
Bienvenue sur le tableau de bord interactif de l’équipe **Mange ta Main**.
Utilisez les pages dans la barre latérale pour explorer les données.
"""
)

# ===== SIDEBAR =====
render_sidebar()


tab1, tab2, tab3 = st.tabs(['Durée des recettes', 'Avis postés', 'Note moyenne'])
with tab1:
    render_duration_recipe(base_url=BASE_URL, logger=struct_logger)

with tab2:
    st.write('Placeholders pour des cards, des graphes Plotly, etc.')
    
with tab3:
    st.write('Placeholders pour des cards, des graphes Plotly, etc.')
