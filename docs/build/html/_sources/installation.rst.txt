Installation
============

Prérequis
---------

**Obligatoire** :

- **Docker 20+** et **Docker Compose 2+**
- Git

**Optionnel** (pour développement local sans Docker) :

- Python 3.11+
- pip ou uv (gestionnaire de paquets)

⚠️ **Important** : Assurez-vous que Docker est en cours d'exécution avant d'exécuter les commandes.

Installation avec Docker (Recommandé)
--------------------------------------

Cette méthode utilise Docker et le développement se fait **directement dans les conteneurs** avec hot reload.

1. Cloner le repository
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone <repository-url>
   cd mange-ta-main

2. Démarrer tous les services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Mode développement** (avec hot reload) :

.. code-block:: bash

   make service-dev-up

**Mode production** :

.. code-block:: bash

   make service-prod-up

Les services seront accessibles sur :

- **Backend** : http://localhost:8000
- **Frontend** : http://localhost:8501
- **API Docs (Swagger)** : http://localhost:8000/docs

3. Arrêter les services
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   make service-stop

4. Nettoyer tout
~~~~~~~~~~~~~~~~

.. code-block:: bash

   make service-clean

Commandes Backend
-----------------

Toutes les commandes depuis le dossier ``backend/`` :

Build et démarrage
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd backend

   # Build image dev
   make build-dev

   # Démarrer en mode dev (avec hot reload)
   make dev-up

   # Build image prod
   make build-prod

   # Démarrer en mode prod
   make prod-up

   # Arrêter
   make stop

Qualité du code
~~~~~~~~~~~~~~~

.. code-block:: bash

   cd backend

   # Linting avec Ruff
   make lint

   # Auto-fix avec Ruff
   make lint-fix

   # Formatage avec Black et isort
   make format

   # Type checking avec Pyright
   make check-types

   # Tout en une fois
   make lint-all

Tests
~~~~~

.. code-block:: bash

   cd backend

   # Lancer les tests avec coverage
   make test

Commandes Frontend
------------------

Toutes les commandes depuis le dossier ``frontend/`` :

Build et démarrage
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd frontend

   # Build image dev
   make build-dev

   # Démarrer en mode dev (avec hot reload)
   make dev-up

   # Build image prod
   make build-prod

   # Démarrer en mode prod
   make prod-up

   # Arrêter
   make stop

Qualité du code
~~~~~~~~~~~~~~~

.. code-block:: bash

   cd frontend

   # Linting avec Ruff
   make lint

   # Auto-fix avec Ruff
   make lint-fix

   # Formatage avec Black et isort
   make format

   # Type checking avec Pyright
   make check-types

   # Tout en une fois
   make lint-all

Tests
~~~~~

.. code-block:: bash

   cd frontend

   # Lancer les tests avec coverage
   make test

Ports des services
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Service
     - Port
     - Description
   * - Backend (FastAPI)
     - 8000
     - API REST
   * - Frontend (Streamlit)
     - 8501
     - Interface utilisateur
   * - Swagger UI
     - 8000/docs
     - Documentation interactive API
   * - ReDoc
     - 8000/redoc
     - Documentation alternative API

Configuration
-------------

Le frontend se connecte automatiquement au backend via :

.. code-block:: bash

   BACKEND_URL=http://mange_ta_main:8000

(Configuré automatiquement en mode développement Docker)

Développement dans Docker
--------------------------

**Hot Reload** :

Le développement se fait **directement dans les conteneurs Docker**. Les volumes montés permettent la synchronisation en temps réel :

- Modifiez un fichier Python sur votre machine
- Les changements sont **immédiatement reflétés** dans le conteneur
- **Pas besoin de rebuild** l'image pour les modifications de code

**Backend** :

.. code-block:: bash

   cd backend
   make dev-up
   # Éditez service/main.py
   # FastAPI recharge automatiquement ✨

**Frontend** :

.. code-block:: bash

   cd frontend
   make dev-up
   # Éditez service/app.py
   # Streamlit recharge automatiquement ✨

Installation locale (Sans Docker)
----------------------------------

⚠️ **Déconseillé** : Cette méthode nécessite de gérer manuellement les dépendances.

Backend
~~~~~~~

.. code-block:: bash

   cd backend
   pip install -e .
   pip install --group dev

   # Lancer
   fastapi dev service/main.py

Frontend
~~~~~~~~

