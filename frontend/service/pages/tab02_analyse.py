import streamlit as st
from components.sidebar import render_sidebar
from components.tab05_personnas import render_listing_personas
from components.tab06_top10_analyse import render_top10_vs_global
from components.tab07_tags import render_top_tags_by_segment

st.title("💬 Classification Comportementale des Contributeurs")

st.markdown(
    """
    Cette section présente une analyse comportementale des contributeurs afin d’identifier les utilisateurs les plus actifs, de comprendre leurs habitudes de publication et de comparer leurs performances avec l’ensemble de la communauté. L’objectif : éclairer les dynamiques d’engagement, détecter les profils moteurs et révéler les tendances structurantes qui influencent la création et la circulation des recettes sur la plateforme.
    """
)
render_sidebar()

tab1, tab2, tab3 = st.tabs(['Utilisateurs Top 10% ', 'Cartographie des tags', 'Personnas'])
with tab1:
    render_top10_vs_global()

with tab2:
    render_top_tags_by_segment()

with tab3:
    render_listing_personas()
