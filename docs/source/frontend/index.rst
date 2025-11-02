Frontend Documentation
=====================

Le frontend est construit avec **Streamlit** et fournit une interface interactive
pour visualiser et analyser les données.

.. toctree::
   :maxdepth: 2
   :caption: Modules Frontend:

   pages
   components
   utils

Vue d'ensemble
--------------

Le frontend offre :

- 📊 Visualisations interactives des données
- 📈 Graphiques et statistiques
- 🔍 Filtres et recherche
- 👥 Analyse de personas
- 🏷️ Analyse de tags

Application principale
----------------------

Point d'entrée de l'application Streamlit.

.. automodule:: service.app
   :members:
   :undoc-members:
   :show-inheritance:

Pages
-----

Page 1 : Données brutes
~~~~~~~~~~~~~~~~~~~~~~~

Affiche les données brutes et permet l'exploration.

.. automodule:: service.pages.tab01_data
   :members:
   :undoc-members:
   :show-inheritance:

Page 2 : Analyses
~~~~~~~~~~~~~~~~~

Affiche les analyses statistiques et visualisations.

.. automodule:: service.pages.tab02_analyse
   :members:
   :undoc-members:
   :show-inheritance:

Page 3 : Conclusions
~~~~~~~~~~~~~~~~~~~~

Présente les conclusions et insights.

.. automodule:: service.pages.tab03_conclusions
   :members:
   :undoc-members:
   :show-inheritance:

Components
----------

Sidebar
~~~~~~~

Barre latérale de navigation.

.. automodule:: service.components.sidebar
   :members:
   :undoc-members:
   :show-inheritance:

Top Contributors
~~~~~~~~~~~~~~~~

Analyse des meilleurs contributeurs.

.. automodule:: service.components.tab01_top_contributors
   :members:
   :undoc-members:
   :show-inheritance:

Duration Recipe
~~~~~~~~~~~~~~~

Analyse des durées de préparation.

.. automodule:: service.components.tab02_duration_recipe
   :members:
   :undoc-members:
   :show-inheritance:

Reviews
~~~~~~~

Analyse des reviews et commentaires.

.. automodule:: service.components.tab03_reviews
   :members:
   :undoc-members:
   :show-inheritance:

Rating
~~~~~~

Analyse des évaluations.

.. automodule:: service.components.tab04_rating
   :members:
   :undoc-members:
   :show-inheritance:

Personnas
~~~~~~~~~

Identification des personas d'utilisateurs.

.. automodule:: service.components.tab05_personnas
   :members:
   :undoc-members:
   :show-inheritance:

Top 10 Analyse
~~~~~~~~~~~~~~

Analyse des top 10 éléments.

.. automodule:: service.components.tab06_top10_analyse
   :members:
   :undoc-members:
   :show-inheritance:

Tags
~~~~

Analyse des tags et catégories.

.. automodule:: service.components.tab07_tags
   :members:
   :undoc-members:
   :show-inheritance:

Utilitaires
-----------

IO Loader
~~~~~~~~~

Chargement et sauvegarde de données.

.. automodule:: service.src.io_loader
   :members:
   :undoc-members:
   :show-inheritance:

Visualization
~~~~~~~~~~~~~

Fonctions de visualisation.

.. automodule:: service.src.viz
   :members:
   :undoc-members:
   :show-inheritance:

Analytics Users
~~~~~~~~~~~~~~~

Fonctions d'analyse des utilisateurs.

.. automodule:: service.src.analytics_users
   :members:
   :undoc-members:
   :show-inheritance:

Domain
~~~~~~

Modèles de domaine du frontend.

.. automodule:: service.domain
   :members:
   :undoc-members:
   :show-inheritance:

Logger
~~~~~~

Système de logging.

.. automodule:: service.logger
   :members:
   :undoc-members:
   :show-inheritance:
