from typing import Optional

import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st
from domain import BASE_URL
from logger import struct_logger


def _format_metric(metric_id: str, value) -> str:
    """Format dashboard metrics using a consistent French-friendly style."""
    if value is None:
        return "-"
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}".replace(",", " ")
    if isinstance(value, float):
        if metric_id.endswith("_pct"):
            return f"{value:.1f}%"
        if "avg" in metric_id or "median" in metric_id:
            return f"{value:.2f}".rstrip("0").rstrip(".")
        return f"{value:.2f}"
    return str(value)


def render_reviews(logger=struct_logger) -> None:  # pragma: no cover - Streamlit UI glue
    """Render the Streamlit tab dedicated to review analytics."""

    st.header("📝 Analyse des avis utilisateurs")
    st.caption(
        "Suivi du volume d'avis, de l'activité des reviewers et de leur impact sur les notes."
    )

    # =========================
    # 1. Indicateurs clés
    # =========================
    try:
        overview_resp = requests.get(f"{BASE_URL}/mange_ta_main/review-overview")
        overview_resp.raise_for_status()
        overview_data = overview_resp.json()
        logger.info("Review overview fetched", count=len(overview_data))
    except requests.RequestException as exc:
        st.error(f"Impossible de récupérer les indicateurs d'avis : {exc}")
        logger.error("Failed to fetch review overview", error=str(exc))
        overview_data = []

    if overview_data:
        overview_df = pd.DataFrame(overview_data)
        metrics_map = {row["metric"]: row["value"] for _, row in overview_df.iterrows()}

        primary_metrics = [
            ("total_reviews", "Avis publiés"),
            ("unique_reviewers", "Reviewers actifs"),
            ("share_recipes_reviewed_pct", "% Recettes avec avis"),
        ]
        secondary_metrics = [
            ("avg_reviews_per_recipe", "Avis moyens/recette"),
            ("median_review_length_words", "Longueur médiane (mots)"),
            ("avg_rating_given", "Note moyenne donnée"),
        ]

        col1, col2, col3 = st.columns(3)
        for col, (metric_id, label) in zip((col1, col2, col3), primary_metrics):
            col.metric(label, _format_metric(metric_id, metrics_map.get(metric_id)))

        col4, col5, col6 = st.columns(3)
        for col, (metric_id, label) in zip((col4, col5, col6), secondary_metrics):
            col.metric(label, _format_metric(metric_id, metrics_map.get(metric_id)))

        insights = []
        total_reviews = metrics_map.get("total_reviews")
        unique_reviewers = metrics_map.get("unique_reviewers")
        share_reviewed_pct = metrics_map.get("share_recipes_reviewed_pct")
        avg_reviews_per_recipe = metrics_map.get("avg_reviews_per_recipe")
        empty_ratio_pct = metrics_map.get("empty_review_ratio_pct")
        median_len = metrics_map.get("median_review_length_words")
        avg_rating_given = metrics_map.get("avg_rating_given")

        if total_reviews and unique_reviewers:
            total_reviews_display = f"{int(total_reviews):,}".replace(",", " ")
            unique_reviewers_display = f"{int(unique_reviewers):,}".replace(",", " ")
            avg_reviews_per_reviewer = (
                total_reviews / unique_reviewers if unique_reviewers else None
            )
            if avg_reviews_per_reviewer:
                insights.append(
                    f"{total_reviews_display} avis ont été publiés par {unique_reviewers_display} reviewers, soit environ {avg_reviews_per_reviewer:.1f} contributions par personne."
                )
        if share_reviewed_pct is not None:
            avg_reviews_recipe_display = (
                f"{avg_reviews_per_recipe:.2f}" if avg_reviews_per_recipe is not None else "-"
            )
            insights.append(
                f"La couverture du catalogue atteint {share_reviewed_pct:.1f} %, avec en moyenne {avg_reviews_recipe_display} avis par recette."
            )
        if empty_ratio_pct is not None and empty_ratio_pct > 0:
            insights.append(
                f"À surveiller : {empty_ratio_pct:.1f} % des interactions ne contiennent pas encore de commentaire exploitable."
            )
        if median_len is not None:
            insights.append(
                f"La médiane des avis textuels s'établit à {median_len:.1f} mots, ce qui traduit un niveau de détail intermédiaire."
            )
        if avg_rating_given is not None:
            insights.append(
                f"Le ton général reste positif avec une note moyenne attribuée de {avg_rating_given:.2f} sur 5."
            )

        if insights:
            st.markdown(" ".join(insights))
    else:
        st.warning("Aucune donnée de synthèse sur les avis n'est disponible.")

    st.divider()

    # =========================
    # 2. Distribution des avis
    # =========================
    st.subheader("Répartition du nombre d'avis par recette")
    view_mode = st.radio(
        "Afficher :",
        ["Nombre de recettes", "Part (%)"],
        horizontal=True,
        key="reviews_distribution_view_mode",
    )

    try:
        dist_resp = requests.get(f"{BASE_URL}/mange_ta_main/review-distribution")
        dist_resp.raise_for_status()
        dist_data = dist_resp.json()
        logger.info("Review distribution fetched", count=len(dist_data))
    except requests.RequestException as exc:
        st.error(f"Erreur lors de la récupération de la distribution d'avis : {exc}")
        logger.error("Failed to fetch review distribution", error=str(exc))
        dist_data = []

    if dist_data:
        dist_df = pd.DataFrame(dist_data).rename(
            columns={
                "reviews_bin": "Tranche d'avis",
                "recipe_count": "Recettes",
                "share_pct": "Part (%)",
                "avg_reviews_in_bin": "Avis moyens",
            }
        )

        try:
            dist_df["Recettes"] = pd.to_numeric(dist_df["Recettes"], errors="coerce")
            dist_df["Part (%)"] = pd.to_numeric(dist_df["Part (%)"], errors="coerce")
            dist_df["Avis moyens"] = pd.to_numeric(dist_df["Avis moyens"], errors="coerce")
        except KeyError:
            pass

        dist_df = dist_df.sort_values("Tranche d'avis")

        def _parse_min_reviews(label: str) -> int:
            s = str(label).replace("+", "")
            try:
                return int(s.split("-")[0])
            except (ValueError, IndexError):
                return 0

        dist_df["__min_reviews"] = dist_df["Tranche d'avis"].apply(_parse_min_reviews)

        target_col = "Recettes" if view_mode == "Nombre de recettes" else "Part (%)"
        chart = (
            alt.Chart(dist_df)
            .mark_bar(color="#5170ff")
            .encode(
                x=alt.X("Tranche d'avis:N", title="Nombre d'avis par recette"),
                y=alt.Y(f"{target_col}:Q", title=view_mode),
                tooltip=[
                    alt.Tooltip("Tranche d'avis:N"),
                    alt.Tooltip("Recettes:Q", format=","),
                    alt.Tooltip("Part (%):Q", format=".1f"),
                    alt.Tooltip("Avis moyens:Q", format=".2f"),
                ],
            )
        )
        st.altair_chart(chart, use_container_width=True)

        top_row: Optional[pd.Series] = None
        if "Recettes" in dist_df.columns and not dist_df["Recettes"].empty:
            top_idx = dist_df["Recettes"].idxmax()
            if pd.notna(top_idx):
                candidate = dist_df.loc[top_idx]
                if isinstance(candidate, pd.DataFrame):
                    top_row = candidate.iloc[0]
                else:
                    top_row = candidate
        if top_row is not None:
            top_label = str(top_row.get("Tranche d'avis", ""))
            recettes_raw = top_row.get("Recettes")
            part_raw = top_row.get("Part (%)")
            avg_reviews_raw = top_row.get("Avis moyens")
            recettes_val = int(float(recettes_raw)) if recettes_raw is not None else 0
            part_val = float(part_raw) if part_raw is not None else 0.0
            avg_reviews_val = float(avg_reviews_raw) if avg_reviews_raw is not None else 0.0
            st.caption(
                f"Tranche la plus fréquente : **{top_label}** "
                f"({recettes_val} recettes, {part_val:.1f}%)."
            )

        dist_insights = []
        zero_mask = dist_df["__min_reviews"] == 0
        if zero_mask.any():
            zero_share = float(dist_df.loc[zero_mask, "Part (%)"].iloc[0])
            dist_insights.append(
                f"Encore {zero_share:.1f} % du catalogue n'a pas reçu de premier avis, laissant un potentiel d'engagement."
            )
        engaged_share = float(dist_df.loc[dist_df["__min_reviews"] >= 5, "Part (%)"].sum())
        if engaged_share > 0:
            dist_insights.append(
                f"À l'inverse, {engaged_share:.1f} % des recettes recueillent au moins cinq avis, signe d'un noyau de contenus phares."
            )
        if top_row is not None and top_label:
            dist_insights.append(
                f"La tranche {top_label} concentre à elle seule {part_val:.1f} % des recettes et génère {avg_reviews_val:.2f} avis en moyenne."
            )
        if dist_insights:
            st.markdown(" ".join(dist_insights))

        dist_df = dist_df.drop(columns="__min_reviews")

        st.dataframe(dist_df, width="stretch", hide_index=True)
        download_csv = dist_df.to_csv(index=False)
        st.download_button(
            "📥 Exporter la distribution",
            download_csv,
            "distribution_avis_recettes.csv",
            "text/csv",
        )
    else:
        st.info("Distribution non disponible.")

    st.divider()

    # =========================
    # 3. Top reviewers
    # =========================
    st.subheader("Reviewers les plus actifs")

    try:
        reviewer_resp = requests.get(f"{BASE_URL}/mange_ta_main/top-reviewers")
        reviewer_resp.raise_for_status()
        reviewer_data = reviewer_resp.json()
        logger.info("Top reviewers fetched", count=len(reviewer_data))
    except requests.RequestException as exc:
        st.error(f"Erreur lors de la récupération des reviewers : {exc}")
        logger.error("Failed to fetch top reviewers", error=str(exc))
        reviewer_data = []

    if reviewer_data:
        reviewers_df = pd.DataFrame(reviewer_data)
        rename_map = {
            "reviewer_id": "Reviewer",
            "reviews_count": "Nombre d'avis",
            "share_pct": "Part (%)",
            "avg_rating_given": "Note moyenne donnée",
            "avg_review_length_words": "Longueur moyenne (mots)",
            "first_review_date": "Premier avis",
            "last_review_date": "Dernier avis",
        }
        reviewers_df = reviewers_df.rename(columns=rename_map)
        numeric_cols = [
            "Nombre d'avis",
            "Part (%)",
            "Note moyenne donnée",
            "Longueur moyenne (mots)",
        ]
        for col in numeric_cols:
            if col in reviewers_df.columns:
                reviewers_df[col] = pd.to_numeric(reviewers_df[col], errors="coerce")

        top_reviewer = reviewers_df.iloc[0]
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Top reviewer", str(top_reviewer["Reviewer"]))
        col_b.metric(
            "Avis publiés",
            _format_metric("total_reviews", top_reviewer["Nombre d'avis"]),
        )
        col_c.metric("Part du volume", _format_metric("share_pct", top_reviewer.get("Part (%)")))

        bars = (
            alt.Chart(reviewers_df)
            .mark_bar()
            .encode(
                x=alt.X("Nombre d'avis:Q", title="Nombre d'avis"),
                y=alt.Y("Reviewer:N", sort="-x", title="Reviewer"),
                tooltip=[
                    alt.Tooltip("Reviewer:N"),
                    alt.Tooltip("Nombre d'avis:Q", format=","),
                    alt.Tooltip("Part (%):Q", format=".1f"),
                    alt.Tooltip("Longueur moyenne (mots):Q", format=".1f"),
                ],
            )
        )
        st.altair_chart(bars, use_container_width=True)

        st.dataframe(reviewers_df, width="stretch", hide_index=True)

        reviewer_insights = []
        if "Part (%)" in reviewers_df.columns:
            top_share = float(top_reviewer.get("Part (%)", 0.0))
            reviewer_insights.append(
                f"Le reviewer le plus prolifique, {top_reviewer['Reviewer']}, concentre à lui seul {top_share:.1f} % des avis publiés."
            )
            share_top5 = float(reviewers_df["Part (%)"].head(5).sum())
            reviewer_insights.append(
                f"Les cinq contributeurs les plus actifs totalisent {share_top5:.1f} % du volume, confirmant un cœur de communauté très engagé."
            )
        avg_length_top = top_reviewer.get("Longueur moyenne (mots)")
        if pd.notna(avg_length_top):
            reviewer_insights.append(
                f"Leur feedback reste consistant, avec une longueur moyenne de {avg_length_top:.1f} mots pour le reviewer numéro un."
            )
        avg_rating_top = top_reviewer.get("Note moyenne donnée")
        if pd.notna(avg_rating_top):
            reviewer_insights.append(
                f"Le ton demeure globalement bienveillant, puisqu'il attribue une note moyenne de {avg_rating_top:.2f} sur 5."
            )
        if reviewer_insights:
            st.markdown(" ".join(reviewer_insights))
    else:
        st.info("Aucun reviewer actif détecté.")

    st.divider()

    # =========================
    # 4. Commentaires vs recettes publiées
    # =========================
    st.subheader("Commentaires rédigés vs recettes publiées (par utilisateur)")

    try:
        reviewer_vs_recipes_resp = requests.get(f"{BASE_URL}/mange_ta_main/reviewer-vs-recipes")
        reviewer_vs_recipes_resp.raise_for_status()
        reviewer_vs_recipes_data = reviewer_vs_recipes_resp.json()
        logger.info("Reviewer vs recipes fetched", count=len(reviewer_vs_recipes_data))
    except requests.RequestException as exc:
        st.error(f"Erreur lors de la corrélation reviewers / recettes : {exc}")
        logger.error("Failed to fetch reviewer vs recipes", error=str(exc))
        reviewer_vs_recipes_data = []

    if reviewer_vs_recipes_data:
        rr_df = pd.DataFrame(reviewer_vs_recipes_data)
        expected_cols = {"user_id", "reviews_count", "recipes_published"}
        if expected_cols.issubset(rr_df.columns):
            rr_df["reviews_count"] = pd.to_numeric(rr_df["reviews_count"], errors="coerce")
            rr_df["recipes_published"] = pd.to_numeric(rr_df["recipes_published"], errors="coerce")
            if "avg_rating_given" in rr_df.columns:
                rr_df["avg_rating_given"] = pd.to_numeric(
                    rr_df["avg_rating_given"], errors="coerce"
                )
            rr_df = rr_df.dropna(subset=["reviews_count", "recipes_published"])

            if rr_df.empty or rr_df["reviews_count"].nunique() <= 1:
                st.info("Pas assez d'utilisateurs différents pour tracer la relation.")
            else:
                rr_df = rr_df.sort_values("reviews_count")

                tooltip_fields = [
                    alt.Tooltip("user_id:N", title="Utilisateur"),
                    alt.Tooltip("reviews_count:Q", title="Avis rédigés", format=","),
                    alt.Tooltip("recipes_published:Q", title="Recettes publiées", format=","),
                ]
                if "avg_rating_given" in rr_df.columns:
                    tooltip_fields.append(
                        alt.Tooltip(
                            "avg_rating_given:Q",
                            title="Note moyenne donnée",
                            format=".2f",
                        )
                    )

                scatter = (
                    alt.Chart(rr_df)
                    .mark_circle(size=70, opacity=0.7, color="#ff6f61")
                    .encode(
                        x=alt.X("reviews_count:Q", title="Nombre d'avis rédigés"),
                        y=alt.Y("recipes_published:Q", title="Recettes publiées"),
                        tooltip=tooltip_fields,
                    )
                )

                regression = None
                corr_value = None
                if rr_df["reviews_count"].nunique() > 1:
                    try:
                        slope, intercept = np.polyfit(
                            rr_df["reviews_count"],
                            rr_df["recipes_published"],
                            1,
                        )
                        rr_df["predicted_recipes_published"] = (
                            slope * rr_df["reviews_count"] + intercept
                        )
                        corr_value = float(
                            np.corrcoef(
                                rr_df["reviews_count"],
                                rr_df["recipes_published"],
                            )[0, 1]
                        )
                        regression = (
                            alt.Chart(rr_df)
                            .mark_line(color="#27AE60", strokeWidth=2)
                            .encode(
                                x="reviews_count:Q",
                                y="predicted_recipes_published:Q",
                            )
                        )
                    except Exception:
                        regression = None

                chart_obj = scatter if regression is None else scatter + regression
                st.altair_chart(chart_obj.interactive(), use_container_width=True)

                rr_display_cols = [
                    c
                    for c in [
                        "user_id",
                        "reviews_count",
                        "recipes_published",
                        "avg_rating_given",
                    ]
                    if c in rr_df.columns
                ]
                st.dataframe(
                    rr_df[rr_display_cols],
                    width="stretch",
                    hide_index=True,
                )

                narrative_parts = []
                top_reviewer = rr_df.sort_values("reviews_count", ascending=False).iloc[0]
                narrative_parts.append(
                    f"L'utilisateur {top_reviewer['user_id']} est le plus prolifique avec {int(top_reviewer['reviews_count'])} avis rédigés."
                )

                top_author = rr_df.sort_values("recipes_published", ascending=False).iloc[0]
                narrative_parts.append(
                    f"Côté publication, {top_author['user_id']} mène avec {int(top_author['recipes_published'])} recettes au catalogue."
                )

                if corr_value is not None:
                    narrative_parts.append(
                        f"La corrélation linéaire entre avis rédigés et recettes publiées vaut {corr_value:.2f}, "
                        "ce qui suggère une tendance modérée : les contributeurs actifs en publication ne sont pas nécessairement les plus bavards en commentaires."
                    )

                heavy_dual = rr_df[
                    (rr_df["reviews_count"] >= 10) & (rr_df["recipes_published"] >= 5)
                ]
                if not heavy_dual.empty:
                    narrative_parts.append(
                        f"Nous identifions {len(heavy_dual)} 'super contributeurs' qui dépassent 10 avis rédigés et 5 recettes publiées ; un vivier clé pour animer la communauté."
                    )

                st.markdown(" ".join(narrative_parts))
        else:
            st.error("Colonnes inattendues reçues pour la corrélation reviewers / recettes.")
    else:
        st.info("Aucune donnée pour la corrélation entre avis rédigés et recettes publiées.")

    st.divider()

    # =========================
    # 5. Tendance temporelle
    # =========================
    st.subheader("Chronologie des avis publiés")

    try:
        trend_resp = requests.get(f"{BASE_URL}/mange_ta_main/review-trend")
        trend_resp.raise_for_status()
        trend_data = trend_resp.json()
        logger.info("Review trend fetched", count=len(trend_data))
    except requests.RequestException as exc:
        st.error(f"Erreur lors de la récupération de la chronologie : {exc}")
        logger.error("Failed to fetch review trend", error=str(exc))
        trend_data = []

    if trend_data:
        trend_df = pd.DataFrame(trend_data)
        if "period" in trend_df.columns:
            trend_df["period"] = pd.PeriodIndex(trend_df["period"], freq="M").to_timestamp()
        trend_df = trend_df.sort_values("period")

        line = (
            alt.Chart(trend_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("period:T", title="Période"),
                y=alt.Y("reviews_count:Q", title="Avis publiés"),
                tooltip=[
                    alt.Tooltip("period:T", title="Période", format="%Y-%m"),
                    alt.Tooltip("reviews_count:Q", title="Avis", format=","),
                ],
            )
        )

        if "unique_reviewers" in trend_df.columns:
            line2 = (
                alt.Chart(trend_df)
                .mark_line(color="#F39C12")
                .encode(
                    x="period:T",
                    y=alt.Y("unique_reviewers:Q", title="Reviewers uniques"),
                    tooltip=[
                        alt.Tooltip("unique_reviewers:Q", title="Reviewers uniques", format=",")
                    ],
                )
            )
            st.altair_chart((line + line2).interactive(), use_container_width=True)
            st.caption("Bleu : volume d'avis | Orange : reviewers uniques.")
        else:
            st.altair_chart(line.interactive(), use_container_width=True)

        st.dataframe(
            trend_df.rename(columns={"period": "Période"}),
            width="stretch",
            hide_index=True,
        )

        trend_insights = []
        last_row = trend_df.iloc[-1]
        if isinstance(last_row["period"], pd.Timestamp):
            last_period_label = last_row["period"].strftime("%Y-%m")
        else:
            last_period_label = str(last_row["period"])
        trend_insights.append(
            f"Sur le mois {last_period_label}, la plateforme a enregistré {int(last_row['reviews_count'])} avis."
        )
        if "unique_reviewers" in trend_df.columns:
            trend_insights.append(
                f"Ce volume émane de {int(last_row['unique_reviewers'])} reviewers distincts, signe d'une communauté élargie."
            )
        if len(trend_df) >= 6:
            recent_mean = trend_df["reviews_count"].tail(3).mean()
            previous_mean = trend_df["reviews_count"].iloc[-6:-3].mean()
            if pd.notna(previous_mean) and previous_mean > 0:
                delta = (recent_mean - previous_mean) / previous_mean * 100
                trend_insights.append(
                    f"Le momentum des trois derniers mois progresse de {delta:+.1f} % par rapport au trimestre précédent."
                )
        if trend_insights:
            st.markdown(" ".join(trend_insights))
    else:
        st.info("Aucune donnée temporelle pour les avis.")

    st.divider()

    # =========================
    # 6. Avis vs note moyenne
    # =========================
    st.subheader("Relation entre volume d'avis et note moyenne")

    try:
        scatter_resp = requests.get(f"{BASE_URL}/mange_ta_main/reviews-vs-rating")
        scatter_resp.raise_for_status()
        scatter_data = scatter_resp.json()
        logger.info("Reviews vs rating fetched", count=len(scatter_data))
    except requests.RequestException as exc:
        st.error(f"Erreur lors de la récupération des corrélations : {exc}")
        logger.error("Failed to fetch reviews vs rating", error=str(exc))
        scatter_data = []

    if scatter_data:
        scatter_df = pd.DataFrame(scatter_data)
        expected_cols = {"recipe_id", "review_count", "avg_rating"}
        if expected_cols.issubset(scatter_df.columns):
            scatter_df["review_count"] = pd.to_numeric(scatter_df["review_count"], errors="coerce")
            scatter_df["avg_rating"] = pd.to_numeric(scatter_df["avg_rating"], errors="coerce")
            scatter_df = scatter_df.dropna(subset=["review_count", "avg_rating"])

            if not scatter_df.empty:
                scatter_df = scatter_df[scatter_df["review_count"] > 0]
                scatter_df = scatter_df.sort_values("review_count")

                tooltip_fields = [
                    alt.Tooltip("recipe_id:N", title="Recette ID"),
                    alt.Tooltip("review_count:Q", title="Avis", format=","),
                    alt.Tooltip("avg_rating:Q", title="Note moyenne", format=".2f"),
                ]
                if "recipe_name" in scatter_df.columns:
                    tooltip_fields.insert(0, alt.Tooltip("recipe_name:N", title="Recette"))
                if "contributor_id" in scatter_df.columns:
                    tooltip_fields.append(alt.Tooltip("contributor_id:N", title="Contributeur"))

                base = (
                    alt.Chart(scatter_df)
                    .mark_circle(size=70, opacity=0.7)
                    .encode(
                        x=alt.X("review_count:Q", title="Nombre d'avis"),
                        y=alt.Y("avg_rating:Q", title="Note moyenne"),
                        tooltip=tooltip_fields,
                    )
                )

                corr_coef_value = None
                try:
                    slope, intercept = np.polyfit(
                        scatter_df["review_count"], scatter_df["avg_rating"], 1
                    )
                    scatter_df["predicted_avg_rating"] = (
                        slope * scatter_df["review_count"] + intercept
                    )
                    corr_coef_value = float(
                        np.corrcoef(scatter_df["review_count"], scatter_df["avg_rating"])[0, 1]
                    )
                    regression = (
                        alt.Chart(scatter_df)
                        .mark_line(color="#27AE60", strokeWidth=2)
                        .encode(x="review_count:Q", y="predicted_avg_rating:Q")
                    )
                    st.altair_chart((base + regression).interactive(), use_container_width=True)
                    st.caption(
                        f"Régression linéaire : note ≈ {slope:.3f} × avis + {intercept:.3f}."
                    )
                except Exception:
                    st.altair_chart(base.interactive(), use_container_width=True)
                    st.caption("Régression non calculable (données insuffisantes).")

                display_cols = [
                    c
                    for c in [
                        "recipe_name",
                        "recipe_id",
                        "contributor_id",
                        "review_count",
                        "avg_rating",
                    ]
                    if c in scatter_df.columns
                ]
                st.dataframe(scatter_df[display_cols], width="stretch", hide_index=True)

                scatter_insights = []
                if corr_coef_value is not None:
                    scatter_insights.append(
                        f"La corrélation reste modérée (r = {corr_coef_value:.2f}) entre le volume d'avis et la note moyenne."
                    )
                top_recipe = scatter_df.iloc[-1]
                recipe_label = top_recipe.get("recipe_name", f"Recette #{top_recipe['recipe_id']}")
                scatter_insights.append(
                    f"La recette la plus commentée, {recipe_label}, totalise {int(top_recipe['review_count'])} avis pour une moyenne de {top_recipe['avg_rating']:.2f}/5."
                )
                heavy = scatter_df[scatter_df["review_count"] >= 10]
                if not heavy.empty:
                    scatter_insights.append(
                        f"Nous identifions {len(heavy)} recettes très populaires avec au moins dix avis et une moyenne combinée de {heavy['avg_rating'].mean():.2f}/5."
                    )
                if scatter_insights:
                    st.markdown(" ".join(scatter_insights))
            else:
                st.info("Pas assez de points avec avis > 0 pour tracer la relation.")
        else:
            st.error("Colonnes inattendues reçues pour la corrélation avis / note.")
    else:
        st.info("Aucune corrélation à afficher.")
