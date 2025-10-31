import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from logger import struct_logger
from typing import Iterable, Sequence, Tuple

try:  # pragma: no cover - runtime fallback when executed as script
    from ..src.http_client import BackendAPIError, fetch_backend_json
except ImportError:  # pragma: no cover - streamlit run context
    try:
        from src.http_client import BackendAPIError, fetch_backend_json
    except (
        ImportError
    ):  # pragma: no cover - fallback when src is namespaced under service
        from service.src.http_client import BackendAPIError, fetch_backend_json


MAX_CHART_POINTS = 50_000
MAX_TABLE_ROWS = 5_000
MAX_DOWNLOAD_ROWS = 25_000


def _arrow_dataframe(
    data: Iterable[dict],
    expected_cols: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Create a DataFrame backed by Arrow types when possible to reduce RAM usage."""
    if not data:
        return pd.DataFrame(columns=list(expected_cols or []))
    try:
        df = pd.DataFrame(data, dtype_backend="pyarrow")
    except TypeError:  # pragma: no cover - safety net if pandas<2.0 happens
        df = pd.DataFrame(data)
    if expected_cols:
        for col in expected_cols:
            if col not in df.columns:
                df[col] = pd.NA
        df = df[list(dict.fromkeys(expected_cols))]
    return df


def _limit_for_chart(
    df: pd.DataFrame, columns: Sequence[str], max_rows: int
) -> Tuple[pd.DataFrame, bool]:
    view = df.loc[:, list(columns)]
    if max_rows > 0 and len(view) > max_rows:
        return view.sample(max_rows, random_state=42), True
    return view, False


def _limit_for_table(df: pd.DataFrame, max_rows: int) -> Tuple[pd.DataFrame, bool]:
    if max_rows > 0 and len(df) > max_rows:
        return df.head(max_rows), True
    return df, False


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
        data = fetch_backend_json("rating-distribution", ttl=120, timeout=20.0)
        logger.info("Rating distribution fetched", count=len(data))
    except BackendAPIError as exc:
        st.error(f"Erreur lors de la récupération des données : {exc.details}")
        logger.error(
            "Failed to fetch rating distribution", error=str(exc), endpoint=exc.endpoint
        )
        data = []

    if not data:
        st.warning("Aucune donnée disponible")
    else:
        df = _arrow_dataframe(data)

        bin_col = (
            next((c for c in df.columns if "rating" in c and "bin" in c), None)
            or df.columns[0]
        )
        count_col = next(
            (c for c in df.columns if c in ("count", "contributors_count", "n")), None
        )
        share_col = next((c for c in df.columns if "share" in c or "%" in c), None)
        avg_in_bin_col = next(
            (c for c in df.columns if "avg" in c and "rating" in c), None
        )
        cum_share_col = next(
            (c for c in df.columns if "cum" in c and "share" in c), None
        )

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
                df_display["__sort_key"] = df_display["Tranche (note)"].apply(
                    extract_start_value
                )
                df_display = df_display.sort_values("__sort_key").drop(
                    columns="__sort_key"
                )
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
            bar_source = df_display[
                ["Tranche (note)", "Nombre de Contributeurs"]
            ].set_index("Tranche (note)")
        else:
            bar_source = df_display[["Tranche (note)", "Part (%)"]].set_index(
                "Tranche (note)"
            )

        st.bar_chart(bar_source)

        if "Part Cumulée (%)" in df_display.columns:
            st.line_chart(
                df_display[["Tranche (note)", "Part Cumulée (%)"]].set_index(
                    "Tranche (note)"
                )
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
        table_df, table_trimmed = _limit_for_table(
            df_display[display_cols], MAX_TABLE_ROWS
        )
        st.dataframe(table_df, width="stretch", hide_index=True)
        if table_trimmed:
            st.caption(
                f"Table limitée aux {MAX_TABLE_ROWS:,} premières lignes (données complètes via l'API)."
            )

        if len(df_display) <= MAX_DOWNLOAD_ROWS:
            csv = df_display.to_csv(index=False)
            st.download_button(
                "📥 Télécharger CSV",
                csv,
                "repartition_notes_contributeurs.csv",
                "text/csv",
            )
        else:
            st.info(
                "Dataset volumineux : utilisez directement l'API backend pour récupérer l'intégralité de la distribution."
            )

    try:
        corr_data = fetch_backend_json("rating-vs-recipes", ttl=0, timeout=30.0)
        logger.info("Rating vs recipe count fetched", count=len(corr_data))
    except BackendAPIError as exc:
        st.error(
            f"Erreur lors de la récupération de la corrélation note / volume : {exc.details}"
        )
        logger.error(
            "Failed to fetch rating vs recipe count",
            error=str(exc),
            endpoint=exc.endpoint,
        )
        corr_data = []

    st.divider()
    st.subheader("📈 Corrélation note moyenne par contributeur vs volume de recettes")

    if not corr_data:
        st.warning("Aucune donnée disponible pour la corrélation.")
        return

    corr_df = _arrow_dataframe(corr_data)
    rating_cols = {
        "avg_rating",
        "average_rating",
        "mean_rating",
        "rating",
        "avg",
    }
    rating_col = next(
        (
            c
            for c in corr_df.columns
            if c in rating_cols or ("rating" in c and "avg" in c)
        ),
        None,
    )
    if rating_col is None or not {"contributor_id", "recipe_count"}.issubset(
        corr_df.columns
    ):
        st.error(
            "Données inattendues reçues pour la corrélation. Colonnes attendues : contributor_id, recipe_count, avg_rating"
        )
        logger.error(
            "Unexpected columns for rating-vs-recipes", cols=list(corr_df.columns)
        )
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

        chart_cols = [
            "contributor_id",
            "recipe_count",
            "avg_rating",
            "median_rating",
            "predicted_avg_rating",
        ]
        chart_df, chart_trimmed = _limit_for_chart(
            corr_df, chart_cols, MAX_CHART_POINTS
        )

        scatter = (
            alt.Chart(chart_df)
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
            alt.Chart(chart_df)
            .mark_line(color="#5170ff", strokeWidth=2)
            .encode(x="recipe_count", y="predicted_avg_rating")
        )

        st.altair_chart((scatter + regression).interactive(), use_container_width=True)

        st.caption(
            f"Régression linéaire : note moyenne ≈ {slope:.3f} × recettes + {intercept:.3f} "
            f"(corrélation r = {corr_coef:.3f})."
        )
        if chart_trimmed:
            st.caption(
                f"Visualisation limitée à {MAX_CHART_POINTS:,} enregistrements pour éviter les pics mémoire."
            )

    table_df, table_trimmed = _limit_for_table(
        corr_df.rename(
            columns={
                "contributor_id": "Contributeur",
                "recipe_count": "Nombre de recettes",
                "avg_rating": "Note moyenne",
                "median_rating": "Note médiane",
                "predicted_avg_rating": "Note prédite",
            }
        ),
        MAX_TABLE_ROWS,
    )
    st.dataframe(
        table_df,
        width="stretch",
        hide_index=True,
    )
    if table_trimmed:
        st.caption(
            f"Table réduite aux {MAX_TABLE_ROWS:,} premiers contributeurs pour préserver les ressources."
        )
