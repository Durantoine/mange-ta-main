import altair as alt
import numpy as np
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


def render_duration_recipe(
    logger=struct_logger,
) -> None:  # pragma: no cover - Streamlit UI glue
    """Render the Streamlit tab dedicated to recipe durations.

    The tab first maps the distribution of preparation times across discrete
    buckets, then highlights how duration correlates with publication volume
    and reviewer activity. All API calls are guarded; a failure results in a
    visible warning rather than a broken interface.
    """

    st.header("⏱️ Répartition des durées des recettes")
    st.caption("Distribution par tranches de minutes (0–15, 15–30, …, 120+)")

    view_mode = st.radio("Afficher :", ["Nombre de recettes", "Part (%)"], horizontal=True)

    try:
        data = fetch_backend_json("duration-distribution", ttl=120)
        logger.info("Duration distribution fetched", count=len(data))
    except BackendAPIError as exc:
        st.error(f"Erreur lors de la récupération des données : {exc.details}")
        logger.error("Failed to fetch duration distribution", error=str(exc), endpoint=exc.endpoint)
        data = []

    if not data:
        st.warning("Aucune donnée disponible")
    else:
        df = pd.DataFrame(data)

        def extract_start_value(bin_str: str) -> float:
            """Extract the starting number from a bin string like ``0-15`` or ``120+``."""

            if pd.isna(bin_str):
                return -1
            label = str(bin_str)
            if "+" in label:
                return float(label.replace("+", ""))
            parts = label.split("-")
            try:
                return float(parts[0])
            except (ValueError, IndexError):
                return -1

        df["__sort_key"] = df["duration_bin"].apply(extract_start_value)
        df = df.sort_values("__sort_key").drop(columns="__sort_key")

        df_display = df.rename(
            columns={
                "duration_bin": "Tranche (min)",
                "count": "Nombre de Recettes",
                "share": "Part (%)",
                "avg_duration_in_bin": "Durée Moyenne (min)",
                "cum_share": "Part Cumulée (%)",
            }
        )

        df_display["Tranche (min)"] = pd.Categorical(
            df_display["Tranche (min)"],
            categories=df_display["Tranche (min)"].tolist(),
            ordered=True,
        )

        total_recipes = int(df_display["Nombre de Recettes"].sum())
        nb_classes = df_display.shape[0]
        top_bin = df_display.sort_values("Nombre de Recettes", ascending=False).iloc[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Recettes", f"{total_recipes:,}".replace(",", " "))
        with col2:
            st.metric("Nombre de Classes", nb_classes)
        with col3:
            st.metric(
                "Tranche la plus fréquente",
                f"{top_bin['Tranche (min)']} ({int(top_bin['Nombre de Recettes'])})",
            )

        st.subheader("Visualisation")

        if view_mode == "Nombre de recettes":
            bar_source = df_display[["Tranche (min)", "Nombre de Recettes"]].set_index(
                "Tranche (min)"
            )
        else:
            bar_source = df_display[["Tranche (min)", "Part (%)"]].set_index("Tranche (min)")

        st.bar_chart(bar_source)

        st.line_chart(df_display[["Tranche (min)", "Part Cumulée (%)"]].set_index("Tranche (min)"))
        st.caption("Part cumulée des recettes jusqu'à chaque tranche (en %).")

        st.subheader("Détail par tranche")
        st.dataframe(
            df_display[
                [
                    "Tranche (min)",
                    "Nombre de Recettes",
                    "Part (%)",
                    "Durée Moyenne (min)",
                    "Part Cumulée (%)",
                ]
            ],
            width="stretch",
            hide_index=True,
        )

        csv = df_display.to_csv(index=False)
        st.download_button("📥 Télécharger CSV", csv, "repartition_durees_recettes.csv", "text/csv")

    try:
        corr_data = fetch_backend_json("duration-vs-recipe-count", ttl=120)
        logger.info("Duration vs recipe count fetched", count=len(corr_data))
    except BackendAPIError as exc:
        st.error(f"Erreur lors de la récupération de la corrélation durée / volume : {exc.details}")
        logger.error(
            "Failed to fetch duration vs recipe count", error=str(exc), endpoint=exc.endpoint
        )
        corr_data = []

    st.divider()
    st.subheader("📈 Corrélation durée moyenne vs volume de recettes")

    if not corr_data:
        st.warning("Aucune donnée disponible pour la corrélation.")
        return

    corr_df = pd.DataFrame(corr_data)
    required_cols = {"contributor_id", "recipe_count", "avg_duration"}
    if not required_cols.issubset(corr_df.columns):
        st.error("Données inattendues reçues pour la corrélation.")
        logger.error(
            "Unexpected columns for duration-vs-recipe-count",
            cols=list(corr_df.columns),
        )
        return

    corr_df["recipe_count"] = pd.to_numeric(corr_df["recipe_count"], errors="coerce")
    corr_df["avg_duration"] = pd.to_numeric(corr_df["avg_duration"], errors="coerce")
    if "median_duration" not in corr_df.columns:
        corr_df["median_duration"] = np.nan
    corr_df = corr_df.dropna(subset=["recipe_count", "avg_duration"])

    if corr_df.empty or corr_df["recipe_count"].nunique() <= 1:
        st.info("Pas assez de contributeurs différents pour tracer une régression.")
    else:
        x = corr_df["recipe_count"]
        y = corr_df["avg_duration"]
        slope, intercept = np.polyfit(x, y, 1)
        corr_coef = np.corrcoef(x, y)[0, 1]

        corr_df = corr_df.sort_values("recipe_count")
        corr_df["predicted_avg_duration"] = slope * corr_df["recipe_count"] + intercept

        chart = (
            alt.Chart(corr_df)
            .mark_circle(size=60, opacity=0.7)
            .encode(
                x=alt.X("recipe_count", title="Nombre de recettes publiées"),
                y=alt.Y("avg_duration", title="Durée moyenne des recettes (min)"),
                tooltip=[
                    alt.Tooltip("contributor_id", title="Contributeur"),
                    alt.Tooltip("recipe_count", title="Recettes publiées", format=","),
                    alt.Tooltip("avg_duration", title="Durée moyenne (min)", format=".2f"),
                    alt.Tooltip("median_duration", title="Durée médiane (min)", format=".2f"),
                ],
            )
        )

        regression = (
            alt.Chart(corr_df)
            .mark_line(color="#5170ff", strokeWidth=2)
            .encode(x="recipe_count", y="predicted_avg_duration")
        )

        st.altair_chart((chart + regression).interactive(), use_container_width=True)
        st.caption(
            f"Régression linéaire : durée moyenne ≈ {slope:.2f} × recettes + {intercept:.2f} "
            f"(corrélation r = {corr_coef:.2f})."
        )

    st.markdown(
        """
        **✅ Analyse du graphique : corrélation durée moyenne vs volume de recettes**  
        Le nuage de points montre la relation entre le nombre de recettes publiées par un utilisateur et la durée moyenne de ses recettes. La droite de régression quasi horizontale indique une corrélation nulle (r ≈ 0). Autrement dit, la quantité de recettes publiées n’a aucun lien significatif avec leur durée moyenne.

        **🎯 Conclusion**
        - Aucune relation notable entre volume de publication et durée moyenne.  
        - Les recettes longues restent marginales.  
        - La plateforme favorise un format court, même chez les contributeurs les plus actifs.  
        - Les comportements “experts” ne se traduisent pas par des durées plus longues, mais plutôt par diversité ou interaction (cf. typologies).
        """
    )

    st.dataframe(
        corr_df.rename(
            columns={
                "contributor_id": "Contributeur",
                "recipe_count": "Nombre de recettes",
                "avg_duration": "Durée moyenne (min)",
                "median_duration": "Durée médiane (min)",
                "predicted_avg_duration": "Durée prédite (min)",
            }
        ),
        width="stretch",
        hide_index=True,
    )
