Architecture applicative
=========================

Le projet se structure en trois couches principales :

Backend (FastAPI)
-----------------

* **service/layers/api** expose les routes HTTP. Chaque endpoint délègue la logique
  métier à la couche application via l’énumération :class:`service.layers.application.mange_ta_main.AnalysisType`.
* **service/layers/application** regroupe les fonctions d’analyste (pandas +
  numpy). Elles sont documentées et typées pour faciliter leur réutilisation
  dans d’autres contextes (scripts batch, notebooks, etc.).
* **service/layers/infrastructure** s’occupe de l’accès aux données CSV, de la
  configuration du logger et de l’injection de dépendances (via
  ``dependency_injector``).

Frontend (Streamlit)
--------------------

* **service/app.py** instancie la page principale et charge les différentes tabs.
* **service/components** contient une fonction ``render_*`` par onglet. Chaque
  composant appelle les endpoints FastAPI, formate les données et construit les
  visualisations Altair/Streamlit.
* **service/logger.py** fournit un logger structlog-compatible, avec un fallback
  javellisant les keyword arguments et garantissant des logs équivalents en
  local ou sur CI.

Pipeline de données
-------------------

1. Les sources CSV brutes sont chargées via :class:`service.layers.infrastructure.csv_adapter.CSVAdapter`.
2. Les fonctions de nettoyage de ``data_cleaning.py`` standardisent les identifiants,
   suppriment les valeurs aberrantes et persévèrent les jeux “nettoyés”.
3. Les fonctions d'analyse de ``mange_ta_main.py`` produisent des dataframes prêts
   à être consommés par l’API ou par un notebook.

Journalisation et observabilité
-------------------------------

* Le backend écrit simultanément vers la console, ``logs/debug.log`` et
  ``logs/error.log`` grâce à :mod:`service.layers.logger`.
* Le frontend journalise chaque appel API significatif (volume de lignes
  ramenées, erreurs réseau, etc.) afin de faciliter le diagnostic côté UI.
* Les tests unitaires couvrent explicitement les deux branches du logger :
  fallback (sans structlog) et configuration complète (avec structlog).

Références croisées
-------------------

* :doc:`getting-started` pour lancer rapidement l’application.
* :doc:`analytics-review` pour la description détaillée des indicateurs “reviews”.
* :mod:`service.layers.application.mange_ta_main` pour l’implémentation des
  métriques.