.. code-block:: bash

   cd frontend
   pip install -e .
   pip install --group dev

   # Lancer
   streamlit run service/app.py

Vérification de l'installation
-------------------------------

Backend
~~~~~~~

1. Vérifier que le backend répond :

   .. code-block:: bash

      curl http://localhost:8000/mange_ta_main/health

   Réponse attendue :

   .. code-block:: json

      {"status": "healthy"}

2. Vérifier l'API Swagger : http://localhost:8000/docs

3. Lancer les tests :

   .. code-block:: bash

      cd backend
      make test

Frontend
~~~~~~~~

1. Ouvrir http://localhost:8501 dans votre navigateur

2. Vérifier que les données se chargent

3. Lancer les tests :

   .. code-block:: bash

      cd frontend
      make test

Déploiement Kubernetes
-----------------------

Le projet inclut des configurations Kubernetes :

.. code-block:: bash

   # Déployer le backend
   kubectl apply -f deploy-back.yaml

   # Déployer le frontend
   kubectl apply -f deploy-front.yaml

   # Configurer l'ingress
   kubectl apply -f ingress.yaml

Voir les fichiers :

- ``deploy-back.yaml`` - Déploiement backend avec configuration
- ``deploy-front.yaml`` - Déploiement frontend
- ``ingress.yaml`` - Configuration ingress
- ``backend-config.yaml`` - ConfigMap backend

Génération de la documentation
-------------------------------

Pour générer la documentation Sphinx :

1. Installer les dépendances docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Backend
   cd backend
   pip install --group docs

   # Frontend
   cd frontend
   pip install --group docs

2. Générer la documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd docs
   make html

3. Ouvrir la documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # macOS
   open build/html/index.html

   # Linux
   xdg-open build/html/index.html

   # Windows
   start build\html\index.html

Troubleshooting
---------------

Docker n'est pas démarré
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Error: Cannot connect to Docker daemon

**Solution** : Démarrez Docker Desktop

Ports déjà utilisés
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Error: Port 8000 is already in use

**Solution** :

.. code-block:: bash

   # Arrêter tous les conteneurs
   make service-stop

   # Ou identifier et tuer le processus
   lsof -ti:8000 | xargs kill -9

Problèmes de permissions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Error: Permission denied

**Solution** :

.. code-block:: bash

   # Ajouter votre utilisateur au groupe docker (Linux)
   sudo usermod -aG docker $USER

   # Se déconnecter/reconnecter pour appliquer

Hot reload ne fonctionne pas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution** : Vérifiez que vous utilisez ``make dev-up`` et non ``make prod-up``

Les tests échouent
~~~~~~~~~~~~~~~~~~

**Solution** :

.. code-block:: bash

   # Reconstruire les images
   make service-clean
   make service-dev-up

   # Relancer les tests
   cd backend && make test
   cd frontend && make test

Exemples d'utilisation
-----------------------

Démarrage complet en dev
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Depuis la racine du projet
   make service-dev-up

   # Ouvrir dans le navigateur
   # Backend: http://localhost:8000/docs
   # Frontend: http://localhost:8501

Développement backend uniquement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd backend
   make dev-up

   # Dans un autre terminal
   curl http://localhost:8000/mange_ta_main/health

Développement frontend uniquement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # D'abord démarrer le backend
   cd backend
   make dev-up

   # Dans un autre terminal
   cd frontend
   make dev-up

Lancer les tests et vérifier la qualité
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Backend
   cd backend
   make lint-all
   make test

   # Frontend
   cd frontend
   make lint-all
   make test

Nettoyer et redémarrer
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   make service-clean
   make service-dev-up

Ressources
----------

- **Docker** : https://docs.docker.com/get-started/
- **Docker Compose** : https://docs.docker.com/compose/
- **FastAPI** : https://fastapi.tiangolo.com/
- **Streamlit** : https://docs.streamlit.io/
- **Makefile** : https://www.gnu.org/software/make/manual/

Notes importantes
-----------------

- Le développement se fait **dans Docker** avec hot reload
- Les volumes sont montés pour synchronisation temps réel
- **Pas besoin de rebuild** pour les modifications de code en dev
- Les images prod sont immutables et optimisées
- Chaque service (backend/frontend) a son propre Makefile
- Le Makefile global orchestre tous les services
- La couverture de tests minimale est de 80%

See Also
--------

- :doc:`architecture` - Architecture du projet
- :doc:`api` - Documentation API
- :doc:`contributing` - Guide de contribution
