Guide de contribution
====================

Nous accueillons avec plaisir les contributions ! Ce guide vous aidera à contribuer au projet.

Avant de commencer
------------------

1. Lire la documentation
~~~~~~~~~~~~~~~~~~~~~~~~~

Lisez la documentation complète pour comprendre l'architecture et le fonctionnement du projet.

2. Consulter les issues
~~~~~~~~~~~~~~~~~~~~~~~

Regardez les `issues GitHub <https://github.com/your-org/mange-ta-main/issues>`_ pour trouver des tâches à réaliser.

3. Discuter de votre idée
~~~~~~~~~~~~~~~~~~~~~~~~~~

Pour les changements importants, créez d'abord une issue pour discuter de votre proposition.

Configuration de l'environnement de développement
--------------------------------------------------

1. Fork et clone
~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/your-username/mange-ta-main.git
   cd mange-ta-main

2. Créer une branche
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git checkout -b feature/ma-nouvelle-fonctionnalite

3. Installer les dépendances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Backend
   cd backend
   pip install -e .
   pip install --group dev

   # Frontend
   cd ../frontend
   pip install -e .
   pip install --group dev

Standards de code
-----------------

Formatage
~~~~~~~~~

Nous utilisons **Ruff** pour le formatage et le linting :

.. code-block:: bash

   # Backend
   cd backend
   ruff format service/ tests/
   ruff check service/ tests/

   # Frontend
   cd frontend
   ruff format service/ tests/
   ruff check service/ tests/

Type checking
~~~~~~~~~~~~~

Nous utilisons **Pyright** pour la vérification des types :

.. code-block:: bash

   # Backend
   cd backend
   pyright

   # Frontend
   cd frontend
   pyright

Docstrings
~~~~~~~~~~

Utilisez le style **Google Docstrings** :

.. code-block:: python

   def ma_fonction(param1: str, param2: int) -> bool:
       """Courte description de la fonction.

       Description plus détaillée si nécessaire.

       Args:
           param1: Description du premier paramètre
           param2: Description du deuxième paramètre

       Returns:
           Description de ce qui est retourné

       Raises:
           ValueError: Quand param2 est négatif

       Examples:
           >>> ma_fonction("test", 42)
           True
       """
       if param2 < 0:
           raise ValueError("param2 doit être positif")
       return True

Tests
-----

Écrire des tests
~~~~~~~~~~~~~~~~

Tous les nouveaux codes doivent inclure des tests :

.. code-block:: python

   # backend/tests/test_ma_fonctionnalite.py
   import pytest
   from service.layers.application.ma_fonctionnalite import ma_fonction

   def test_ma_fonction_success():
       """Test le cas de succès."""
       result = ma_fonction("test", 42)
       assert result is True

   def test_ma_fonction_error():
       """Test le cas d'erreur."""
       with pytest.raises(ValueError):
           ma_fonction("test", -1)

Lancer les tests
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Backend
   cd backend
   pytest

   # Frontend
   cd frontend
   pytest

   # Avec coverage
   pytest --cov=service --cov-report=html

Coverage
~~~~~~~~

Le projet vise une couverture de tests de **80%** minimum.

Vérifiez la couverture :

.. code-block:: bash

   coverage report
   coverage html  # Génère un rapport HTML dans htmlcov/

Processus de contribution
--------------------------

1. Faire vos modifications
~~~~~~~~~~~~~~~~~~~~~~~~~~

Travaillez sur votre branche et committez régulièrement :

.. code-block:: bash

   git add .
   git commit -m "feat: ajout de la nouvelle fonctionnalité"

2. Vérifier la qualité
~~~~~~~~~~~~~~~~~~~~~~

Avant de pousser, vérifiez que tout passe :

.. code-block:: bash

   # Formatage
   ruff format .
   ruff check .

   # Type checking
   pyright

   # Tests
   pytest

   # Coverage
   coverage run -m pytest
   coverage report

3. Pousser votre branche
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git push origin feature/ma-nouvelle-fonctionnalite

4. Créer une Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~

- Allez sur GitHub et créez une Pull Request
- Décrivez clairement vos changements
- Référencez les issues concernées
- Ajoutez des captures d'écran si pertinent

5. Review et feedback
~~~~~~~~~~~~~~~~~~~~~

