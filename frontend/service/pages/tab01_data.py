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

# Utiliser st.cache_data pour éviter de recharger à chaque interaction
@st.cache_data(ttl=3600)
def load_dataset(dataset_type: str):
    """Load dataset from backend with caching."""
    url = f"{BASE_URL}/mange_ta_main/load-data?data_type={dataset_type}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data) if data else None

# Charger automatiquement le dataset sélectionné
struct_logger.info("Starting data load", data_type=data_type)
with st.spinner("Chargement du dataset..."):
    try:
        struct_logger.info("Calling load_dataset", data_type=data_type)
        df = load_dataset(data_type)
        struct_logger.info("load_dataset returned", is_none=df is None, is_empty=df.empty if df is not None else None)

        if df is None or df.empty:
            st.warning("Aucune donnée reçue du backend.")
            struct_logger.warning("Empty data received", data_type=data_type)
        else:
            struct_logger.info("Data loaded successfully", rows=len(df), columns=len(df.columns))
            struct_logger.info("About to display success message and dataframe")
            st.success(f"Dataset chargé : {len(df)} lignes, {len(df.columns)} colonnes")
            struct_logger.info("Success message displayed, now showing dataframe")
            st.dataframe(df.head(100))
            struct_logger.info("Dataframe displayed")

            # Bouton de téléchargement
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le dataset complet (CSV)",
                data=csv,
                file_name=f"{data_type}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            struct_logger.info("Download button displayed")

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors du chargement : {str(e)}")
        struct_logger.error("Failed to load data", error=str(e), data_type=data_type)
    except Exception as e:
        st.error(f"Erreur inattendue : {str(e)}")
        struct_logger.error("Unexpected error", error=str(e), data_type=data_type)
