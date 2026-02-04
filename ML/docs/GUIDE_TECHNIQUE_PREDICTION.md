# Guide ML – Pipeline & Utilisation (Smart Care)

**But** : document unique qui explique la pipeline ML, sa structure, et comment l’utiliser / l’étendre sans modifier la logique métier.

---

## 1. Vue d’ensemble

Le pipeline prédit **J+4** le **nombre d’admissions** à partir des données du jour **J**. Le flux est :

1. **Chargement** du CSV brut.
2. **Feature engineering** (calendar, lags, règles métier, one-hot).
3. **Sélection** des features numériques.
4. **Split temporel** train/test.
5. **Baselines + modèles ML**.
6. **Évaluation** (MAE, MAPE, sMAPE).
7. **Sauvegarde** des artefacts (modèles + colonnes + métriques).
8. **Inférence** à partir d’une ligne de features alignée.

---

## 2. Structure ML (dossier `ml/`)

```
ml/
├── data/
│   └── raw/                         # CSV bruts
├── artifacts/                       # modèles + métriques + feature_columns
├── smartcare_model/                 # package ML (code)
│   ├── data/                        # chargement
│   ├── features/                    # engineering + selection
│   ├── training/                    # entrainement + baselines
│   ├── inference/                   # prediction
│   ├── evaluation/                  # metriques
│   ├── models/                      # registry des modeles
│   └── artifacts/                   # persistance
├── train_poc.py                     # lance l’entrainement complet
└── predict_example.py               # exemple CLI de prediction
```

---

## 3. Données attendues

- **Fichier CSV** dans `ml/data/raw/`.
- Le loader cherche un fichier dont le nom contient :
  `daily_hospital_context_2022-2024_generated.csv`.
- Les **nombres utilisent des virgules** pour les décimales : conversion en float faite au chargement.
- La colonne `date` est convertie au format datetime puis triée.

---

## 4. Pipeline de features (résumé)

- **Cible** : `y = nombre_admissions.shift(-4)`
- **Calendrier** : `is_weekend`, `is_holiday`, `veille_holiday`, `lendemain_holiday`
- **Lags** : `adm_lag_1,4,7,14,28`
- **Rolling** : `adm_roll_mean_7,14,28`, `adm_roll_std_7`
- **Diffs** : `adm_diff_1`, `adm_diff_7`
- **Règles métier** : multiplicateurs (jour, saison, vacances, canicule, événement)
- **Catégorielles** : one‑hot sur `meteo_principale` et `evenement_special`

Les lignes incomplètes (lags/rolling) sont supprimées avant entraînement.

---

## 5. Fonctions clés (API publique)

Le package expose une API stable via `smartcare_model` :

- `load_raw_dataframe()` : charge et nettoie le CSV.
- `build_feature_dataframe(df)` : applique toutes les transformations.
- `train_models(train_ratio=0.8)` : entraine baselines + modèles, sauvegarde les artefacts.
- `load_artifacts(model_name="gradient_boosting")` : charge modèle + `feature_columns.json`.
- `prepare_prediction_row(feature_df, feature_cols, target_date=None)` : sélectionne la ligne à prédire.
- `apply_overrides(row, feature_cols, meteo=None, event=None)` : override météo / événement.
- `predict_from_features(row, model, feature_cols, safety_margin=0.10)` : prediction + marge de sécurité.

---

## 6. Entrainement

Depuis la racine du repo :

```bash
python ml/train_poc.py
```

Ce script :
- entraine les baselines + modèles,
- évalue (MAE, MAPE, sMAPE),
- écrit les artefacts dans `ml/artifacts/`.

---

## 7. Inférence (exemple simple)

```python
from smartcare_model import (
    load_raw_dataframe,
    build_feature_dataframe,
    load_artifacts,
    prepare_prediction_row,
    apply_overrides,
    predict_from_features,
)

raw_df = load_raw_dataframe()
feature_df = build_feature_dataframe(raw_df)
model, feature_cols = load_artifacts()  # gradient_boosting par defaut

row = prepare_prediction_row(feature_df, feature_cols, target_date="2024-06-15")
row = apply_overrides(row, feature_cols, meteo="Pluie", event="Epidemie_grippe")
result = predict_from_features(row, model, feature_cols)
```

---

## 8. Artefacts et contrat d’interface

Dossier : `ml/artifacts/`
- `feature_columns.json` : **ordre canonique** des features (a respecter en inference).
- `metrics.json` : métriques par baseline / modèle.
- `gradient_boosting.joblib`, `random_forest.joblib` : modèles entrainés.

**Règle d’or** : toujours construire `X = df[feature_cols]` pour aligner l’ordre des features.

---

## 9. Métriques (pourquoi et comment)

- **MAE** : erreur absolue moyenne (en admissions).
- **MAPE** : erreur relative moyenne en %, lisible métier.
- **sMAPE** : version symétrique plus robuste quand `y` est faible.

La contrainte “≤ 10 %” doit être attachée explicitement à la métrique choisie (souvent MAPE).

---

## 10. Ajouter un nouveau modèle (ex. Prophet)

1. Implémenter un modèle respectant `fit(X, y)` / `predict(X)`.
2. L’ajouter dans `smartcare_model/models/registry.py` (dict `build_models`).
3. Relancer `python ml/train_poc.py` pour générer les artefacts.
4. Charger le modèle via `load_artifacts(model_name="...")`.

---

## 10bis. Modèle Prophet (prévisions multi-jours)

Le projet inclut un pipeline dédié **Prophet** pour la prévision **par date**
(pas J+4). Il est utilisé uniquement pour l’onglet multi-jours dans l’app.

### Entraînement

Depuis la racine du repo :

```bash
python tools/train_poc.py
```

Entraîner **uniquement Prophet** :

```bash
python tools/train_poc.py --prophet-only
```

Pour lancer un **grid tuning** simple :

```bash
python tools/train_poc.py --prophet-only --tune
```

Artefacts générés dans `ml/artifacts/` :
- `prophet.joblib` : export joblib (contient JSON + regressseurs)
- `metrics.json` : entrée `"prophet"` ajoutée

### Régressseurs

Prophet utilise :
- températures, indices, vacances (numériques)
- one‑hot météo / événements
- **vacances + événements** en tant que **holidays Prophet**
 - **régressseurs hospitaliers** (lits/occupation/personnel)

Hyperparamètres appliqués :
- `seasonality_mode="multiplicative"`
- `changepoint_prior_scale=0.1`
- `seasonality_prior_scale=10.0`
- saisonnalité mensuelle (période 30.5, fourier_order 5)

Pour les **valeurs futures**, le pipeline applique :
- moyennes mensuelles pour les variables numériques,
- mode mensuel pour la météo,
- événements = “Aucun” (fallback sur le mode global si “Aucun” absent).

---

## 11. Points d’attention

- **Fichier CSV introuvable** : vérifier `ml/data/raw` et le nom du fichier.
- **Alignement features/modèle** : toujours utiliser `feature_columns.json`.
- **Lags/rolling NaN** : normal en début de série, d’où le `dropna`.
- **Catégories météo/événements** : dépend des valeurs réelles du CSV (one‑hot).

---

## 12. Résumé opérationnel

- Entrainement : `python ml/train_poc.py`
- Artefacts : `ml/artifacts/`
- Inférence : `load_raw_dataframe → build_feature_dataframe → load_artifacts → prepare_prediction_row → predict_from_features`

Document unique à maintenir si la structure ou les features changent.
