import pandas as pd
import streamlit as st
from logger import struct_logger

try:  # pragma: no cover - runtime fallback when executed as script
    from ..src.http_client import BackendAPIError, fetch_backend_json
except ImportError:  # pragma: no cover - streamlit run context
    try:
        from src.http_client import BackendAPIError, fetch_backend_json
    except ImportError:  # pragma: no cover - fallback when src is namespaced under service
        from service.src.http_client import BackendAPIError, fetch_backend_json


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
        data = fetch_backend_json("most-recipes-contributors", ttl=120)
        struct_logger.info("Most active contributors fetched", count=len(data))
    except BackendAPIError as exc:
        st.error(f"Erreur lors de la récupération des données : {exc.details}")
        struct_logger.error("Failed to fetch most active", error=str(exc), endpoint=exc.endpoint)
        data = []

    if not data:
        st.warning("Aucune donnée disponible")
        return

    df = pd.DataFrame(data)
    if df.empty or df.shape[1] < 2:
        st.warning("Format de données inattendu pour les contributeurs.")
        return

    try:
        df.columns = ["Contributeur ID", "Nombre de Recettes"]
    except ValueError:
        st.warning("Format de données inattendu pour les contributeurs.")
        return

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
