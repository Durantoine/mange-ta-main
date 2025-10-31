Guide de démarrage
==================

Ce guide décrit la marche à suivre pour installer le projet, lancer les services
Backend et Frontend, exécuter la batterie de tests et générer la documentation.

Prérequis
---------

* Python 3.10 ou supérieur (les environnements CI utilisent Python 3.13).
* `uv <https://github.com/astral-sh/uv>`_ pour la gestion déterministe des dépendances.
* Docker Desktop ou équivalent (facultatif mais pratique pour reproduire la CI).
* `make` (GNU Make) pour profiter des raccourcis fournis.

Installation locale
-------------------

1. Cloner le dépôt et installer les dépendances partagées ::

      git clone git@github.com:Durantoine/mange-ta-main.git
      cd mange-ta-main
      uv sync

2. Initialiser les sous-projets :

   * Backend ::

         cd backend
         uv run pre-commit install        # optionnel mais recommandé
         uv run python -m pip install -e .    # installe le backend en mode editable

   * Frontend ::

         cd ../frontend
         uv run pre-commit install

Exécution en mode développement
-------------------------------

Backend (API FastAPI) ::

    cd backend
    uv run uvicorn service.main:app --reload --port 8000

Frontend (Streamlit) ::

    cd frontend
    uv run streamlit run service/app.py

Les deux services attendent que les CSV se trouvent dans ``backend/service/layers/infrastructure/data``.

Alternative Docker Compose
--------------------------

Pour se rapprocher de la pipeline CI :

.. code-block:: bash

   # backend
   cd backend
   docker compose -f compose-backend.yaml up --build

   # frontend
   cd ../frontend
   docker compose -f compose-front.yaml up --build

L’intelligence artificielle du layer application est chargée au démarrage via le mécanisme
``lifespan`` de FastAPI.

Qualité, tests et couverture
----------------------------

Lint & typage Backend ::

    cd backend
    make lint-all       # ruff + isort + black + pyright

Tests Backend + couverture ::

    make test           # pytest + coverage report

Lint & typage Frontend ::

    cd ../frontend
    make lint-all

Tests Frontend + couverture ::

    make test

Les rapports coverage sont affichés en console. Pour un rapport HTML ::

    coverage html
    open htmlcov/index.html

Construction de la documentation
--------------------------------

Depuis la racine du dépôt ::

    make docs

La commande installe les dépendances Sphinx (via ``docs/requirements.txt``)
et génère ``docs/_build/html/index.html``. En cas de modification majeure,
nettoyez le répertoire de build avant de relancer ::

    make -C docs clean
    make docs

Structure du dépôt
------------------

* ``backend/`` : API FastAPI, pipeline pandas, tests unitaires backend.
* ``frontend/`` : application Streamlit et tests associés.
* ``docs/`` : documentation Sphinx (guides, API, architecture).
* ``EDA/`` : notebooks exploratoires et jeux de données bruts/nettoyés.

Prochaines étapes
-----------------

* Lire :doc:`architecture` pour une vue d’ensemble des modules.
* Consulter :doc:`analytics-review` pour comprendre le calcul des métriques
  utilisées dans l’onglet *Reviews*.
* Explorer :doc:`api/index` pour la référence complète des fonctions Python.
