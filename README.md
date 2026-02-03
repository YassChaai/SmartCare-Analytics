# 🏥 Smart Care Dashboard - Pitié-Salpêtrière

Dashboard interactif pour la gestion et la prédiction des ressources hospitalières.

## 📋 Fonctionnalités

### 🏠 Accueil
- KPIs en temps réel (occupation, admissions, urgences, personnel)
- Graphiques de synthèse
- Alertes et événements actifs

### 📊 Analyse Exploratoire
- Tendances temporelles (quotidien, hebdomadaire, mensuel)
- Matrice de corrélations
- Impact météo sur l'activité
- Statistiques descriptives complètes

### 🎯 Simulation de Scénarios
- **Épidémie** (Grippe/Covid)
- **Canicule** / Vague de froid
- **Grève du personnel**
- **Afflux massif** (accidents)
- **Périodes de vacances**
- **Scénario personnalisé**

Chaque simulation inclut :
- Projection sur N jours
- Évaluation des risques
- Besoins en ressources
- Estimation des coûts
- Recommandations d'actions

### 🔮 Prédiction
- **Prédiction simple** : Une journée spécifique
- **Prédiction multi-jours** : Jusqu'à 90 jours
- **Support modèle ML** : Intégration facile du modèle .pkl
- Intervalles de confiance
- Comparaison avec historique

### 💡 Recommandations Automatiques
- **Recommandations du jour** (priorités : Critique/Haute/Moyenne/Optimisation)
- **Planification hebdomadaire** (analyse par jour)
- **Optimisation stratégique** (capacités, RH, ROI)

## 🚀 Installation

### Prérequis
- Python 3.8+
- Environnement virtuel activé

### Installation des dépendances

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate  # Windows

# Installer les packages
pip install streamlit pandas numpy plotly scikit-learn seaborn openpyxl
```

## 💻 Utilisation

### Lancer le dashboard

```bash
streamlit run app.py
```

Le dashboard s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`

### Structure des fichiers

```
smart care/
├── app.py                          # Application principale
├── pages/
│   ├── __init__.py
│   ├── simulation.py               # Module simulation
│   ├── prediction.py               # Module prédiction
│   └── recommandations.py          # Module recommandations
├── model_prediction.pkl            # Modèle ML (à ajouter)
├── Jeu de données - Smart Care - daily_hospital_context_2022-2024_generated.csv
└── README.md
```

## 🤖 Intégration du Modèle ML

### Pour votre collègue qui développe le modèle :

1. **Format du modèle** : Fichier `.pkl` (pickle)

2. **Sauvegarder le modèle** :
```python
import pickle

# Après entraînement de votre modèle
with open('model_prediction.pkl', 'wb') as f:
    pickle.dump(model, f)
```

3. **Placer le fichier** : Copier `model_prediction.pkl` à la racine du projet

4. **Rechargement** : Le dashboard détectera automatiquement le modèle au démarrage

### Features attendues par le modèle :

#### Temporelles
- `jour_semaine` (str: Lundi-Dimanche)
- `jour_mois` (int: 1-31)
- `semaine_annee` (int: 1-53)
- `mois` (int: 1-12)
- `annee` (int)
- `saison` (str: Hiver/Printemps/Été/Automne)

#### Contextuelles
- `vacances_scolaires` (bool: 0/1)
- `temperature_moyenne` (float)
- `temperature_min` (float)
- `temperature_max` (float)
- `meteo_principale` (str)
- `evenement_special` (str)

#### Hospitalières (optionnel)
- `lits_total` (int)
- `nb_medecins_disponibles` (int)
- `nb_infirmiers_disponibles` (int)
- `nb_aides_soignants_disponibles` (int)

### Variables à prédire :
- `nombre_admissions`
- `nombre_passages_urgences`
- `taux_occupation_lits`

## 📊 Données

Le dashboard utilise le fichier CSV généré contenant :
- **1098 jours** de données (2022-2024)
- **27 variables** (temporelles, météo, hospitalières, événements)

### Principales variables :
- Admissions, passages urgences, hospitalisations
- Occupation lits (nb + taux)
- Personnel (médecins, infirmiers, aides-soignants)
- Météo (température, conditions)
- Événements spéciaux (épidémies, canicules, etc.)

## 🎨 Personnalisation

### Modifier les seuils d'alerte

Dans `app.py` :
```python
# Seuil critique occupation lits
if current_occupation > 0.85:  # Modifier ici

# Seuil minimum personnel
if current_staff < 0.85:  # Modifier ici
```

### Ajouter un nouveau scénario

Dans `pages/simulation.py`, ajouter dans la liste :
```python
scenario_type = st.selectbox(
    "Type de scénario",
    [
        # ... existants
        "🆕 Nouveau Scénario"
    ]
)
```

## 📈 Conseils pour la soutenance

### Structure de présentation suggérée (20 min)

1. **Contexte** (2 min)
   - Problématique Pitié-Salpêtrière
   - Objectifs du projet

2. **Données & Analyse** (3 min)
   - Montrer l'Analyse Exploratoire
   - Corrélations clés découvertes

3. **Démonstration Live** (8 min)
   - Scénario épidémie grippe (simulation)
   - Prédiction 30 jours
   - Recommandations automatiques

4. **Modèle Prédictif** (3 min)
   - Présenter le modèle ML
   - Résultats et performance

5. **Impact & Stratégie** (3 min)
   - ROI estimé
   - Plan déploiement

6. **Q&A** (5-10 min)

### Points forts à mettre en avant

✅ **Interface intuitive** et professionnelle
✅ **Simulations réalistes** avec projections détaillées
✅ **Prédictions actionnables** avec intervalles de confiance
✅ **Recommandations automatiques** priorisées
✅ **Modulaire** : Facile d'intégrer le modèle ML
✅ **Export des résultats** (CSV, TXT)

## 🐛 Dépannage

### Le dashboard ne se lance pas
```bash
# Vérifier l'environnement
pip list

# Réinstaller streamlit
pip install --upgrade streamlit
```

### Erreur de chargement CSV
- Vérifier que le fichier CSV est bien dans le dossier du projet
- Vérifier le nom du fichier (espaces, caractères spéciaux)

### Le modèle ML n'est pas détecté
- Vérifier que `model_prediction.pkl` est à la racine
- Cliquer sur "🔄 Recharger l'application" dans l'onglet Upload

## 📞 Support

Pour toute question pendant le projet :
- Vérifier ce README
- Consulter les commentaires dans le code
- Tester les exemples fournis

## 🎯 Checklist avant soutenance

- [ ] Dashboard se lance sans erreur
- [ ] Toutes les pages sont accessibles
- [ ] Simulations fonctionnent pour tous les scénarios
- [ ] Modèle ML intégré (si disponible)
- [ ] Graphiques s'affichent correctement
- [ ] Export CSV/TXT fonctionne
- [ ] Préparer 2-3 scénarios de démo
- [ ] Tester sur l'ordinateur de présentation

---

**Bonne chance pour la soutenance ! 🚀**

Projet réalisé dans le cadre du projet DATA - Promo 2026
