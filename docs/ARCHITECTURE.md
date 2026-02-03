# 🏗️ Architecture de l'Application Smart Care

## 📁 Structure du Projet

```
smart care/
├── app.py                          # 🏠 Application principale avec navigation
├── pages/                          # 📄 Modules des pages
│   ├── __init__.py                 # Initialisation du package
│   ├── simulation.py               # 🎯 Simulations de scénarios
│   ├── prediction.py               # 🔮 Prédictions ML
│   └── recommandations.py          # 💡 Recommandations automatiques
├── docs/                           # 📚 Documentation
│   ├── GUIDE_STREAMLIT.md          # Guide Streamlit
│   ├── ARCHITECTURE.md             # Ce fichier
│   └── GUIDE_UTILISATION.md        # Guide utilisateur
├── Jeu de données - Smart Care - *.csv  # 📊 Données
├── model_prediction.pkl            # 🤖 Modèle ML (à créer)
├── Pipfile                         # 📦 Dépendances
├── Pipfile.lock                    # 🔒 Versions exactes
└── README.md                       # 📖 Documentation principale
```

## 🎯 Flux de Données

```
┌─────────────────┐
│   CSV Files     │  ← Données historiques (2022-2024)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   load_data()   │  ← Chargement et nettoyage (@st.cache_data)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ st.session_state│  ← Stockage en mémoire (DataFrame)
│      .df         │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌───────┐│
│  │ Accueil  │  │ Analyse  │  │ Simu  ││
│  └──────────┘  └──────────┘  └───────┘│
│  ┌──────────┐  ┌──────────┐           │
│  │Prédiction│  │  Recomm  │           │
│  └──────────┘  └──────────┘           │
│                                         │
└─────────────────────────────────────────┘
         │
         ↓
┌─────────────────┐
│  Visualisation  │  ← Graphiques, Tableaux, KPIs
│   (Browser)     │
└─────────────────┘
```

## 📄 Description des Fichiers

### 1. app.py (Application Principale) 🏠

**Rôle** : Point d'entrée de l'application, gère la navigation et contient 2 pages intégrées.

**Sections principales** :

```python
# 1. CONFIGURATION
st.set_page_config(...)  # Configuration de la page

# 2. CSS PERSONNALISÉ
st.markdown("""<style>...</style>""")  # Styles custom

# 3. FONCTIONS DE CHARGEMENT
@st.cache_data
def load_data():  # Charge et nettoie les données CSV
    ...

@st.cache_resource
def load_ml_model():  # Charge le modèle ML si disponible
    ...

# 4. CHARGEMENT INITIAL
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# 5. NAVIGATION
page = st.navigation([
    st.Page(...),  # Définition des pages
])

# 6. PAGE ACCUEIL
if selected_page == "🏠 Accueil":
    # KPIs
    # Graphiques de synthèse
    # Alertes

# 7. PAGE ANALYSE EXPLORATOIRE
elif selected_page == "📊 Analyse Exploratoire":
    # Filtres
    # 4 Onglets d'analyse
```

**Fonctions clés** :

| Fonction | Rôle | Décorateur |
|----------|------|------------|
| `load_data()` | Charge le CSV, nettoie les données, convertit les types | `@st.cache_data` |
| `load_ml_model()` | Charge le fichier .pkl du modèle ML | `@st.cache_resource` |

**Données utilisées** :
- DataFrame principal : `st.session_state.df`
- Colonnes principales : `date`, `nombre_admissions`, `nombre_passages_urgences`, `taux_occupation_lits`, personnel, météo

---

### 2. pages/simulation.py (Simulations) 🎯

**Rôle** : Simule différents scénarios d'affluence hospitalière.

**Scénarios disponibles** :

| Scénario | Emoji | Impact Principal | Durée typique |
|----------|-------|-----------------|---------------|
| Épidémie | 🦠 | +30% admissions, +20% urgences | 30-90 jours |
| Canicule | 🔥 | +40% urgences, +15% admissions | 5-15 jours |
| Vague de froid | ❄️ | +25% urgences, +10% admissions | 7-20 jours |
| Grève | 🚫 | -40% personnel disponible | 1-10 jours |
| Afflux massif | 🚨 | +100% urgences immédiates | 1-3 jours |
| Vacances | 📅 | -15% admissions programmées | 14-60 jours |
| Personnalisé | 🎯 | Réglages manuels | Variable |

