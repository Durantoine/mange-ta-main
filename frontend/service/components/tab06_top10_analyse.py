import altair as alt
import pandas as pd
import streamlit as st
from logger import struct_logger

from ..src.http_client import BackendAPIError, fetch_backend_json


def render_top10_vs_global(logger=struct_logger) -> None:  # pragma: no cover - Streamlit UI glue
    """Render the comparison dashboard between the top cohort and global users."""
    st.header("🏅 Utilisateurs Top 10% vs Global")
    st.caption("Comparaison des comportements des contributeurs les plus actifs")

    try:
        data = fetch_backend_json("top-10-percent-contributors", ttl=300)
        logger.info("Top 10% contributor metrics fetched", count=len(data))
    except BackendAPIError as exc:
        st.error(f"Erreur lors de la récupération des données : {exc.details}")
        logger.error("Failed to fetch top 10% metrics", error=str(exc), endpoint=exc.endpoint)
        return

    if not data:
        st.warning("Aucune donnée disponible.")
        return

    df = pd.DataFrame(data)

    # Affichage chiffres clés
    col1, col2 = st.columns(2)
    top_count_series = df.loc[df["population"] == "top_10_percent", "contributor_count"]
    global_count_series = df.loc[df["population"] == "global", "contributor_count"]

    top_count = int(top_count_series.iloc[0]) if not top_count_series.empty else 0
    global_count = int(global_count_series.iloc[0]) if not global_count_series.empty else 0

    with col1:
        st.metric("Contributeurs Top 10%", top_count)
    with col2:
        st.metric("Contributeurs Total", global_count)

    st.subheader("📊 Comparaisons visuelles")

    charts = [
        (
            "Durée moyenne des recettes (min)",
            "avg_duration_minutes",
            "Durée moyenne (min)",
        ),
        (
            "Note moyenne (/5)",
            "avg_rating",
            "Note moyenne (/5)",
        ),
        (
            "Nombre moyen de commentaires",
            "avg_comments",
            "Commentaires moyens",
        ),
    ]

    for title, value_col, axis_title in charts:
        chart_df = df.loc[:, ["population", value_col]].rename(
            columns={"population": "Population", value_col: "Valeur"}
        )
        chart_df["Population"] = chart_df["Population"].map(
            {"top_10_percent": "Top 10 %", "global": "Global"}
        )

        st.markdown(f"#### {title}")
        chart = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X("Population:N", title="Population"),
                y=alt.Y("Valeur:Q", title=axis_title),
                color=alt.Color("Population:N", title="Population"),
                tooltip=[
                    alt.Tooltip("Population:N", title="Population"),
                    alt.Tooltip("Valeur:Q", title=axis_title, format=".2f"),
                ],
            )
            .properties(width="container")
        )
        st.altair_chart(chart, use_container_width=True)

    st.markdown(
        """
    ### ✨ Lecture
    - **Durée plus élevée** chez le Top 10% ? → contributeurs experts
    - **Plus de commentaires** ? → profils engagés
    - **Meilleure note moyenne** ? → qualité supérieure de contenu
    """
    )

    st.subheader("Tableau détaillé")
    st.dataframe(df, hide_index=True)

    # Téléchargement CSV global
    csv = df.to_csv(index=False)
    st.download_button("📥 Télécharger CSV", csv, "top10_vs_global.csv", "text/csv")

    st.markdown(
        """
        ### 🧠 Synthèse stratégique

        - ✅ Les utilisateurs les plus actifs ne sont pas plus experts (durée similaire)
        - ✅ Leur qualité perçue (notes) est équivalente au reste
        - ✅ Leur engagement communautaire est nettement supérieur (commentaires)

        ### 🎯 Implications business

        Ces contributeurs jouent un rôle social plus que technique :

        - Ils sont des **animateurs de communauté** plutôt que des chefs étoilés.
        - Ils mériteraient :
            - des badges d’engagement,
            - une mise en avant éditoriale,
            - des fonctionnalités sociales adaptées.

        ### 🧩 Conclusion

        Le top 10 % n’est pas défini par une cuisine plus longue ou meilleure, mais par sa capacité à susciter de la discussion.
        Ce sont les **moteurs conversationnels** de la plateforme. Pour la croissance, ce sont eux qu’il faut fidéliser.
        """
    )
