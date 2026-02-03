## Guide d’intégration – SmartCare ML

### 1. Structure fournie
```
SmartCare/
├── data/raw/…                         # CSV bruts (non modifiés)
├── artifacts/                        # Modèles exportés après entraînement
│   ├── feature_columns.json          # ordre exact des features
│   ├── metrics.json                  # MAE/MAPE/sMAPE baselines+ML
│   ├── gradient_boosting.joblib      # modèle principal (J+4)
│   └── random_forest.joblib
├── smartcare_model/                  # package réutilisable
│   ├── __init__.py
│   └── pipeline.py                   # pipeline complet (train + prédiction)
├── train_poc.py                      # lance un entraînement complet
└── predict_example.py                # exemple CLI de prédiction
```

### 2. Pipeline (package `smartcare_model`)

- `load_raw_dataframe()` : lit le CSV principal depuis `data/raw`, convertit les types (dates + floats).
- `build_feature_dataframe(df)` : applique toutes les transformations (target `y`, lags, rolling, features calendrier, multiplicateurs règles, one-hot météo/événements). *Pas de fuite temporelle : toutes les opérations utilisent uniquement les données dispo au jour J.*
- `train_models(train_ratio=0.8)` : split temporel, baselines, RandomForest + GradientBoosting. Les artefacts sont écrits dans `artifacts/` via `save_artifacts`.
- `load_artifacts(model_name="gradient_boosting")` : charge un modèle `.joblib` + la liste des features.
- `prepare_prediction_row(feature_df, feature_cols, target_date=None)` : récupère la dernière ligne exploitable (ou une date précise J) avec toutes les features alignées.
- `apply_overrides(row, feature_cols, meteo=None, event=None)` : permet au front de simuler une météo ou un événement différent (met toutes les colonnes `meteo_*`/`event_*` à 0 puis active celle choisie si elle existe). 
- `predict_from_features(row, model, feature_cols, safety_margin=0.10)` : renvoie `prediction` (J+4) et `prediction_safe` (= +10 % pour marge sécurité), ainsi que `date_J` utilisée.

### 3. Entraînement (à relancer si nouvelles données)
```bash
python train_poc.py
```
Ce script importe `train_models()` et recrée tout le dossier `artifacts/`. Le CLI affiche les métriques pour baselines et modèles ML. Aucun autre fichier n’est modifié.

### 4. Exemple d’intégration dans le dashboard
Dans `pages/prediction.py` (Streamlit ou autre) :
```python
from smartcare_model import (
    load_raw_dataframe,
    build_feature_dataframe,
    load_artifacts,
    prepare_prediction_row,
    apply_overrides,
    predict_from_features,
)

# Chargement unique au démarrage
RAW_DF = load_raw_dataframe()
FEATURE_DF = build_feature_dataframe(RAW_DF)
MODEL, FEATURE_COLS = load_artifacts()  # gradient_boosting par défaut

def predict(date=None, meteo=None, event=None):
    row = prepare_prediction_row(FEATURE_DF, FEATURE_COLS, target_date=date)
    row = apply_overrides(row, FEATURE_COLS, meteo=meteo, event=event)
    return predict_from_features(row, MODEL, FEATURE_COLS)
```
Puis, dans la page :
```python
result = predict(
    date=selected_date,
    meteo=selected_meteo,     # ex. "Pluie", "Canicule", "Gris"… (respecter noms colo)
    event=selected_event,     # ex. "Epidemie_grippe", "Canicule", "Aucun"
)
st.metric("Prédiction J+4", round(result["prediction"], 2))
st.metric("Prédiction sécurisée (+10%)", round(result["prediction_safe"], 2))
```

### 5. Remarques importantes
- **Colonnes catégorielles** : les noms de colonnes one-hot sont basés sur les valeurs REELLES du CSV. Exemple : `event_Epidemie_grippe`, `event_Vague_froid`, `event_Aucun`. Vérifier les options disponibles côté front (via `FEATURE_COLS`).
- **Métriques** : voir `artifacts/metrics.json`. Aujourd’hui, Gradient Boosting ~19 % MAPE (non conforme à l’objectif 10 %, mais baseline doc). 
- **Sécurité** : la marge de +10 % est appliquée dans `predict_from_features`. Si la logique doit changer (ex. marge variable), modifier uniquement ce point.
- **Ajout d’autres modèles** : il suffit de compléter le dict `models` dans `pipeline.train_models` (LightGBM, XGBoost, etc.) et le folder `artifacts/` contiendra les `.joblib` correspondants.
- **Nouvelles données** : déposer le nouveau CSV dans `data/raw/` (même nom ou contenant le hint `daily_hospital_context_2022-2024_generated.csv`). Relancer `train_poc.py` → artefacts mis à jour.
- **Utilisation hors POC** : si le front souhaite charger uniquement les artefacts sans recalculer les features à chaque requête, prévoir une étape de pré-calcul et stockage en base. Pour ce POC, le chargement complet reste simple et rapide (dataset < 2 ans).

### 6. Contenu à transmettre au dev front
- `smartcare_model/` (package)
- `artifacts/` (modèles + colonnes + métriques)
- `train_poc.py` (pour réentraînement local si besoin)
- `predict_example.py` (script de test manuel ou CI)
- Documentation : `docs/GUIDE_TECHNIQUE_PREDICTION.md` + ce `GUIDE_INTEGRATION_DEV.md`

Avec ces éléments, il peut reconstruire `pages/prediction.py` (et d’autres pages) en important directement le package. Aucun accès direct aux CSV n’est nécessaire pendant l’intégration si les artefacts sont fournis.