**Architecture du code** :

```python
# 1. INTERFACE DE CONFIGURATION
scenario_type = st.selectbox(...)  # Choix du scénario
start_date = st.date_input(...)    # Date de début
duration = st.slider(...)           # Durée en jours
intensity = st.slider(...)          # Intensité (0-1)

# 2. PARAMÈTRES D'IMPACT (sliders)
impact_admissions = st.slider(...)  # % d'augmentation admissions
impact_urgences = st.slider(...)    # % d'augmentation urgences
impact_personnel = st.slider(...)   # % de personnel disponible
impact_lits = st.slider(...)        # Pression sur les lits

# 3. CALCUL DE LA BASELINE (référence)
baseline = {
    'admissions': df_recent['nombre_admissions'].mean(),
    'urgences': df_recent['nombre_passages_urgences'].mean(),
    'occupation': df_recent['taux_occupation_lits'].mean(),
    'personnel': ...
}

# 4. PROJECTION SUR N JOURS
dates = pd.date_range(start_date, periods=duration)
for i, date in enumerate(dates):
    progression = np.sin(i * np.pi / duration)  # Courbe progressive
    admissions_proj = baseline + (impact * progression)
    # ...

# 5. VISUALISATION
fig = px.line(...)  # Graphiques des projections
st.plotly_chart(fig)

# 6. ANALYSE DES RISQUES
if occupation_max > 0.85:
    risk_level = "🔴 CRITIQUE"
elif occupation_max > 0.75:
    risk_level = "🟠 MODÉRÉ"
else:
    risk_level = "🟢 FAIBLE"

# 7. CALCUL DES BESOINS
beds_needed = max(0, occupation_proj - capacity)
staff_needed = max(0, required_staff - available_staff)

# 8. RECOMMANDATIONS
recommendations = generate_recommendations(risk_level, scenario_type, metrics)

# 9. EXPORT
csv = projection_df.to_csv()
st.download_button("📥 Télécharger CSV", csv)
```

**Données en sortie** :
- DataFrame de projection : `projection_df` avec colonnes date, admissions, urgences, occupation, personnel
- Métriques de risque : niveau de risque, besoins supplémentaires, coûts estimés
- Liste de recommandations : actions prioritaires

---

### 3. pages/prediction.py (Prédictions) 🔮

**Rôle** : Prédire l'activité hospitalière future avec un modèle ML ou statistique.

**3 Onglets** :

#### Onglet 1 : Prédiction Simple (1 jour)

```python
# 1. INPUTS
date = st.date_input("Date à prédire")
temperature = st.slider("Température", -10, 40, 20)
meteo = st.selectbox("Météo", ["Ensoleillé", "Nuageux", ...])
event = st.selectbox("Événement", ["Aucun", "Épidémie", ...])

# 2. PRÉDICTION
if model_available:
    # Utilise le modèle ML
    features = prepare_features_for_model(date, temp, meteo, event)
    predictions = model.predict(features)
else:
    # Utilise le modèle statistique de secours
    predictions = predict_with_stats(df, date, temp, meteo, event)

# 3. AFFICHAGE RÉSULTATS
st.metric("Admissions prévues", predictions['admissions'])
st.metric("Passages urgences", predictions['urgences'])
st.metric("Taux occupation", predictions['occupation'])
```

#### Onglet 2 : Prédiction Multi-jours (1-90 jours)

```python
# 1. SÉLECTION PLAGE
start_date = st.date_input("Date début")
end_date = st.date_input("Date fin")

# 2. OPTIONS AVANCÉES
with st.expander("Options avancées"):
    consider_seasonality = st.checkbox("Prendre en compte la saisonnalité")
    consider_trend = st.checkbox("Inclure la tendance")
    confidence_level = st.slider("Niveau de confiance", 0.8, 0.99, 0.95)

# 3. GÉNÉRATION DES PRÉDICTIONS
dates = pd.date_range(start_date, end_date)
predictions_list = []
for date in dates:
    pred = predict_with_stats(df, date, ...)
    predictions_list.append(pred)

# 4. VISUALISATION
fig = px.line(predictions_df, x='date', y=['admissions', 'urgences'])
st.plotly_chart(fig)

# 5. ANALYSE
critical_days = predictions_df[predictions_df['occupation'] > 0.85]
st.warning(f"⚠️ {len(critical_days)} jours critiques détectés")

# 6. EXPORT
csv = predictions_df.to_csv()
st.download_button("📥 Télécharger", csv)
```

