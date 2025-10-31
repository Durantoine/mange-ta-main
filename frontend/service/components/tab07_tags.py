import altair as alt
import pandas as pd
import requests
import streamlit as st
from domain import BASE_URL
from logger import struct_logger

SEGMENT_ORDER = [
    "Super Cookers",
    "Quick Cookers",
    "Sweet Lovers",
    "Talkative Tasters",
    "Experimental Foodies",
    "Everyday Cookers",
]


def render_top_tags_by_segment(
    logger=struct_logger,
) -> None:  # pragma: no cover - Streamlit UI glue
    """Render the persona segmentation view and associated top tags.

    Cette section combine :

    * un tableau récapitulatif des caractéristiques de segments (durée moyenne,
      note moyenne, volume d'avis) ;
    * une visualisation Altair permettant de comparer les tags dominants selon
      l'axe sélectionné (volume ou pourcentage) ;
    * un bouton de téléchargement CSV pour faciliter des analyses hors produit.

    Chaque appel réseau est journalisé via ``logger`` afin de faciliter le
    diagnostic en cas de “404” ou de latence prolongée côté API.
    """

    st.header("🏷️ Cartographie des tags")
    st.caption("Analyse de la popularité et de la distribution des tags au sein de la communauté")

    data = [
        {
            "Segment": "Super Cookers",
            "Durée recette (moyenne)": "55 min",
            "Note moyenne (/5)": 4.4,
            "Nombre moyen d’avis": 12,
        },
        {
            "Segment": "Quick Cookers",
            "Durée recette (moyenne)": "18 min",
            "Note moyenne (/5)": 3.6,
            "Nombre moyen d’avis": 3,
        },
        {
            "Segment": "Sweet Lovers",
            "Durée recette (moyenne)": "40 min",
            "Note moyenne (/5)": 4.2,
            "Nombre moyen d’avis": 6,
        },
        {
            "Segment": "Talkative Tasters",
            "Durée recette (moyenne)": "35 min",
            "Note moyenne (/5)": 3.8,
            "Nombre moyen d’avis": 18,
        },
        {
            "Segment": "Experimental Foodies",
            "Durée recette (moyenne)": "45 min",
            "Note moyenne (/5)": 3.5,
            "Nombre moyen d’avis": 10,
        },
        {
            "Segment": "Everyday Cookers",
            "Durée recette (moyenne)": "30 min",
            "Note moyenne (/5)": 3.9,
            "Nombre moyen d’avis": 7,
        },
    ]

    st.markdown(
        """
        Ces paramètres ont été établis dans le cadre d’une analyse de clustering,
        dont l’objectif était de détecter des regroupements naturels d’utilisateurs
        en fonction de leurs habitudes de publication, de leurs préférences culinaires
        et de leur niveau d’engagement.
        """
    )

    df_header = pd.DataFrame(data)
    st.table(df_header)

    st.divider()

    metric = st.radio("Afficher :", ["Volume (count)", "Part (%)"], horizontal=True, index=0)
    value_col = "count" if metric.startswith("Volume") else "share_pct"
    y_title = "Occurrences" if value_col == "count" else "Part (%)"

    try:
        response = requests.get(f"{BASE_URL}/mange_ta_main/top-tags-by-segment")
        response.raise_for_status()
        data = response.json()
        logger.info("Top tags by segment fetched", count=len(data))
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        logger.error("Failed to fetch top tags by segment", error=str(e))
        return
    else:
        if not data:
            st.warning("Aucune donnée disponible")
            return

        df = pd.DataFrame(data)
        required_cols = {"segment", "persona", "tag", "count", "share_pct"}
        if not required_cols.issubset(df.columns):
            st.error("Données inattendues reçues pour les tags par segment.")
            logger.error("Unexpected columns for top-tags-by-segment", cols=list(df.columns))
            return

        df["segment"] = df["segment"] + 1

        df["persona"] = pd.Categorical(df["persona"], categories=SEGMENT_ORDER, ordered=True)

        st.subheader("📊 Top tags par persona")

        st.markdown(
            """
            Cette visualisation met en évidence les tags les plus utilisés par segment d’utilisateurs.
            Les thématiques culinaires récurrentes permettent de caractériser les préférences et
            les modes de contribution propres à chaque persona. En comparant les volumes et parts
            d’occurrence, il devient possible d’identifier des centres d’intérêt dominants,
            des spécificités de comportement, ainsi que des opportunités de ciblage éditorial.
            """
        )

        cols = st.columns(2)
        col_idx = 0

        for persona in SEGMENT_ORDER:
            seg_df = df[df["persona"] == persona].copy()
            if seg_df.empty:
                continue

            seg_df = seg_df.sort_values(value_col, ascending=False)

            chart = (
                alt.Chart(seg_df)
                .mark_bar()
                .encode(
                    x=alt.X("tag:N", sort="-y", title="Tag"),
                    y=alt.Y(f"{value_col}:Q", title=y_title),
                    tooltip=[
                        alt.Tooltip("segment:Q", title="Segment"),
                        alt.Tooltip("tag:N", title="Tag"),
                        alt.Tooltip("count:Q", title="Occurrences", format=","),
                        alt.Tooltip("share_pct:Q", title="Part (%)", format=".2f"),
                    ],
                )
                .properties(width="container", height=260, title=f"{persona}")
            )

            with cols[col_idx]:
                st.altair_chart(chart, use_container_width=True)
            col_idx = (col_idx + 1) % 2

        st.subheader("Données détaillées")
        st.dataframe(
            df.sort_values(["persona", value_col], ascending=[True, False]),
            hide_index=True,
            use_container_width=True,
        )

        csv = df.to_csv(index=False)
        st.download_button("📥 Télécharger CSV", csv, "top_tags_by_segment.csv", "text/csv")

        st.markdown(
            """
            ### 🔍 Lecture générale

            On observe une forte homogénéité dans les tags dominants entre segments :
            `preparation`, `time-to-make` et `course` figurent systématiquement dans le trio de tête.
            Ce sont des tags indiquant structure, fonction et contexte de la recette — des dimensions
            transversales, indépendantes du profil culinaire.

            Les tags `main-ingredient` et `dietary` occupent ensuite les positions 4 et 5 selon les segments,
            reflétant une recherche axée sur ingrédients et contraintes alimentaires.

            ### 🧑‍🍳 Super Cookers

            - Forte représentativité des tags techniques (`preparation`, `main-ingredient`),
            - Intérêt marqué pour les contraintes diététiques,
            - Comportement cohérent : ces utilisateurs cherchent à optimiser des recettes complexes.
            👉 Leur usage des tags traduit une volonté de maîtrise, pas juste de consommation.

            ### ⚡ Quick Cookers

            - Tag `easy` très présent (4ᵉ position),
            - Forte importance de `time-to-make`.
            👉 Ces utilisateurs cherchent à cuisiner rapidement avec un minimum d’effort et privilégient les filtres facilitant la préparation.

            ### 🍫 Sweet Lovers

            - Pas de tag pâtissier dans le top 5 (car la data est comptée globalement),
            - Forte présence de `main-ingredient` (logique : chocolat, fruits, etc.),
            - Poids comparable de `dietary`, probablement pour les régimes spécifiques.
            👉 Ils catégorisent surtout par ingrédients sucrés et temps de préparation.

            ### 💬 Talkative Tasters

            - Plus fort taux de `preparation` et `time-to-make` (~6 %),
            - Tags plus généralistes que prévu.
            👉 Beaucoup commentent des recettes variées plutôt que publier des contenus spécialisés :
            un rôle d’animateurs communautaires.

            ### 🌍 Experimental Foodies

            - Forte utilisation de `main-ingredient`,
            - `dietary` en 5ᵉ position.
            👉 Ils jouent sur les ingrédients (épices, légumineuses, sauces rares), ce qui reflète leur exploration gastronomique.

            ### 🍽️ Everyday Cookers

            - `preparation` et `time-to-make` sont surpondérés (~5.7 %),
            - `dietary` également stable.
            👉 Ils cherchent un compromis praticité / repas du quotidien ; l’usage des tags sert à filtrer vite et efficacement.

            ### 📌 Interprétation transversale

            - Les tags sont utilisés comme filtres pratiques plus que marqueurs identitaires.
            - Le temps (`time-to-make`) est un critère central pour tous (pressés, experts, familles).
            - La diète est un levier majeur (santé, allergies, éthique).
            - Les ingrédients restent la clé de la recherche culinaire (orientation “liste de courses”).

            ### 🎯 Insights actionnables (produit / UX)

            - Mettre davantage en avant les filtres temps, ingrédients et régimes.
            - Proposer des parcours personnalisés par persona :
              - recettes rapides (Quick Cookers),
              - masterclass techniques (Super Cookers),
              - inspirations internationales (Experimental Foodies).
            - Suggérer des packs curatoriaux par ingrédients (pivot commun à tous).

            ### 🧠 Conclusion

            Les tags dominants ne révèlent pas des goûts culinaires complexes, mais une rationalisation du parcours utilisateur :
            - préparer vite,
            - trouver avec précision,
            - filtrer par contraintes,
            - maîtriser les ingrédients.

            Ce sont des signaux UX forts, plus que des traits culinaires profonds, qui montrent une plateforme orientée praticité et navigation fonctionnelle.
            """
        )
