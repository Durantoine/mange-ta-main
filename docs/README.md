# Documentation Mange Ta Main

Ce dossier contient la documentation Sphinx du projet Mange Ta Main.

## Installation des dépendances

Installez les dépendances de documentation dans les projets backend et frontend :

```bash
# Backend
cd backend
pip install --group docs

# Frontend
cd frontend
pip install --group docs
```

Ou avec uv :

```bash
# Backend
cd backend
uv pip install --group docs

# Frontend
cd frontend
uv pip install --group docs
```

## Générer la documentation

### HTML (recommandé)

```bash
cd docs
make html
```

La documentation sera générée dans `docs/build/html/`.

Pour visualiser :

```bash
# macOS
open build/html/index.html

# Linux
xdg-open build/html/index.html

# Windows
start build\html\index.html
```

### Autres formats

```bash
# PDF (nécessite LaTeX)
make latexpdf

# ePub
make epub

# Texte simple
make text

# Man pages
make man
```

## Voir tous les formats disponibles

```bash
make help
```

## Mode développement avec auto-reload

Pour un développement interactif avec rechargement automatique :

```bash
pip install sphinx-autobuild
sphinx-autobuild source build/html
```

Puis ouvrez http://localhost:8000 dans votre navigateur.

## Nettoyer les fichiers générés

```bash
make clean
```

## Structure de la documentation

```
docs/
├── source/
│   ├── conf.py              # Configuration Sphinx
│   ├── index.rst            # Page d'accueil
│   ├── introduction.rst     # Introduction au projet
│   ├── installation.rst     # Guide d'installation
│   ├── architecture.rst     # Architecture du projet
│   ├── api.rst             # Documentation de l'API REST
│   ├── contributing.rst     # Guide de contribution
│   ├── backend/            # Documentation du backend
│   │   └── index.rst
│   ├── frontend/           # Documentation du frontend
│   │   └── index.rst
│   ├── _static/            # Fichiers statiques (CSS, images)
│   └── _templates/         # Templates personnalisés
├── build/                   # Documentation générée (ignoré par git)
├── Makefile                # Makefile pour Linux/macOS
└── make.bat                # Script pour Windows
```

## Documenter votre code

### Docstrings Python (Style Google)

Utilisez le style Google Docstrings pour documenter vos fonctions :

```python
def ma_fonction(param1: str, param2: int) -> bool:
    """Courte description de la fonction.

    Description plus détaillée si nécessaire, qui peut s'étendre
    sur plusieurs lignes.

    Args:
        param1: Description du premier paramètre
        param2: Description du deuxième paramètre. Les descriptions
            peuvent aussi s'étendre sur plusieurs lignes.

    Returns:
        Description de ce qui est retourné. Peut être sur plusieurs
        lignes également.

    Raises:
        ValueError: Quand param2 est négatif
        TypeError: Quand param1 n'est pas une chaîne

    Examples:
        >>> ma_fonction("test", 42)
        True
        >>> ma_fonction("hello", -1)
        Traceback (most recent call last):
        ...
        ValueError: param2 doit être positif

    Note:
        Notes importantes sur l'utilisation de la fonction.

    Warning:
        Avertissements pour les utilisateurs.
    """
    if param2 < 0:
        raise ValueError("param2 doit être positif")
    return True
```

### Docstrings pour les classes

```python
class MaClasse:
    """Courte description de la classe.

    Description détaillée de la classe, son rôle, son utilisation.

    Attributes:
        attribut1: Description de l'attribut 1
        attribut2: Description de l'attribut 2

    Examples:
        >>> obj = MaClasse("value")
        >>> obj.method()
        'result'
    """

    def __init__(self, param: str):
        """Initialise la classe.

        Args:
            param: Description du paramètre d'initialisation
        """
        self.attribut1 = param

    def method(self) -> str:
        """Description de la méthode.

        Returns:
            Description du retour
        """
        return self.attribut1
```

### Docstrings pour les modules

Au début de chaque fichier Python :

```python
"""Nom du module.

Description détaillée du module, son rôle dans l'application,
et comment l'utiliser.

Examples:
    Exemples d'utilisation du module::

        from module import fonction
        result = fonction()
"""
```

## Ajouter un nouveau fichier à la documentation

1. Créez un fichier `.rst` dans `docs/source/` :

```bash
touch docs/source/mon_nouveau_sujet.rst
```

2. Ajoutez-le au `toctree` dans `index.rst` :

```rst
.. toctree::
   :maxdepth: 2

   introduction
   installation
   mon_nouveau_sujet
```

3. Générez la documentation :

```bash
cd docs
make html
```

## Autodoc - Documentation automatique depuis le code

Pour documenter automatiquement un module Python :

```rst
Backend API
===========

.. automodule:: service.layers.api.mange_ta_main
   :members:
   :undoc-members:
   :show-inheritance:
```

Options disponibles :

- `:members:` - Inclure tous les membres
- `:undoc-members:` - Inclure les membres sans docstring
- `:show-inheritance:` - Montrer l'héritage des classes
- `:private-members:` - Inclure les membres privés
- `:special-members:` - Inclure les méthodes spéciales (`__init__`, etc.)

## Vérifier la documentation

### Vérifier les liens cassés

```bash
make linkcheck
```

### Vérifier la couverture de la documentation

```bash
make coverage
```

Cela génère un rapport montrant quelles fonctions/classes n'ont pas de docstring.

## Configuration avancée

La configuration se trouve dans `docs/source/conf.py`.

### Changer le thème

Modifiez dans `conf.py` :

```python
html_theme = 'sphinx_rtd_theme'  # Read the Docs theme (par défaut)
# html_theme = 'alabaster'       # Thème Alabaster
# html_theme = 'furo'            # Thème Furo (moderne)
```

### Ajouter des extensions

Dans `conf.py`, ajoutez à la liste `extensions` :

```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx_autodoc_typehints',
    'myst_parser',
    # Ajoutez vos extensions ici
]
```

## Ressources

- [Documentation officielle Sphinx](https://www.sphinx-doc.org/)
- [Guide des docstrings Google](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Sphinx Napoleon (Google/NumPy style)](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
- [Read the Docs](https://readthedocs.org/)

## Problèmes courants

### Import errors lors de la génération

Si Sphinx ne trouve pas vos modules, vérifiez `sys.path` dans `conf.py` :

```python
import sys
import os
sys.path.insert(0, os.path.abspath('../../backend'))
sys.path.insert(0, os.path.abspath('../../frontend'))
```

### Warnings sur les docstrings

Assurez-vous que vos docstrings suivent le format Google :

```python
def fonction(param: str) -> int:
    """Description.

    Args:
        param: Description

    Returns:
        Description
    """
```

### Build échoue avec des erreurs

Nettoyez et reconstruisez :

```bash
make clean
make html
```
