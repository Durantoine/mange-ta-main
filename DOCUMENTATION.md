# 📚 Documentation Sphinx - Mange Ta Main

Documentation complète du projet avec Sphinx.

## 🚀 Démarrage rapide

### Installation

```bash
# Backend
cd backend
pip install --group docs

# Frontend
cd frontend
pip install --group docs
```

### Génération

```bash
cd docs
make html
open build/html/index.html  # macOS
```

Pour plus de détails, voir [docs/QUICKSTART.md](docs/QUICKSTART.md)

## 📖 Documentation disponible

### En ligne

Une fois générée, la documentation HTML se trouve dans `docs/build/html/`

### Structure

- **Introduction** - Présentation du projet
- **Installation** - Guide d'installation complet
- **Architecture** - Architecture en couches du projet
- **API Reference** - Documentation complète de l'API REST
- **Backend** - Documentation des modules backend
- **Frontend** - Documentation des modules frontend
- **Contributing** - Guide de contribution

## 📝 Comment documenter votre code

### Style de docstrings

Nous utilisons le **style Google Docstrings** :

```python
def ma_fonction(param1: str, param2: int = 10) -> bool:
    """Courte description (impératif : "Fait quelque chose").

    Description détaillée optionnelle sur plusieurs lignes.
    Explique le contexte, les cas d'usage, les comportements spéciaux.

    Args:
        param1: Description du premier paramètre
        param2: Description du deuxième paramètre avec valeur par défaut

    Returns:
        Description de ce qui est retourné

    Raises:
        ValueError: Quand param2 est négatif
        TypeError: Quand param1 n'est pas une chaîne

    Examples:
        >>> ma_fonction("test", 42)
        True
        >>> ma_fonction("hello")
        True

    Note:
        Notes importantes pour l'utilisateur.

    Warning:
        Avertissements sur l'utilisation.

    See Also:
        autre_fonction: Fonction similaire
        module.fonction: Fonction liée
    """
    if param2 < 0:
        raise ValueError("param2 doit être positif")
    return True
```

### Documenter une classe

```python
class MaClasse:
    """Courte description de la classe.

    Description détaillée du rôle et de l'utilisation de la classe.
    Expliquez quand et comment l'utiliser.

    Attributes:
        attribut_public: Description de l'attribut public
        autre_attribut: Description d'un autre attribut

    Examples:
        Créer une instance et l'utiliser::

            >>> obj = MaClasse("valeur")
            >>> result = obj.method()
            >>> print(result)
            'valeur'

    Note:
        Notes importantes sur l'utilisation de la classe.
    """

    def __init__(self, param: str):
        """Initialise une instance de MaClasse.

        Args:
            param: Description du paramètre d'initialisation
        """
        self.attribut_public = param

    def method(self) -> str:
        """Description de la méthode.

        Returns:
            Description du retour
        """
        return self.attribut_public
```

### Documenter un module

Au début de chaque fichier Python :

```python
"""Titre du module (court).

Description détaillée du module, son rôle dans l'application,
et quand l'utiliser.

Ce module fournit des fonctionnalités pour...

Examples:
    Utilisation basique du module::

        from mon_module import ma_fonction
        result = ma_fonction(param)

    Utilisation avancée::

        from mon_module import MaClasse
        obj = MaClasse()
        obj.method()

Note:
    Notes importantes sur le module.

Attributes:
    CONSTANTE_MODULE: Description de la constante
"""

# Imports...
```

## 🛠️ Commandes utiles

```bash
# Générer la documentation HTML
cd docs
make html

# Mode développement avec auto-reload
pip install sphinx-autobuild
sphinx-autobuild source build/html --open-browser

# Générer en PDF (nécessite LaTeX)
make latexpdf

# Nettoyer les fichiers générés
make clean

# Vérifier les liens cassés
make linkcheck

# Vérifier la couverture de documentation
make coverage

# Voir toutes les commandes
make help
```

## 📂 Structure du projet docs/

```
docs/
├── source/                      # Sources de la documentation
│   ├── conf.py                  # Configuration Sphinx
│   ├── index.rst                # Page d'accueil
│   ├── introduction.rst         # Introduction
│   ├── installation.rst         # Installation
│   ├── architecture.rst         # Architecture
│   ├── api.rst                  # API REST
│   ├── contributing.rst         # Guide de contribution
│   ├── backend/                 # Documentation backend
│   │   └── index.rst
│   ├── frontend/                # Documentation frontend
│   │   └── index.rst
│   ├── _static/                 # Fichiers statiques (CSS, images)
│   └── _templates/              # Templates personnalisés
├── build/                       # Documentation générée (gitignored)
│   └── html/                    # HTML généré
├── Makefile                     # Pour Linux/macOS
├── make.bat                     # Pour Windows
├── README.md                    # Guide complet
└── QUICKSTART.md                # Guide de démarrage rapide
```

