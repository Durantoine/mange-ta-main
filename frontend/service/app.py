import streamlit as st

BASE_URL = "http://mange_ta_main:8000/mange_ta_main"

st.set_page_config(page_title="Mangetamain Dashboard", layout="wide")

st.title("🍽️ Mange ta Main — Analyse des contributeurs")


st.image("images/mouette.jpg", caption="La mouette surveille le projet 🐦")

st.markdown("""
Bienvenue sur le tableau de bord interactif de l’équipe **Mange ta Main**.
Utilisez les pages dans la barre latérale pour explorer les données.
""")

st.caption('Interface de base — ajoute tes pages et modules au fur et à mesure.')

# ===== SIDEBAR =====
with st.sidebar:
    st.header('Navigation')
    st.page_link('/app/service/app.py', label='🏠 Accueil')
    st.page_link('/app/service/pages/01_Overview.py', label='🧭 Données (Overview)')
    st.page_link('/app/service/pages/02_Top_Contributors.py')
    st.page_link('/app/service/pages/03_Raw_Data.py', label='🔌 Raw data')

    st.divider()
    st.subheader('Paramètres')
    st.toggle('Mode démo', key='demo_mode', value=True)
    st.caption('Les paramètres ici sont globaux (session_state).')

# ===== CONTENU D'ACCUEIL =====
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
kpi_col1.metric('Utilisateurs (estim.)', '—')
kpi_col2.metric('Interactions (estim.)', '—')
kpi_col3.metric('Recettes (estim.)', '—')

st.info(
    'Astuce : ajoute rapidement des KPI en lisant le DataFrame depuis le backend, '
    'ou en affichant les tailles/ bornes min-max (via la page Overview).'
)

tab1, tab2 = st.tabs(['📊 Présentation', '🧱 À venir'])
with tab1:
    st.write(
        '- Cette interface affiche une image, un header, un menu latéral.\n'
        '- Ajoute tes graphiques dans ⁠ pages/01_Overview.py ⁠ et ⁠ pages/02_Top_Contributors.py ⁠.\n'
        '- Les appels API se font via un petit helper dans ⁠ service/src/api.py ⁠.'
    )
with tab2:
    st.write('Placeholders pour des cards, des graphes Plotly, etc.')