#### Onglet 3 : Upload Modèle ML

```python
# 1. UPLOAD
uploaded_file = st.file_uploader("Choisir un fichier .pkl")

if uploaded_file:
    # 2. SAUVEGARDE
    with open("model_prediction.pkl", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # 3. CONFIRMATION
    st.success("✅ Modèle importé avec succès")
    
    # 4. RECHARGEMENT
    if st.button("🔄 Recharger l'application"):
        st.rerun()

# DOCUMENTATION POUR LE COLLÈGUE
st.info("""
**Format attendu du modèle :**
- Fichier pickle (.pkl)
- Méthode predict() disponible
- Features attendues : [liste]
""")
```

**Fonctions de prédiction** :

```python
def predict_with_stats(df, date, temperature, meteo, event):
    """
    Modèle statistique de secours (fonctionne sans ML)
    """
    # 1. Filtrer les jours similaires
    similar_days = df[
        (df['jour_semaine'] == date.weekday()) &
        (df['saison'] == get_season(date))
    ]
    
    # 2. Calculer la baseline
    baseline_admissions = similar_days['nombre_admissions'].mean()
    baseline_urgences = similar_days['nombre_passages_urgences'].mean()
    
    # 3. Appliquer les ajustements contextuels
    if event == "Épidémie":
        baseline_admissions *= 1.4
        baseline_urgences *= 1.2
    elif meteo == "Canicule":
        baseline_urgences *= 1.25
    # ...
    
    # 4. Ajouter de la variabilité
    admissions = np.random.normal(baseline_admissions, std)
    
    return {
        'admissions': admissions,
        'urgences': urgences,
        'occupation': occupation
    }

def prepare_features_for_model(date, temp, meteo, event):
    """
    Prépare les features pour le modèle ML
    """
    return {
        'jour_semaine': date.weekday(),
        'jour_mois': date.day,
        'mois': date.month,
        'saison': get_season(date),
        'temperature_moyenne': temp,
        'meteo_principale': meteo,
        'evenement_special': event,
        # ...
    }
```

---

### 4. pages/recommandations.py (Recommandations) 💡

**Rôle** : Générer des recommandations automatiques basées sur l'analyse des données.

**3 Onglets** :

#### Onglet 1 : Recommandations du Jour

```python
# 1. ANALYSE DE LA SITUATION ACTUELLE
last_7_days = df.tail(7)
last_30_days = df.tail(30)

current_occupation = last_7_days['taux_occupation_lits'].mean()
current_staff = last_7_days['taux_couverture_personnel'].mean()
trend_admissions = (last_7_days - last_30_days).mean()

# 2. AFFICHAGE DE L'ÉTAT
col1, col2, col3 = st.columns(3)
with col1:
    if current_occupation > 0.85:
        st.markdown("🔴 Occupation CRITIQUE")
    elif current_occupation > 0.75:
        st.markdown("🟠 Occupation ÉLEVÉE")
    else:
        st.markdown("🟢 Occupation NORMALE")

# 3. GÉNÉRATION DES RECOMMANDATIONS
recommendations = generate_recommendations(
    occ=current_occupation,
    staff=current_staff,
    trend_occ=trend_occupation,
    trend_adm=trend_admissions,
    events=current_events
)

# 4. AFFICHAGE PAR PRIORITÉ
for priority in ['CRITIQUE', 'HAUTE', 'MOYENNE', 'OPTIMISATION']:
    recs = [r for r in recommendations if r['priority'] == priority]
    for rec in recs:
        with st.expander(f"{priority} - {rec['title']}"):
            st.write(rec['description'])
            st.write(f"**Impact** : {rec['impact']}")
            st.write(f"**Délai** : {rec['delay']}")
            for action in rec['actions']:
                st.write(f"• {action}")
```

#### Onglet 2 : Planification Hebdomadaire

