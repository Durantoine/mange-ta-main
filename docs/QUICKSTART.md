# Guide de démarrage rapide - Documentation Sphinx

Ce guide vous permet de générer rapidement la documentation du projet.

## 🚀 Démarrage en 3 étapes

### 1. Installer les dépendances

Depuis la racine du projet :

```bash
# Backend
cd backend
pip install --group docs

# Frontend
cd ../frontend
pip install --group docs
```

### 2. Générer la documentation

```bash
cd ../docs
make html
```

### 3. Visualiser la documentation

```bash
# macOS
open build/html/index.html

# Linux
xdg-open build/html/index.html

# Windows
start build\html\index.html
```

## 🔥 Mode développement avec auto-reload

Pour travailler sur la documentation avec rechargement automatique :

```bash
# Installer sphinx-autobuild
pip install sphinx-autobuild

# Lancer le serveur
cd docs
sphinx-autobuild source build/html --open-browser
```

Ouvrez http://localhost:8000 - la page se rechargera automatiquement à chaque modification !

## 📝 Ajouter de la documentation à votre code

### Pour une fonction

```python
def ma_fonction(param: str) -> int:
    """Courte description.

    Args:
        param: Description du paramètre

    Returns:
        Description du retour

    Examples:
        >>> ma_fonction("test")
        42
    """
    return 42
```

### Pour une classe

```python
class MaClasse:
    """Courte description de la classe.

    Attributes:
        attribut: Description de l'attribut

    Examples:
        >>> obj = MaClasse()
        >>> obj.method()
    """

    def __init__(self):
        """Initialise l'instance."""
        self.attribut = "valeur"
```

### Pour un module

Au début du fichier :

```python
"""Nom du module.

Description du module et de son rôle.

Examples:
    Comment utiliser ce module::

        from module import fonction
        resultat = fonction()
"""
```

## 🎯 Commandes utiles

```bash
# Générer la documentation HTML
make html

# Générer en PDF (nécessite LaTeX)
make latexpdf

# Nettoyer les fichiers générés
make clean

# Vérifier les liens cassés
make linkcheck

# Voir toutes les commandes disponibles
make help
```

## 📚 Structure de la documentation

- `source/index.rst` - Page d'accueil
- `source/introduction.rst` - Introduction au projet
- `source/installation.rst` - Guide d'installation
- `source/architecture.rst` - Architecture du projet
- `source/api.rst` - Documentation de l'API REST
- `source/backend/` - Documentation du backend
- `source/frontend/` - Documentation du frontend
- `source/contributing.rst` - Guide de contribution

## ⚙️ Configuration

La configuration se trouve dans `source/conf.py`.

### Extensions activées

- `sphinx.ext.autodoc` - Documentation automatique depuis le code
- `sphinx.ext.napoleon` - Support Google/NumPy docstrings
- `sphinx.ext.viewcode` - Liens vers le code source
- `sphinx.ext.intersphinx` - Liens vers d'autres documentations
- `sphinx_autodoc_typehints` - Meilleur support des type hints
- `myst_parser` - Support Markdown

### Thème

Le thème utilisé est `sphinx_rtd_theme` (Read the Docs).

## 🆘 Problèmes courants

### "Module not found"

Vérifiez que `sys.path` est correctement configuré dans `conf.py` :

```python
sys.path.insert(0, os.path.abspath('../../backend'))
sys.path.insert(0, os.path.abspath('../../frontend'))
```

### Docstring warnings

Assurez-vous de suivre le format Google :

```python
def fonction(param: str) -> int:
    """Description.

    Args:
        param: Description

    Returns:
        Description
    """
```

### Build échoue

Nettoyez et reconstruisez :

```bash
make clean && make html
```

## 📖 Ressources

- [Documentation Sphinx](https://www.sphinx-doc.org/)
- [Google Docstrings Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)

## ✅ Checklist pour documenter un nouveau module

- [ ] Ajouter un docstring au module (en haut du fichier)
- [ ] Documenter toutes les fonctions publiques
- [ ] Documenter toutes les classes publiques
- [ ] Ajouter des exemples d'utilisation
- [ ] Créer/mettre à jour le fichier `.rst` correspondant
- [ ] Régénérer la documentation : `make html`
- [ ] Vérifier le résultat dans le navigateur

Bon courage ! 🚀
