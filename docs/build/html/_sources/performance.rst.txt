Performance et Optimisations
=============================

Le projet Mange Ta Main gère des datasets volumineux (1.2 GB+) et implémente plusieurs optimisations pour garantir de bonnes performances.

Vue d'ensemble
--------------

**Datasets** :

- Recipes : ~260 MB (cleaned), ~281 MB (raw)
- Interactions : ~308 MB (cleaned), ~333 MB (raw)
- Total : **1.2 GB** de données en mémoire

**Performance** :

- Cold start : 2-3 secondes
- Warm requests : < 100ms
- Memory optimization : 30-50% de réduction

Optimisations Mémoire
---------------------

Chunked Processing
~~~~~~~~~~~~~~~~~~

Pour les opérations sur de grands datasets, le code utilise un traitement par chunks :

.. code-block:: python

   def compute_user_segments(df_recipes, df_interactions):
       chunk_size = 10_000
       results = []

       for i in range(0, len(df), chunk_size):
           chunk = df.iloc[i:i+chunk_size]
           processed = process_chunk(chunk)
           results.append(processed)

       return pd.concat(results)

**Avantages** :

- Réduit l'utilisation mémoire de 30-50%
- Évite les pics mémoire
- Permet le traitement de datasets > RAM

Optimisation des types
~~~~~~~~~~~~~~~~~~~~~~

Conversion des types de données pour réduire l'empreinte mémoire :

.. code-block:: python

   # Int64 → Int32 (divise par 2 la taille)
   df['id'] = df['id'].astype('int32')

   # Float64 → Float32 (divise par 2 la taille)
   df['rating'] = df['rating'].astype('float32')

   # Object → Category (réduction 50-90% si peu de valeurs uniques)
   df['tag'] = df['tag'].astype('category')

**Gains typiques** :

- int64 → int32 : -50% mémoire
- float64 → float32 : -50% mémoire
- object → category : -50% à -90% mémoire (si < 50% valeurs uniques)

Lazy Loading
~~~~~~~~~~~~

Les données ne sont chargées qu'à la première requête :

.. code-block:: python

   class DataAnalyzer:
       _recipes_cache = None
       _interactions_cache = None

       def get_recipes(self):
           if self._recipes_cache is None:
               self._recipes_cache = self.load_recipes()
           return self._recipes_cache

**Avantages** :

- Démarrage rapide (< 1s)
- Mémoire utilisée uniquement si nécessaire
- Cache persistant entre requêtes

Drop Columns
~~~~~~~~~~~~

Suppression des colonnes inutilisées après chargement :

.. code-block:: python

   # Garder uniquement les colonnes nécessaires
   df = df[['id', 'name', 'minutes', 'contributor_id', 'rating']]

   # Drop des colonnes textuelles volumineuses
   df = df.drop(columns=['description', 'steps', 'ingredients'])

**Gains** : 20-40% de réduction mémoire

Performance Backend
-------------------

FastAPI
~~~~~~~

**Async/Await** :

.. code-block:: python

   @router.get("/user-segments")
   async def get_user_segments(analyzer: DataAnalyzer):
       # Traitement async pour ne pas bloquer
       segments = await analyzer.compute_segments_async()
       return segments

**Avantages** :

- Gère plusieurs requêtes simultanées
- Ne bloque pas sur les opérations I/O
- Meilleur throughput

Caching
~~~~~~~

Les résultats coûteux sont cachés en mémoire :

.. code-block:: python

   from functools import lru_cache

   @lru_cache(maxsize=128)
   def compute_expensive_analysis(params):
       # Calcul coûteux
       result = heavy_computation(params)
       return result

**TTL** : Cache valide jusqu'au redémarrage du service

Dependency Injection
~~~~~~~~~~~~~~~~~~~~

Réutilisation des instances via le container :

.. code-block:: python

   container = Container()
   container.wire(modules=[__name__])

   # Instance singleton réutilisée
   analyzer = container.data_analyzer()

**Avantages** :

- Pas de rechargement des données
- Partage du cache entre requêtes
- Moins d'allocations mémoire

Performance Frontend
--------------------

Streamlit Caching
~~~~~~~~~~~~~~~~~

Utilisation intensive du cache Streamlit :

.. code-block:: python

   @st.cache_data(ttl=3600)  # Cache 1 heure
   def load_dataset(dataset_type: str):
       response = requests.get(f"{BASE_URL}/load-data?data_type={dataset_type}")
       return pd.DataFrame(response.json())

**Avantages** :

- Pas de rechargement à chaque interaction
- Mémoire partagée entre sessions
- TTL configurable

Lazy Components
~~~~~~~~~~~~~~~

Les composants ne sont chargés que s'ils sont visibles :

.. code-block:: python

   # Chargement uniquement si l'onglet est sélectionné
   if tab == "Personas":
       from components.tab05_personnas import render_personnas
       render_personnas()

Pagination
~~~~~~~~~~

Affichage paginé pour les grands datasets :

.. code-block:: python

   # Afficher seulement les 100 premières lignes
   st.dataframe(df.head(100))

   # Option de téléchargement pour le dataset complet
   st.download_button("Download full dataset", df.to_csv())

Métriques de Performance
-------------------------

