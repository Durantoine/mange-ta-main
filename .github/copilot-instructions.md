# Instructions pour les agents IA sur le projet mange-ta-main

## Vue d'ensemble
Ce projet est une application big data composée de plusieurs services (backend, frontend, exploration de données) organisés en dossiers séparés et orchestrés via Docker Compose. Le backend et le frontend sont tous deux containerisés, utilisent Python 3.11+, et gèrent leurs dépendances avec UV. Les workflows de développement et de production sont distincts.

## Structure principale
- `backend/service/` : code source Python du backend (architecture hexagonale : api, application, domain, infrastructure)
- `backend/tests/` : tests unitaires et d'intégration pour le backend
- `frontend/service/` : code source Python du frontend (app Flask)
- `frontend/tests/` : tests pour le frontend
- `EDA/` : notebooks et scripts d'exploration de données
- `recipe/` : données brutes et consignes
- `Makefile` (à la racine, dans backend et frontend) : commandes pour build, test, lint, etc.
- `compose.yaml` et `compose-prod-override.yaml` : configuration Docker Compose pour dev et prod

## Workflows critiques
- **Build et lancement (dev/prod) :**
  - `make build-dev` / `make build-prod` : build des images Docker
  - `make dev-up` / `make prod-up` : lancement des environnements
  - `make stop` : arrêt de tous les containers
- **Qualité et tests :**
  - `make lint` : vérification Ruff
  - `make format` : formatage Black
  - `make check-types` : vérification MyPy
  - `make test` : exécution des tests Pytest
  - `make lint-all` : toutes les vérifications
  - ⚠️ Toujours builder l'image (`make build-dev`) après ajout de fichiers dans `service/` ou `tests/` pour que le container les voie

## Conventions spécifiques
- Architecture hexagonale pour le backend : séparer API, logique métier, domaine et infrastructure
- Les tests doivent être dans `tests/` avec un `__init__.py` présent
- Les environnements dev montent les sources en volume, les changements sont immédiats
- Les environnements prod n'incluent que les dépendances de production
- Les notebooks d'exploration sont dans `EDA/`, les données dans `recipe/`

## Points d'intégration et dépendances
- Utilisation de Docker et Docker Compose pour tous les services
- UV pour la gestion des dépendances Python
- Backend et frontend communiquent via API HTTP (voir configs Compose)
- Les notebooks peuvent charger les données de `recipe/RAW_recipes.csv` ou `EDA/data/`

## Exemples de commandes
```bash
make build-dev
make dev-up
make lint
make test
```

## Fichiers clés à consulter
- `backend/service/main.py` : point d'entrée backend
- `frontend/service/app.py` : point d'entrée frontend
- `compose.yaml` : orchestration des services
- `Makefile` : commandes automatisées
- `pyproject.toml` : dépendances et configuration

---

Pour toute convention non documentée ici, se référer aux README des dossiers ou aux fichiers de configuration. N'hésitez pas à demander des précisions sur les workflows ou conventions spécifiques.
