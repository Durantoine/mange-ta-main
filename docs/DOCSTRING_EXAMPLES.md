# Exemples de Docstrings - Style Google

Ce document contient des exemples de docstrings pour différents cas d'usage.

## Table des matières

- [Fonctions simples](#fonctions-simples)
- [Fonctions avec valeurs par défaut](#fonctions-avec-valeurs-par-défaut)
- [Fonctions avec exceptions](#fonctions-avec-exceptions)
- [Fonctions avec types complexes](#fonctions-avec-types-complexes)
- [Classes](#classes)
- [Méthodes de classe](#méthodes-de-classe)
- [Propriétés](#propriétés)
- [Décorateurs](#décorateurs)
- [Générateurs](#générateurs)
- [Async/Await](#asyncawait)
- [Modules](#modules)

## Fonctions simples

```python
def add(a: int, b: int) -> int:
    """Additionne deux nombres entiers.

    Args:
        a: Premier nombre
        b: Deuxième nombre

    Returns:
        La somme de a et b

    Examples:
        >>> add(2, 3)
        5
        >>> add(-1, 1)
        0
    """
    return a + b
```

## Fonctions avec valeurs par défaut

```python
def greet(name: str, prefix: str = "Bonjour", punctuation: str = "!") -> str:
    """Génère un message de salutation personnalisé.

    Args:
        name: Nom de la personne à saluer
        prefix: Formule de salutation. Par défaut "Bonjour"
        punctuation: Ponctuation finale. Par défaut "!"

    Returns:
        Message de salutation formaté

    Examples:
        >>> greet("Alice")
        'Bonjour Alice!'
        >>> greet("Bob", prefix="Salut", punctuation=".")
        'Salut Bob.'
    """
    return f"{prefix} {name}{punctuation}"
```

## Fonctions avec exceptions

```python
def divide(a: float, b: float) -> float:
    """Divise deux nombres.

    Args:
        a: Numérateur
        b: Dénominateur

    Returns:
        Résultat de la division a/b

    Raises:
        ValueError: Si b est égal à zéro
        TypeError: Si a ou b ne sont pas des nombres

    Examples:
        >>> divide(10, 2)
        5.0
        >>> divide(10, 0)
        Traceback (most recent call last):
        ...
        ValueError: Division par zéro impossible

    Warning:
        Attention aux problèmes de précision avec les flottants
    """
    if b == 0:
        raise ValueError("Division par zéro impossible")
    return a / b
```

## Fonctions avec types complexes

```python
from typing import Dict, List, Optional, Union

def process_data(
    items: List[Dict[str, Union[int, str]]],
    filter_key: Optional[str] = None,
    min_value: int = 0
) -> Dict[str, List[str]]:
    """Traite une liste de dictionnaires et regroupe par catégorie.

    Cette fonction filtre les items selon une clé optionnelle et une valeur
    minimale, puis regroupe les résultats par catégorie.

    Args:
        items: Liste de dictionnaires contenant les données à traiter.
            Chaque dict doit avoir les clés 'category', 'value', et 'name'.
        filter_key: Clé optionnelle pour filtrer les résultats.
            Si None, aucun filtrage n'est appliqué.
        min_value: Valeur minimale pour filtrer les items. Les items
            avec une valeur inférieure sont exclus.

    Returns:
        Dictionnaire où les clés sont les catégories et les valeurs
        sont des listes de noms d'items dans cette catégorie.

    Raises:
        KeyError: Si un item n'a pas les clés requises
        TypeError: Si items n'est pas une liste

    Examples:
        >>> data = [
        ...     {'category': 'A', 'value': 10, 'name': 'item1'},
        ...     {'category': 'B', 'value': 20, 'name': 'item2'},
        ...     {'category': 'A', 'value': 5, 'name': 'item3'}
        ... ]
        >>> process_data(data, min_value=8)
        {'A': ['item1'], 'B': ['item2']}

    Note:
        Les items avec des valeurs égales à min_value sont inclus.
    """
    result: Dict[str, List[str]] = {}
    for item in items:
        if item['value'] >= min_value:
            category = item['category']
            if category not in result:
                result[category] = []
            result[category].append(item['name'])
    return result
```

## Classes

```python
class Recipe:
    """Représente une recette de cuisine.

    Une recette contient un nom, une durée de préparation,
    des ingrédients et des étapes de préparation.

    Attributes:
        name: Nom de la recette
        duration: Durée de préparation en minutes
        ingredients: Liste des ingrédients nécessaires
        steps: Liste des étapes de préparation

    Examples:
        Créer et utiliser une recette::

            >>> recipe = Recipe("Pâtes carbonara", 30)
            >>> recipe.add_ingredient("Pâtes", "500g")
            >>> recipe.add_step("Faire bouillir l'eau")
            >>> print(recipe.name)
            'Pâtes carbonara'

    Note:
        Les durées sont toujours en minutes.
    """

    def __init__(self, name: str, duration: int):
        """Initialise une nouvelle recette.

        Args:
            name: Nom de la recette
            duration: Durée de préparation en minutes

        Raises:
            ValueError: Si duration est négatif
        """
        if duration < 0:
            raise ValueError("La durée ne peut pas être négative")
        self.name = name
        self.duration = duration
        self.ingredients: List[tuple[str, str]] = []
        self.steps: List[str] = []

    def add_ingredient(self, name: str, quantity: str) -> None:
        """Ajoute un ingrédient à la recette.

        Args:
            name: Nom de l'ingrédient
            quantity: Quantité nécessaire (avec unité)

        Examples:
            >>> recipe = Recipe("Gâteau", 45)
            >>> recipe.add_ingredient("Farine", "250g")
            >>> recipe.add_ingredient("Sucre", "200g")
        """
        self.ingredients.append((name, quantity))

    def add_step(self, description: str) -> None:
        """Ajoute une étape de préparation.

        Args:
            description: Description de l'étape
        """
        self.steps.append(description)

    def __str__(self) -> str:
        """Retourne une représentation textuelle de la recette.

        Returns:
            Description formatée de la recette
        """
        return f"{self.name} ({self.duration} min)"

    def __repr__(self) -> str:
        """Retourne une représentation technique de la recette.

        Returns:
            Chaîne permettant de recréer l'objet
        """
        return f"Recipe(name={self.name!r}, duration={self.duration})"
```

## Méthodes de classe

```python
class DataProcessor:
    """Processeur de données avec cache.

    Attributes:
        _cache: Cache interne des données traitées
    """

    _cache: Dict[str, Any] = {}

    @classmethod
    def from_file(cls, filepath: str) -> 'DataProcessor':
        """Crée un processeur depuis un fichier.

        Factory method qui charge les données depuis un fichier
        et crée une instance configurée.

        Args:
            filepath: Chemin vers le fichier de données

        Returns:
            Instance de DataProcessor configurée

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si le format du fichier est invalide

        Examples:
            >>> processor = DataProcessor.from_file('data.csv')
            >>> processor.process()
        """
        # Implémentation...
        return cls()

    @staticmethod
    def validate_data(data: Dict[str, Any]) -> bool:
        """Valide le format des données.

        Méthode statique qui vérifie que les données respectent
        le format attendu.

        Args:
            data: Données à valider

        Returns:
            True si les données sont valides, False sinon

        Examples:
            >>> DataProcessor.validate_data({'key': 'value'})
            True
            >>> DataProcessor.validate_data({})
            False
        """
        return bool(data)
```

## Propriétés

```python
class Temperature:
    """Représente une température avec conversions automatiques.

    Attributes:
        _celsius: Température en Celsius (stockage interne)
    """

    def __init__(self, celsius: float):
        """Initialise avec une température en Celsius.

        Args:
            celsius: Température en degrés Celsius
        """
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        """Température en degrés Celsius.

        Returns:
            Température en °C
        """
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        """Définit la température en Celsius.

        Args:
            value: Nouvelle température en °C
        """
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        """Température en degrés Fahrenheit.

        Returns:
            Température en °F

        Examples:
            >>> temp = Temperature(0)
            >>> temp.fahrenheit
            32.0
            >>> temp = Temperature(100)
            >>> temp.fahrenheit
            212.0
        """
        return self._celsius * 9/5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        """Définit la température en Fahrenheit.

        Args:
            value: Nouvelle température en °F
        """
        self._celsius = (value - 32) * 5/9
```

## Décorateurs

```python
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar('T')

def cache_result(func: Callable[..., T]) -> Callable[..., T]:
    """Décorateur qui met en cache le résultat d'une fonction.

    Ce décorateur stocke les résultats des appels précédents
    et les réutilise pour les mêmes arguments.

    Args:
        func: Fonction à décorer

    Returns:
        Fonction décorée avec mise en cache

    Examples:
        >>> @cache_result
        ... def fibonacci(n: int) -> int:
        ...     if n < 2:
        ...         return n
        ...     return fibonacci(n-1) + fibonacci(n-2)
        >>> fibonacci(10)
        55

    Note:
        Le cache persiste durant toute la durée de vie du programme.

    Warning:
        N'utilisez pas ce décorateur sur des fonctions avec effets
        de bord ou dont les résultats changent dans le temps.
    """
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper
```

## Générateurs

```python
from typing import Iterator

def chunked(items: List[T], size: int) -> Iterator[List[T]]:
    """Divise une liste en chunks de taille fixe.

    Génère des sous-listes de taille `size` à partir de `items`.
    Le dernier chunk peut être plus petit si la liste n'est pas
    divisible par `size`.

    Args:
        items: Liste d'items à diviser
        size: Taille de chaque chunk

    Yields:
        Sous-listes de taille `size` (ou moins pour le dernier)

    Raises:
        ValueError: Si size <= 0

    Examples:
        >>> list(chunked([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
        >>> for chunk in chunked(range(10), 3):
        ...     print(chunk)
        [0, 1, 2]
        [3, 4, 5]
        [6, 7, 8]
        [9]

    Note:
        Cette fonction utilise un générateur pour économiser
        la mémoire avec de grandes listes.
    """
    if size <= 0:
        raise ValueError("size doit être positif")

    for i in range(0, len(items), size):
        yield items[i:i + size]
```

## Async/Await

```python
import asyncio
from typing import List

async def fetch_data(url: str) -> Dict[str, Any]:
    """Récupère des données depuis une URL de manière asynchrone.

    Args:
        url: URL à interroger

    Returns:
        Données JSON parsées

    Raises:
        aiohttp.ClientError: Si la requête échoue
        asyncio.TimeoutError: Si la requête dépasse le timeout

    Examples:
        >>> async def main():
        ...     data = await fetch_data('https://api.example.com/data')
        ...     print(data)
        >>> asyncio.run(main())

    Note:
        Cette fonction doit être appelée avec `await` dans un
        contexte asynchrone.
    """
    # Implémentation avec aiohttp...
    await asyncio.sleep(1)  # Simulation
    return {"status": "ok"}

async def fetch_multiple(urls: List[str]) -> List[Dict[str, Any]]:
    """Récupère des données depuis plusieurs URLs en parallèle.

    Utilise asyncio.gather pour exécuter toutes les requêtes
    simultanément, ce qui est beaucoup plus rapide que les
    requêtes séquentielles.

    Args:
        urls: Liste des URLs à interroger

    Returns:
        Liste des réponses dans le même ordre que les URLs

    Raises:
        aiohttp.ClientError: Si au moins une requête échoue

    Examples:
        >>> urls = ['https://api.example.com/1', 'https://api.example.com/2']
        >>> async def main():
        ...     results = await fetch_multiple(urls)
        ...     print(len(results))
        >>> asyncio.run(main())
        2

    Note:
        Toutes les requêtes sont lancées en parallèle pour
        maximiser les performances.
    """
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)
```

## Modules

Au début d'un fichier Python :

```python
"""Module de traitement de données de recettes.

Ce module fournit des fonctions et classes pour charger, nettoyer
et analyser des données de recettes de cuisine. Il fait partie de
la layer Application dans notre architecture en couches.

Le module gère :
- Le chargement des données depuis différentes sources (CSV, JSON)
- Le nettoyage et la normalisation des données
- La détection et suppression des outliers
- Les transformations de données pour l'analyse

Examples:
    Utilisation basique::

        from service.layers.application import data_cleaning
        df = data_cleaning.load_recipes('recipes.csv')
        df_clean = data_cleaning.remove_outliers(df)
        df_norm = data_cleaning.normalize_ids(df_clean, DataType.RECIPES)

    Avec un adapter personnalisé::

        adapter = CustomCSVAdapter()
        processor = DataCleaning(adapter)
        result = processor.process()

Attributes:
    DEFAULT_OUTLIER_FACTOR (float): Facteur par défaut pour la détection
        des outliers (valeur : 5.0)
    SUPPORTED_FORMATS (List[str]): Formats de fichiers supportés

See Also:
    service.layers.infrastructure.csv_adapter: Pour l'accès aux données
    service.layers.domain.mange_ta_main: Pour les modèles de données

Note:
    Ce module nécessite pandas >= 2.0.0 et numpy >= 1.20.0

Todo:
    * Ajouter le support pour les fichiers Parquet
    * Implémenter la détection automatique du type de données
    * Ajouter des métriques de qualité des données
"""

# Imports...
```

## Conseils généraux

### ✅ À faire

- Utilisez l'impératif : "Calcule", "Retourne", "Crée"
- Première ligne < 80 caractères
- Ajoutez des exemples concrets
- Documentez les exceptions
- Utilisez les type hints
- Ajoutez des notes et warnings quand nécessaire

### ❌ À éviter

- Répéter le nom de la fonction dans la description
- Descriptions vagues ("fait des trucs")
- Oublier de documenter les paramètres
- Oublier de documenter les exceptions
- Exemples qui ne marchent pas
- Documentation obsolète

### Format général

```python
def fonction():
    """Courte description (1 ligne).

    Description détaillée sur plusieurs lignes si nécessaire.
    Expliquez le contexte, les cas d'usage, etc.

    Args:
        param: Description

    Returns:
        Description

    Raises:
        Exception: Quand

    Examples:
        >>> fonction()
        result

    Note:
        Note importante

    Warning:
        Avertissement

    See Also:
        autre_fonction: Lien vers fonction liée
    """
```

## Validation des docstrings

Pour vérifier vos docstrings :

```bash
# Avec pydocstyle
pip install pydocstyle
pydocstyle votre_fichier.py

# Avec pylint
pylint --disable=all --enable=missing-docstring votre_fichier.py

# Avec la documentation Sphinx
cd docs
make coverage
```
