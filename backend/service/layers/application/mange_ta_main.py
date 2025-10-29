from enum import StrEnum
from typing import Optional, Sequence, Union, Dict, Any, List
import ast

import numpy as np
import pandas as pd

from service.layers.application.interfaces.interface import IDataAdapter
from service.layers.infrastructure.types import DataType


# ===============================
# Constantes & Types
# ===============================

SEGMENT_INFO: Dict[int, Dict[str, Any]] = {
    0: {"persona": "Super Cookers",        "ref_avg_minutes": 55, "ref_avg_rating": 4.4, "ref_avg_reviews": 12},
    1: {"persona": "Quick Cookers",        "ref_avg_minutes": 18, "ref_avg_rating": 3.6, "ref_avg_reviews": 3},
    2: {"persona": "Sweet Lovers",         "ref_avg_minutes": 40, "ref_avg_rating": 4.2, "ref_avg_reviews": 6},
    3: {"persona": "Talkative Tasters",    "ref_avg_minutes": 35, "ref_avg_rating": 3.8, "ref_avg_reviews": 18},
    4: {"persona": "Experimental Foodies", "ref_avg_minutes": 45, "ref_avg_rating": 3.5, "ref_avg_reviews": 10},
    5: {"persona": "Everyday Cookers",     "ref_avg_minutes": 30, "ref_avg_rating": 3.9, "ref_avg_reviews": 7},
}


class AnalysisType(StrEnum):
    NO_ANALYSIS = "no_analysis"
    NUMBER_RECIPES = "number_recipes"
    BEST_RECIPES = "best_recipes"
    NUMBER_COMMENTS = "number_comments"
    DURATION_DISTRIBUTION = "duration_distribution"
    DURATION_VS_RECIPE_COUNT = "duration_vs_recipe_count"
    TOP_10_PERCENT_CONTRIBUTORS = "top_10_percent_contributors"
    USER_SEGMENTS = "user_segments"                 # 👈 nouveau
    TOP_TAGS_BY_SEGMENT = "top_tags_by_segment"     # 👈 nouveau
    RATING_DISTRIBUTION = "rating_distribution"
    RATING_VS_RECIPES = "rating_vs_recipes"

# ===============================
# Utilitaires
# ===============================

def _parse_tags_to_list(v) -> List[str]:
    """
    Transforme la colonne tags en liste de strings, de façon robuste.
    Accepte: liste Python, string de liste "['a','b']", string "a,b,c".
    """
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
    """
    Retourne le nombre de recettes par contributeur (tri décroissant).
    Colonnes: contributor_id, 0 (count)
    """
    number_recipes_contributors = (
        df_recipes.groupby("contributor_id").size().sort_values(ascending=False).reset_index()
    )
    return number_recipes_contributors


def best_ratings_contributors(
    df_recipes: pd.DataFrame,
    df_interactions: pd.DataFrame
) -> pd.DataFrame:
    """
    Contributeurs avec meilleure note moyenne (>=5 recettes).
    Colonnes: contributor_id, avg_rating, num_recipes
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
    """
    Répartition (histogramme) des durées de recettes (global ou par groupe).
    Colonnes: (group_cols), duration_bin, count, share, avg_duration_in_bin, cum_share
    """
    df = df_recipes.copy()
    df[duration_col] = pd.to_numeric(df[duration_col], errors="coerce")
    df = df.dropna(subset=[duration_col])

    # Bins
    resolved_bins: Union[int, Sequence[float]]
    resolved_labels: Optional[Sequence[str]] = labels
    if bins is None:
        resolved_bins = [0, 15, 30, 45, 60, 90, 120, np.inf]
        if resolved_labels is None:
            resolved_labels = ["0–15", "15–30", "30–45", "45–60", "60–90", "90–120", "120+"]
    else:
        resolved_bins = bins

    # Si bins est un entier -> classes égales
    if isinstance(resolved_bins, int):
        vmin, vmax = df[duration_col].min(), df[duration_col].max()
        resolved_bins = np.linspace(vmin, vmax, resolved_bins + 1).tolist()

    # Découpage
    df["duration_bin"] = pd.cut(
        df[duration_col], bins=resolved_bins, labels=resolved_labels,
        include_lowest=True, right=False,
    )

    # Agrégats
    group_cols_list = list(group_cols) if group_cols else []
    group_keys = group_cols_list + ["duration_bin"]

    agg = (
        df.groupby(group_keys)
          .agg(count=(duration_col, "size"), avg_duration_in_bin=(duration_col, "mean"))
          .reset_index()
    )

    # Parts
    if group_cols_list:
        totals = agg.groupby(group_cols_list)["count"].sum().reset_index(name="total_count")
        out = agg.merge(totals, on=group_cols_list, how="left")
    else:
        total_count = agg["count"].sum()
        out = agg.assign(total_count=total_count)

    out["share"] = (out["count"] / out["total_count"] * 100).round(2)

    # Part cumulée
    out = out.sort_values(group_cols_list + ["duration_bin"]).reset_index(drop=True)
    if group_cols_list:
        out["cum_share"] = out.groupby(group_cols_list)["share"].cumsum().round(2)
    else:
        out["cum_share"] = out["share"].cumsum().round(2)

    out = out.drop(columns=["total_count"])
    out["avg_duration_in_bin"] = pd.to_numeric(out["avg_duration_in_bin"], errors="coerce").round(1)

    return out


def duration_vs_recipe_count(
    df_recipes: pd.DataFrame,
    duration_col: str = "minutes",
) -> pd.DataFrame:
    """
    Agrège: nombre de recettes par contributeur, durée moyenne/médiane.
    Colonnes: contributor_id, recipe_count, avg_duration, median_duration
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
    duration_col: str = "minutes"
) -> pd.DataFrame:
    """
    Compare Top 10% de contributeurs vs global sur:
      - durée moyenne des recettes
      - note moyenne
      - nombre moyen de commentaires
    Colonnes: population, avg_duration_minutes, avg_rating, avg_comments, contributor_count
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
        .groupby("recipe_id")["rating"].mean().mean()
    )
    avg_comments_top = (
        df_interactions[df_interactions["recipe_id"].isin(df_top["id"])]
        .groupby("recipe_id")["rating"].count().mean()
    )

    # GLOBAL
    avg_duration_global = df[duration_col].mean()
    avg_rating_global = df_interactions.groupby("recipe_id")["rating"].mean().mean()
    avg_comments_global = df_interactions.groupby("recipe_id")["rating"].count().mean()

    result = pd.DataFrame([
        {
            "population": "top_10_percent",
            "avg_duration_minutes": round(float(avg_duration_top), 2) if pd.notna(avg_duration_top) else None,
            "avg_rating": round(float(avg_rating_top), 2) if pd.notna(avg_rating_top) else None,
            "avg_comments": round(float(avg_comments_top), 2) if pd.notna(avg_comments_top) else None,
            "contributor_count": int(len(top_contributors))
        },
        {
            "population": "global",
            "avg_duration_minutes": round(float(avg_duration_global), 2) if pd.notna(avg_duration_global) else None,
            "avg_rating": round(float(avg_rating_global), 2) if pd.notna(avg_rating_global) else None,
            "avg_comments": round(float(avg_comments_global), 2) if pd.notna(avg_comments_global) else None,
            "contributor_count": int(df["contributor_id"].nunique())
        }
    ])
    return result

def compute_user_segments(
    df_recipes: pd.DataFrame,
    df_interactions: pd.DataFrame,
    duration_col: str = "minutes",
) -> pd.DataFrame:
    """
    Calcule pour chaque contributeur:
      - avg_minutes, avg_rating, avg_reviews
      - segment (0..5) assigné au plus proche centroïde (SEGMENT_INFO)
      - persona (libellé)
    Retour: contributor_id, avg_minutes, avg_rating, avg_reviews, segment, persona
    """
    df_r = df_recipes[["id", "contributor_id", duration_col]].copy()
    df_r[duration_col] = pd.to_numeric(df_r[duration_col], errors="coerce")

    df_i = df_interactions[["recipe_id", "rating"]].copy()
    df_i["rating"] = pd.to_numeric(df_i["rating"], errors="coerce")

    # Moyenne minutes par contributeur
    g_minutes = (
        df_r.groupby("contributor_id", dropna=True)[duration_col]
            .mean()
            .rename("avg_minutes")
    )

    # Note moyenne par recette, puis moyenne par contributeur
    recipe_avg_rating = df_i.groupby("recipe_id")["rating"].mean().rename("recipe_avg_rating")
    g_rating = (
        df_r.merge(recipe_avg_rating, left_on="id", right_index=True, how="left")
            .groupby("contributor_id")["recipe_avg_rating"].mean()
            .rename("avg_rating")
    )

    # Nombre d'avis par recette, puis moyenne par contributeur
    recipe_review_count = df_i.groupby("recipe_id")["rating"].count().rename("review_count")
    g_reviews = (
        df_r.merge(recipe_review_count, left_on="id", right_index=True, how="left")
            .groupby("contributor_id")["review_count"].mean()
            .rename("avg_reviews")
    )

    df_users = (
        pd.concat([g_minutes, g_rating, g_reviews], axis=1)
          .reset_index()
          .dropna(subset=["avg_minutes", "avg_rating", "avg_reviews"])
    )

    if df_users.empty:
        return pd.DataFrame(columns=["contributor_id","avg_minutes","avg_rating","avg_reviews","segment","persona"])

    # Matrices utilisateurs (N x 3) et centroïdes (K x 3)
    U = df_users[["avg_minutes", "avg_rating", "avg_reviews"]].to_numpy(dtype=float)
    centroids_df = pd.DataFrame.from_dict(SEGMENT_INFO, orient="index")
    C = centroids_df[["ref_avg_minutes", "ref_avg_rating", "ref_avg_reviews"]].to_numpy(dtype=float)

    # Distances euclidiennes (vectorisé): (N, K)
    distances = np.sqrt(((U[:, None, :] - C[None, :, :]) ** 2).sum(axis=2))

    # Assignation au centroïde le plus proche (0..K-1) — correspond à l'index de centroids_df (0..5)
    seg_idx = distances.argmin(axis=1)
    df_users["segment"] = seg_idx

    # Ajout du libellé de persona
    df_users = df_users.merge(
        centroids_df.reset_index().rename(columns={"index": "segment"})[["segment", "persona"]],
        on="segment", how="left"
    )

    # Finitions
    df_users["avg_minutes"] = df_users["avg_minutes"].round(2)
    df_users["avg_rating"] = df_users["avg_rating"].round(2)
    df_users["avg_reviews"] = df_users["avg_reviews"].round(2)

    return df_users[["contributor_id", "avg_minutes", "avg_rating", "avg_reviews", "segment", "persona"]]


def top_tags_by_segment_from_users(
    df_recipes: pd.DataFrame,
    df_user_segments: pd.DataFrame,
    tags_col: str = "tags",
    top_k: int = 5,
) -> pd.DataFrame:
    """
    Renvoie, pour chaque segment (issu de df_user_segments), les top-K tags les plus utilisés.
    Colonnes: segment, persona, tag, count, share_pct
    """
    # Join recettes ↔ segments utilisateurs via contributor_id
    df_r = df_recipes[["id", "contributor_id", tags_col]].copy()
    df_r = df_r.merge(
        df_user_segments[["contributor_id", "segment", "persona"]],
        on="contributor_id",
        how="inner"
    )

    # Parse tags -> liste
    df_r[tags_col] = df_r[tags_col].apply(_parse_tags_to_list)

    # Explode
    df_tags = df_r.explode(tags_col).dropna(subset=[tags_col])
    if df_tags.empty:
        return pd.DataFrame(columns=["segment", "persona", "tag", "count", "share_pct"])

    # Comptage
    counts = (
        df_tags.groupby(["segment", "persona", tags_col], dropna=False)
               .size()
               .reset_index(name="count")
    )

    # Part par segment
    totals = counts.groupby(["segment", "persona"])["count"].sum().reset_index(name="segment_total")
    counts = counts.merge(totals, on=["segment", "persona"], how="left")
    counts["share_pct"] = (counts["count"] / counts["segment_total"] * 100).round(2)

    # Top-K par segment
    counts = counts.sort_values(["segment", "count"], ascending=[True, False])
    topk = counts.groupby("segment").head(top_k).reset_index(drop=True)

    topk = topk.rename(columns={tags_col: "tag"})
    return (
        topk[["segment", "persona", "tag", "count", "share_pct"]]
            .sort_values(["segment", "count"], ascending=[True, False])
            .reset_index(drop=True)
    )
    


def _find_col(df: pd.DataFrame, candidates):
    """Outil permettant de sélectionner une colonne parmi plusieurs candidats."""
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


def rating_distribution(
    df_recipes: pd.DataFrame,
    df_interactions: pd.DataFrame,
    bins: Optional[Union[int, Sequence[float]]] = [0, 1, 2, 3, 4, 5],
    labels: Optional[Sequence[str]] = None
) -> pd.DataFrame:
    # Précautions sur les dataframes
    if df_interactions is None or df_interactions.empty or df_recipes is None or df_recipes.empty:
        return pd.DataFrame(columns=["rating_bin", "count", "share", "avg_rating_in_bin", "cum_share"])

    recipe_id_col = _find_col(df_interactions, ["recipe_id", "recipe", "id"])
    rating_col = _find_col(df_interactions, ["rating", "score", "stars"])
    recipe_id_in_recipes = _find_col(df_recipes, ["id", "recipe_id"])

    if recipe_id_col is None or rating_col is None or recipe_id_in_recipes is None:
        return pd.DataFrame(columns=["rating_bin", "count", "share", "avg_rating_in_bin", "cum_share"])

    # Note moyenne par recette
    per_recipe = (
        df_interactions
        .dropna(subset=[recipe_id_col, rating_col])
        .groupby(recipe_id_col)[rating_col]
        .mean()
        .reset_index(name="avg_rating")
    )

    merged = per_recipe.merge(df_recipes[[recipe_id_in_recipes, "contributor_id"]].rename(columns={recipe_id_in_recipes: recipe_id_col}),
                              on=recipe_id_col, how="left")

    if "contributor_id" not in merged.columns:
        contrib_col = _find_col(df_recipes, ["contributor_id", "contributor", "author", "user"])
        if contrib_col:
            merged = per_recipe.merge(df_recipes[[recipe_id_in_recipes, contrib_col]].rename(columns={recipe_id_in_recipes: recipe_id_col, contrib_col: "contributor_id"}),
                                      on=recipe_id_col, how="left")
        else:
            return pd.DataFrame(columns=["rating_bin", "count", "share", "avg_rating_in_bin", "cum_share"])

    # Notes moyennes des contributeurs
    avg = merged.dropna(subset=["contributor_id"]).groupby("contributor_id")["avg_rating"].mean().reset_index(name="avg_rating")

    if labels is None:
        labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]
        labels[-1] = f"{bins[-2]}+"

    avg["rating_bin"] = pd.cut(avg["avg_rating"], bins=bins, labels=labels, include_lowest=True, right=False)

    distribution = (
        avg.groupby("rating_bin")
           .agg(count=("contributor_id", "nunique"), avg_rating_in_bin=("avg_rating", "mean"))
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
    df_recipes: pd.DataFrame,
    df_interactions: pd.DataFrame
) -> pd.DataFrame:
    if df_recipes is None or df_recipes.empty:
        return pd.DataFrame(columns=["contributor_id", "recipe_count", "avg_rating", "median_rating"])

    recipe_id_col = _find_col(df_interactions, ["recipe_id", "recipe", "id"])
    rating_col = _find_col(df_interactions, ["rating", "score", "stars"])
    recipe_id_in_recipes = _find_col(df_recipes, ["id", "recipe_id"])
    contrib_col = _find_col(df_recipes, ["contributor_id", "contributor", "author", "user"])

    if recipe_id_in_recipes is None or contrib_col is None:
        return pd.DataFrame(columns=["contributor_id", "recipe_count", "avg_rating", "median_rating"])

    recipe_counts = df_recipes.groupby(contrib_col).size().reset_index(name="recipe_count").rename(columns={contrib_col: "contributor_id"})

    if df_interactions is None or df_interactions.empty or recipe_id_col is None or rating_col is None:
        recipe_counts["avg_rating"] = np.nan
        recipe_counts["median_rating"] = np.nan
        return recipe_counts[["contributor_id", "recipe_count", "avg_rating", "median_rating"]]

    per_recipe = (
        df_interactions.dropna(subset=[recipe_id_col, rating_col])
                       .groupby(recipe_id_col)[rating_col]
                       .agg(["mean", "median"])
                       .reset_index()
                       .rename(columns={"mean": "avg_rating", "median": "median_rating"})
    )

    merged = per_recipe.merge(df_recipes[[recipe_id_in_recipes, contrib_col]].rename(columns={recipe_id_in_recipes: recipe_id_col, contrib_col: "contributor_id"}),
                              on=recipe_id_col, how="left").dropna(subset=["contributor_id"])

    contrib_ratings = merged.groupby("contributor_id").agg(avg_rating=("avg_rating", "mean"), median_rating=("median_rating", "median")).reset_index()

    result = contrib_ratings.merge(recipe_counts, on="contributor_id", how="right")
    result["recipe_count"] = pd.to_numeric(result["recipe_count"], errors="coerce").fillna(0).astype(int)
    result["avg_rating"] = pd.to_numeric(result.get("avg_rating"), errors="coerce")
    result["median_rating"] = pd.to_numeric(result.get("median_rating"), errors="coerce")

    return result[["contributor_id", "recipe_count", "avg_rating", "median_rating"]]



# ===============================
# Orchestrateur
# ===============================

class DataAnylizer:

    def __init__(self, csv_adapter: IDataAdapter):
        self.df_recipes = csv_adapter.load(DataType.RECIPES)
        self.df_interactions = csv_adapter.load(DataType.INTERACTIONS)

    def get_raw_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        return self.df_recipes, self.df_interactions

    def process_data(self, analysis_type: AnalysisType) -> pd.DataFrame:
        match analysis_type:

            case AnalysisType.NUMBER_RECIPES:
                return most_recipes_contributors(self.df_recipes)

            case AnalysisType.BEST_RECIPES:
                return best_ratings_contributors(self.df_recipes, self.df_interactions)

            case AnalysisType.DURATION_DISTRIBUTION:
                return average_duration_distribution(self.df_recipes, duration_col="minutes")

            case AnalysisType.DURATION_VS_RECIPE_COUNT:
                return duration_vs_recipe_count(self.df_recipes, duration_col="minutes")

            case AnalysisType.TOP_10_PERCENT_CONTRIBUTORS:
                return top_10_percent_contributors(self.df_recipes, self.df_interactions, duration_col="minutes")

            case AnalysisType.USER_SEGMENTS:
                # Table des utilisateurs avec attribution de segment
                return compute_user_segments(self.df_recipes, self.df_interactions, duration_col="minutes")

            case AnalysisType.TOP_TAGS_BY_SEGMENT:
                # Calcule d'abord les segments utilisateurs, puis les top tags
                df_users = compute_user_segments(self.df_recipes, self.df_interactions, duration_col="minutes")
                return top_tags_by_segment_from_users(self.df_recipes, df_users, tags_col="tags", top_k=5)
            
            case AnalysisType.RATING_DISTRIBUTION:
                return rating_distribution(
                    self.df_recipes,
                    self.df_interactions
                )
            
            case AnalysisType.RATING_VS_RECIPES:
                return rating_vs_recipe_count(
                    self.df_recipes,
                    self.df_interactions
                )
            case _:
                raise ValueError(f"Analyse non supportée : {analysis_type}")