```python
# 1. ANALYSE PAR JOUR DE LA SEMAINE
weekly_stats = df.groupby('jour_semaine').agg({
    'nombre_admissions': ['mean', 'std'],
    'nombre_passages_urgences': ['mean', 'std'],
    'taux_occupation_lits': ['mean', 'max']
})

# 2. VISUALISATION
fig = px.bar(weekly_stats, x=days, y='admissions_mean', error_y='admissions_std')
st.plotly_chart(fig)

# 3. RECOMMANDATIONS PAR JOUR
for day in ['Lundi', 'Mardi', ...]:
    with st.expander(f"📅 {day}"):
        if is_low_activity_day(day):
            st.write("• Programmer interventions chirurgicales non-urgentes")
            st.write("• Effectuer maintenance préventive")
        elif is_high_activity_day(day):
            st.write("• Renforcer personnel aux urgences")
            st.write("• Anticiper besoins en lits")
```

#### Onglet 3 : Optimisation Stratégique

```python
# 1. ANALYSE DES TENDANCES MENSUELLES
monthly_trends = df.groupby(df['date'].dt.to_period('M')).agg({
    'nombre_admissions': 'sum',
    'nombre_passages_urgences': 'sum'
})

fig = px.line(monthly_trends, title="Évolution mensuelle")
st.plotly_chart(fig)

# 2. ANALYSE SAISONNIÈRE
seasonal_patterns = df.groupby('saison').agg({
    'taux_occupation_lits': 'mean',
    'nombre_admissions': 'mean'
})

st.bar_chart(seasonal_patterns)

# 3. IMPACT DES ÉVÉNEMENTS
events_impact = df.groupby('evenement_special').agg({
    'nombre_admissions': 'mean',
    'nombre_passages_urgences': 'mean'
})

st.table(events_impact)

# 4. OPTIMISATION DE LA CAPACITÉ
avg_occupation = df['taux_occupation_lits'].mean()
max_occupation = df['taux_occupation_lits'].max()
critical_days = len(df[df['taux_occupation_lits'] > 0.85])
critical_pct = (critical_days / len(df)) * 100

if critical_pct > 10:
    st.warning(f"""
    ⚠️ **Capacité insuffisante**
    - Jours critiques : {critical_pct:.1f}%
    - Recommandation : Augmenter capacité de {calculate_needed_beds()} lits
    """)

# 5. CALCULATEUR ROI
st.subheader("💰 Calculateur de Retour sur Investissement")
reduction_days = st.slider("Réduction jours critiques (%)", 0, 100, 50)
cost_per_bed = 500  # €/jour
savings = reduction_days * critical_days * cost_per_bed
st.metric("Économies estimées", f"{savings:,.0f} €")
```

**Fonction de génération de recommandations** :

```python
def generate_recommendations(occ, staff, trend_occ, trend_adm, events):
    """
    Génère des recommandations basées sur les métriques actuelles
    """
    recommendations = []
    
    # RÈGLE 1 : Occupation critique
    if occ > 0.85:
        recommendations.append({
            'priority': 'CRITIQUE',
            'title': 'Saturation des lits - Plan blanc à envisager',
            'description': f"Taux d'occupation {occ*100:.1f}% > 85%",
            'impact': "Réduction refus d'admission, amélioration qualité",
            'delay': 'Immédiat (0-4h)',
            'actions': [
                'Activer plan blanc niveau 1',
                'Identifier lits mobilisables',
                'Accélérer sorties patients stabilisés'
            ]
        })
    
    # RÈGLE 2 : Personnel insuffisant
    if staff < 0.85:
        recommendations.append({
            'priority': 'CRITIQUE',
            'title': 'Couverture personnel insuffisante',
            'description': f"Taux de couverture {staff*100:.1f}% < 85%",
            'impact': "Qualité des soins, charge de travail",
            'delay': 'Immédiat (0-24h)',
            'actions': [
                'Rappel personnel de garde',
                'Annuler congés non-prioritaires',
                'Contact agences intérim'
            ]
        })
    
    # RÈGLE 3 : Tendance à la hausse
    if trend_occ > 0.05:  # Augmentation de 5%
        recommendations.append({
            'priority': 'HAUTE',
            'title': 'Tendance occupation à la hausse',
            'description': f"Augmentation de {trend_occ*100:.1f}% détectée",
            'impact': "Anticipation saturation",
            'delay': 'Court terme (24-72h)',
            'actions': [
                'Préparer plan de contingence',
                'Augmenter veille quotidienne',
                'Prévoir ressources additionnelles'
            ]
        })
    
    # RÈGLE 4 : Événements spéciaux
    if 'Epidemie' in events:
        recommendations.extend(get_event_specific_actions('Epidemie'))
    
    # RÈGLE 5 : Conditions favorables (optimisation)
    if occ < 0.65 and staff > 0.90:
        recommendations.append({
            'priority': 'OPTIMISATION',
            'title': 'Conditions favorables - Opportunités',
            'description': "Faible occupation et personnel suffisant",
            'impact': "Efficience opérationnelle",
            'delay': 'Moyen terme (1-2 semaines)',
            'actions': [
                'Programmer interventions reportées',
                'Formation du personnel',
                'Maintenance préventive équipements'
            ]
        })
    
    return recommendations
```

