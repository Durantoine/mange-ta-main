API Reference Complète
======================

Documentation complète de l'API REST du backend avec **19 endpoints réels**.

Base URL
--------

- Développement : ``http://localhost:8000``
- Production : ``https://your-domain.com``
- Préfixe : ``/mange_ta_main``

Vue d'ensemble
--------------

L'API expose **19 endpoints** (18 GET + 1 POST) organisés en **6 catégories** :

1. **Gestion des données** (4 endpoints) - Chargement, nettoyage, debug
2. **Analyse contributeurs** (2 endpoints) - Top contributeurs par recettes/notes
3. **Analyse durée** (2 endpoints) - Distribution et corrélations
4. **Top performers** (3 endpoints) - Segmentation utilisateurs, personas
5. **Analyse ratings** (2 endpoints) - Distribution et corrélations
6. **Analyse reviews** (6 endpoints) - Statistiques et tendances temporelles

.. contents:: Table des matières
   :local:
   :depth: 2

---

1. Gestion des données
-----------------------

GET /mange_ta_main/health
~~~~~~~~~~~~~~~~~~~~~~~~~~

Vérifier que l'API est opérationnelle.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   {
     "status": "healthy"
   }

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/health

GET /mange_ta_main/load-data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Charger un dataset (recettes ou interactions).

**Paramètres** :

- ``data_type`` (query, string, **requis**) : ``recipes`` ou ``interactions``

**Réponse** : Array d'objets (format varie selon le type)

**Recettes** :

.. code-block:: json

   [
     {
       "id": 137739,
       "name": "arriba   baked winter squash mexican style",
       "minutes": 55,
       "contributor_id": 1,
       "submitted": "2005-09-16",
       "tags": "['60-minutes-or-less', 'time-to-make', 'course']",
       "nutrition": "[51.5, 0.0, 13.0, 0.0, 2.0, 0.0, 4.0]",
       "n_steps": 11,
       "steps": "['make a choice']",
       "description": "delicious...",
       "ingredients": "['winter squash', 'mexican seasoning']",
       "n_ingredients": 7
     }
   ]

**Interactions** :

.. code-block:: json

   [
     {
       "user_id": 1,
       "recipe_id": 137739,
       "date": "2002-01-01",
       "rating": 5,
       "review": "Great recipe!"
     }
   ]

**Exemple** :

.. code-block:: bash

   curl "http://localhost:8000/mange_ta_main/load-data?data_type=recipes"
   curl "http://localhost:8000/mange_ta_main/load-data?data_type=interactions"

POST /mange_ta_main/clean-raw-data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Déclencher le nettoyage et la normalisation des données brutes.

**Body (optionnel)** :

.. code-block:: json

   {
     "force": false
   }

**Réponse** :

.. code-block:: json

   {
     "status": "success",
     "message": "Data cleaned successfully"
   }

**Exemple** :

.. code-block:: bash

   curl -X POST http://localhost:8000/mange_ta_main/clean-raw-data \
     -H "Content-Type: application/json" \
     -d '{"force": false}'

GET /mange_ta_main/debug/memory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Obtenir les statistiques d'utilisation mémoire du processus.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   {
     "memory_mb": 450.5,
     "peak_memory_mb": 520.3,
     "timestamp": "2025-11-02T16:00:00Z"
   }

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/debug/memory

---

2. Analyse des contributeurs
-----------------------------

GET /mange_ta_main/most-recipes-contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Obtenir les contributeurs ayant publié le plus de recettes.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "contributor_id": 123,
       "num_recipes": 150,
       "avg_rating": 4.5,
       "total_reviews": 450
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/most-recipes-contributors

GET /mange_ta_main/best-ratings-contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Obtenir les contributeurs avec les meilleures notes moyennes.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "contributor_id": 456,
       "avg_rating": 4.8,
       "num_recipes": 50,
       "num_reviews": 200,
       "total_ratings": 4850
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/best-ratings-contributors

---

3. Analyse durée des recettes
------------------------------

GET /mange_ta_main/duration-distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Distribution des recettes par tranches de durée.

**Paramètres** : Aucun

**Tranches de durée** : 0-15, 15-30, 30-45, 45-60, 60-90, 90-120, 120+ minutes

**Réponse** :

