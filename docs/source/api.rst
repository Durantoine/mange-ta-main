API Reference
=============

Documentation complète de l'API REST du backend.

Base URL
--------

En développement local : ``http://localhost:8000``

En production : ``https://your-domain.com``

Endpoints
---------

Health Check
~~~~~~~~~~~~

Vérifier que l'API est en ligne.

.. code-block:: http

   GET /health

**Réponse** :

.. code-block:: json

   {
     "status": "healthy",
     "version": "0.1.0"
   }

**Codes de statut** :

- ``200 OK`` : L'API fonctionne correctement

Recipes
~~~~~~~

Récupérer les recettes
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/v1/recipes

**Paramètres de requête** :

- ``limit`` (optionnel, int) : Nombre maximum de recettes à retourner
- ``offset`` (optionnel, int) : Décalage pour la pagination
- ``sort_by`` (optionnel, str) : Champ pour trier (ex: "rating", "duration")
- ``order`` (optionnel, str) : Ordre de tri ("asc" ou "desc")

**Exemple de requête** :

.. code-block:: bash

   curl -X GET "http://localhost:8000/api/v1/recipes?limit=10&offset=0&sort_by=rating&order=desc"

**Réponse** :

.. code-block:: json

   {
     "recipes": [
       {
         "id": 1,
         "name": "Poulet rôti",
         "duration": 60,
         "rating": 4.5,
         "tags": ["viande", "four"],
         "contributor_id": "user123"
       }
     ],
     "total": 100,
     "limit": 10,
     "offset": 0
   }

**Codes de statut** :

- ``200 OK`` : Succès
- ``400 Bad Request`` : Paramètres invalides
- ``500 Internal Server Error`` : Erreur serveur

Récupérer une recette spécifique
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/v1/recipes/{recipe_id}

**Paramètres de chemin** :

- ``recipe_id`` (int) : ID de la recette

**Exemple de requête** :

.. code-block:: bash

   curl -X GET "http://localhost:8000/api/v1/recipes/123"

**Réponse** :

.. code-block:: json

   {
     "id": 123,
     "name": "Poulet rôti",
     "duration": 60,
     "rating": 4.5,
     "tags": ["viande", "four"],
     "contributor_id": "user123",
     "description": "Délicieux poulet rôti au four",
     "ingredients": ["poulet", "sel", "poivre"],
     "steps": ["Préchauffer le four", "Assaisonner le poulet", "Cuire 60 min"]
   }

**Codes de statut** :

- ``200 OK`` : Succès
- ``404 Not Found`` : Recette non trouvée
- ``500 Internal Server Error`` : Erreur serveur

Statistics
~~~~~~~~~~

Statistiques globales
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/v1/statistics

**Réponse** :

.. code-block:: json

   {
     "total_recipes": 50000,
     "total_users": 10000,
     "average_rating": 4.2,
     "average_duration": 45,
     "total_reviews": 150000
   }

Statistiques des contributeurs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/v1/statistics/contributors

**Réponse** :

.. code-block:: json

   {
     "top_contributors": [
       {
         "user_id": "user123",
         "recipe_count": 150,
         "average_rating": 4.7
       }
     ],
     "total_contributors": 10000
   }

Statistiques des tags
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/v1/statistics/tags

**Réponse** :

.. code-block:: json

   {
     "top_tags": [
       {
         "tag": "végétarien",
         "count": 5000
       },
       {
         "tag": "rapide",
         "count": 4500
       }
     ],
     "total_tags": 500
   }

Personas
~~~~~~~~

Analyse des personas
^^^^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/v1/personas

**Réponse** :

.. code-block:: json

   {
     "personas": [
       {
         "name": "Chef professionnel",
         "characteristics": {
           "recipe_count": "> 50",
           "average_duration": "> 60 min",
           "favorite_tags": ["gastronomique", "technique"]
         },
         "user_count": 500
       },
       {
         "name": "Cuisinier amateur",
         "characteristics": {
           "recipe_count": "< 10",
           "average_duration": "< 30 min",
           "favorite_tags": ["rapide", "facile"]
         },
         "user_count": 5000
       }
     ]
   }

Modèles de données
------------------

Recipe
~~~~~~

.. code-block:: python

   class Recipe:
       id: int
       name: str
       duration: int  # en minutes
       rating: float  # 0-5
       tags: list[str]
       contributor_id: str
       description: str | None
       ingredients: list[str]
       steps: list[str]
       created_at: datetime
       updated_at: datetime

User
~~~~

.. code-block:: python

   class User:
       id: str
       username: str
       recipe_count: int
       average_rating: float
       created_at: datetime

Review
~~~~~~

.. code-block:: python

   class Review:
       id: int
       recipe_id: int
       user_id: str
       rating: float
       comment: str
       created_at: datetime

Gestion des erreurs
-------------------

Format des erreurs
~~~~~~~~~~~~~~~~~~

Toutes les erreurs suivent ce format :

.. code-block:: json

   {
     "error": {
       "code": "ERROR_CODE",
       "message": "Description de l'erreur",
       "details": {}
     }
   }

Codes d'erreur courants
~~~~~~~~~~~~~~~~~~~~~~~

- ``400`` : Bad Request - Paramètres invalides
- ``401`` : Unauthorized - Authentification requise
- ``403`` : Forbidden - Accès refusé
- ``404`` : Not Found - Ressource non trouvée
- ``422`` : Unprocessable Entity - Validation échouée
- ``500`` : Internal Server Error - Erreur serveur
- ``503`` : Service Unavailable - Service temporairement indisponible

Rate Limiting
-------------

L'API est limitée à :

- **100 requêtes par minute** par IP
- **1000 requêtes par heure** par IP

Les headers de réponse incluent :

.. code-block:: http

   X-RateLimit-Limit: 100
   X-RateLimit-Remaining: 95
   X-RateLimit-Reset: 1623456789

Authentification
----------------

Pour le moment, l'API est publique et ne nécessite pas d'authentification.

Une authentification par token JWT sera ajoutée dans une future version.

Versioning
----------

L'API suit le versioning sémantique.

La version actuelle est ``v1`` et tous les endpoints commencent par ``/api/v1/``.

Les versions obsolètes seront maintenues pendant au moins 6 mois après le déploiement
d'une nouvelle version majeure.

OpenAPI / Swagger
-----------------

La documentation interactive Swagger est disponible à :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI JSON** : http://localhost:8000/openapi.json
