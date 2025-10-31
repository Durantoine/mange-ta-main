import streamlit as st

try:
    from ..components.sidebar import render_sidebar
except ImportError:  # pragma: no cover - fallback for standalone execution
    from components.sidebar import render_sidebar

render_sidebar()

st.title("💬 Conclusions de l'étude")

st.markdown(
    """
    Cette section présente les conclusions de l'analyse comportementale des contributeurs permettant d’identifier les utilisateurs les plus actifs, de comprendre leurs habitudes de publication et de comparer leurs performances avec l’ensemble de la communauté. L’objectif : éclairer les dynamiques d’engagement, détecter les profils moteurs et révéler les tendances structurantes qui influencent la création et la circulation des recettes sur la plateforme.
    """
)

st.markdown(
    """
### 🔎 Ce qui distingue réellement les plus gros contributeurs

L’analyse montre que le volume de publication n’est pas corrélé à :

- la longueur des recettes,
- leur richesse nutritionnelle,
- ou leur difficulté.

Ce sont plutôt des **dynamiques comportementales** qui différencient les segments les plus productifs :

✅ **Talkative Tasters** : publications régulières + commentaires massifs → ils génèrent une boucle d’engagement continue.

✅ **Super Cookers** : expertise, recherche de maîtrise → ils produisent davantage de recettes longues et structurées.

✅ **Experimental Foodies** : curiosité gastronomique, tests, itérations → leur exploration les pousse à publier plus souvent.

---

### 🚧 Segments moins prolifiques

⚠️ **Quick Cookers** : la cuisine “express” génère moins de diversité → moins de motifs pour publier.

⚠️ **Sweet Lovers** : publication déclenchée par l'inspiration sucrée → comportement saisonnier / ponctuel.

⚠️ **Everyday Cookers** : usage routinier, volume modéré et stable.

---

### 🧬 Les trois moteurs comportementaux du volume

Les contributeurs les plus actifs se distinguent par :

✅ l’envie de partager (**Talkative Tasters**)  
✅ la volonté de maîtriser (**Super Cookers**)  
✅ la curiosité exploratoire (**Experimental Foodies**)  

… et **pas** par :

❌ le thème des recettes  
❌ la catégorie de plat  
❌ la durée moyenne de préparation  

---

### 🎯 Synthèse stratégique (volume-driven)

Pour augmenter le nombre de recettes publiées, il faudra :

#### 🔥 Amplifier les moteurs naturels

- **Talkative Tasters** → challenges commentés, badges d’interaction
- **Super Cookers** → valorisation des recettes complexes et techniques
- **Experimental Foodies** → défis thématiques, “boîte mystère”

#### 🍪 Stimuler les segments sous-productifs

- **Quick Cookers** → template “Déposer votre recette en 30 secondes”
- **Everyday Cookers** → menus hebdo → incitation à publier
- **Sweet Lovers** → défis saisonniers (Pâques, Noël, Halloween)

---

### 🧠 Conclusion

Le profil qui contribue le plus **n’est pas** un expert technique pur.

C’est un utilisateur :

- engagé (**Talkative Tasters**),
- curieux (**Experimental Foodies**),
- perfectionniste (**Super Cookers**).

Ce sont eux qui :

✅ publient plus souvent  
✅ documentent davantage  
✅ alimentent la boucle communautaire  

👉 Pour soutenir la croissance, il faudra les **activer**, les **valoriser**, et les **fidéliser**.
"""
)
