import streamlit as st
import pandas as pd
import requests
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from service.logger import struct_logger
from service.app import BASE_URL

import streamlit as st
import pandas as pd
import requests
from service.logger import struct_logger
from service.app import BASE_URL

st.title("👨‍🍳 Top Contributeurs")
tab1, tab2 = st.tabs(["🏆 Plus Actifs", "⭐ Meilleures Notes"])

# --- TAB 1: Most Active Contributors ---
with tab1:
    st.subheader("Contributeurs avec le plus de recettes")
    
    try:
        response = requests.get(f"{BASE_URL}/most-recipes-contributors")
        response.raise_for_status()
        data = response.json()
        struct_logger.info("Most active contributors fetched", count=len(data))
        
        if data:
            df = pd.DataFrame(data)
            df.columns = ['Contributeur ID', 'Nombre de Recettes']
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Contributeurs", len(df))
            with col2:
                st.metric("Top Contributeur", f"{df.iloc[0]['Nombre de Recettes']} recettes")
            with col3:
                avg_recipes = df['Nombre de Recettes'].mean()
                st.metric("Moyenne", f"{avg_recipes:.1f} recettes")
            
            # Bar chart top 10
            top10 = df.head(10).copy()
            top10['Rank'] = range(1, 11)
            st.bar_chart(top10.set_index('Rank')['Nombre de Recettes'])
            
            # Table top 20
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)
            
            # Download
            csv = df.to_csv(index=False)
            st.download_button("📥 Télécharger CSV", csv, "contributeurs_actifs.csv", "text/csv")
        else:
            st.warning("Aucune donnée disponible")
            
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        struct_logger.error("Failed to fetch most active", error=str(e))

# --- TAB 2: Best Rated Contributors ---
with tab2:
    st.subheader("Contributeurs avec les meilleures notes moyennes")
    st.caption("(minimum 5 recettes)")
    
    try:
        response = requests.get(f"{BASE_URL}/best-ratings-contributors")
        response.raise_for_status()
        data = response.json()
        struct_logger.info("Best rated contributors fetched", count=len(data))
        
        if data:
            df = pd.DataFrame(data)
            df.columns = ['Contributeur ID', 'Note Moyenne', 'Nombre de Recettes']
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Contributeurs", len(df))
            with col2:
                st.metric("Meilleure Note", f"{df.iloc[0]['Note Moyenne']:.2f}/5")
            with col3:
                avg_rating = df['Note Moyenne'].mean()
                st.metric("Note Moyenne Globale", f"{avg_rating:.2f}/5")
            
            # Filter
            min_recipes = st.slider("Nombre minimum de recettes", 5, 50, 5)
            df_filtered = df[df['Nombre de Recettes'] >= min_recipes]
            
            # Scatter chart - Note vs Nombre de recettes
            scatter_data = df_filtered[['Nombre de Recettes', 'Note Moyenne']].copy()
            scatter_data = scatter_data.rename(columns={
                'Nombre de Recettes': 'recipes',
                'Note Moyenne': 'rating'
            })
            st.scatter_chart(scatter_data, x='recipes', y='rating', height=400)
            st.caption("Relation entre nombre de recettes et note moyenne")
            
            # Table
            st.dataframe(df_filtered.head(20), use_container_width=True, hide_index=True)
            
            # Download
            csv = df_filtered.to_csv(index=False)
            st.download_button("📥 Télécharger CSV", csv, "contributeurs_notes.csv", "text/csv")
        else:
            st.warning("Aucune donnée disponible")
            
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        struct_logger.error("Failed to fetch best rated", error=str(e))