---

## 🔄 Interactions Entre Modules

```
┌─────────────┐
│   app.py    │  ← Charge les données une fois
└──────┬──────┘
       │
       ├→ st.session_state.df (DataFrame partagé)
       │
       ↓
┌─────────────────────────────────────┐
│  Toutes les pages accèdent à :     │
│  - st.session_state.df              │
│  - st.session_state.model (si ML)   │
└─────────────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────┐
│ Pages individuelles (autonomes) :   │
│ - simulation.py                      │
│ - prediction.py                      │
│ - recommandations.py                 │
└──────────────────────────────────────┘
```

**Principe** : 
- `app.py` charge les données et les stocke dans `st.session_state.df`
- Chaque page accède à `st.session_state.df` directement
- Aucune page ne modifie le DataFrame original
- Les pages sont **indépendantes** et **autonomes**

---

## 🎨 Système de Style

**CSS Personnalisé dans app.py** :

```python
st.markdown("""
    <style>
    /* Alertes colorées */
    .alert-box {
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-red {
        background-color: #fee;
        border-left: 5px solid #f00;
    }
    .alert-orange {
        background-color: #fff3cd;
        border-left: 5px solid #ff8800;
    }
    .alert-green {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    
    /* Cartes de métriques */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)
```

**Utilisation** :

```python
# Alerte rouge
st.markdown("""
    <div class="alert-box alert-red">
        🔴 <strong>CRITIQUE</strong><br>
        Occupation > 85%
    </div>
""", unsafe_allow_html=True)

# Carte métrique
st.markdown("""
    <div class="metric-card">
        <h3>1250</h3>
        <p>Admissions ce mois</p>
    </div>
""", unsafe_allow_html=True)
```

---

## 🧪 Tests et Débogage

### Messages de débogage

```python
import streamlit as st

# Activer le mode debug
DEBUG = True

if DEBUG:
    st.write("DEBUG - DataFrame shape:", df.shape)
    st.write("DEBUG - Colonnes:", df.columns.tolist())
    st.write("DEBUG - Valeurs manquantes:", df.isnull().sum())
```

### Expander pour les détails techniques

```python
with st.expander("🔍 Détails techniques"):
    st.write("**Dernière mise à jour** :", df['date'].max())
    st.write("**Nombre de lignes** :", len(df))
    st.dataframe(df.describe())
```

---

## 📊 Performance et Optimisation

### 1. Cache des Données

```python
@st.cache_data  # ← Ne charge qu'une fois
def load_data():
    return pd.read_csv("data.csv")

# Utilisé partout sans recharger
df = load_data()
```

### 2. Cache du Modèle ML

```python
@st.cache_resource  # ← Pour les objets non-sérialisables
def load_ml_model():
    with open("model.pkl", "rb") as f:
        return pickle.load(f)
```

### 3. Session State

```python
# Charge une seule fois
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# Réutilise dans toutes les pages
df = st.session_state.df
```

---

## 🚀 Points Clés à Retenir

1. **app.py** = Point d'entrée + Navigation + 2 pages intégrées
2. **pages/*.py** = Modules indépendants accessibles via navigation
3. **st.session_state.df** = DataFrame partagé entre toutes les pages
4. **@st.cache_data** = Évite de recharger les données à chaque interaction
5. **Chaque page est autonome** = Pas de dépendances entre pages
6. **CSS personnalisé** = Améliore l'apparence
7. **Modularité** = Facile d'ajouter/modifier des pages

---

## 🎓 Pour Aller Plus Loin

1. Ouvrez `app.py` et identifiez les 5 sections principales
2. Ouvrez `pages/simulation.py` et tracez le flux de données
3. Modifiez une couleur dans le CSS et observez le changement
4. Ajoutez un `st.write("DEBUG")` pour comprendre l'exécution

**Astuce** : Utilisez `st.write()` partout pour déboguer ! C'est votre meilleur ami en Streamlit 🐛
