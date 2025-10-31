"""Collection of analytical helpers powering the API and dashboards."""

import ast
from enum import StrEnum
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
import pandas as pd

from service.layers.application.exceptions import UnsupportedAnalysisError
from service.layers.application.interfaces.interface import IDataAdapter
from service.layers.infrastructure.types import DataType

# ===============================
# Constantes & Types
# ===============================

SEGMENT_INFO: Dict[int, Dict[str, Any]] = {
    0: {
        "persona": "Super Cookers",
        "ref_avg_minutes": 55,
        "ref_avg_rating": 4.4,
        "ref_avg_reviews": 12,
    },
    1: {
        "persona": "Quick Cookers",
        "ref_avg_minutes": 18,
        "ref_avg_rating": 3.6,
        "ref_avg_reviews": 3,
    },
    2: {
        "persona": "Sweet Lovers",
        "ref_avg_minutes": 40,
        "ref_avg_rating": 4.2,
        "ref_avg_reviews": 6,
    },
    3: {
        "persona": "Talkative Tasters",
        "ref_avg_minutes": 35,
        "ref_avg_rating": 3.8,
        "ref_avg_reviews": 18,
    },
    4: {
        "persona": "Experimental Foodies",
        "ref_avg_minutes": 45,
        "ref_avg_rating": 3.5,
        "ref_avg_reviews": 10,
    },
    5: {
        "persona": "Everyday Cookers",
        "ref_avg_minutes": 30,
        "ref_avg_rating": 3.9,
        "ref_avg_reviews": 7,
    },
}


class AnalysisType(StrEnum):
    NO_ANALYSIS = "no_analysis"
    NUMBER_RECIPES = "number_recipes"
    BEST_RECIPES = "best_recipes"
    NUMBER_COMMENTS = "number_comments"
    DURATION_DISTRIBUTION = "duration_distribution"
    DURATION_VS_RECIPE_COUNT = "duration_vs_recipe_count"
    TOP_10_PERCENT_CONTRIBUTORS = "top_10_percent_contributors"
    USER_SEGMENTS = "user_segments"  # 👈 nouveau
    TOP_TAGS_BY_SEGMENT = "top_tags_by_segment"  # 👈 nouveau
    RATING_DISTRIBUTION = "rating_distribution"
    RATING_VS_RECIPES = "rating_vs_recipes"
    REVIEW_OVERVIEW = "review_overview"
    REVIEW_DISTRIBUTION = "review_distribution"
    REVIEWER_ACTIVITY = "reviewer_activity"
    REVIEW_TEMPORAL_TREND = "review_temporal_trend"
    REVIEWS_VS_RATING = "reviews_vs_rating"
    REVIEWER_VS_RECIPES = "reviewer_vs_recipes"


# ===============================
# Utilitaires
# ===============================


def _parse_tags_to_list(v) -> List[str]:
    """Normalise the ``tags`` column into a clean list of strings."""
    if isinstance(v, list):
        return [str(t).strip().lower() for t in v if str(t).strip()]
    if pd.isna(v):
        return []
    s = str(v).strip()
    try:
        parsed = ast.literal_eval(s) if (s.startswith("[") and s.endswith("]")) else s
        if isinstance(parsed, list):
            return [str(t).strip().lower() for t in parsed if str(t).strip()]
        # fallback: split simple
        return [t.strip().lower() for t in str(parsed).split(",") if t.strip()]
    except Exception:
        return [t.strip().lower() for t in s.split(",") if t.strip()]


# ===============================
# Fonctions
# ===============================


def most_recipes_contributors(df_recipes: pd.DataFrame) -> pd.DataFrame:
    """Rank contributors by the number of published recipes.

    Args:
        df_recipes: Dataset containing at least the columns ``id`` and
            ``contributor_id``.

    Returns:
        Dataframe ordered by ``Nombre de Recettes`` with one row per contributor.
    """
    number_recipes_contributors = (
        df_recipes.groupby("contributor_id").size().sort_values(ascending=False).reset_index()
    )
    return number_recipes_contributors


def best_ratings_contributors(
    df_recipes: pd.DataFrame, df_interactions: pd.DataFrame
) -> pd.DataFrame:
    """Highlight contributors with the highest average rating.

    Args:
        df_recipes: Recipe catalogue with ``id`` and ``contributor_id``.
        df_interactions: Interactions dataframe containing ``recipe_id`` and
            ``rating``.

    Returns:
        A dataframe with ``contributor_id``, ``avg_rating`` and ``num_recipes``
        sorted by decreasing average rating and filtered so only authors with at
        least five recipes remain.
    """
    avg_ratings = (
        df_interactions.groupby("recipe_id")["rating"].mean().reset_index(name="avg_rating")
    )

    df = df_recipes.merge(avg_ratings, how="left", left_on="id", right_on="recipe_id")

    contributor_counts = df.groupby("contributor_id")["id"].count().reset_index(name="num_recipes")
    contributor_avg = df.groupby("contributor_id")["avg_rating"].mean().reset_index()

    contributor_stats = contributor_avg.merge(contributor_counts, on="contributor_id")
    contributor_stats = contributor_stats[contributor_stats["num_recipes"] >= 5]

    contributor_stats = (
        contributor_stats.sort_values(by="avg_rating", ascending=False)
        .reset_index(drop=True)
        .where(pd.notna(contributor_stats), None)
    )
    return contributor_stats


