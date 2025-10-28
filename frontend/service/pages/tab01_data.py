import pandas as pd
import requests
import streamlit as st
from components.sidebar import render_sidebar
from domain import BASE_URL
from logger import struct_logger

render_sidebar()
st.header("🔌 Visualisation et export des donnée")
st.markdown(
    """
    Cet espace vous permet de sélectionner le dataset de votre choix puis de le charger en un clic.
    Une fois affichées, les données peuvent être :

    - ✅ Visualisées directement dans l’interface pour une exploration rapide  
    - ✅ Téléchargées afin de réaliser vos propres analyses, traitements ou archivages

    Que vous souhaitiez consulter quelques entrées ou travailler en profondeur, cette section offre une expérience simple, flexible et accessible, adaptée à tous les besoins data.
    """
)

data_type = st.selectbox("Choisir le dataset", ["recipes", "interactions"])

if st.button("Charger le dataset"):
    with st.spinner("Chargement..."):
        url = f"{BASE_URL}/mange_ta_main/load-data?data_type={data_type}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            struct_logger.error(e)

        else:
            print(type(data))
            df = pd.DataFrame(data)
            struct_logger.info(df)
            st.dataframe(df.head(100))
