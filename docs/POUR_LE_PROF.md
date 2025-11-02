# 📖 Documentation pour le Professeur

## Accès rapide à la documentation

### Option A : Documentation pré-générée (le plus simple) ⭐

Si la documentation HTML a été pré-générée et commitée dans le repo :

1. **Ouvrir le fichier HTML directement** :
   ```bash
   # macOS
   open docs/build/html/index.html

   # Linux
   xdg-open docs/build/html/index.html

   # Windows
   start docs\build\html\index.html
   ```

2. **Ou double-cliquer** sur le fichier `docs/build/html/index.html` dans votre explorateur de fichiers

Aucune installation requise ! La documentation s'ouvre directement dans votre navigateur.

---

### Option B : Générer la documentation localement

Si la documentation n'est pas pré-générée, vous pouvez la générer en quelques minutes :

#### Étape 1 : Installer les dépendances

```bash
# Backend
cd backend
pip install --group docs

# Frontend
cd ../frontend
pip install --group docs
```

#### Étape 2 : Générer la documentation

```bash
cd ../docs
make html
```

Sous Windows, utilisez `make.bat html` à la place de `make html`.

#### Étape 3 : Ouvrir dans le navigateur

```bash
# macOS
open build/html/index.html

# Linux
xdg-open build/html/index.html

# Windows
start build\html\index.html
```

**Temps total : ~2-3 minutes**

---

## 📚 Contenu de la documentation

La documentation complète inclut :

### 1. Introduction
- Présentation du projet Mange Ta Main
- Fonctionnalités principales
- Technologies utilisées (FastAPI, Streamlit, Docker)
- Architecture globale

### 2. Installation
- Guide d'installation complet
- Configuration backend et frontend
- Docker Compose
- Variables d'environnement

### 3. Architecture
- Architecture en couches (Clean Architecture)
- Layer API, Application, Domain, Infrastructure
- Architecture frontend (Pages, Composants)
- Flux de données
- Diagrammes explicatifs

### 4. API Reference
- Documentation complète de l'API REST
- Tous les endpoints détaillés
- Exemples de requêtes/réponses
- Modèles de données
- Gestion des erreurs

### 5. Backend
- Documentation auto-générée de tous les modules
- Docstrings détaillés
- Exemples d'utilisation

### 6. Frontend
- Documentation des pages Streamlit
- Documentation des composants
- Utilitaires et helpers

### 7. Guide de contribution
- Standards de code
- Processus de contribution
- Tests et coverage
- Bonnes pratiques

---

## 🎯 Navigation dans la documentation

Une fois ouverte dans le navigateur :

- **Navigation latérale** : Cliquez sur les sections pour naviguer
- **Recherche** : Utilisez la barre de recherche en haut à gauche
- **Liens internes** : Cliquez sur les liens pour naviguer entre les sections
- **Code source** : Liens [source] pour voir le code Python original
- **Index** : Liste alphabétique de tous les modules, classes, fonctions

---

## ❓ Problèmes courants

### "make: command not found" (Windows)

Sur Windows, utilisez `make.bat` à la place de `make` :

```bash
make.bat html
```

### "pip install --group docs" ne fonctionne pas

Si vous utilisez une ancienne version de pip, essayez :

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints myst-parser
```

### La documentation ne s'affiche pas correctement

Vérifiez que vous ouvrez bien le fichier `index.html` et non un autre fichier.
Le chemin complet est : `docs/build/html/index.html`

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Consultez [docs/README.md](README.md) pour plus de détails
2. Consultez [docs/QUICKSTART.md](QUICKSTART.md) pour un guide rapide
3. Contactez l'équipe du projet

---

## 🌐 Alternative : Documentation en ligne

Si une URL Read the Docs est fournie, vous pouvez simplement ouvrir cette URL dans votre navigateur sans rien installer.

---

**Bonne lecture ! 📚**
