Application : analyses et services
==================================

``backend.service.layers.application.mange_ta_main`` concentre toutes les
fonctions analytiques utilisées par l’API et le tableau de bord. Le cœur du
module est la classe ``DataAnylizer`` qui met en cache les deux jeux de données
et route les demandes (``AnalysisType``) vers la fonction dédiée.

Fonctions phares
----------------

.. list-table::
   :header-rows: 1

   * - Fonction
     - Objectif
   * - ``most_recipes_contributors``
     - Classement des auteurs par volume de publication.
   * - ``best_ratings_contributors``
     - Mesure des meilleures notes moyennes par auteur.
   * - ``review_overview``
     - KPI globaux sur le volume d’avis, d’auteurs et le taux de recettes commentées.
   * - ``review_distribution_per_recipe``
     - Histogramme du nombre d’avis par recette.
   * - ``reviews_vs_rating``
     - Corrélation entre quantité d’avis et note moyenne.
   * - ``reviewer_reviews_vs_recipes``
     - Analyse croisée entre recettes publiées et avis déposés par auteur.

Chaque fonction retourne un ``pandas.DataFrame`` normalisé (noms de colonnes en
français, valeurs préparées pour Streamlit). Les transformations s’appuient sur
des helpers tels que ``_parse_tags_to_list`` pour harmoniser les tags ou
``segment_personas`` pour la segmentation contributeurs.

Nettoyage des données
---------------------

Le module ``backend.service.layers.application.data_cleaning`` orchestre le
pipeline de préparation des CSV bruts :

* ``clean_data`` charge le jeu ``recipes`` ou ``interactions``, applique
  ``remove_outliers`` (IQR), homogénéise les identifiants avec ``normalize_ids``
  puis renvoie un JSON prêt à être persistant par l’adapter.
* Les colonnes de type liste sont désérialisées via ``ast.literal_eval`` et les
  ``NaN`` convertis en ``None`` pour rester compatibles avec FastAPI.

Exceptions personnalisées
-------------------------

``backend.service.layers.application.exceptions`` rassemble les exceptions
propres au projet. ``DataNormalizationError`` est levée lors d’un nettoyage
impossible (jeu inconnu, colonne manquante) tandis qu’``UnsupportedAnalysisError``
signale un ``AnalysisType`` non pris en charge. L’API les convertit en erreurs
HTTP 400 pour informer clairement le client.