def average_duration_distribution(
    df_recipes: pd.DataFrame,
    duration_col: str = "minutes",
    bins: Optional[Union[int, Sequence[float]]] = None,
    labels: Optional[Sequence[str]] = None,
    group_cols: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Build a histogram-like distribution for recipe durations.

    Args:
        df_recipes: Recipes dataframe holding the duration column.
        duration_col: Column to analyse (defaults to ``minutes``).
        bins: Either an integer describing the number of bins or explicit
            edges passed to :func:`pandas.cut`.
        labels: Optional labels per bin.
        group_cols: Optional columns used to compute distributions per cohort.

    Returns:
        A dataframe with the bin label, count, share and cumulative share
        (optionally split by ``group_cols``).
    """
    df = df_recipes.copy()
    df[duration_col] = pd.to_numeric(df[duration_col], errors="coerce")
    df = df.dropna(subset=[duration_col])

    # Derive bin edges used to stratify recipes by duration.
    resolved_bins: Union[int, Sequence[float]]
    resolved_labels: Optional[Sequence[str]] = labels
    if bins is None:
        resolved_bins = [0, 15, 30, 45, 60, 90, 120, np.inf]
        if resolved_labels is None:
            resolved_labels = [
                "0–15",
                "15–30",
                "30–45",
                "45–60",
                "60–90",
                "90–120",
                "120+",
            ]
    else:
        resolved_bins = bins

    # When an integer is provided, generate evenly spaced bins.
    if isinstance(resolved_bins, int):
        vmin, vmax = df[duration_col].min(), df[duration_col].max()
        resolved_bins = np.linspace(vmin, vmax, resolved_bins + 1).tolist()

    # Cut the durations into the resolved bins.
    df["duration_bin"] = pd.cut(
        df[duration_col],
        bins=resolved_bins,
        labels=resolved_labels,
        include_lowest=True,
        right=False,
    )

    # Aggregate counts and mean duration per bin.
    group_cols_list = list(group_cols) if group_cols else []
    group_keys = group_cols_list + ["duration_bin"]

    agg = (
        df.groupby(group_keys, observed=False)
        .agg(count=(duration_col, "size"), avg_duration_in_bin=(duration_col, "mean"))
        .reset_index()
    )

    # Compute shares within each group (or globally).
    if group_cols_list:
        totals = (
            agg.groupby(group_cols_list, observed=False)["count"]
            .sum()
            .reset_index(name="total_count")
        )
        out = agg.merge(totals, on=group_cols_list, how="left")
    else:
        total_count = agg["count"].sum()
        out = agg.assign(total_count=total_count)

    out["share"] = (out["count"] / out["total_count"] * 100).round(2)

    # Compute the cumulative share to ease interpretation.
    out = out.sort_values(group_cols_list + ["duration_bin"]).reset_index(drop=True)
    if group_cols_list:
        out["cum_share"] = out.groupby(group_cols_list, observed=False)["share"].cumsum().round(2)
    else:
        out["cum_share"] = out["share"].cumsum().round(2)

    out = out.drop(columns=["total_count"])
    out["avg_duration_in_bin"] = pd.to_numeric(out["avg_duration_in_bin"], errors="coerce").round(1)

    return out


def duration_vs_recipe_count(
    df_recipes: pd.DataFrame,
    duration_col: str = "minutes",
) -> pd.DataFrame:
    """Compute publication volume and duration statistics per contributor.

    Args:
        df_recipes: Recipes dataframe with at least ``contributor_id`` and the
            specified duration column.
        duration_col: Name of the column storing recipe durations.

    Returns:
        Dataframe containing per-contributor recipe counts and duration stats.
    """
    df = df_recipes.copy()
    df = df.dropna(subset=["contributor_id"])
    df[duration_col] = pd.to_numeric(df[duration_col], errors="coerce")
    df = df.dropna(subset=[duration_col])

    agg = (
        df.groupby("contributor_id")
        .agg(
            recipe_count=("id", "size"),
            avg_duration=(duration_col, "mean"),
            median_duration=(duration_col, "median"),
        )
        .reset_index()
    )

    if agg.empty:
        return agg

    agg["avg_duration"] = agg["avg_duration"].round(2)
    agg["median_duration"] = agg["median_duration"].round(2)
    return agg


def top_10_percent_contributors(
    df_recipes: pd.DataFrame,
    df_interactions: pd.DataFrame,
    duration_col: str = "minutes",
) -> pd.DataFrame:
    """Compare the most prolific authors with the rest of the catalogue.

    Args:
        df_recipes: Recipe dataframe used to compute volume and duration stats.
        df_interactions: Interactions dataframe to derive ratings and comments.
        duration_col: Column containing the recipe duration in minutes.

    Returns:
        A dataframe with two rows – top cohort and global – each exposing the
        contributor count and several aggregate metrics.
    """
    df = df_recipes.copy()
    df[duration_col] = pd.to_numeric(df[duration_col], errors="coerce")

    # Recettes par contributeur & seuil Top10%
    contrib_count = df.groupby("contributor_id")["id"].count().reset_index(name="num_recipes")
    threshold = contrib_count["num_recipes"].quantile(0.90)

    top_contributors = contrib_count[contrib_count["num_recipes"] >= threshold]["contributor_id"]
    df_top = df[df["contributor_id"].isin(top_contributors)]

    # TOP 10%
    avg_duration_top = df_top[duration_col].mean()
    avg_rating_top = (
        df_interactions[df_interactions["recipe_id"].isin(df_top["id"])]
        .groupby("recipe_id")["rating"]
        .mean()
        .mean()
    )
    avg_comments_top = (
        df_interactions[df_interactions["recipe_id"].isin(df_top["id"])]
        .groupby("recipe_id")["rating"]
        .count()
        .mean()
    )

    # GLOBAL
    avg_duration_global = df[duration_col].mean()
    avg_rating_global = df_interactions.groupby("recipe_id")["rating"].mean().mean()
    avg_comments_global = df_interactions.groupby("recipe_id")["rating"].count().mean()

    result = pd.DataFrame(
        [
            {
                "population": "top_10_percent",
                "avg_duration_minutes": (
                    round(float(avg_duration_top), 2) if pd.notna(avg_duration_top) else None
                ),
                "avg_rating": round(float(avg_rating_top), 2) if pd.notna(avg_rating_top) else None,
                "avg_comments": (
                    round(float(avg_comments_top), 2) if pd.notna(avg_comments_top) else None
                ),
                "contributor_count": int(len(top_contributors)),
            },
            {
                "population": "global",
                "avg_duration_minutes": (
                    round(float(avg_duration_global), 2) if pd.notna(avg_duration_global) else None
                ),
                "avg_rating": (
                    round(float(avg_rating_global), 2) if pd.notna(avg_rating_global) else None
                ),
                "avg_comments": (
                    round(float(avg_comments_global), 2) if pd.notna(avg_comments_global) else None
                ),
                "contributor_count": int(df["contributor_id"].nunique()),
            },
        ]
    )
    return result


def compute_user_segments(
    df_recipes: pd.DataFrame,
    df_interactions: pd.DataFrame,
    duration_col: str = "minutes",
) -> pd.DataFrame:
    """Assign each contributor to one of the predefined behavioural personas.

    Args:
        df_recipes: Recipe dataframe containing contributor identifiers and
            preparation durations.
        df_interactions: Interactions dataframe providing rating information.
        duration_col: Column name holding the preparation time in minutes.

    Returns:
        A dataframe listing per-contributor averages and the matching segment.
    """
    df_r = df_recipes[["id", "contributor_id", duration_col]].copy()
    df_r[duration_col] = pd.to_numeric(df_r[duration_col], errors="coerce")

    df_i = df_interactions[["recipe_id", "rating"]].copy()
    df_i["rating"] = pd.to_numeric(df_i["rating"], errors="coerce")

    # Moyenne minutes par contributeur
    g_minutes = (
        df_r.groupby("contributor_id", dropna=True)[duration_col].mean().rename("avg_minutes")
    )

    # Note moyenne par recette, puis moyenne par contributeur
    recipe_avg_rating = df_i.groupby("recipe_id")["rating"].mean().rename("recipe_avg_rating")
    g_rating = (
        df_r.merge(recipe_avg_rating, left_on="id", right_index=True, how="left")
        .groupby("contributor_id")["recipe_avg_rating"]
        .mean()
        .rename("avg_rating")
    )

    # Nombre d'avis par recette, puis moyenne par contributeur
    recipe_review_count = df_i.groupby("recipe_id")["rating"].count().rename("review_count")
    g_reviews = (
        df_r.merge(recipe_review_count, left_on="id", right_index=True, how="left")
        .groupby("contributor_id")["review_count"]
        .mean()
        .rename("avg_reviews")
    )

    df_users = (
        pd.concat([g_minutes, g_rating, g_reviews], axis=1)
        .reset_index()
        .dropna(subset=["avg_minutes", "avg_rating", "avg_reviews"])
    )

    if df_users.empty:
        return pd.DataFrame(
            columns=[
                "contributor_id",
                "avg_minutes",
                "avg_rating",
                "avg_reviews",
                "segment",
                "persona",
            ]
        )

    # Build matrices for users (N x 3) and centroids (K x 3).
    U = df_users[["avg_minutes", "avg_rating", "avg_reviews"]].to_numpy(dtype=float)
    centroids_df = pd.DataFrame.from_dict(SEGMENT_INFO, orient="index")
    C = centroids_df[["ref_avg_minutes", "ref_avg_rating", "ref_avg_reviews"]].to_numpy(dtype=float)

    # Vectorised Euclidean distance between every user and persona centroid.
    distances = np.sqrt(((U[:, None, :] - C[None, :, :]) ** 2).sum(axis=2))

    # Assign each user to the nearest centroid (index matches SEGMENT_INFO keys).
    seg_idx = distances.argmin(axis=1)
    df_users["segment"] = seg_idx

    # Enrich with the persona label for display purposes.
    df_users = df_users.merge(
        centroids_df.reset_index().rename(columns={"index": "segment"})[["segment", "persona"]],
        on="segment",
        how="left",
    )

    # Final formatting for readability.
    df_users["avg_minutes"] = df_users["avg_minutes"].round(2)
    df_users["avg_rating"] = df_users["avg_rating"].round(2)
    df_users["avg_reviews"] = df_users["avg_reviews"].round(2)

    return df_users[
        [
            "contributor_id",
            "avg_minutes",
            "avg_rating",
            "avg_reviews",
            "segment",
            "persona",
        ]
    ]


def top_tags_by_segment_from_users(
    df_recipes: pd.DataFrame,
    df_user_segments: pd.DataFrame,
    tags_col: str = "tags",
    top_k: int = 5,
) -> pd.DataFrame:
    """Return the top ``top_k`` tags used by each contributor segment."""
    # Join recipes with user segments through the contributor identifier.
    df_r = df_recipes[["id", "contributor_id", tags_col]].copy()
    df_r = df_r.merge(
        df_user_segments[["contributor_id", "segment", "persona"]],
        on="contributor_id",
        how="inner",
    )

    # Parse the raw tag representation into lists.
    df_r[tags_col] = df_r[tags_col].apply(_parse_tags_to_list)

    # Expand one row per tag to simplify aggregations.
    df_tags = df_r.explode(tags_col).dropna(subset=[tags_col])
    if df_tags.empty:
        return pd.DataFrame(columns=["segment", "persona", "tag", "count", "share_pct"])

    # Count tag occurrences per segment.
    counts = (
        df_tags.groupby(["segment", "persona", tags_col], dropna=False, observed=False)
        .size()
        .reset_index(name="count")
    )

    # Compute shares within each (segment, persona) pair.
    totals = (
        counts.groupby(["segment", "persona"], observed=False)["count"]
        .sum()
        .reset_index(name="segment_total")
    )
    counts = counts.merge(totals, on=["segment", "persona"], how="left")
    counts["share_pct"] = (counts["count"] / counts["segment_total"] * 100).round(2)

    # Keep only the top-k tags per segment for display purposes.
    counts = counts.sort_values(["segment", "count"], ascending=[True, False])
    topk = counts.groupby("segment").head(top_k).reset_index(drop=True)

    topk = topk.rename(columns={tags_col: "tag"})
    return (
        topk[["segment", "persona", "tag", "count", "share_pct"]]
        .sort_values(["segment", "count"], ascending=[True, False])
        .reset_index(drop=True)
    )


def _find_col(df: Optional[pd.DataFrame], candidates):
    """Return the first column matching one of ``candidates`` (case-insensitive)."""
    if df is None:
        return None
    cols = list(df.columns)
    for c in candidates:
        if c in cols:
            return c
        lc = c.lower()
        for col in cols:
            if col.lower() == lc:
                return col
    for token in candidates:
        for col in cols:
            if token in col.lower():
                return col
    return None


def _non_empty_text_mask(series: Optional[pd.Series]) -> pd.Series:
    """Return a boolean mask highlighting non-empty review strings."""
    if series is None:
        return pd.Series(dtype=bool)
    return (
        series.fillna("").astype(str).str.replace(r"<br\\s*/?>", " ", regex=True).str.strip().ne("")
    )


def _word_count(series: Optional[pd.Series]) -> pd.Series:
    """Approximate the word count for each review entry."""
    if series is None or series.empty:
        return pd.Series(dtype=float)
    clean = series.fillna("").astype(str).str.replace(r"<br\\s*/?>", " ", regex=True).str.strip()
    return clean.str.split().map(len).astype(float)


def rating_distribution(
    df_recipes: Optional[pd.DataFrame],
    df_interactions: Optional[pd.DataFrame],
    bins: Optional[Sequence[float]] = (0, 1, 2, 3, 4, 5),
    labels: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Compute a distribution of contributors grouped by their mean rating."""
    if df_recipes is None or df_recipes.empty or df_interactions is None or df_interactions.empty:
        return pd.DataFrame(
            columns=["rating_bin", "count", "share", "avg_rating_in_bin", "cum_share"]
        )

    recipe_id_col = _find_col(df_interactions, ["recipe_id", "recipe", "id"])
    rating_col = _find_col(df_interactions, ["rating", "score", "stars"])
    recipe_id_in_recipes = _find_col(df_recipes, ["id", "recipe_id"])

    if recipe_id_col is None or rating_col is None or recipe_id_in_recipes is None:
        return pd.DataFrame(
            columns=["rating_bin", "count", "share", "avg_rating_in_bin", "cum_share"]
        )

    per_recipe = (
        df_interactions.dropna(subset=[recipe_id_col, rating_col])
        .groupby(recipe_id_col, observed=False)[rating_col]
        .mean()
        .reset_index(name="avg_rating")
    )

    contrib_col = _find_col(df_recipes, ["contributor_id", "contributor", "author", "user"])
    if contrib_col is None:
        return pd.DataFrame(
            columns=["rating_bin", "count", "share", "avg_rating_in_bin", "cum_share"]
        )

    recipes_meta = df_recipes[[recipe_id_in_recipes, contrib_col]].rename(
        columns={recipe_id_in_recipes: recipe_id_col, contrib_col: "contributor_id"}
    )

    merged = per_recipe.merge(recipes_meta, on=recipe_id_col, how="left")

    avg = (
        merged.dropna(subset=["contributor_id"])
        .groupby("contributor_id", observed=False)["avg_rating"]
        .mean()
        .reset_index(name="avg_rating")
    )

    bins_sequence = list(bins) if bins is not None else [0, 1, 2, 3, 4, 5]
    if len(bins_sequence) < 2:
        return pd.DataFrame(
            columns=["rating_bin", "count", "share", "avg_rating_in_bin", "cum_share"]
        )

    if labels is None:
        generated_labels = [
            f"{bins_sequence[i]}-{bins_sequence[i + 1]}" for i in range(len(bins_sequence) - 1)
        ]
        if generated_labels:
            generated_labels[-1] = f"{bins_sequence[-2]}+"
        resolved_labels: Optional[Sequence[str]] = generated_labels
    else:
        resolved_labels = labels

    avg["rating_bin"] = pd.cut(
        avg["avg_rating"],
        bins=bins_sequence,
        labels=resolved_labels,
        include_lowest=True,
        right=False,
    )

    distribution = (
        avg.groupby("rating_bin", observed=False)
        .agg(
            count=("contributor_id", "nunique"),
            avg_rating_in_bin=("avg_rating", "mean"),
        )
        .reset_index()
    )

    total = int(distribution["count"].sum()) if not distribution.empty else 0
    if total == 0:
        distribution["share"] = 0.0
        distribution["cum_share"] = 0.0
    else:
        distribution["share"] = (distribution["count"] / total * 100).round(2)
        distribution["cum_share"] = distribution["share"].cumsum().round(2)

    distribution["rating_bin"] = distribution["rating_bin"].astype(str)
    return distribution[["rating_bin", "count", "share", "avg_rating_in_bin", "cum_share"]]


def rating_vs_recipe_count(
    df_recipes: Optional[pd.DataFrame],
    df_interactions: Optional[pd.DataFrame],
) -> pd.DataFrame:
    """Correlate recipe volume with average and median ratings per author."""
    if df_recipes is None or df_recipes.empty:
        return pd.DataFrame(
            columns=["contributor_id", "recipe_count", "avg_rating", "median_rating"]
        )

    recipe_id_col = _find_col(df_interactions, ["recipe_id", "recipe", "id"])
    rating_col = _find_col(df_interactions, ["rating", "score", "stars"])
    recipe_id_in_recipes = _find_col(df_recipes, ["id", "recipe_id"])
    contrib_col = _find_col(df_recipes, ["contributor_id", "contributor", "author", "user"])

    if recipe_id_in_recipes is None or contrib_col is None:
        return pd.DataFrame(
            columns=["contributor_id", "recipe_count", "avg_rating", "median_rating"]
        )

    recipe_counts = (
        df_recipes.groupby(contrib_col)
        .size()
        .reset_index(name="recipe_count")
        .rename(columns={contrib_col: "contributor_id"})
    )

    if (
        df_interactions is None
        or df_interactions.empty
        or recipe_id_col is None
        or rating_col is None
    ):
        recipe_counts["avg_rating"] = np.nan
        recipe_counts["median_rating"] = np.nan
        return recipe_counts[["contributor_id", "recipe_count", "avg_rating", "median_rating"]]

    per_recipe = (
        df_interactions.dropna(subset=[recipe_id_col, rating_col])
        .groupby(recipe_id_col, observed=False)[rating_col]
        .agg(["mean", "median"])
        .reset_index()
        .rename(columns={"mean": "avg_rating", "median": "median_rating"})
    )

    merged = per_recipe.merge(
        df_recipes[[recipe_id_in_recipes, contrib_col]].rename(
            columns={recipe_id_in_recipes: recipe_id_col, contrib_col: "contributor_id"}
        ),
        on=recipe_id_col,
        how="left",
    ).dropna(subset=["contributor_id"])

    contrib_ratings = (
        merged.groupby("contributor_id", observed=False)
        .agg(
            avg_rating=("avg_rating", "mean"),
            median_rating=("median_rating", "median"),
        )
        .reset_index()
    )

    result = contrib_ratings.merge(recipe_counts, on="contributor_id", how="right")
    result["recipe_count"] = (
        pd.to_numeric(result["recipe_count"], errors="coerce").fillna(0).astype(int)
    )
    avg_rating_series = result.get("avg_rating")
    median_rating_series = result.get("median_rating")
    if avg_rating_series is not None:
        result["avg_rating"] = pd.to_numeric(avg_rating_series, errors="coerce")
    else:
        result["avg_rating"] = np.nan
    if median_rating_series is not None:
        result["median_rating"] = pd.to_numeric(median_rating_series, errors="coerce")
    else:
        result["median_rating"] = np.nan

    return result[["contributor_id", "recipe_count", "avg_rating", "median_rating"]]


def review_overview(
    df_recipes: Optional[pd.DataFrame],
    df_interactions: Optional[pd.DataFrame],
) -> pd.DataFrame:
    """Summarise global KPIs about textual reviews and their authors.

    Args:
        df_recipes: Catalogue of recipes. At minimum, an ``id`` (or ``recipe_id``)
            column must be present so that we can evaluate the coverage rate.
        df_interactions: Log of user interactions containing review text, ratings
            and identifiers (``recipe_id`` and ``user_id``). Empty strings are
            considered missing reviews.

    Returns:
        A tidy dataframe with two columns, ``metric`` and ``value``. The returned
        metrics include total review volume, catalogue coverage, reviewer activity
        and descriptive statistics (length of comments, note moyenne, …).
        If the inputs are incomplete, an empty dataframe is returned.

    Notes:
        - Only catalogue recipes are considered when computing the coverage
          percentage; this prevents ratios above 100 % when the interaction table
          references deleted or unpublished recipes.
        - The function gracefully handles datasets with no written reviews
          (all metrics fall back to zero or ``None``).
    """
    if df_recipes is None or df_recipes.empty or df_interactions is None or df_interactions.empty:
        return pd.DataFrame(columns=["metric", "value"])

    recipe_id_recipes = _find_col(df_recipes, ["id", "recipe_id"])
    recipe_id_interactions = _find_col(df_interactions, ["recipe_id", "recipe", "id"])
    user_col = _find_col(df_interactions, ["user_id", "user", "reviewer"])
    review_col = _find_col(df_interactions, ["review", "comment", "text"])
    rating_col = _find_col(df_interactions, ["rating", "score", "stars"])

    if (
        recipe_id_recipes is None
        or recipe_id_interactions is None
        or user_col is None
        or review_col is None
    ):
        return pd.DataFrame(columns=["metric", "value"])

    df_int = df_interactions.copy()
    mask_reviews = _non_empty_text_mask(df_int[review_col])
    total_interactions = len(df_int)
    total_reviews = int(mask_reviews.sum())

    # Intersection stricte pour éviter d'inclure des recettes supprimées
    catalog_recipe_ids = set(df_recipes[recipe_id_recipes].dropna().unique())
    reviewed_recipe_ids = set(df_int.loc[mask_reviews, recipe_id_interactions].dropna().unique())
    recipes_with_reviews = len(catalog_recipe_ids.intersection(reviewed_recipe_ids))
    total_recipes = len(catalog_recipe_ids)
    unique_reviewers = int(df_int.loc[mask_reviews, user_col].nunique(dropna=True))

    reviews_per_recipe = (
        df_int.loc[mask_reviews].groupby(recipe_id_interactions, observed=False)[review_col].size()
    )

    empty_reviews = total_interactions - total_reviews
    empty_ratio = (empty_reviews / total_interactions * 100) if total_interactions else 0.0

    avg_reviews_per_recipe = (
        float(reviews_per_recipe.mean()) if not reviews_per_recipe.empty else 0.0
    )
    median_reviews_per_recipe = (
        float(reviews_per_recipe.median()) if not reviews_per_recipe.empty else 0.0
    )

    review_lengths = _word_count(df_int.loc[mask_reviews, review_col])
    avg_review_length = float(review_lengths.mean()) if not review_lengths.empty else None
    median_review_length = float(review_lengths.median()) if not review_lengths.empty else None

    avg_rating_given = None
    if rating_col and rating_col in df_int.columns:
        ratings = pd.to_numeric(df_int.loc[mask_reviews, rating_col], errors="coerce").dropna()
        if not ratings.empty:
            avg_rating_given = float(ratings.mean())

    rows = [
        {"metric": "total_reviews", "value": total_reviews},
        {"metric": "recipes_with_reviews", "value": recipes_with_reviews},
        {"metric": "total_recipes", "value": total_recipes},
        {
            "metric": "share_recipes_reviewed_pct",
            "value": round(recipes_with_reviews / total_recipes * 100, 2) if total_recipes else 0.0,
        },
        {"metric": "unique_reviewers", "value": unique_reviewers},
        {"metric": "avg_reviews_per_recipe", "value": round(avg_reviews_per_recipe, 2)},
        {
            "metric": "median_reviews_per_recipe",
            "value": round(median_reviews_per_recipe, 2),
        },
        {"metric": "empty_review_ratio_pct", "value": round(empty_ratio, 2)},
    ]

    if avg_review_length is not None:
        rows.append({"metric": "avg_review_length_words", "value": round(avg_review_length, 1)})
    if median_review_length is not None:
        rows.append(
            {
                "metric": "median_review_length_words",
                "value": round(median_review_length, 1),
            }
        )
    if avg_rating_given is not None:
        rows.append({"metric": "avg_rating_given", "value": round(avg_rating_given, 2)})

    return pd.DataFrame(rows)


def review_distribution_per_recipe(
    df_recipes: Optional[pd.DataFrame],
    df_interactions: Optional[pd.DataFrame],
    bins: Optional[Sequence[float]] = (0, 1, 2, 3, 5, 10, 20, 50, np.inf),
) -> pd.DataFrame:
    """Describe how the number of reviews is distributed across recipes.

    Args:
        df_recipes: Recipe catalogue dataframe. Only the identifier column is
            required; duplicates or missing rows are dropped automatically.
        df_interactions: Interactions dataframe supplying review text and
            recipe identifiers.
        bins: Optional sequence of monotonically increasing cut points used to
            bucket recipes by review count. The default mirrors what is shown in
            the dashboard (0, 1, 2, 3, 5, 10, 20, 50, 50+).

    Returns:
        A dataframe with one row per bin. For each tranche we provide the number
        of recipes, the percentage of the catalogue they represent and the average
        review count. If the inputs are not usable, an empty dataframe with the
        expected schema is returned.
    """
    if df_recipes is None or df_recipes.empty or df_interactions is None or df_interactions.empty:
        return pd.DataFrame(
            columns=["reviews_bin", "recipe_count", "share_pct", "avg_reviews_in_bin"]
        )

    recipe_id_recipes = _find_col(df_recipes, ["id", "recipe_id"])
    recipe_id_interactions = _find_col(df_interactions, ["recipe_id", "recipe", "id"])
    review_col = _find_col(df_interactions, ["review", "comment", "text"])

    if recipe_id_recipes is None or recipe_id_interactions is None or review_col is None:
        return pd.DataFrame(
            columns=["reviews_bin", "recipe_count", "share_pct", "avg_reviews_in_bin"]
        )

    df_int = df_interactions.copy()
    mask_reviews = _non_empty_text_mask(df_int[review_col])

    recipes_frame = (
        df_recipes[[recipe_id_recipes]]
        .dropna()
        .drop_duplicates()
        .rename(columns={recipe_id_recipes: "recipe_id"})
    )
    review_counts = (
        df_int.loc[mask_reviews, [recipe_id_interactions]]
        .assign(count=1)
        .groupby(recipe_id_interactions, observed=False)["count"]
        .sum()
        .reset_index()
        .rename(columns={recipe_id_interactions: "recipe_id", "count": "review_count"})
    )

    merged = recipes_frame.merge(review_counts, on="recipe_id", how="left").fillna(
        {"review_count": 0}
    )
    merged["review_count"] = merged["review_count"].astype(int)

    def _format_bin(lower, upper):
        lower_int = int(lower)
        if np.isinf(upper):
            return f"{lower_int}+"
        upper_int = int(upper) - 1
        if upper_int < lower_int:
            upper_int = lower_int
        if lower_int == upper_int:
            return f"{lower_int}"
        return f"{lower_int}-{upper_int}"

    bins_sequence = list(bins) if bins is not None else [0, 1, 2, 3, 5, 10, 20, 50, np.inf]
    if len(bins_sequence) < 2:
        return pd.DataFrame(
            columns=["reviews_bin", "recipe_count", "share_pct", "avg_reviews_in_bin"]
        )

    labels = [
        _format_bin(bins_sequence[i], bins_sequence[i + 1]) for i in range(len(bins_sequence) - 1)
    ]

    merged["reviews_bin"] = pd.cut(
        merged["review_count"],
        bins=bins_sequence,
        include_lowest=True,
        right=False,
        labels=labels,
    )

    distribution = (
        merged.groupby("reviews_bin", observed=False)
        .agg(
            recipe_count=("recipe_id", "size"),
            avg_reviews_in_bin=("review_count", "mean"),
        )
        .reset_index()
        .rename(columns={"reviews_bin": "reviews_bin"})
    )
    distribution["reviews_bin"] = distribution["reviews_bin"].astype(str)

    total_recipes = distribution["recipe_count"].sum()
    if total_recipes:
        distribution["share_pct"] = (distribution["recipe_count"] / total_recipes * 100).round(2)
    else:
        distribution["share_pct"] = 0.0

    distribution["avg_reviews_in_bin"] = pd.to_numeric(
        distribution["avg_reviews_in_bin"], errors="coerce"
    ).round(2)

    return distribution[["reviews_bin", "recipe_count", "share_pct", "avg_reviews_in_bin"]]


def reviewer_activity(
    df_interactions: Optional[pd.DataFrame],
    top_n: int = 20,
) -> pd.DataFrame:
    """Summarise reviewer engagement and return the top ``top_n`` profiles.

    Args:
        df_interactions: Interactions dataframe containing reviewer identifiers,
            textual reviews and optional ratings/dates.
        top_n: Number of reviewers to keep after sorting by review volume.

    Returns:
        A dataframe ordered by ``reviews_count`` (descending) and limited to
        ``top_n`` rows. Typical columns include:
        ``reviewer_id``, ``reviews_count``, ``share_pct``, ``avg_rating_given``,
        ``avg_review_length_words`` and the first/last review dates (if available).
        An empty dataframe is returned when no textual reviews are present.

    Notes:
        - ``share_pct`` is computed relatively to the number of non-empty reviews
          to ensure the percentages sum to 100 across all reviewers.
        - Non textual interactions (empty strings, nulls) are filtered out via
          :func:`_non_empty_text_mask` before aggregation.
    """
    if df_interactions is None or df_interactions.empty:
        return pd.DataFrame(
            columns=[
                "reviewer_id",
                "reviews_count",
                "share_pct",
                "avg_rating_given",
                "avg_review_length_words",
                "first_review_date",
                "last_review_date",
            ]
        )

    user_col = _find_col(df_interactions, ["user_id", "user", "reviewer"])
    review_col = _find_col(df_interactions, ["review", "comment", "text"])
    rating_col = _find_col(df_interactions, ["rating", "score", "stars"])
    date_col = _find_col(df_interactions, ["date", "created_at", "timestamp"])

    if user_col is None or review_col is None:
        return pd.DataFrame(
            columns=[
                "reviewer_id",
                "reviews_count",
                "share_pct",
                "avg_rating_given",
                "avg_review_length_words",
                "first_review_date",
                "last_review_date",
            ]
        )

    df_int = df_interactions.copy()
    mask_reviews = _non_empty_text_mask(df_int[review_col])
    df_reviews = df_int.loc[mask_reviews].copy()

    if df_reviews.empty:
        return pd.DataFrame(
            columns=[
                "reviewer_id",
                "reviews_count",
                "share_pct",
                "avg_rating_given",
                "avg_review_length_words",
                "first_review_date",
                "last_review_date",
            ]
        )

    df_reviews["review_length_words"] = _word_count(df_reviews[review_col])

    agg_map = {
        "reviews_count": (review_col, "size"),
        "avg_review_length_words": ("review_length_words", "mean"),
    }
    if rating_col:
        agg_map["avg_rating_given"] = (rating_col, "mean")
    if date_col:
        df_reviews[date_col] = pd.to_datetime(df_reviews[date_col], errors="coerce")
        agg_map["first_review_date"] = (date_col, "min")
        agg_map["last_review_date"] = (date_col, "max")

    activity = (
        df_reviews.groupby(user_col, observed=False)
        .agg(**agg_map)
        .reset_index()
        .rename(columns={user_col: "reviewer_id"})
    )

    total_reviews = activity["reviews_count"].sum()
    activity["share_pct"] = (
        (activity["reviews_count"] / total_reviews * 100).round(2) if total_reviews else 0.0
    )

    if "avg_rating_given" in activity.columns:
        activity["avg_rating_given"] = pd.to_numeric(
            activity["avg_rating_given"], errors="coerce"
        ).round(2)
    activity["avg_review_length_words"] = pd.to_numeric(
        activity["avg_review_length_words"], errors="coerce"
    ).round(1)

    if "first_review_date" in activity.columns:
        activity["first_review_date"] = activity["first_review_date"].dt.strftime("%Y-%m-%d")
    if "last_review_date" in activity.columns:
        activity["last_review_date"] = activity["last_review_date"].dt.strftime("%Y-%m-%d")

    activity = (
        activity.sort_values("reviews_count", ascending=False).head(top_n).reset_index(drop=True)
    )

    cols = ["reviewer_id", "reviews_count", "share_pct", "avg_review_length_words"]
    if "avg_rating_given" in activity.columns:
        cols.append("avg_rating_given")
    if "first_review_date" in activity.columns:
        cols.append("first_review_date")
    if "last_review_date" in activity.columns:
        cols.append("last_review_date")

    return activity[cols]


def review_temporal_trend(
    df_interactions: Optional[pd.DataFrame],
) -> pd.DataFrame:
    """Aggregate review activity by month to expose temporal dynamics.

    Args:
        df_interactions: Interactions dataframe. Must include a date column,
            review content and, ideally, reviewer identifiers and ratings.

    Returns:
        A dataframe indexed by month (``period`` as ``YYYY-MM``) containing the
        number of reviews collected, the number of unique reviewers and the mean
        rating when available. Empty inputs yield an empty dataframe with the
        expected columns.

    Notes:
        The grouping uses ``freq='ME'`` (month end) so that the trend aligns with
        calendar months even when the raw dataset has sparse dates.
    """
    if df_interactions is None or df_interactions.empty:
        return pd.DataFrame(
            columns=["period", "reviews_count", "unique_reviewers", "avg_rating_given"]
        )

    date_col = _find_col(df_interactions, ["date", "created_at", "timestamp"])
    review_col = _find_col(df_interactions, ["review", "comment", "text"])
    user_col = _find_col(df_interactions, ["user_id", "user", "reviewer"])
    rating_col = _find_col(df_interactions, ["rating", "score", "stars"])

    if date_col is None or review_col is None:
        return pd.DataFrame(
            columns=["period", "reviews_count", "unique_reviewers", "avg_rating_given"]
        )

    df_int = df_interactions.copy()
    df_int[date_col] = pd.to_datetime(df_int[date_col], errors="coerce")
    df_int = df_int.dropna(subset=[date_col])

    mask_reviews = _non_empty_text_mask(df_int[review_col])
    df_reviews = df_int.loc[mask_reviews].copy()

    if df_reviews.empty:
        return pd.DataFrame(
            columns=["period", "reviews_count", "unique_reviewers", "avg_rating_given"]
        )

    agg_dict = {
        "reviews_count": (review_col, "size"),
    }
    if user_col:
        agg_dict["unique_reviewers"] = (user_col, "nunique")
    if rating_col:
        agg_dict["avg_rating_given"] = (rating_col, "mean")

    trend = (
        df_reviews.groupby(pd.Grouper(key=date_col, freq="ME"))
        .agg(**agg_dict)
        .reset_index()
        .rename(columns={date_col: "period_start"})
    )

    trend["period"] = trend["period_start"].dt.to_period("M").astype(str)

    if "avg_rating_given" in trend.columns:
        trend["avg_rating_given"] = pd.to_numeric(trend["avg_rating_given"], errors="coerce").round(
            2
        )

    cols = ["period", "reviews_count"]
    if "unique_reviewers" in trend.columns:
        trend["unique_reviewers"] = trend["unique_reviewers"].fillna(0).astype(int)
        cols.append("unique_reviewers")
    if "avg_rating_given" in trend.columns:
        cols.append("avg_rating_given")

    return trend[cols]


def reviews_vs_rating(
    df_recipes: Optional[pd.DataFrame],
    df_interactions: Optional[pd.DataFrame],
) -> pd.DataFrame:
    """Combine review counts and ratings for each recipe.

    Args:
        df_recipes: Recipe catalogue including identifiers, titles and contributors.
        df_interactions: Interactions dataframe providing review text and ratings.

    Returns:
        A tidy dataframe with identifiers, review volume, average rating and
        optional metadata (recipe name, contributor). Missing values are coerced
        to sensible defaults (e.g. zero reviews, ``NaN`` rating).
    """
    if df_recipes is None or df_recipes.empty or df_interactions is None or df_interactions.empty:
        return pd.DataFrame(
            columns=[
                "recipe_id",
                "review_count",
                "avg_rating",
                "recipe_name",
                "contributor_id",
            ]
        )

    recipe_id_recipes = _find_col(df_recipes, ["id", "recipe_id"])
    recipe_id_interactions = _find_col(df_interactions, ["recipe_id", "recipe", "id"])
    review_col = _find_col(df_interactions, ["review", "comment", "text"])
    rating_col = _find_col(df_interactions, ["rating", "score", "stars"])
    name_col = _find_col(df_recipes, ["name", "title", "recipe"])
    contributor_col = _find_col(df_recipes, ["contributor_id", "contributor", "author", "user"])

    if (
        recipe_id_recipes is None
        or recipe_id_interactions is None
        or review_col is None
        or rating_col is None
    ):
        return pd.DataFrame(
            columns=[
                "recipe_id",
                "review_count",
                "avg_rating",
                "recipe_name",
                "contributor_id",
            ]
        )

    df_int = df_interactions.copy()
    mask_reviews = _non_empty_text_mask(df_int[review_col])

    review_counts = (
        df_int.loc[mask_reviews]
        .groupby(recipe_id_interactions)[review_col]
        .size()
        .reset_index(name="review_count")
        .rename(columns={recipe_id_interactions: "recipe_id"})
    )

    avg_ratings = (
        df_int.groupby(recipe_id_interactions)[rating_col]
        .mean()
        .reset_index(name="avg_rating")
        .rename(columns={recipe_id_interactions: "recipe_id"})
    )

    meta_cols = [recipe_id_recipes]
    rename_map = {recipe_id_recipes: "recipe_id"}
    if name_col:
        meta_cols.append(name_col)
        rename_map[name_col] = "recipe_name"
    if contributor_col:
        meta_cols.append(contributor_col)
        rename_map[contributor_col] = "contributor_id"

    recipes_meta = df_recipes[meta_cols].drop_duplicates().rename(columns=rename_map)

    result = review_counts.merge(avg_ratings, on="recipe_id", how="left")
    result = result.merge(recipes_meta, on="recipe_id", how="left")

    if "avg_rating" in result.columns:
        result["avg_rating"] = pd.to_numeric(result["avg_rating"], errors="coerce").round(2)
    else:
        result["avg_rating"] = np.nan
    if "review_count" in result.columns:
        result["review_count"] = (
            pd.to_numeric(result["review_count"], errors="coerce").fillna(0).astype(int)
        )
    else:
        result["review_count"] = 0

    cols = ["recipe_id", "review_count", "avg_rating"]
    if "recipe_name" in result.columns:
        cols.append("recipe_name")
    if "contributor_id" in result.columns:
        cols.append("contributor_id")

    return result[cols]


def reviewer_reviews_vs_recipes(
    df_recipes: Optional[pd.DataFrame],
    df_interactions: Optional[pd.DataFrame],
) -> pd.DataFrame:
    """Contrast the number of reviews written by a user and their publications.

    Args:
        df_recipes: Recipe catalogue used to count how many recipes each
            contributor has published. Can be ``None`` if the information is
            unavailable.
        df_interactions: Interactions dataframe containing reviews and ratings.

    Returns:
        A dataframe with one row per user. It exposes the number of reviews they
        have written, the number of recipes they have published (if known) and
        their average rating. Empty inputs produce an empty dataframe with the
        expected columns.
    """
    if df_interactions is None or df_interactions.empty:
        return pd.DataFrame(
            columns=[
                "user_id",
                "reviews_count",
                "recipes_published",
                "avg_rating_given",
            ]
        )

    user_col = _find_col(df_interactions, ["user_id", "user", "reviewer"])
    review_col = _find_col(df_interactions, ["review", "comment", "text"])
    rating_col = _find_col(df_interactions, ["rating", "score", "stars"])
    contributor_col = _find_col(df_recipes, ["contributor_id", "contributor", "author", "user"])

    if user_col is None:
        return pd.DataFrame(
            columns=[
                "user_id",
                "reviews_count",
                "recipes_published",
                "avg_rating_given",
            ]
        )

    df_reviews = df_interactions.copy()
    if review_col:
        mask_reviews = _non_empty_text_mask(df_reviews[review_col])
        df_reviews = df_reviews.loc[mask_reviews]

    reviews_count = (
        df_reviews.groupby(user_col)
        .size()
        .reset_index(name="reviews_count")
        .rename(columns={user_col: "user_id"})
    )

    if rating_col and rating_col in df_interactions.columns:
        ratings = (
            df_interactions.groupby(user_col)[rating_col]
            .mean()
            .reset_index(name="avg_rating_given")
            .rename(columns={user_col: "user_id"})
        )
        reviews_count = reviews_count.merge(ratings, on="user_id", how="left")
    else:
        reviews_count["avg_rating_given"] = np.nan

    if df_recipes is not None and not df_recipes.empty and contributor_col:
        recipes_count = (
            df_recipes.groupby(contributor_col)
            .size()
            .reset_index(name="recipes_published")
            .rename(columns={contributor_col: "user_id"})
        )
    else:
        recipes_count = pd.DataFrame(columns=["user_id", "recipes_published"])

    result = reviews_count.merge(recipes_count, on="user_id", how="outer")
    result["reviews_count"] = (
        pd.to_numeric(result["reviews_count"], errors="coerce").fillna(0).astype(int)
    )
    if "recipes_published" in result.columns:
        result["recipes_published"] = (
            pd.to_numeric(result["recipes_published"], errors="coerce").fillna(0).astype(int)
        )
    else:
        result["recipes_published"] = 0
    if "avg_rating_given" in result.columns:
        result["avg_rating_given"] = pd.to_numeric(
            result["avg_rating_given"], errors="coerce"
        ).round(2)
    else:
        result["avg_rating_given"] = np.nan

    result["user_id"] = result["user_id"].astype(object)

    return result[["user_id", "reviews_count", "recipes_published", "avg_rating_given"]]


# ===============================
# Orchestrateur
# ===============================


class DataAnylizer:
    """Container orchestrant les analyses côté backend.

    Les datasets sont chargés une seule fois à l'initialisation (recettes et
    interactions), puis les méthodes d'analyse sont mises à disposition via
    :meth:`process_data`. Cette classe est injectée dans l'API FastAPI pour
    garantir un cache en mémoire performant.
    """

    def __init__(self, csv_adapter: IDataAdapter):
        """Charge immédiatement les jeux de données via l’adapter fourni."""
        self.df_recipes = csv_adapter.load(DataType.RECIPES)
        self.df_interactions = csv_adapter.load(DataType.INTERACTIONS)

    def get_raw_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Retourne les dataframes bruts (recettes, interactions)."""
        return self.df_recipes, self.df_interactions

    def process_data(self, analysis_type: AnalysisType) -> pd.DataFrame:
        """Route la demande d'analyse vers la fonction adéquate."""
        if analysis_type == AnalysisType.NUMBER_RECIPES:
            return most_recipes_contributors(self.df_recipes)
        if analysis_type == AnalysisType.BEST_RECIPES:
            return best_ratings_contributors(self.df_recipes, self.df_interactions)
        if analysis_type == AnalysisType.DURATION_DISTRIBUTION:
            return average_duration_distribution(self.df_recipes, duration_col="minutes")
        if analysis_type == AnalysisType.DURATION_VS_RECIPE_COUNT:
            return duration_vs_recipe_count(self.df_recipes, duration_col="minutes")
        if analysis_type == AnalysisType.TOP_10_PERCENT_CONTRIBUTORS:
            return top_10_percent_contributors(
                self.df_recipes, self.df_interactions, duration_col="minutes"
            )
        if analysis_type == AnalysisType.USER_SEGMENTS:
            # Compute persona assignment once and reuse the dataframe below.
            return compute_user_segments(
                self.df_recipes, self.df_interactions, duration_col="minutes"
            )
        if analysis_type == AnalysisType.TOP_TAGS_BY_SEGMENT:
            # Compute user segments first, then derive their favourite tags.
            df_users = compute_user_segments(
                self.df_recipes, self.df_interactions, duration_col="minutes"
            )
            return top_tags_by_segment_from_users(
                self.df_recipes, df_users, tags_col="tags", top_k=5
            )
        if analysis_type == AnalysisType.RATING_DISTRIBUTION:
            return rating_distribution(self.df_recipes, self.df_interactions)
        if analysis_type == AnalysisType.RATING_VS_RECIPES:
            return rating_vs_recipe_count(self.df_recipes, self.df_interactions)
        if analysis_type == AnalysisType.REVIEW_OVERVIEW:
            return review_overview(self.df_recipes, self.df_interactions)
        if analysis_type == AnalysisType.REVIEW_DISTRIBUTION:
            return review_distribution_per_recipe(self.df_recipes, self.df_interactions)
        if analysis_type == AnalysisType.REVIEWER_ACTIVITY:
            return reviewer_activity(self.df_interactions)
        if analysis_type == AnalysisType.REVIEW_TEMPORAL_TREND:
            return review_temporal_trend(self.df_interactions)
        if analysis_type == AnalysisType.REVIEWS_VS_RATING:
            return reviews_vs_rating(self.df_recipes, self.df_interactions)
        if analysis_type == AnalysisType.REVIEWER_VS_RECIPES:
            return reviewer_reviews_vs_recipes(self.df_recipes, self.df_interactions)
        raise UnsupportedAnalysisError(f"Unsupported analysis type: {analysis_type}")
