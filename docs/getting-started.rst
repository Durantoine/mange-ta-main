Guide de démarrage
==================

Prérequis
---------

* Python 3.10 ou supérieur (le projet s'exécute actuellement sous Python 3.13).
* `uv <https://github.com/astral-sh/uv>`_ pour la gestion reproductible des environnements.
* Docker (facultatif mais recommandé pour aligner votre environnement avec la CI).


Installation locale
-------------------

.. code-block:: bash

   git clone git@github.com:Durantoine/mange-ta-main.git
   cd mange-ta-main
   uv sync          # installe les dépendances backend et frontend

Pour lancer les tests et collecter la couverture :

.. code-block:: bash

   cd backend
   make lint-all
   make test

   cd ../frontend
   make lint-all
   make test


Construire la documentation
---------------------------

Les sources Sphinx se trouvent dans ``docs/``. Installez les dépendances
spécifiques à la documentation puis générez les pages HTML :

.. code-block:: bash

   pip install -r docs/requirements.txt
   make -C docs html

La documentation est ensuite disponible dans ``docs/_build/html/index.html``.


Organisation du dépôt
---------------------

* ``backend/`` : services FastAPI, analyses pandas et scripts de nettoyage.
* ``frontend/`` : interface Streamlit pour l'exploration des données.
* ``docs/`` : documentation utilisateur et technique (Sphinx).


Aller plus loin
---------------

* Consulter :doc:`api/index` pour la référence des modules Python.
* Ajouter vos notes et tutoriels sous ``docs/`` en utilisant les ``toctree`` déjà
  présents.
