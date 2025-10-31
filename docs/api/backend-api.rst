Couche API : routes FastAPI
===========================

Le module ``backend.service.layers.api.mange_ta_main`` centralise toutes les
routes FastAPI exposées au frontend Streamlit. Chaque endpoint délègue la
logique métier à la couche application et sérialise le résultat en JSON.

Endpoints principaux
--------------------

.. list-table::
   :header-rows: 1

   * - Route
     - Description
     - Analyse déclenchée
   * - ``GET /mange_ta_main/health``
     - Vérifie la disponibilité de l'API.
     - —
   * - ``GET /mange_ta_main/load-data``
     - Retourne les jeux ``recipes`` ou ``interactions`` bruts.
     - —
   * - ``GET /mange_ta_main/most-recipes-contributors``
     - Classe les contributeurs selon le nombre de recettes publiées.
     - ``AnalysisType.NUMBER_RECIPES``
   * - ``GET /mange_ta_main/best-ratings-contributors``
     - Met en avant les auteurs les mieux notés.
     - ``AnalysisType.BEST_RECIPES``
   * - ``GET /mange_ta_main/review-overview``
     - Fournit des KPI agrégés sur l’activité des avis.
     - ``AnalysisType.REVIEW_OVERVIEW``
   * - ``GET /mange_ta_main/reviewer-vs-recipes``
     - Compare publication de recettes et génération d’avis par contributeur.
     - ``AnalysisType.REVIEWER_VS_RECIPES``
   * - ``POST /mange_ta_main/clean-raw-data``
     - Lance le pipeline de nettoyage et persiste les CSV normalisés.
     - Fonction ``clean_data`` de la couche application.

Chaque handler récupère un ``DataAnylizer`` injecté via la dépendance
``get_data_analyzer``. Les exceptions de normalisation sont converties en
``HTTPException`` avec un message utilisateur clair.

Infrastructure
--------------

``backend.service.layers.infrastructure.csv_adapter`` encapsule les accès aux
CSV. L’adapter charge les fichiers bruts ou nettoyés, sauvegarde les jeux
transformés et journalise les accès pour faciliter le suivi des pipelines.
