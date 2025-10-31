import streamlit as st
from components.sidebar import render_sidebar
from components.tab01_top_contributors import render_top_contributors
from components.tab02_duration_recipe import render_duration_recipe
from components.tab03_reviews import render_reviews
from components.tab04_rating import render_user_rating

st.cache_data.clear()
st.cache_resource.clear()

st.set_page_config(page_title="Mangetamain Dashboard", layout="wide")

st.image("images/home_ban_big.png", width="stretch")

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
render_top_contributors()
st.divider()

st.markdown(
    """
Bienvenue sur le tableau de bord interactif de l’équipe **Mange ta Main**.
Utilisez les pages dans la barre latérale pour explorer les données.
"""
)

# ===== SIDEBAR =====
render_sidebar()


tab1, tab2, tab3 = st.tabs(["Durée des recettes", "Avis postés", "Note moyenne"])
with tab1:
    render_duration_recipe()

with tab2:
    render_reviews()

with tab3:
    render_user_rating()