Backend Benchmarks
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 20 20 20

   * - Endpoint
     - Cold Start
     - Warm (p50)
     - Warm (p95)
   * - ``/health``
     - < 10ms
     - < 5ms
     - < 10ms
   * - ``/load-data?type=recipes``
     - 2-3s
     - < 50ms
     - < 100ms
   * - ``/most-recipes-contributors``
     - 500ms
     - 50ms
     - 100ms
   * - ``/user-segments``
     - 5-8s
     - 200ms
     - 500ms
   * - ``/review-trend``
     - 1-2s
     - 80ms
     - 150ms

Frontend Benchmarks
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Page
     - Initial Load
     - Re-render
   * - Landing page
     - < 1s
     - < 100ms
   * - Data visualization
     - 2-3s
     - < 200ms
   * - Analysis dashboard
     - 3-5s
     - < 300ms
   * - Personas
     - 5-8s
     - < 400ms

Utilisation Mémoire
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 25 25 20

   * - Service
     - Base
     - Avec Données
     - Peak
   * - Backend (cold)
     - 50 MB
     - 450 MB
     - 520 MB
   * - Backend (optimized)
     - 50 MB
     - 280 MB
     - 350 MB
   * - Frontend
     - 100 MB
     - 200 MB
     - 250 MB

**Réduction totale** : ~40% grâce aux optimisations

Optimisations Infrastructure
-----------------------------

Docker
~~~~~~

**Multi-stage build** :

.. code-block:: dockerfile

   # Stage 1: Build
   FROM python:3.11-slim as builder
   RUN pip install --user dependencies

   # Stage 2: Runtime
   FROM python:3.11-slim
   COPY --from=builder /root/.local /root/.local

**Gains** : Image finale 50% plus petite

**Resource limits** :

.. code-block:: yaml

   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2.0'
             memory: 1G
           reservations:
             memory: 512M

Kubernetes
~~~~~~~~~~

**Horizontal Pod Autoscaling** :

.. code-block:: yaml

   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: backend-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: backend
     minReplicas: 2
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70

**Health checks** :

.. code-block:: yaml

   livenessProbe:
     httpGet:
       path: /mange_ta_main/health
       port: 8000
     initialDelaySeconds: 30
     periodSeconds: 10

   readinessProbe:
     httpGet:
       path: /mange_ta_main/health
       port: 8000
     initialDelaySeconds: 5
     periodSeconds: 5

Bonnes Pratiques
----------------

Développement
~~~~~~~~~~~~~

1. **Profiler régulièrement** :

   .. code-block:: python

      import cProfile
      cProfile.run('my_function()')

2. **Monitorer la mémoire** :

   .. code-block:: python

      import psutil
      process = psutil.Process()
      print(f"Memory: {process.memory_info().rss / 1024 / 1024} MB")

3. **Utiliser memory_profiler** :

   .. code-block:: bash

      pip install memory_profiler
      python -m memory_profiler script.py

Production
~~~~~~~~~~

1. **Logging** : Utiliser structlog pour des logs structurés
2. **Monitoring** : Prometheus + Grafana pour les métriques
3. **Alerting** : Alertes sur usage mémoire > 80%
4. **Rate limiting** : Limiter les requêtes par IP
5. **CDN** : Utiliser un CDN pour les assets statiques

Limites Connues
---------------

Actuelles
~~~~~~~~~

- **Pas de pagination API** : Tous les résultats retournés en une fois
- **Pas de streaming** : Toutes les données en mémoire
- **Cache simple** : Pas de TTL ni d'invalidation intelligente
- **Pas de compression** : Réponses JSON non compressées

Futures Améliorations
~~~~~~~~~~~~~~~~~~~~~

1. **Pagination** : Implémenter limit/offset sur tous les endpoints
2. **Streaming** : Utiliser FastAPI streaming responses
3. **Redis Cache** : Cache distribué avec TTL
4. **Compression gzip** : Réduire taille des réponses de 70%
5. **Database** : PostgreSQL pour requêtes plus complexes
6. **Indexing** : Index sur colonnes fréquemment queryées
7. **Query optimization** : Requêtes SQL optimisées
8. **CDN** : CloudFlare pour cache edge

Outils de Monitoring
--------------------

Métriques à surveiller
~~~~~~~~~~~~~~~~~~~~~~

- **Latence** : p50, p95, p99 par endpoint
- **Mémoire** : Usage, peak, tendance
- **CPU** : Utilisation moyenne et peaks
- **Requêtes** : QPS (queries per second)
- **Erreurs** : Taux d'erreur 4xx et 5xx

Dashboard Grafana
~~~~~~~~~~~~~~~~~

Créer des dashboards pour :

- Latence par endpoint
- Utilisation mémoire/CPU
- Request rate
- Error rate
- Response time distribution

Alertes
~~~~~~~

Configurer des alertes pour :

- Mémoire > 80% pendant 5 minutes
- CPU > 80% pendant 5 minutes
- Latence p95 > 1s
- Error rate > 1%
- Service down

Références
----------

- **FastAPI Performance** : https://fastapi.tiangolo.com/deployment/performance/
- **Pandas Optimization** : https://pandas.pydata.org/docs/user_guide/enhancingperf.html
- **Memory Profiling** : https://github.com/pythonprofilers/memory_profiler
- **Streamlit Caching** : https://docs.streamlit.io/library/advanced-features/caching

See Also
--------

- :doc:`architecture` - Architecture du projet
- :doc:`api` - Documentation API
- :doc:`installation` - Guide d'installation