## 🎨 Extensions Sphinx activées

- **sphinx.ext.autodoc** - Documentation automatique depuis le code
- **sphinx.ext.napoleon** - Support Google/NumPy docstrings
- **sphinx.ext.viewcode** - Liens vers le code source
- **sphinx.ext.intersphinx** - Liens vers autres documentations
- **sphinx.ext.todo** - Support des TODOs
- **sphinx.ext.coverage** - Couverture de documentation
- **sphinx_autodoc_typehints** - Meilleur support des type hints
- **myst_parser** - Support Markdown (.md)

## 📋 Checklist pour documenter un nouveau module

- [ ] Ajouter un docstring en haut du fichier (module-level)
- [ ] Documenter toutes les fonctions publiques
- [ ] Documenter toutes les classes publiques
- [ ] Documenter les méthodes `__init__` des classes
- [ ] Ajouter des exemples d'utilisation avec `Examples:`
- [ ] Documenter les exceptions levées avec `Raises:`
- [ ] Ajouter des notes/warnings si nécessaire
- [ ] Créer/mettre à jour le fichier `.rst` correspondant
- [ ] Ajouter le module au `toctree` approprié
- [ ] Régénérer la documentation : `make html`
- [ ] Vérifier le résultat dans le navigateur

## 🔍 Qualité de la documentation

### Vérifier la couverture

```bash
cd docs
make coverage
# Voir le rapport dans build/coverage/python.txt
```

### Vérifier les liens

```bash
make linkcheck
# Voir le rapport dans build/linkcheck/output.txt
```

### Standards de qualité

Chaque fonction/classe publique doit avoir :

1. ✅ Un docstring descriptif
2. ✅ Description de tous les paramètres (`Args:`)
3. ✅ Description du retour (`Returns:`)
4. ✅ Liste des exceptions (`Raises:`)
5. ✅ Au moins un exemple (`Examples:`)
6. ✅ Type hints Python

## 🎯 Bonnes pratiques

### Docstrings

- Utilisez l'impératif ("Calcule", pas "Calcul" ou "Calculer")
- Première ligne : description courte (< 80 caractères)
- Ligne vide entre résumé et description détaillée
- Ajoutez des exemples concrets
- Documentez les effets de bord
- Mentionnez les valeurs par défaut importantes

### Exemples

- Utilisez `>>>` pour les exemples interactifs (doctest)
- Montrez les cas d'usage typiques
- Incluez les imports nécessaires
- Montrez les erreurs possibles

### Organisation

- Un fichier `.rst` par grande section
- Utilisez `automodule` pour la documentation automatique
- Groupez les modules liés ensemble
- Créez une hiérarchie logique avec `toctree`

## 🆘 Dépannage

### "Module not found" lors de la génération

Vérifiez `sys.path` dans `source/conf.py` :

```python
sys.path.insert(0, os.path.abspath('../../backend'))
sys.path.insert(0, os.path.abspath('../../frontend'))
```

### Warnings sur les docstrings

- Assurez-vous de suivre exactement le format Google
- Vérifiez l'indentation (4 espaces)
- Ligne vide entre les sections
- Format exact : `Args:`, `Returns:`, `Raises:`, `Examples:`

### Build échoue

```bash
# Nettoyer et reconstruire
make clean
make html

# Voir les erreurs détaillées
make html SPHINXOPTS="-v"
```

### Liens intersphinx ne marchent pas

Vérifiez la configuration dans `conf.py` :

```python
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}
```

## 📚 Ressources

### Documentation officielle

- [Sphinx](https://www.sphinx-doc.org/)
- [Google Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Napoleon Extension](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)

### Tutoriels

- [Sphinx Tutorial](https://www.sphinx-doc.org/en/master/tutorial/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Documenting Python Code](https://realpython.com/documenting-python-code/)

### Exemples de projets

- [Requests](https://requests.readthedocs.io/)
- [Django](https://docs.djangoproject.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pandas](https://pandas.pydata.org/docs/)

## 🤝 Contribution

Lors de votre contribution, n'oubliez pas de :

1. Documenter tout nouveau code
2. Mettre à jour la documentation existante si nécessaire
3. Vérifier que `make html` fonctionne sans erreur
4. Vérifier la couverture : `make coverage`
5. Inclure des exemples d'utilisation

Voir [docs/source/contributing.rst](docs/source/contributing.rst) pour plus de détails.

## 📞 Support

- **Issues** : Créez une issue sur GitHub
- **Documentation** : Consultez [docs/README.md](docs/README.md)
- **Quickstart** : Voir [docs/QUICKSTART.md](docs/QUICKSTART.md)

---

**Projet** : Mange Ta Main
**Version** : 0.1.0
**Documentation générée avec** : Sphinx + Read the Docs Theme
