# 🚀 Guide Streamlit pour Débutants

## Qu'est-ce que Streamlit ?

Streamlit est un framework Python qui permet de créer des **applications web interactives** en quelques lignes de code, sans connaître HTML/CSS/JavaScript.

## 📋 Concepts de Base

### 1. Structure d'une Application Streamlit

```python
import streamlit as st

# Tout le code s'exécute de haut en bas à chaque interaction
st.title("Mon Application")  # Titre
st.write("Hello World!")     # Texte simple

# Widgets interactifs
nombre = st.slider("Choisir un nombre", 0, 100)
st.write(f"Vous avez choisi: {nombre}")
```

### 2. Principe de Fonctionnement ⚡

**IMPORTANT** : Le script entier se réexécute **à chaque interaction** !

```python
import streamlit as st

# Ce code s'exécute à chaque fois qu'un widget change
st.write("Script réexécuté !")

nombre = st.slider("Valeur", 0, 10)
# Quand le slider bouge → tout le script se relance
```

### 3. Le Cache (@st.cache_data)

Pour éviter de recharger les données à chaque fois :

```python
import streamlit as st
import pandas as pd

@st.cache_data  # ← Met en cache le résultat
def load_data():
    # Cette fonction ne s'exécute qu'une seule fois
    return pd.read_csv("data.csv")

# Première fois : charge le CSV
# Fois suivantes : utilise le cache
df = load_data()
```

**Dans notre app** :
```python
@st.cache_data
def load_data():
    # Charge une seule fois, même si la page se recharge 100 fois
    df = pd.read_csv(...)
    return df
```

### 4. Session State (st.session_state)

Pour **conserver des valeurs** entre les réexécutions :

```python
import streamlit as st

# Initialiser une variable qui persiste
if 'compteur' not in st.session_state:
    st.session_state.compteur = 0

# Bouton qui incrémente
if st.button("Cliquer"):
    st.session_state.compteur += 1

st.write(f"Nombre de clics: {st.session_state.compteur}")
```

**Dans notre app** :
```python
if 'df' not in st.session_state:
    st.session_state.df = load_data()
# Le DataFrame reste en mémoire entre les pages
```

## 🎨 Widgets Principaux

### Affichage

```python
st.title("Titre Principal")
st.header("En-tête")
st.subheader("Sous-titre")
st.write("Texte normal")
st.markdown("**Gras** _italique_")
st.code("x = 42", language="python")
```

### Métriques (KPI)

```python
st.metric(
    label="Admissions",
    value=245,
    delta=+12,  # Affiche +12 en vert
    delta_color="normal"  # "normal", "inverse", "off"
)
```

### Entrées Utilisateur

```python
# Texte
nom = st.text_input("Votre nom")

# Nombre
age = st.number_input("Âge", min_value=0, max_value=120)

# Slider
temperature = st.slider("Température", -10.0, 40.0, 20.0)

# Sélection
choix = st.selectbox("Méteo", ["Ensoleillé", "Nuageux", "Pluvieux"])

# Cases à cocher
actif = st.checkbox("Activer")

# Date
date = st.date_input("Choisir une date")

# Bouton
if st.button("Valider"):
    st.write("Bouton cliqué !")
```

### Layout (Organisation)

#### Colonnes

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("KPI 1", 100)

with col2:
    st.metric("KPI 2", 200)

with col3:
    st.metric("KPI 3", 300)
```

#### Onglets

```python
tab1, tab2, tab3 = st.tabs(["📊 Graphiques", "📋 Tableau", "⚙️ Config"])

with tab1:
    st.write("Contenu onglet 1")

with tab2:
    st.write("Contenu onglet 2")
```

#### Expander (Accordéon)

```python
with st.expander("Cliquer pour voir les détails"):
    st.write("Contenu caché par défaut")
```

#### Sidebar (Barre latérale)

```python
with st.sidebar:
    st.title("Navigation")
    page = st.radio("Page", ["Accueil", "Analyse", "Prédiction"])
```

### Graphiques

```python
import plotly.express as px

# Créer un graphique Plotly
fig = px.line(df, x='date', y='valeur')

# Afficher dans Streamlit
st.plotly_chart(fig, use_container_width=True)
```

### Tableaux

```python
import pandas as pd

df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})

# Tableau simple
st.dataframe(df)

# Tableau avec mise en forme
st.dataframe(df.style.highlight_max(axis=0))

# Tableau statique
st.table(df)
```

## 🎯 Structure Multi-Pages

**Nouvelle méthode Streamlit (celle utilisée dans notre app)** :

```
mon_projet/
├── app.py              # Page principale
└── pages/
    ├── 1_analyse.py    # Page 1
    ├── 2_prediction.py # Page 2
    └── 3_simulation.py # Page 3
