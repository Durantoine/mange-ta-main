Personas et Segmentation Utilisateurs
======================================

Le projet Mange Ta Main utilise **K-means clustering** pour identifier 6 personas d'utilisateurs distincts basés sur leur comportement culinaire.

Vue d'ensemble
--------------

La segmentation est basée sur 3 dimensions principales :

- **avg_minutes** : Durée moyenne des recettes publiées
- **avg_rating** : Note moyenne reçue
- **avg_reviews** : Nombre moyen de commentaires reçus par recette

L'algorithme K-means utilise la distance euclidienne pour assigner chaque contributeur à l'un des 6 clusters.

Les 6 Personas
--------------

1. Super Cookers 👨‍🍳⭐
~~~~~~~~~~~~~~~~~~~~~~~

**Profil** : Les experts de la cuisine

- **Durée moyenne** : 55 minutes
- **Note moyenne** : 4.4/5
- **Reviews moyennes** : 12 par recette

**Caractéristiques** :

- Recettes élaborées et techniques
- Excellente qualité constante
- Fort engagement de la communauté
- Recettes très commentées et appréciées

**Tags favoris** : desserts, advanced, gourmet, technique

**Exemple** : Chef expérimenté publiant des recettes sophistiquées

2. Quick Cookers ⚡🍳
~~~~~~~~~~~~~~~~~~~~~

**Profil** : Les pressés efficaces

- **Durée moyenne** : 18 minutes
- **Note moyenne** : 3.6/5
- **Reviews moyennes** : 3 par recette

**Caractéristiques** :

- Recettes rapides et pratiques
- Qualité correcte mais basique
- Peu d'engagement communautaire
- Focus sur la simplicité

**Tags favoris** : 30-minutes-or-less, easy, quick, weeknight

**Exemple** : Parent occupé cherchant des solutions rapides

3. Sweet Lovers 🍰❤️
~~~~~~~~~~~~~~~~~~~~~

**Profil** : Les passionnés de pâtisserie

- **Durée moyenne** : 40 minutes
- **Note moyenne** : 4.2/5
- **Reviews moyennes** : 6 par recette

**Caractéristiques** :

- Spécialisés dans les desserts
- Bonne qualité et créativité
- Engagement modéré de la communauté
- Équilibre durée/qualité

**Tags favoris** : desserts, chocolate, cakes, cookies, baking

**Exemple** : Amateur de pâtisserie partageant ses créations

4. Talkative Tasters 💬🍽️
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Profil** : Les sociaux engagés

- **Durée moyenne** : 35 minutes
- **Note moyenne** : 3.8/5
- **Reviews moyennes** : 18 par recette

**Caractéristiques** :

- Forte interaction communautaire
- Recettes qui génèrent de la discussion
- Qualité moyenne mais très commentées
- Focus sur l'aspect social

**Tags favoris** : family, entertaining, comfort-food, beginner-cook

**Exemple** : Animateur de communauté culinaire

5. Experimental Foodies 🧪🍴
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Profil** : Les créatifs audacieux

- **Durée moyenne** : 45 minutes
- **Note moyenne** : 3.5/5
- **Reviews moyennes** : 10 par recette

**Caractéristiques** :

- Recettes originales et expérimentales
- Résultats variables (risque/récompense)
- Engagement modéré
- Innovation et créativité

**Tags favoris** : ethnic, fusion, unusual, exotic

**Exemple** : Cuisinier aventureux testant de nouvelles combinaisons

6. Everyday Cookers 🏠👨‍🍳
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Profil** : Les cuisiniers du quotidien

- **Durée moyenne** : 30 minutes
- **Note moyenne** : 3.9/5
- **Reviews moyennes** : 7 par recette

**Caractéristiques** :

- Recettes équilibrées et fiables
- Bonne qualité sans prise de tête
- Engagement modéré
- Valeur sûre

**Tags favoris** : main-dish, healthy, weeknight-meals, family-friendly

**Exemple** : Cuisinier régulier avec un répertoire solide

Algorithme de Segmentation
---------------------------

Méthode
~~~~~~~

**K-means clustering** avec 6 clusters

