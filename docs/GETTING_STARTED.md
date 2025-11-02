# 🚀 Guide de démarrage - Documentation Sphinx

Guide complet pour installer et utiliser Sphinx sur le projet Mange Ta Main.

## 📋 Table des matières

1. [Installation](#1-installation)
2. [Première génération](#2-première-génération)
3. [Explorer la documentation](#3-explorer-la-documentation)
4. [Documenter votre code](#4-documenter-votre-code)
5. [Mode développement](#5-mode-développement)
6. [Déploiement](#6-déploiement)

---

## 1. Installation

### Étape 1.1 : Installer les dépendances backend

```bash
cd backend
pip install --group docs
```

Ou avec uv :

```bash
uv pip install --group docs
```

Cela installe :
- sphinx
- sphinx-rtd-theme
- sphinx-autodoc-typehints
- myst-parser

### Étape 1.2 : Installer les dépendances frontend

```bash
cd ../frontend
pip install --group docs
```

### Vérification

```bash
python -c "import sphinx; print(sphinx.__version__)"
```

Devrait afficher quelque chose comme `7.x.x`

---

## 2. Première génération

### Étape 2.1 : Aller dans le dossier docs

```bash
cd ../docs
```

### Étape 2.2 : Générer la documentation HTML

**Sur macOS/Linux :**

```bash
make html
```

**Sur Windows :**

```bash
make.bat html
```

### Étape 2.3 : Vérifier la génération

Vous devriez voir :

```
Running Sphinx v7.x.x
building [html]: targets for X source files that are out of date
updating environment: [new config] X added, 0 changed, 0 removed
...
build succeeded.

The HTML pages are in build/html.
```

---

## 3. Explorer la documentation

### Étape 3.1 : Ouvrir dans le navigateur

**Sur macOS :**

```bash
open build/html/index.html
```

**Sur Linux :**

```bash
xdg-open build/html/index.html
```

**Sur Windows :**

```bash
start build\html\index.html
```

### Étape 3.2 : Parcourir les sections

La documentation contient :

- 📖 **Introduction** - Vue d'ensemble du projet
- 🔧 **Installation** - Guide d'installation complet
- 🏗️ **Architecture** - Architecture en couches
- 🔌 **API Reference** - Documentation de l'API REST
- 💻 **Backend** - Modules backend détaillés
- 🎨 **Frontend** - Composants frontend
- 🤝 **Contributing** - Guide de contribution

---

## 4. Documenter votre code

### Étape 4.1 : Ajouter un docstring à une fonction

Ouvrez un fichier Python et ajoutez :

```python
def ma_nouvelle_fonction(param: str) -> int:
    """Courte description de la fonction.

    Args:
        param: Description du paramètre

    Returns:
        Description du retour

    Examples:
        >>> ma_nouvelle_fonction("test")
        42
    """
    return 42
```

### Étape 4.2 : Régénérer la documentation

```bash
cd docs
make html
```

### Étape 4.3 : Vérifier dans le navigateur

Rafraîchissez la page dans votre navigateur pour voir vos changements.

---

## 5. Mode développement

### Étape 5.1 : Installer sphinx-autobuild

```bash
pip install sphinx-autobuild
```

### Étape 5.2 : Lancer le serveur avec auto-reload

```bash
cd docs
sphinx-autobuild source build/html
```

Ou avec ouverture automatique du navigateur :

```bash
sphinx-autobuild source build/html --open-browser
```

### Étape 5.3 : Développer

1. Ouvrez http://localhost:8000
2. Modifiez vos fichiers `.rst` ou vos docstrings Python
3. Sauvegardez
4. La page se recharge automatiquement ! 🎉

### Arrêter le serveur

Appuyez sur `Ctrl+C` dans le terminal

---

## 6. Déploiement

### Option A : Read the Docs

1. Créez un compte sur https://readthedocs.org
2. Connectez votre repository GitHub
3. Ajoutez un fichier `.readthedocs.yaml` :

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.11"

sphinx:
  configuration: docs/source/conf.py

python:
  install:
    - method: pip
      path: backend
      extra_requirements:
        - docs
    - method: pip
      path: frontend
      extra_requirements:
        - docs
```

4. Pushez sur GitHub
5. RTD build automatiquement ! 🚀

### Option B : GitHub Pages

1. Générez la documentation :

```bash
cd docs
make html
```

2. Copiez le contenu de `build/html/` vers une branche `gh-pages`

3. Activez GitHub Pages dans les settings du repo

### Option C : Serveur manuel

1. Générez la documentation :

```bash
make html
```

2. Copiez `build/html/` sur votre serveur web

3. Configurez votre serveur pour servir ces fichiers

---

## 🎯 Commandes essentielles

```bash
# Générer HTML
make html

# Nettoyer
make clean

# Régénérer complètement
make clean && make html

# Vérifier les liens
make linkcheck

# Vérifier la couverture
make coverage

# Générer PDF (nécessite LaTeX)
make latexpdf

# Mode développement
sphinx-autobuild source build/html
```

---

## 📝 Checklist de démarrage

- [ ] Dépendances installées (backend + frontend)
- [ ] Documentation générée (`make html`)
- [ ] Documentation visible dans le navigateur
- [ ] Au moins une fonction documentée avec un docstring
- [ ] Documentation régénérée avec succès
- [ ] Mode autobuild testé (optionnel)
- [ ] Lu le guide de contribution (`contributing.rst`)

---

## 🆘 Problèmes courants

### "make: command not found"

Sur Windows, utilisez `make.bat` à la place de `make`.

### "sphinx-build: command not found"

Installez les dépendances :

```bash
cd backend
pip install --group docs
```

### "Module not found" lors de la génération

Vérifiez que `sys.path` est bien configuré dans `docs/source/conf.py` :

```python
sys.path.insert(0, os.path.abspath('../../backend'))
sys.path.insert(0, os.path.abspath('../../frontend'))
```

### La documentation ne se met pas à jour

Nettoyez et régénérez :

```bash
make clean
make html
```

### Erreurs dans les docstrings

Assurez-vous de suivre le format Google Docstrings :

```python
def fonction(param: str) -> int:
    """Description.

    Args:
        param: Description

    Returns:
        Description
    """
```

Note : Ligne vide entre les sections, indentation de 4 espaces.

---

## 📚 Ressources supplémentaires

- **Guide complet** : Voir [docs/README.md](README.md)
- **Exemples de docstrings** : Voir [docs/DOCSTRING_EXAMPLES.md](DOCSTRING_EXAMPLES.md)
- **Documentation du projet** : Voir [DOCUMENTATION.md](../DOCUMENTATION.md)
- **Documentation Sphinx** : https://www.sphinx-doc.org/

---

## 🎓 Prochaines étapes

Une fois que vous maîtrisez les bases :

1. **Personnaliser le thème** - Modifiez `html_theme` dans `conf.py`
2. **Ajouter des extensions** - Explorez les extensions Sphinx
3. **Créer des sections personnalisées** - Ajoutez vos propres `.rst`
4. **Améliorer les docstrings** - Documentez plus de fonctions
5. **Déployer sur Read the Docs** - Rendez la doc publique

---

## ✅ Vous êtes prêt !

Vous savez maintenant :

- ✅ Installer Sphinx
- ✅ Générer la documentation
- ✅ Visualiser la documentation
- ✅ Documenter votre code
- ✅ Utiliser le mode développement
- ✅ Résoudre les problèmes courants

**Bonne documentation ! 📚✨**

---

**Questions ?** Consultez [docs/README.md](README.md) ou créez une issue sur GitHub.