.. code-block:: json

   [
     {
       "duration_bin": "0-15 min",
       "count": 5000,
       "percentage": 25.5,
       "cumulative_percentage": 25.5
     },
     {
       "duration_bin": "15-30 min",
       "count": 8000,
       "percentage": 40.8,
       "cumulative_percentage": 66.3
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/duration-distribution

GET /mange_ta_main/duration-vs-recipe-count
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Corrélation entre durée moyenne et nombre de recettes par contributeur.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "contributor_id": 123,
       "avg_minutes": 45.5,
       "num_recipes": 50
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/duration-vs-recipe-count

---

4. Top performers et segmentation
----------------------------------

GET /mange_ta_main/top-10-percent-contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Statistiques détaillées des 10% meilleurs contributeurs.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "contributor_id": 789,
       "num_recipes": 200,
       "avg_rating": 4.7,
       "total_reviews": 1500,
       "percentile": 95.5
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/top-10-percent-contributors

GET /mange_ta_main/user-segments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Segmentation des utilisateurs en 6 personas via K-means clustering.

**Paramètres** : Aucun

**Les 6 personas** :

0. **Super Cookers** - Recettes longues (55 min), excellentes notes (4.4), très commentées (12)
1. **Quick Cookers** - Recettes rapides (18 min), notes moyennes (3.6), peu commentées (3)
2. **Sweet Lovers** - Recettes moyennes (40 min), bonnes notes (4.2), moyennement commentées (6)
3. **Talkative Tasters** - Recettes moyennes (35 min), notes correctes (3.8), très commentées (18)
4. **Experimental Foodies** - Recettes moyennes-longues (45 min), notes moyennes (3.5), commentées (10)
5. **Everyday Cookers** - Recettes courtes-moyennes (30 min), bonnes notes (3.9), moyennement commentées (7)

**Réponse** :

.. code-block:: json

   [
     {
       "contributor_id": 123,
       "segment": 0,
       "persona": "Super Cookers",
       "avg_minutes": 55.2,
       "avg_rating": 4.4,
       "avg_reviews": 12.3,
       "num_recipes": 50
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/user-segments

GET /mange_ta_main/top-tags-by-segment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Top 5 tags les plus utilisés par chaque persona.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "segment": 0,
       "persona": "Super Cookers",
       "tag": "desserts",
       "count": 1500,
       "rank": 1
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/top-tags-by-segment

---

5. Analyse des ratings
-----------------------

GET /mange_ta_main/rating-distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Distribution des notes moyennes des contributeurs.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "rating_bin": "4.0-4.5",
       "count": 2500,
       "percentage": 35.5
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/rating-distribution

GET /mange_ta_main/rating-vs-recipes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Corrélation entre note moyenne et nombre de recettes.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "contributor_id": 123,
       "avg_rating": 4.5,
       "num_recipes": 50
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/rating-vs-recipes

---

6. Analyse des reviews
-----------------------

GET /mange_ta_main/review-overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Statistiques globales sur les reviews.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   {
     "total_reviews": 150000,
     "avg_review_length": 250.5,
     "reviews_with_text": 120000,
     "reviews_with_text_percentage": 80.0,
     "avg_reviews_per_recipe": 7.5
   }

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/review-overview

GET /mange_ta_main/review-distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Distribution du nombre de reviews par recette.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "review_count_bin": "0-5 reviews",
       "recipe_count": 5000,
       "percentage": 45.5
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/review-distribution

GET /mange_ta_main/top-reviewers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Top 20 reviewers les plus actifs.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "user_id": 456,
       "num_reviews": 1500,
       "avg_rating_given": 4.2,
       "rank": 1
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/top-reviewers

GET /mange_ta_main/review-trend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tendance temporelle des reviews (par mois).

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "year_month": "2008-01",
       "review_count": 1200,
       "avg_rating": 4.1
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/review-trend

GET /mange_ta_main/reviews-vs-rating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Corrélation entre nombre de reviews et note moyenne d'une recette.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "recipe_id": 137739,
       "num_reviews": 50,
       "avg_rating": 4.5
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/reviews-vs-rating

GET /mange_ta_main/reviewer-vs-recipes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Analyse du double rôle : reviewers qui publient aussi des recettes.

**Paramètres** : Aucun

**Réponse** :

.. code-block:: json

   [
     {
       "user_id": 123,
       "num_reviews_given": 200,
       "num_recipes_published": 50,
       "avg_rating_received": 4.3,
       "avg_rating_given": 4.1
     }
   ]

**Exemple** :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/reviewer-vs-recipes

---

Format de réponse
-----------------

Toutes les réponses GET (sauf health et memory) retournent un array d'objets JSON :

.. code-block:: json

   [
     {"key1": "value1", "key2": 123},
     {"key1": "value2", "key2": 456}
   ]

Gestion des valeurs spéciales
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``NaN`` → ``null``
- ``Infinity`` → ``null``
- ``-Infinity`` → ``null``
- Categorical data → convertie en string

Gestion des erreurs
--------------------

Format standard
~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "detail": "Description de l'erreur"
   }

Codes HTTP
~~~~~~~~~~

- ``200 OK`` : Succès
- ``400 Bad Request`` : Paramètres invalides
- ``404 Not Found`` : Ressource non trouvée
- ``422 Unprocessable Entity`` : Validation échouée
- ``500 Internal Server Error`` : Erreur serveur

Exemples d'erreurs
~~~~~~~~~~~~~~~~~~

**Paramètre invalide** :

.. code-block:: json

   {
     "detail": "Invalid data_type. Must be 'recipes' or 'interactions'"
   }

**Ressource non trouvée** :

.. code-block:: json

   {
     "detail": "Recipe not found"
   }

Performance
-----------

Optimisations
~~~~~~~~~~~~~

- **Mémoire** : 30-50% de réduction via chunked processing
- **Cold start** : 2-3 secondes (chargement initial des données)
- **Warm requests** : < 100ms pour la plupart des endpoints
- **Cache** : Données gardées en mémoire après première requête

Limites
~~~~~~~

- **Taille des datasets** : recipes (~260 MB), interactions (~310 MB)
- **Timeout** : 60 secondes par défaut
- **Rate limiting** : Non implémenté (à configurer selon les besoins)

Documentation interactive
--------------------------

Swagger UI
~~~~~~~~~~

Interface Swagger disponible à : http://localhost:8000/docs

ReDoc
~~~~~

Documentation ReDoc disponible à : http://localhost:8000/redoc

OpenAPI JSON
~~~~~~~~~~~~

Schéma OpenAPI disponible à : http://localhost:8000/openapi.json
