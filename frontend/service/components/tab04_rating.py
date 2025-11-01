import gc
import importlib
import json
from typing import Any, Iterable, Sequence, Tuple, cast

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from logger import struct_logger
from pandas import Series
from pandas.api.types import is_float_dtype, is_integer_dtype, is_object_dtype

try:
    _orjson_runtime = importlib.import_module("orjson")
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    _orjson_runtime = None

orjson = cast(Any, _orjson_runtime)

try:  # pragma: no cover - runtime fallback when executed as script
    from ..src.http_client import BackendAPIError, fetch_backend_json
except ImportError:  # pragma: no cover - streamlit run context
    try:
        from src.http_client import BackendAPIError, fetch_backend_json
    except ImportError:  # pragma: no cover - fallback when src is namespaced under service
        from service.src.http_client import BackendAPIError, fetch_backend_json


CATEGORY_THRESHOLD = 500
MAX_JSON_RECORDS = 1_000
MAX_CHART_POINTS = 2_000
MAX_TABLE_ROWS = 200


def _arrow_dataframe(  # pragma: no cover - deterministic conversion helper
    data: Iterable[dict[str, Any]],
    expected_cols: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Create a DataFrame backed by Arrow types when possible to reduce RAM usage."""
    records = list(data)
    if not records:
        return pd.DataFrame(columns=list(expected_cols or []))

    df = pd.DataFrame(records)
    try:
        df = df.convert_dtypes(dtype_backend="pyarrow")
    except TypeError:  # pragma: no cover - safety net if pandas<2.0 happens
        df = df.convert_dtypes()
    if expected_cols:
        for col in expected_cols:
            if col not in df.columns:
                df[col] = pd.NA
        df = df[list(dict.fromkeys(expected_cols))]
    return df


def _optimise_dataframe(  # pragma: no cover - dtype tuning helper
    df: pd.DataFrame, categorical_threshold: int = CATEGORY_THRESHOLD
) -> pd.DataFrame:
    """Downcast numeric columns and convert low-cardinality strings to categories."""
    if df.empty:
        return df

    df = df.convert_dtypes()

    for col in df.columns:
        series = df[col]
        dtype = series.dtype
        if is_integer_dtype(dtype):
            try:
                df[col] = series.astype(pd.Int32Dtype())
            except (TypeError, ValueError, OverflowError):
                df[col] = series.astype(pd.Int64Dtype())
        elif is_float_dtype(dtype):
            try:
                df[col] = series.astype(pd.Float32Dtype())
            except (TypeError, ValueError):
                df[col] = series.astype(pd.Float64Dtype())
        elif is_object_dtype(dtype):
            unique_count = series.nunique(dropna=True)
            if unique_count and (
                unique_count <= categorical_threshold or unique_count <= len(series) * 0.4
            ):
                try:
                    df[col] = series.astype("category")
                except (TypeError, ValueError):
                    pass

    return df


def _safe_int_cast(  # pragma: no cover - dtype helper
    series: Series, dtype: pd.api.extensions.ExtensionDtype | None = None
) -> Series:
    """Cast to a nullable integer dtype with fallback to ``Int64`` on overflow."""
    target_dtype = dtype or pd.Int32Dtype()
    try:
        return series.astype(target_dtype)
    except (TypeError, ValueError, OverflowError):
        return series.astype(pd.Int64Dtype())


def _safe_float_cast(  # pragma: no cover - dtype helper
    series: Series, dtype: pd.api.extensions.ExtensionDtype | None = None
) -> Series:
    """Cast to a float dtype, keeping a ``Float64`` fallback when needed."""
    target_dtype = dtype or pd.Float32Dtype()
    try:
        return series.astype(target_dtype)
    except (TypeError, ValueError):
        return series.astype(pd.Float64Dtype())


def _trim_records(  # pragma: no cover - deterministic slicing helper
    data: Iterable[dict[str, Any]], limit: int = MAX_JSON_RECORDS
) -> Tuple[list[dict[str, Any]], bool]:
    records = list(data)
    if limit > 0 and len(records) > limit:
        return records[:limit], True
    return records, False


def _limit_frame(  # pragma: no cover - view helper
    df: pd.DataFrame, limit: int, message: str | None = None
) -> pd.DataFrame:
    if limit > 0 and len(df) > limit:
        if message:
            st.caption(message)
        return df.head(limit)
    return df


def _encode_json(payload: Iterable[dict[str, Any]]) -> bytes:  # pragma: no cover - I/O helper
    if orjson is not None:
        return orjson.dumps(payload)
    return json.dumps(list(payload), ensure_ascii=False, separators=(",", ":")).encode("utf-8")


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
        logger.error("Failed to fetch rating distribution", error=str(exc), endpoint=exc.endpoint)
        data = []

    if not data:
        st.warning("Aucune donnée disponible")
    else:
        data, dist_trimmed = _trim_records(data)
        df = _arrow_dataframe(data)

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
        if "Nombre de Contributeurs" in df_display.columns:
            df_display["Nombre de Contributeurs"] = _safe_int_cast(
                pd.to_numeric(df_display["Nombre de Contributeurs"], errors="coerce")
            )
        if "Part (%)" in df_display.columns:
            df_display["Part (%)"] = _safe_float_cast(
                pd.to_numeric(df_display["Part (%)"], errors="coerce")
            )
        if "Note Moyenne (bin)" in df_display.columns:
            df_display["Note Moyenne (bin)"] = _safe_float_cast(
                pd.to_numeric(df_display["Note Moyenne (bin)"], errors="coerce")
            )
        if "Part Cumulée (%)" in df_display.columns:
            df_display["Part Cumulée (%)"] = _safe_float_cast(
                pd.to_numeric(df_display["Part Cumulée (%)"], errors="coerce")
            )

        df_display = _optimise_dataframe(df_display)

        contrib_series = df_display["Nombre de Contributeurs"]
        total_contrib = int(contrib_series.dropna().sum()) if contrib_series.notna().any() else 0
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

        chart_base = _limit_frame(
            df_display,
            MAX_CHART_POINTS,
            message=(
                f"Graphique limité aux {MAX_CHART_POINTS:,} classes de notes."
                if df_display.shape[0] > MAX_CHART_POINTS
                else None
            ),
        )

        if view_mode == "Nombre de contributeurs":
            bar_source = chart_base[["Tranche (note)", "Nombre de Contributeurs"]].set_index(
                "Tranche (note)"
            )
        else:
            bar_source = chart_base[["Tranche (note)", "Part (%)"]].set_index("Tranche (note)")

        st.bar_chart(bar_source)

        if "Part Cumulée (%)" in chart_base.columns:
            st.line_chart(
                chart_base[["Tranche (note)", "Part Cumulée (%)"]].set_index("Tranche (note)")
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
        table_df = _limit_frame(
            df_display[display_cols],
            MAX_TABLE_ROWS,
            message=(
                f"Table limitée aux {MAX_TABLE_ROWS:,} premières classes pour maîtriser la mémoire."
                if df_display.shape[0] > MAX_TABLE_ROWS
                else None
            ),
        )
        st.dataframe(table_df, width="stretch", hide_index=True)

        download_json = _encode_json(data)
        st.download_button(
            "📥 Télécharger JSON",
            download_json,
            "repartition_notes_contributeurs.json",
            "application/json",
        )
        if dist_trimmed:
            st.caption(
                f"Distribution tronquée aux {MAX_JSON_RECORDS:,} premières classes pour réduire la consommation mémoire."
            )
        del download_json, df_display, table_df, chart_base
        gc.collect()

    try:
        corr_data = fetch_backend_json("rating-vs-recipes", ttl=0, timeout=30.0)
        logger.info("Rating vs recipe count fetched", count=len(corr_data))
    except BackendAPIError as exc:
        st.error(f"Erreur lors de la récupération de la corrélation note / volume : {exc.details}")
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

    corr_data, corr_trimmed = _trim_records(corr_data)
    corr_df = _arrow_dataframe(corr_data)
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

    corr_df["recipe_count"] = _safe_int_cast(
        pd.to_numeric(corr_df["recipe_count"], errors="coerce")
    )
    corr_df[rating_col] = _safe_float_cast(pd.to_numeric(corr_df[rating_col], errors="coerce"))
    corr_df = corr_df.rename(columns={rating_col: "avg_rating"})
    if "median_rating" in corr_df.columns:
        corr_df["median_rating"] = _safe_float_cast(
            pd.to_numeric(corr_df["median_rating"], errors="coerce")
        )
    else:
        corr_df["median_rating"] = _safe_float_cast(pd.Series(np.nan, index=corr_df.index))
    corr_df = corr_df.dropna(subset=["recipe_count", "avg_rating"])

    if corr_df.empty or corr_df["recipe_count"].nunique() <= 1:
        st.info("Pas assez de contributeurs différents pour tracer une régression.")
    else:
        x = corr_df["recipe_count"].astype("Float64")
        y = corr_df["avg_rating"].astype("Float64")
        slope, intercept = np.polyfit(x, y, 1)
        corr_coef = np.corrcoef(x, y)[0, 1]

        corr_df = corr_df.sort_values("recipe_count")
        predicted = slope * x + intercept
        corr_df["predicted_avg_rating"] = _safe_float_cast(
            pd.Series(predicted, index=corr_df.index)
        )

        corr_df = _optimise_dataframe(corr_df)

        chart_df = _limit_frame(
            corr_df,
            MAX_CHART_POINTS,
            message=(
                f"Nuage limité à {MAX_CHART_POINTS:,} contributeurs pour limiter la mémoire."
                if len(corr_df) > MAX_CHART_POINTS
                else None
            ),
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
        table_df = corr_df.rename(
            columns={
                "contributor_id": "Contributeur",
                "recipe_count": "Nombre de recettes",
                "avg_rating": "Note moyenne",
                "median_rating": "Note médiane",
                "predicted_avg_rating": "Note prédite",
            }
        )
        table_df = _limit_frame(
            table_df,
            MAX_TABLE_ROWS,
            message=(
                f"Table limitée aux {MAX_TABLE_ROWS:,} contributeurs pour limiter la mémoire."
                if len(table_df) > MAX_TABLE_ROWS
                else None
            ),
        )
        st.dataframe(
            table_df,
            width="stretch",
            hide_index=True,
        )

        download_json = _encode_json(corr_data)
        st.download_button(
            "📥 Exporter corrélation (JSON)",
            download_json,
            "rating_vs_recipes.json",
            "application/json",
        )
        if corr_trimmed:
            st.caption(f"Corrélation calculée sur les {MAX_JSON_RECORDS:,} premiers contributeurs.")
        del table_df, corr_df, chart_df, download_json
        gc.collect()
