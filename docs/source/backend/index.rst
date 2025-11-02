Backend Documentation
====================

Le backend est construit avec **FastAPI** et suit une architecture en couches.

.. toctree::
   :maxdepth: 2
   :caption: Modules Backend:

   api
   application
   domain
   infrastructure

Vue d'ensemble
--------------

Le backend expose une API REST pour :

- Récupérer les données de recettes
- Effectuer des analyses statistiques
- Nettoyer et traiter les données
- Fournir des métriques et insights

Structure des modules
---------------------

API Layer
~~~~~~~~~

Gère les endpoints HTTP et la validation des requêtes.

.. automodule:: service.layers.api.mange_ta_main
   :members:
   :undoc-members:
   :show-inheritance:

Application Layer
~~~~~~~~~~~~~~~~~

Contient la logique métier et les cas d'usage.

.. automodule:: service.layers.application.mange_ta_main
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: service.layers.application.data_cleaning
   :members:
   :undoc-members:
   :show-inheritance:

Domain Layer
~~~~~~~~~~~~

Définit les modèles et entités métier.

.. automodule:: service.layers.domain.mange_ta_main
   :members:
   :undoc-members:
   :show-inheritance:

Infrastructure Layer
~~~~~~~~~~~~~~~~~~~~

Gère l'accès aux données et aux ressources externes.

.. automodule:: service.layers.infrastructure.csv_adapter
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: service.layers.infrastructure.types
   :members:
   :undoc-members:
   :show-inheritance:

Container (Dependency Injection)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration de l'injection de dépendances.

.. automodule:: service.container
   :members:
   :undoc-members:
   :show-inheritance:

Logger
~~~~~~

Système de logging structuré.

.. automodule:: service.layers.logger
   :members:
   :undoc-members:
   :show-inheritance:
