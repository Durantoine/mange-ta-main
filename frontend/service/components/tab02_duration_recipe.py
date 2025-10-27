from pathlib import Path
from domain import BASE_URL

import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st

try:
    from ..logger import struct_logger
except ImportError:  # pragma: no cover
    import sys

    COMPONENT_PARENT = Path(__file__).resolve().parent.parent
    if str(COMPONENT_PARENT) not in sys.path:
        sys.path.append(str(COMPONENT_PARENT))
    from logger import struct_logger  # type: ignore

def render_duration_recipe(
    base_url: str = BASE_URL,
    logger=struct_logger,
) -> None:
    """Render duration distribution analysis and correlation charts."""

    st.header("⏱️ Répartition des durées des recettes")
    st.caption("Distribution par tranches de minutes (0–15, 15–30, …, 120+)")

    view_mode = st.radio("Afficher :", ["Nombre de recettes", "Part (%)"], horizontal=True)

    try:
        response = requests.get(f"{base_url}/mange_ta_main/duration-distribution")
        response.raise_for_status()
        data = response.json()
        logger.info("Duration distribution fetched", count=len(data))
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        logger.error("Failed to fetch duration distribution", error=str(e))
    else:
        if not data:
            st.warning("Aucune donnée disponible")
        else:
            df = pd.DataFrame(data)

            df_display = df.rename(
                columns={
                    "duration_bin": "Tranche (min)",
                    "count": "Nombre de Recettes",
                    "share": "Part (%)",
                    "avg_duration_in_bin": "Durée Moyenne (min)",
                    "cum_share": "Part Cumulée (%)",
                }
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
                bar_source = df_display[["Tranche (min)", "Nombre de Recettes"]].set_index("Tranche (min)")
            else:
                bar_source = df_display[["Tranche (min)", "Part (%)"]].set_index("Tranche (min)")

            st.bar_chart(bar_source)

            st.line_chart(
                df_display[["Tranche (min)", "Part Cumulée (%)"]].set_index("Tranche (min)")
            )
            st.caption("Part cumulée des recettes jusqu’à chaque tranche (en %).")

            st.subheader("Détail par tranche")
            st.dataframe(
                df_display[
                    ["Tranche (min)", "Nombre de Recettes", "Part (%)", "Durée Moyenne (min)", "Part Cumulée (%)"]
                ],
                width="stretch",
                hide_index=True,
            )

            csv = df_display.to_csv(index=False)
            st.download_button("📥 Télécharger CSV", csv, "repartition_durees_recettes.csv", "text/csv")

    try:
        corr_response = requests.get(f"{base_url}/mange_ta_main/duration-vs-recipe-count")
        corr_response.raise_for_status()
        corr_data = corr_response.json()
        logger.info("Duration vs recipe count fetched", count=len(corr_data))
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération de la corrélation durée / volume : {e}")
        logger.error("Failed to fetch duration vs recipe count", error=str(e))
    else:
        st.divider()
        st.subheader("📈 Corrélation durée moyenne vs volume de recettes")

        if not corr_data:
            st.warning("Aucune donnée disponible pour la corrélation.")
        else:
            corr_df = pd.DataFrame(corr_data)
            required_cols = {"contributor_id", "recipe_count", "avg_duration"}
            if not required_cols.issubset(corr_df.columns):
                st.error("Données inattendues reçues pour la corrélation.")
            else:
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
                        .encode(
                            x="recipe_count",
                            y="predicted_avg_duration",
                        )
                    )

                    combined_chart = alt.layer(chart, regression).interactive()
                    st.altair_chart(combined_chart, use_container_width=True)

                st.caption(
                    f"Régression linéaire : durée moyenne ≈ {slope:.2f} × recettes + {intercept:.2f} "
                    f"(corrélation r = {corr_coef:.2f})."
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
                    use_container_width=True,
                    hide_index=True,
                )