```

**app.py** :
```python
import streamlit as st

st.set_page_config(page_title="Mon App", layout="wide")

page = st.navigation([
    st.Page("pages/analyse.py", title="📊 Analyse"),
    st.Page("pages/prediction.py", title="🔮 Prédiction"),
])

page.run()
```

**pages/analyse.py** :
```python
import streamlit as st

st.title("Page d'Analyse")
# Contenu de la page
```

## 💡 Bonnes Pratiques

### 1. Utiliser le Cache

```python
# ❌ Mauvais : Recharge à chaque interaction
def load_data():
    return pd.read_csv("big_file.csv")

# ✅ Bon : Charge une seule fois
@st.cache_data
def load_data():
    return pd.read_csv("big_file.csv")
```

### 2. Initialiser Session State

```python
# Au début de l'app
if 'data' not in st.session_state:
    st.session_state.data = load_data()
```

### 3. Organiser le Code

```python
# ✅ Bon : Fonctions réutilisables
def display_kpis(df):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", df['value'].sum())
    # ...

# Appel simple
display_kpis(st.session_state.df)
```

### 4. Gérer les Erreurs

```python
try:
    df = pd.read_csv("data.csv")
    st.success("✅ Données chargées avec succès")
except FileNotFoundError:
    st.error("❌ Fichier non trouvé")
    st.stop()  # Arrête l'exécution
```

## 🎨 CSS Personnalisé

Vous pouvez ajouter du CSS pour personnaliser l'apparence :

```python
st.markdown("""
    <style>
    .big-font {
        font-size: 30px !important;
        color: red;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Texte en rouge</p>', unsafe_allow_html=True)
```

**Dans notre app** :
```python
st.markdown("""
    <style>
    .alert-box {
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-red {
        background-color: #fee;
        border-left: 5px solid #f00;
    }
    </style>
""", unsafe_allow_html=True)
```

## 🔄 Cycle de Vie d'une Page

1. **Utilisateur ouvre l'app** → Script s'exécute
2. **Utilisateur clique sur un bouton** → Script se réexécute
3. **Utilisateur change un slider** → Script se réexécute
4. **Utilisateur change de page** → Nouveau script s'exécute

```python
import streamlit as st

# S'exécute à CHAQUE interaction
st.write("Début du script")

# Widget
value = st.slider("Valeur", 0, 10)

# S'exécute à CHAQUE interaction
st.write(f"Valeur actuelle: {value}")
st.write("Fin du script")
```

## 🚀 Commandes Essentielles

```bash
# Lancer l'app
streamlit run app.py

# Lancer sur un port spécifique
streamlit run app.py --server.port 8502

# Désactiver le mode "wide"
streamlit run app.py --theme.base "dark"

# Avec pipenv
pipenv run streamlit run app.py
```

## 📊 Exemple Complet

```python
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration
st.set_page_config(page_title="Dashboard", layout="wide")

# Cache
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

# Chargement
df = load_data()

# Titre
st.title("🏥 Mon Dashboard")

# Sidebar
with st.sidebar:
    st.header("Filtres")
    date_min = st.date_input("Date début")
    date_max = st.date_input("Date fin")

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total", len(df))
with col2:
    st.metric("Moyenne", f"{df['value'].mean():.1f}")
with col3:
    st.metric("Max", df['value'].max())

# Graphique
fig = px.line(df, x='date', y='value', title="Évolution")
st.plotly_chart(fig, use_container_width=True)

# Tableau
st.dataframe(df)
```

## 🔗 Ressources

- **Documentation officielle** : https://docs.streamlit.io
- **Galerie d'exemples** : https://streamlit.io/gallery
- **Cheat Sheet** : https://cheat-sheet.streamlit.app

## 🎓 Exercice : Comprendre le Code de Notre App

Ouvrez `app.py` et identifiez :

1. **Cache** : Ligne avec `@st.cache_data` → Évite de recharger les données
2. **Session State** : `st.session_state.df` → Conserve le DataFrame
3. **Navigation** : `st.navigation([...])` → Création du menu
4. **Colonnes** : `st.columns(4)` → Layout en 4 colonnes
5. **Métriques** : `st.metric(...)` → Affichage des KPIs
6. **Graphiques** : `st.plotly_chart(...)` → Affichage Plotly

Chaque interaction (changement de page, filtre, etc.) réexécute le script, mais :
- Les données restent en cache (`@st.cache_data`)
- Les variables persistent (`st.session_state`)

C'est ça la magie de Streamlit ! 🎩✨
