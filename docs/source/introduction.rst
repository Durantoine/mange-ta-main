Introduction
============

Présentation
------------

**Mange Ta Main** est une application d'analyse de données de recettes de cuisine.
Elle permet d'explorer, analyser et visualiser des données culinaires à grande échelle.

Fonctionnalités principales
----------------------------

- 📊 Analyse des contributions des utilisateurs
- ⏱️ Analyse des durées de préparation des recettes
- ⭐ Analyse des évaluations et reviews
- 👥 Identification de personas d'utilisateurs
- 🏷️ Analyse des tags et catégories
- 📈 Visualisations interactives

Technologies utilisées
----------------------

Backend
~~~~~~~

- **FastAPI** : Framework web moderne et rapide
- **Pandas** : Manipulation et analyse de données
- **Pydantic** : Validation des données
- **Dependency Injector** : Injection de dépendances
- **StructLog** : Logging structuré

Frontend
~~~~~~~~

- **Streamlit** : Interface utilisateur interactive
- **Pandas** : Manipulation de données
- **Requests** : Communication avec l'API backend
- **StructLog** : Logging structuré

Architecture
------------

Le projet suit une architecture en couches (Clean Architecture) :

- **Layer API** : Points d'entrée HTTP (routes FastAPI)
- **Layer Application** : Logique métier et cas d'usage
- **Layer Domain** : Modèles et entités métier
- **Layer Infrastructure** : Accès aux données (CSV, etc.)

Public cible
------------

Cette application est destinée à :

- Analystes de données culinaires
- Chercheurs en sciences alimentaires
- Développeurs souhaitant apprendre FastAPI et Streamlit
- Toute personne intéressée par l'analyse de données de recettes
