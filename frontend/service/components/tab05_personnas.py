import streamlit as st


def render_listing_personas():

    st.header("🧑‍🍳 Segmentation des personas")
    st.caption("Classification comportementale des contributeurs selon leurs habitudes culinaires")
    st.markdown(
        """
Les utilisateurs disposent d’un socle de tags communs, dominé par `preparation`, `time-to-make` et `course`.
Ces tags structurent la recette (comment préparer), la contrainte temporelle (combien de temps) et le contexte
(quel type de plat). Leur omniprésence suggère une utilisation fonctionnelle et rationnelle du tagging.

Les tags `main-ingredient` et `dietary`, systématiquement dans le top 5, confirment :
- une recherche par ingrédients (logique “liste de courses”),
- des contraintes alimentaires (santé, allergies, préférences).

Ces dynamiques sont relativement homogènes… mais appliquées différemment selon le profil.

---

### 🧑‍🍳 Super Cookers

- Forte représentativité pour `preparation`, `course` et `main-ingredient`.
- Surpondération des contraintes alimentaires (`dietary`).
👉 Ces utilisateurs structurent leurs recettes en profondeur, optimisent les ingrédients et maîtrisent la complexité.

Ils font partie des personnes qui publient **le plus de recettes**, et leur usage des tags traduit une approche chef/technicité.

**👉 Recommandations produit :**
• Badges “chef expert” valorisant la complexité technique  
• Suggestions avancées d’accords d’ingrédients  
• Mode “pas à pas” premium avec minutage intelligent  
• Filtre avancé par type de plat + difficulté  

---

### ⚡ Quick Cookers

- `easy` apparaît dans leur top tags (4ᵉ position).
- `time-to-make` est crucial.
👉 Leur objectif : cuisiner vite, efficacement, sans complexité.

Ils publient un volume élevé de recettes simples, contribuant massivement au catalogue de “cuisine du quotidien”.

**👉 Recommandations produit :**
• Filtre express “<20 min” mis en avant  
• Bouton “Recette du quotidien”  
• Playlist hebdo “Batch cooking rapide”  
• Notion visuelle de “niveau d’effort”  

---

### 🍫 Sweet Lovers

- Importance de `main-ingredient` (logique avec chocolat, fruits, caramel…).
- `dietary` est également présent (sans gluten, vegan pâtisserie…).
👉 Ces personnes catégorisent via ingrédients sucrés et contraintes.

Ils publient fréquemment des recettes pâtissières — souvent très commentées et bien notées.

**👉 Recommandations produit :**
• Collections par ingrédient clé (chocolat, miel, caramel…)  
• Mode “pâtisserie débutant → expert”  
• Astuces de texture (cuisson, repos, température)  
• Badge “meilleurs desserts”  

---

### 💬 Talkative Tasters

- Surpondération de `preparation` et `time-to-make` (~6 %).
- Tagging transversal, non spécialisé.
👉 Ils commentent davantage qu’ils ne spécialisent leur cuisine.

Ils publient un volume conséquent, mais surtout animent la plateforme via retours détaillés.

**👉 Recommandations produit :**
• Badges d’engagement “critique culinaire”  
• Mise en avant des retours argumentés  
• Votes “utile / pas utile” sur commentaires  
• Flux d’activité social personnalisé  

---

### 🌍 Experimental Foodies

- Utilisation marquée de `main-ingredient` et `dietary`.
- Ils explorent arômes, substitutions, cuisines du monde.
👉 Profil curieux, testeur, innovant.

Ils publient beaucoup de recettes atypiques, enrichissant la diversité de la plateforme.

**👉 Recommandations produit :**
• Algorithme de découverte gustative “vous pourriez aimer…”  
• Challenges culinaires hebdomadaires  
• Mise en avant d’alternatives (sans gluten, fusion food…)  
• Mode “Random surprenant”  

---

### 🍽️ Everyday Cookers

- `preparation` et `time-to-make` surpondérés (~5.7 %).
- `dietary` est stable.
👉 Ils cuisinent pour la famille, dans des contraintes temporelles réalistes.

Ils publient un volume constant et prévisible, jouant un rôle de **fond de catalogue** stable.

**👉 Recommandations produit :**
• Liste de courses automatique  
• Menus équilibrés sur 5 jours  
• Astuces pour varier sans complexifier  
• Recettes familiales “testées par enfants”  

---

### 📌 Interprétation transversale

- Les tags structurent le **parcours de recherche** plus que l’identité culinaire.
- Le temps est un critère universel (experts, familles, pressés).
- Les ingrédients dirigent la découverte (logique d’achat).
- Les contraintes alimentaires deviennent mainstream.

---

### 🏆 Qui poste le plus de recettes ?

Les segments publiant le plus sont :
- **Super Cookers** (recettes complexes),
- **Quick Cookers** (fort volume, faible durée),
- **Sweet Lovers** (effet pâtisserie dopamine).

Ils tirent la croissance du catalogue.

Les profils les moins volumétriques (mais stratégiques) sont :
- **Talkative Tasters** (engagement via avis),
- **Experimental Foodies** (diversité culinaire),
- **Everyday Cookers** (stabilité).

---

### 🎯 Insights actionnables (produit / UX)

- Surpondérer les filtres **temps**, **régime**, **ingrédient** dans la navigation.
- Proposer des parcours personnalisés par persona (expertise, rapidité, découverte).
- Créer des défis saisonniers pour stimuler la publication.
- Gamifier les contributions de qualité.

---

### 🧠 Conclusion

Les tags ne révèlent pas seulement des goûts culinaires :
ils révèlent **comment** les utilisateurs publient.

Les plus gros contributeurs :
- maîtrisent les ingrédients,
- optimisent le temps,
- catégorisent finement,
- alimentent la profondeur du catalogue.

La plateforme n’est pas seulement un livre de recettes :
c’est un **système d’indexation culinaire optimisé**, piloté par ses contributeurs clés.
        """
    )
