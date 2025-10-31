import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from logger import struct_logger

from ..src.http_client import BackendAPIError, fetch_backend_json


def render_user_rating(
    logger=struct_logger,
) -> None:  # pragma: no cover - Streamlit UI glue
    """Render the Streamlit tab dedicated to contributor ratings.

    The tab provides two complementary angles:

    - A histogram of average ratings awarded to each contributor, with toggleable
      display between raw counts and percentages.
    - A scatter/correlation view juxtaposing publication volume and rating.

    All API calls are wrapped with defensive error handling so that the UI remains
    readable even if the backend temporarily fails.
    """

    st.header("⭐ Répartition des notes moyennes des contributeurs")
    st.caption(
        "Distribution des notes moyennes attribuées aux recettes par contributeur (ex. 0–1, 1–2, …, 4–5)"
    )

    view_mode = st.radio(
        "Afficher :",
        ["Nombre de contributeurs", "Part (%)"],
        horizontal=True,
        key="rating_distribution_view_mode",
    )

    try:
        data = fetch_backend_json("rating-distribution", ttl=300)
        logger.info("Rating distribution fetched", count=len(data))
    except BackendAPIError as exc:
        st.error(f"Erreur lors de la récupération des données : {exc.details}")
        logger.error("Failed to fetch rating distribution", error=str(exc), endpoint=exc.endpoint)
        data = []

    if not data:
        st.warning("Aucune donnée disponible")
    else:
        df = pd.DataFrame(data)

        bin_col = (
            next((c for c in df.columns if "rating" in c and "bin" in c), None) or df.columns[0]
        )
        count_col = next((c for c in df.columns if c in ("count", "contributors_count", "n")), None)
        share_col = next((c for c in df.columns if "share" in c or "%" in c), None)
        avg_in_bin_col = next((c for c in df.columns if "avg" in c and "rating" in c), None)
        cum_share_col = next((c for c in df.columns if "cum" in c and "share" in c), None)

        rename_map = {bin_col: "Tranche (note)"}
        if count_col:
            rename_map[count_col] = "Nombre de Contributeurs"
        if share_col:
            rename_map[share_col] = "Part (%)"
        if avg_in_bin_col:
            rename_map[avg_in_bin_col] = "Note Moyenne (bin)"
        if cum_share_col:
            rename_map[cum_share_col] = "Part Cumulée (%)"

        df_display = df.rename(columns=rename_map)

        def extract_start_value(bin_str: str) -> float:
            if pd.isna(bin_str):
                return -1
            label = str(bin_str)
            if "+" in label:
                try:
                    return float(label.replace("+", "").split()[0])
                except Exception:
                    return -1
            parts = label.split("-")
            try:
                return float(parts[0])
            except Exception:
                return -1

        if "Tranche (note)" in df_display.columns:
            try:
                df_display["__sort_key"] = df_display["Tranche (note)"].apply(extract_start_value)
                df_display = df_display.sort_values("__sort_key").drop(columns="__sort_key")
            except Exception:
                pass

        if "Nombre de Contributeurs" not in df_display.columns:
            df_display["Nombre de Contributeurs"] = 0

        total_contrib = int(df_display["Nombre de Contributeurs"].sum())
        nb_classes = df_display.shape[0]
        top_bin = (
            df_display.sort_values("Nombre de Contributeurs", ascending=False).iloc[0]
            if not df_display.empty
            else None
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Contributeurs (dans distribution)",
                f"{total_contrib:,}".replace(",", " "),
            )
        with col2:
            st.metric("Nombre de Classes", nb_classes)
        with col3:
            if top_bin is not None and "Tranche (note)" in top_bin:
                st.metric(
                    "Tranche la plus fréquente",
                    f"{top_bin['Tranche (note)']} ({int(top_bin['Nombre de Contributeurs'])})",
                )
            else:
                st.metric("Tranche la plus fréquente", "-")

        st.subheader("Visualisation")

        if view_mode == "Nombre de contributeurs":
            bar_source = df_display[["Tranche (note)", "Nombre de Contributeurs"]].set_index(
                "Tranche (note)"
            )
        else:
            bar_source = df_display[["Tranche (note)", "Part (%)"]].set_index("Tranche (note)")

        st.bar_chart(bar_source)

        if "Part Cumulée (%)" in df_display.columns:
            st.line_chart(
                df_display[["Tranche (note)", "Part Cumulée (%)"]].set_index("Tranche (note)")
            )
            st.caption("Part cumulée des contributeurs jusqu'à chaque tranche (en %).")

        st.subheader("Détail par tranche")
        display_cols = [
            c
            for c in [
                "Tranche (note)",
                "Nombre de Contributeurs",
                "Part (%)",
                "Note Moyenne (bin)",
                "Part Cumulée (%)",
            ]
            if c in df_display.columns
        ]
        st.dataframe(df_display[display_cols], width="stretch", hide_index=True)

        csv = df_display.to_csv(index=False)
        st.download_button(
            "📥 Télécharger CSV",
            csv,
            "repartition_notes_contributeurs.csv",
            "text/csv",
        )

    try:
        corr_data = fetch_backend_json("rating-vs-recipes", ttl=300)
        logger.info("Rating vs recipe count fetched", count=len(corr_data))
    except BackendAPIError as exc:
        st.error(f"Erreur lors de la récupération de la corrélation note / volume : {exc.details}")
        logger.error(
            "Failed to fetch rating vs recipe count", error=str(exc), endpoint=exc.endpoint
        )
        corr_data = []

    st.divider()
    st.subheader("📈 Corrélation note moyenne par contributeur vs volume de recettes")

    if not corr_data:
        st.warning("Aucune donnée disponible pour la corrélation.")
        return

    corr_df = pd.DataFrame(corr_data)
    rating_cols = {
        "avg_rating",
        "average_rating",
        "mean_rating",
        "rating",
        "avg",
    }
    rating_col = next(
        (c for c in corr_df.columns if c in rating_cols or ("rating" in c and "avg" in c)),
        None,
    )
    if rating_col is None or not {"contributor_id", "recipe_count"}.issubset(corr_df.columns):
        st.error(
            "Données inattendues reçues pour la corrélation. Colonnes attendues : contributor_id, recipe_count, avg_rating"
        )
        logger.error("Unexpected columns for rating-vs-recipes", cols=list(corr_df.columns))
        return

    corr_df["recipe_count"] = pd.to_numeric(corr_df["recipe_count"], errors="coerce")
    corr_df[rating_col] = pd.to_numeric(corr_df[rating_col], errors="coerce")
    corr_df = corr_df.rename(columns={rating_col: "avg_rating"})
    if "median_rating" not in corr_df.columns:
        corr_df["median_rating"] = np.nan
    corr_df = corr_df.dropna(subset=["recipe_count", "avg_rating"])

    if corr_df.empty or corr_df["recipe_count"].nunique() <= 1:
        st.info("Pas assez de contributeurs différents pour tracer une régression.")
    else:
        x = corr_df["recipe_count"]
        y = corr_df["avg_rating"]
        slope, intercept = np.polyfit(x, y, 1)
        corr_coef = np.corrcoef(x, y)[0, 1]

        corr_df = corr_df.sort_values("recipe_count")
        corr_df["predicted_avg_rating"] = slope * corr_df["recipe_count"] + intercept

        scatter = (
            alt.Chart(corr_df)
            .mark_circle(size=60, opacity=0.7)
            .encode(
                x=alt.X("recipe_count", title="Nombre de recettes publiées"),
                y=alt.Y("avg_rating", title="Note moyenne par contributeur"),
                tooltip=[
                    alt.Tooltip("contributor_id", title="Contributeur"),
                    alt.Tooltip("recipe_count", title="Recettes publiées", format=","),
                    alt.Tooltip("avg_rating", title="Note moyenne", format=".2f"),
                    alt.Tooltip("median_rating", title="Note médiane", format=".2f"),
                ],
            )
        )

        regression = (
            alt.Chart(corr_df)
            .mark_line(color="#5170ff", strokeWidth=2)
            .encode(x="recipe_count", y="predicted_avg_rating")
        )

        st.altair_chart((scatter + regression).interactive(), use_container_width=True)

        st.caption(
            f"Régression linéaire : note moyenne ≈ {slope:.3f} × recettes + {intercept:.3f} "
            f"(corrélation r = {corr_coef:.3f})."
        )

    st.dataframe(
        corr_df.rename(
            columns={
                "contributor_id": "Contributeur",
                "recipe_count": "Nombre de recettes",
                "avg_rating": "Note moyenne",
                "median_rating": "Note médiane",
                "predicted_avg_rating": "Note prédite",
            }
        ),
        width="stretch",
        hide_index=True,
    )