.. code-block:: python

   from sklearn.cluster import KMeans

   # Features utilisées
   features = ['avg_minutes', 'avg_rating', 'avg_reviews']

   # Clustering
   kmeans = KMeans(n_clusters=6, random_state=42)
   segments = kmeans.fit_predict(user_features)

Distance
~~~~~~~~

Distance euclidienne calculée pour assigner chaque utilisateur au cluster le plus proche :

.. math::

   d(u, c) = \sqrt{(u_{minutes} - c_{minutes})^2 + (u_{rating} - c_{rating})^2 + (u_{reviews} - c_{reviews})^2}

Où :
- :math:`u` = features de l'utilisateur
- :math:`c` = centroid du cluster

Optimisation
~~~~~~~~~~~~

Pour les grands datasets (> 100K utilisateurs) :

- **Chunked processing** : 10K utilisateurs à la fois
- **Memory optimization** : 30-50% de réduction mémoire
- **Caching** : Segments calculés une fois et cachés

Utilisation
-----------

Via l'API
~~~~~~~~~

Obtenir les segments de tous les utilisateurs :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/user-segments

Réponse :

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

Obtenir les tags par segment :

.. code-block:: bash

   curl http://localhost:8000/mange_ta_main/top-tags-by-segment

Via le frontend
~~~~~~~~~~~~~~~

Section "Personas" du dashboard Streamlit :

1. Naviguez vers la page "Analyse"
2. Sélectionnez l'onglet "Personas"
3. Visualisez la distribution des 6 personas
4. Explorez les tags favoris par persona

Applications
------------

Marketing
~~~~~~~~~

- Cibler les "Super Cookers" pour des recettes premium
- Proposer des recettes rapides aux "Quick Cookers"
- Recommander des desserts aux "Sweet Lovers"

Recommandation
~~~~~~~~~~~~~~

- Recommander des recettes similaires au persona
- Suggérer des auteurs du même segment
- Personnaliser le feed selon le persona

Analyse
~~~~~~~

- Comprendre les différents types d'utilisateurs
- Identifier les besoins de chaque segment
- Optimiser l'expérience utilisateur par persona

Stratégie Contenu
~~~~~~~~~~~~~~~~~

- Créer du contenu adapté à chaque persona
- Équilibrer l'offre entre les segments
- Engager chaque communauté différemment

Statistiques
------------

Distribution des Personas
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 20 30

   * - Persona
     - % Utilisateurs
     - Avg Recipes
     - Engagement
   * - Super Cookers
     - 15%
     - 75
     - Très élevé
   * - Quick Cookers
     - 25%
     - 30
     - Faible
   * - Sweet Lovers
     - 20%
     - 45
     - Moyen
   * - Talkative Tasters
     - 12%
     - 40
     - Très élevé
   * - Experimental Foodies
     - 18%
     - 35
     - Moyen
   * - Everyday Cookers
     - 10%
     - 55
     - Moyen-Élevé

Métriques Clés
~~~~~~~~~~~~~~

- **Silhouette Score** : 0.65 (bonne séparation des clusters)
- **Inertie** : Optimale pour K=6
- **Stabilité** : 95% des utilisateurs gardent le même segment après recalcul

Évolution Temporelle
~~~~~~~~~~~~~~~~~~~~

Les personas peuvent évoluer au fil du temps :

- **Quick Cooker → Everyday Cooker** : Progression naturelle
- **Sweet Lover → Super Cooker** : Spécialisation
- **Everyday Cooker → Experimental Foodie** : Exploration

Code Source
-----------

L'implémentation complète est disponible dans :

- **Backend** : ``service/layers/application/mange_ta_main.py``
- **Fonction** : ``compute_user_segments()``
- **Constants** : ``SEGMENT_INFO`` dictionnaire

.. code-block:: python

   SEGMENT_INFO = {
       0: {"persona": "Super Cookers", ...},
       1: {"persona": "Quick Cookers", ...},
       # ... etc
   }

Références
----------

- K-means Clustering : https://scikit-learn.org/stable/modules/clustering.html#k-means
- User Segmentation Best Practices : https://www.nngroup.com/articles/personas/
- Recipe Analytics : https://www.food52.com/blog/25708-recipe-analytics

See Also
--------

- :doc:`api` - API endpoints pour récupérer les segments
- :doc:`frontend/index` - Composant UI personas
- :doc:`backend/index` - Implémentation backend
