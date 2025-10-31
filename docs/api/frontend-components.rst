Composants Streamlit
====================

Les composants de ``frontend.service.components`` orchestrent les onglets du
tableau de bord Streamlit. Chaque module encapsule le rendu d’une section et
déclenche les appels API nécessaires.

Vue d’ensemble
--------------

.. list-table::
   :header-rows: 1

   * - Module
     - Objectif
   * - ``tab01_top_contributors``
     - Affiche le classement des contributeurs les plus actifs avec métriques clés et export CSV.
   * - ``tab02_duration_recipe``
     - Analyse la durée de préparation (histogrammes, répartition par tranches et commentaires narratifs).
   * - ``tab03_reviews``
     - Met en scène les indicateurs d’avis, la typologie des reviewers et la corrélation avis/recettes.
   * - ``tab04_rating``
     - Visualise la distribution des notes et les comportements associés (top / long tail).
   * - ``tab06_top10_analyse``
     - Compare le top 10 % des auteurs aux autres via des graphiques secondaires.
   * - ``tab07_tags``
     - Explore les tags culinaires dominants par persona et propose des téléchargements ciblés.

Tous les composants consomment ``BASE_URL`` depuis ``frontend.service.domain`` et
utilisent ``struct_logger`` pour tracer les interactions (succès comme erreurs).
Ils exposent une fonction ``render_*`` unique qui peut être appelée depuis
``frontend/service/app.py`` pour composer l’expérience utilisateur.
