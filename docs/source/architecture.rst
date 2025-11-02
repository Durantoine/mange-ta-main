Architecture
============

Vue d'ensemble
--------------

Le projet **Mange Ta Main** suit les principes de la **Clean Architecture** (Architecture Hexagonale),
ce qui permet une séparation claire des responsabilités et une meilleure testabilité.

Structure du projet
-------------------

.. code-block:: text

   mange-ta-main/
   ├── backend/                 # API Backend FastAPI
   │   ├── service/
   │   │   ├── layers/
   │   │   │   ├── api/         # Layer API (routes HTTP)
   │   │   │   ├── application/ # Layer Application (logique métier)
   │   │   │   ├── domain/      # Layer Domain (modèles)
   │   │   │   └── infrastructure/ # Layer Infrastructure (données)
   │   │   ├── main.py          # Point d'entrée FastAPI
   │   │   └── container.py     # Configuration DI
   │   ├── tests/               # Tests backend
   │   └── pyproject.toml
   │
   ├── frontend/                # Application Streamlit
   │   ├── service/
   │   │   ├── pages/           # Pages Streamlit
   │   │   ├── components/      # Composants réutilisables
   │   │   ├── src/             # Utilitaires
   │   │   └── app.py           # Point d'entrée Streamlit
   │   ├── tests/               # Tests frontend
   │   └── pyproject.toml
   │
   ├── docs/                    # Documentation Sphinx
   │   ├── source/
   │   └── build/
   │
   └── compose.yaml             # Docker Compose

Architecture en couches (Backend)
---------------------------------

Le backend suit une architecture en 4 couches :

1. Layer API
~~~~~~~~~~~~

**Responsabilité** : Gestion des requêtes HTTP et des routes

- Définit les endpoints FastAPI
- Valide les requêtes entrantes
- Formate les réponses HTTP
- Gère les erreurs HTTP

**Fichiers** : ``backend/service/layers/api/``

2. Layer Application
~~~~~~~~~~~~~~~~~~~~

**Responsabilité** : Logique métier et orchestration

- Implémente les cas d'usage
- Orchestre les appels aux différents services
- Applique les règles métier
- Traitement et nettoyage des données

**Fichiers** : ``backend/service/layers/application/``

3. Layer Domain
~~~~~~~~~~~~~~~

**Responsabilité** : Modèles et entités métier

- Définit les modèles de données
- Contient la logique métier pure
- Indépendant de toute technologie

**Fichiers** : ``backend/service/layers/domain/``

4. Layer Infrastructure
~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilité** : Accès aux données et services externes

- Lecture/écriture de fichiers (CSV, etc.)
- Accès aux bases de données
- Appels à des APIs externes
- Gestion du cache

**Fichiers** : ``backend/service/layers/infrastructure/``

Injection de dépendances
------------------------

Le projet utilise **dependency-injector** pour gérer les dépendances.

Configuration dans ``container.py`` :

.. code-block:: python

   from dependency_injector import containers, providers

   class Container(containers.DeclarativeContainer):
       # Configuration
       config = providers.Configuration()

       # Infrastructure
       csv_adapter = providers.Singleton(CSVAdapter)

       # Application
       data_cleaning = providers.Factory(DataCleaning)

       # API
       api_service = providers.Factory(
           APIService,
           data_cleaning=data_cleaning
       )

Architecture Frontend
---------------------

Le frontend Streamlit est organisé en :

Pages
~~~~~

Différentes pages de l'application :

- ``tab01_data.py`` : Visualisation des données brutes
- ``tab02_analyse.py`` : Analyses statistiques
- ``tab03_conclusions.py`` : Conclusions et insights

**Fichiers** : ``frontend/service/pages/``

Components
~~~~~~~~~~

Composants réutilisables :

- ``sidebar.py`` : Barre latérale de navigation
- ``tab01_top_contributors.py`` : Top contributeurs
- ``tab02_duration_recipe.py`` : Analyse des durées
- ``tab03_reviews.py`` : Analyse des reviews
- ``tab04_rating.py`` : Analyse des ratings
- ``tab05_personnas.py`` : Analyse des personas
- ``tab06_top10_analyse.py`` : Top 10 analyses
- ``tab07_tags.py`` : Analyse des tags

**Fichiers** : ``frontend/service/components/``

Flux de données
---------------

.. code-block:: text

   1. Utilisateur fait une requête HTTP
      ↓
   2. Layer API reçoit la requête (FastAPI)
      ↓
   3. Layer Application traite la logique métier
      ↓
   4. Layer Domain fournit les modèles
      ↓
   5. Layer Infrastructure accède aux données
      ↓
   6. Réponse remonte les layers
      ↓
   7. Frontend Streamlit affiche les résultats

Communication Backend ↔ Frontend
---------------------------------

Le frontend communique avec le backend via des requêtes HTTP REST :

.. code-block:: python

   # Frontend fait une requête
   response = requests.get("http://backend:8000/api/recipes")
   data = response.json()

   # Backend répond avec des données JSON
   @app.get("/api/recipes")
   def get_recipes():
       return {"recipes": [...]}

Avantages de cette architecture
--------------------------------

✅ **Séparation des préoccupations** : Chaque layer a une responsabilité claire

✅ **Testabilité** : Facile de tester chaque layer indépendamment

✅ **Maintenabilité** : Code organisé et facile à comprendre

✅ **Évolutivité** : Facile d'ajouter de nouvelles fonctionnalités

✅ **Indépendance** : Les layers ne dépendent pas des détails d'implémentation

✅ **Réutilisabilité** : Les composants peuvent être réutilisés