- Un mainteneur reviewera votre PR
- Répondez aux commentaires et faites les ajustements nécessaires
- Une fois approuvée, votre PR sera mergée

Convention de commits
---------------------

Nous suivons la convention `Conventional Commits <https://www.conventionalcommits.org/>`_ :

.. code-block:: text

   <type>(<scope>): <description>

   [corps optionnel]

   [footer optionnel]

Types
~~~~~

- ``feat``: Nouvelle fonctionnalité
- ``fix``: Correction de bug
- ``docs``: Documentation uniquement
- ``style``: Formatage (pas de changement de code)
- ``refactor``: Refactoring du code
- ``test``: Ajout ou modification de tests
- ``chore``: Tâches de maintenance

Exemples
~~~~~~~~

.. code-block:: bash

   git commit -m "feat(api): ajout endpoint GET /recipes/{id}"
   git commit -m "fix(frontend): correction affichage des tags"
   git commit -m "docs: ajout guide de contribution"
   git commit -m "test(backend): ajout tests pour data_cleaning"

Structure des Pull Requests
----------------------------

Titre
~~~~~

Utilisez la même convention que les commits :

.. code-block:: text

   feat(api): Ajout endpoint pour filtrer les recettes

Description
~~~~~~~~~~~

Incluez :

1. **Contexte** : Pourquoi ce changement est nécessaire
2. **Changements** : Ce qui a été modifié
3. **Tests** : Comment tester les changements
4. **Screenshots** : Si changements visuels (frontend)
5. **Breaking changes** : Si applicable

Exemple :

.. code-block:: markdown

   ## Contexte
   Les utilisateurs ont besoin de filtrer les recettes par tags.

   ## Changements
   - Ajout d'un paramètre `tags` à l'endpoint `/recipes`
   - Ajout de la logique de filtrage dans `application` layer
   - Ajout des tests unitaires et d'intégration

   ## Tests
   ```bash
   pytest tests/test_recipes_filtering.py
   ```

   ## Breaking changes
   Aucun

Checklist
~~~~~~~~~

.. code-block:: markdown

   - [ ] Tests ajoutés et passent
   - [ ] Documentation mise à jour
   - [ ] Code formaté avec Ruff
   - [ ] Type checking passe (Pyright)
   - [ ] Aucun conflit avec main
   - [ ] Commits suivent la convention

Revue de code
-------------

Que regarder
~~~~~~~~~~~~

Lors de la revue d'une PR, vérifiez :

- ✅ **Fonctionnalité** : Le code fait ce qu'il est censé faire
- ✅ **Tests** : Les tests couvrent les cas importants
- ✅ **Qualité** : Le code est lisible et maintenable
- ✅ **Performance** : Pas de problèmes de performance évidents
- ✅ **Sécurité** : Pas de vulnérabilités
- ✅ **Documentation** : Docstrings et commentaires appropriés

Feedback constructif
~~~~~~~~~~~~~~~~~~~~

Donnez un feedback :

- Constructif et respectueux
- Avec des suggestions concrètes
- En expliquant le "pourquoi"

Bonnes pratiques
----------------

Architecture
~~~~~~~~~~~~

- Respectez l'architecture en couches
- Ne créez pas de dépendances circulaires
- Gardez les layers indépendants

Code
~~~~

- Fonctions courtes et focalisées (< 20 lignes idéalement)
- Noms explicites pour variables et fonctions
- Évitez la duplication de code (DRY)
- Commentez le "pourquoi", pas le "quoi"

Tests
~~~~~

- Tests unitaires pour la logique métier
- Tests d'intégration pour les endpoints
- Tests de bout en bout pour les scénarios critiques
- Mockez les dépendances externes

Documentation
~~~~~~~~~~~~~

- Docstrings pour toutes les fonctions publiques
- README à jour
- Documentation Sphinx pour l'architecture
- Exemples de code

Git
~~~

- Commits atomiques et cohérents
- Messages de commit clairs
- Branches à courte durée de vie
- Rebase avant de merger (si besoin)

Questions ?
-----------

Si vous avez des questions :

1. Consultez la documentation
2. Cherchez dans les issues existantes
3. Créez une nouvelle issue avec le label ``question``
4. Contactez l'équipe sur [votre canal de communication]

Merci pour votre contribution ! 🎉
