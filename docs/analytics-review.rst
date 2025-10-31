Analyse des avis
================

Cette page décrit les principaux indicateurs calculés pour l’onglet *Reviews*
du tableau de bord. Toutes les fonctions proviennent de
:mod:`service.layers.application.mange_ta_main`.

Synthèse globale (:func:`review_overview`)
------------------------------------------

* **total_reviews** : nombre total d’interactions contenant un avis textuel.
* **recipes_with_reviews** : nombre de recettes du catalogue ayant reçu au
  moins un avis exploitable.
* **share_recipes_reviewed_pct** : couverture du catalogue, calculée en
  considérant uniquement l’intersection entre recettes *publiées* et recettes
  *commentées*. Cette approche garantit un taux ≤ 100 %.
* **empty_review_ratio_pct** : proportion d’interactions ne contenant pas
  de texte (utile pour suivre la qualité des contributions).
* **avg/median_review_length_words** : descriptive statistics (longueur des avis).

Répartition par recette (:func:`review_distribution_per_recipe`)
----------------------------------------------------------------

Les recettes sont réparties par nombre d’avis. Pour chaque tranche, nous stockons :

* le volume de recettes concernées,
* la part qu’elles représentent dans le catalogue,
* le nombre moyen d’avis par recette dans la tranche.

Le paramètre ``bins`` est configurable afin d’adapter la granularité.

Activité des reviewers (:func:`reviewer_activity`)
--------------------------------------------------

* **reviews_count** : nombre d’avis publiés par reviewer.
* **share_pct** : part relative au sein de l’ensemble des avis (somme = 100 %).
* **avg_review_length_words** : longueur textuelle moyenne.
* **avg_rating_given** : note moyenne donnée (si disponible).
* **first/last_review_date** : bornes temporelles d’activité.

Tendance temporelle (:func:`review_temporal_trend`)
---------------------------------------------------

Les avis sont agrégés au format mensuel (``YYYY-MM``) pour suivre les vagues
de contributions. La série contient les colonnes suivantes :

* nombre d’avis collectés,
* nombre de reviewers uniques actifs,
* note moyenne des avis (si présente dans les données brutes).

Corrélation avis / notes (:func:`reviews_vs_rating`)
----------------------------------------------------

Pour chaque recette, nous consolidons :

* le volume total d’avis,
* la note moyenne,
* la référence recette (nom + auteur).

Cette jointure est exploitée par le frontend pour produire une matrice de
correlation permettant d’identifier les recettes les plus discutées et/ou
les mieux notées.

Comparaison reviewers vs recettes (:func:`reviewer_reviews_vs_recipes`)
-----------------------------------------------------------------------

Cette fonction rapproche l’activité commentaires d’un utilisateur et sa
production de recettes. Elle permet de détecter les profils experts
(``reviews_count`` élevé et ``recipes_published`` modéré) ou, inversement,
les contributeurs prolifiques qui génèrent peu de retours.
