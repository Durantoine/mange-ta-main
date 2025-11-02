Installation
============

Prérequis
---------

- Python 3.11 ou supérieur
- pip ou uv (gestionnaire de paquets)
- Docker (optionnel, pour le déploiement)
- Git

Installation locale
-------------------

1. Cloner le repository
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone <repository-url>
   cd mange-ta-main

2. Installation du backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd backend
   pip install -e .
   pip install --group dev  # Pour les dépendances de développement

Ou avec uv :

.. code-block:: bash

   cd backend
   uv pip install -e .
   uv pip install --group dev

3. Installation du frontend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd frontend
   pip install -e .
   pip install --group dev

Ou avec uv :

.. code-block:: bash

   cd frontend
   uv pip install -e .
   uv pip install --group dev

4. Installer les dépendances de documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Dans backend/
   pip install --group docs

   # Dans frontend/
   pip install --group docs

Lancement de l'application
---------------------------

Backend
~~~~~~~

.. code-block:: bash

   cd backend
   fastapi dev service/main.py

Le backend sera accessible sur http://localhost:8000

Frontend
~~~~~~~~

.. code-block:: bash

   cd frontend
   streamlit run service/app.py

Le frontend sera accessible sur http://localhost:8501

Avec Docker Compose
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   docker-compose up

Variables d'environnement
--------------------------

Backend
~~~~~~~

Créer un fichier ``.env`` dans le dossier ``backend/`` :

.. code-block:: bash

   # Configuration de l'API
   API_HOST=0.0.0.0
   API_PORT=8000

   # Chemins des données
   DATA_PATH=/path/to/data

Frontend
~~~~~~~~

Créer un fichier ``.env`` dans le dossier ``frontend/`` :

.. code-block:: bash

   # URL du backend
   BACKEND_URL=http://localhost:8000

Vérification de l'installation
-------------------------------

Pour vérifier que tout fonctionne correctement :

.. code-block:: bash

   # Lancer les tests du backend
   cd backend
   pytest

   # Lancer les tests du frontend
   cd frontend
   pytest

Génération de la documentation
-------------------------------

.. code-block:: bash

   cd docs
   make html

La documentation sera générée dans ``docs/build/html/``.

Pour voir la documentation :

.. code-block:: bash

   # macOS
   open docs/build/html/index.html

   # Linux
   xdg-open docs/build/html/index.html

   # Windows
   start docs/build/html/index.html
