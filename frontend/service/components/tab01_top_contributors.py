import pandas as pd
import requests
import streamlit as st
from domain import BASE_URL
from logger import struct_logger


def render_top_contributors(
    show_title: bool = True,
) -> None:  # pragma: no cover - Streamlit UI glue
    """Display the dashboard section dedicated to prolific contributors.

    The view exposes the top authors (par nombre de recettes publiées) along
    with quick metrics and a downloadable CSV extract. Network errors are logged
    and surfaced to the user without interrupting the session.
    """

    if show_title:
        st.title("👨‍🍳 Top Contributeurs")

    st.subheader("Contributeurs avec le plus de recettes")

    try:
        response = requests.get(f"{BASE_URL}/mange_ta_main/most-recipes-contributors")
        response.raise_for_status()
        data = response.json()
        struct_logger.info("Most active contributors fetched", count=len(data))

        if data:
            df = pd.DataFrame(data)
            df.columns = ["Contributeur ID", "Nombre de Recettes"]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Contributeurs", len(df))
            with col2:
                st.metric("Top Contributeur", f"{df.iloc[0]['Nombre de Recettes']} recettes")
            with col3:
                avg_recipes = df["Nombre de Recettes"].mean()
                st.metric("Moyenne", f"{avg_recipes:.1f} recettes")

            top10 = df.head(10).copy()
            top10["Rank"] = range(1, 11)
            st.bar_chart(top10.set_index("Rank")["Nombre de Recettes"])

            st.dataframe(df.head(20), width="stretch", hide_index=True)

            csv = df.to_csv(index=False)
            st.download_button("📥 Télécharger CSV", csv, "contributeurs_actifs.csv", "text/csv")
        else:
            st.warning("Aucune donnée disponible")

    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        struct_logger.error("Failed to fetch most active", error=str(e))
