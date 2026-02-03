# Guide technique – Prédiction des volumes hospitaliers (Smart Care)

**Public** : Professeur / évaluation – Spé Data & IA  
**Objectif** : Document de référence pour développer et évaluer le POC de prédiction (J+4).  
**Contrainte** : Erreur ≤ 10 %, surestimation préférée (sécurité), priorité à la performance brute.

---

## 1. Objectif du projet (POC – 3 jours)

- **Cible principale** : prédire à **J+4** le **nombre d’admissions** (`nombre_admissions`).
- **Cibles optionnelles** : lits occupés, nb médecins, nb infirmiers, nb aides-soignants.
- **Usages** : planification RH, anticipation des tensions (lits / sous-effectif), simulation (météo, événements).
- **Pas de front pour l’instant** : entraînement du modèle et validation uniquement.

---

## 2. Formulation ML

- **Type** : régression supervisée.
- **Horizon** : mono-horizon J+4.
- **Formulation** : *À partir des données du jour J, prédire les admissions au jour J+4.*

---

## 3. Dataset – Fichier et colonnes

**Fichier** :  
`data/raw/Jeu de données - Smart Care - daily_hospital_context_2022-2024_generated.csv`

**Colonnes existantes (noms réels dans le CSV)** :

| Groupe        | Colonnes |
|---------------|----------|
| Date / temps  | `date`, `jour_semaine`, `jour_mois`, `semaine_annee`, `mois`, `annee`, `saison` |
| Vacances      | `vacances_scolaires` (déjà calculé, 0/1) |
| Température   | `temperature_moyenne`, `temperature_min`, `temperature_max` |
| Météo         | `meteo_principale` (catégorielle) |
| Indices       | `indice_chaleur`, `indice_froid` |
| Lits / RH     | `lits_total`, `lits_occupes`, `taux_occupation_lits`, `nb_medecins_disponibles`, `nb_infirmiers_disponibles`, `nb_aides_soignants_disponibles`, `taux_couverture_personnel` |
| Cible / flux  | `nombre_admissions`, `nombre_passages_urgences`, `nombre_hospitalisations`, `nombre_sorties` |
| Événements    | `evenement_special` (catégorielle), `impact_evenement_estime` |

**Attention** : les nombres utilisent la **virgule** comme séparateur décimal (ex. `"11,1"`). À convertir en float à l’import.

---

## 3.1 Règles de génération du dataset (connaissance métier)

Le jeu de données a été construit à partir de **règles pédagogiques** qui encodent la logique métier. **Oui, ces règles aident le modèle** : elles décrivent les effets que les données contiennent déjà (jour de la semaine, vacances, saison, événements). On peut s'en servir pour des **features dérivées**, une **baseline règles** et l'**interprétabilité**.

### Résumé des règles (multiplicateurs sur les admissions)

| Règle | Facteur | Multiplicateurs (admissions) |
|-------|---------|-------------------------------|
| **Jour de la semaine** (base = 1.00) | Lundi 1.10, Mardi 1.05, Mer/Jeu 1.00, Ven 0.95, Sam 0.85, Dim 0.80 | `mult_jour_semaine` |
| **Vacances scolaires (Paris)** | Hors vacances 1.00, Vacances 0.90 | déjà dans `vacances_scolaires` |
| **Saison** | Hiver 1.15, Printemps 1.00, Été 0.90, Automne 1.05 | `mult_saison` depuis `saison` |
| **Grippe** (6–10 sem, déc–fév) | Début 1.10, Pic 1.30, Fin 1.15 | `evenement_special` + phase si dispo |
| **Gastro** (3–5 sem, hiver) | Début 1.10, Pic 1.20, Fin 1.05 | idem |
| **Canicule** (5–10 j, été) | &lt;30°C 1.00, 30–34°C 1.10, ≥35°C 1.25 | `temperature_*` + `meteo_principale` |
| **Pollen** (avr–juin) | Faible 1.00, Moyen 1.05, Fort 1.10 | `evenement_special` |

*Personnel* : même logique jour de la semaine (Ven 0.95, Sam 0.85, Dim 0.80) ; vacances 0.85 ; grippe active 1.05–1.10.

*Lits occupés* : capacité 1800, évolution = Lits_j-1 + Admissions × taux_hosp − Sorties (taux hosp. ~20–30 %, séjour 5–7 j).

### Comment utiliser ces règles pour le modèle

1. **Features dérivées (recommandé)**  
   Créer des colonnes qui encodent explicitement les multiplicateurs :
   - `mult_jour_semaine` : 1.10 (Lundi), 1.05 (Mardi), 1.00 (Mer/Jeu), 0.95 (Ven), 0.85 (Sam), 0.80 (Dim).
   - `mult_saison` : 1.15 (Hiver), 1.00 (Printemps), 0.90 (Été), 1.05 (Automne).
   - `mult_vacances` : 1.0 si hors vacances, 0.9 si vacances (ou réutiliser `vacances_scolaires`).
   - Optionnel : `mult_canicule` à partir de `temperature_max` (ex. 1.0 / 1.1 / 1.25 selon seuils).

   Le modèle peut les utiliser tels quels ou les pondérer (arbre / gradient). Ça injecte de la connaissance métier et peut améliorer la généralisation.

2. **Baseline « règles »**  
   En plus des baselines naïves (lag_4, lag_7, roll_mean_7), une **baseline rule-based** :
   - Partir d'une base (ex. `adm_roll_mean_7` ou `adm_lag_7`).
   - Appliquer les multiplicateurs jour × vacances × saison × événement (si disponible).
   - Comparer cette baseline aux modèles ML : si le ML ne bat pas cette baseline, revoir les features ou le pipeline.

3. **Interprétabilité**  
   Vérifier que les importances de features (Random Forest / GBM) sont cohérentes avec ces règles (ex. `jour_semaine`, `saison`, `vacances_scolaires` bien placés). Incohérence forte = à investiguer.

---

## 4. Cible (OBLIGATOIRE)

À créer dans le dataset :

```python
df["y"] = df["nombre_admissions"].shift(-4)
```

- `y` = admissions **observées** 4 jours plus tard.
- Utilisée **uniquement** pour entraînement et évaluation, **jamais** comme feature.
- Conséquence : supprimer les **4 dernières lignes** (pas de `y` pour ces dates). C’est attendu.

---

## 5. Features à créer

### 5.1 Features calendrier (fort signal)

À dériver à partir de `date` / `jour_semaine` / `vacances_scolaires` :

| Feature             | Description |
|---------------------|-------------|
| `is_weekend`        | 1 si samedi ou dimanche, 0 sinon |
| `is_holiday`        | 1 si jour férié (ou réutiliser `vacances_scolaires` si c’est la définition retenue) |
| `veille_holiday`    | 1 si le lendemain est férié/vacances |
| `lendemain_holiday` | 1 si la veille est férié/vacances |

*À préciser en code : si “holiday” = vacances scolaires uniquement, alors `is_holiday` peut être égal à `vacances_scolaires`.*

### 5.2 Features temporelles sur les admissions (CRITIQUES)

Toutes basées sur **`nombre_admissions`**, avec **information disponible au jour J uniquement** (pas de fuite de futur).

**Lags** (obligatoires) :

- `adm_lag_1`, `adm_lag_7`, `adm_lag_14`, `adm_lag_28`

**Moyennes glissantes** :

- `adm_roll_mean_7`, `adm_roll_mean_14`, `adm_roll_mean_28`

**Variabilité** :

- `adm_roll_std_7`

**Optionnel** :

- `adm_diff_1`, `adm_diff_7` (différences entre J et J-1, J et J-7)

Sans ces colonnes, le modèle sera faible. Les calculer **avant** le split temporel, puis supprimer les lignes où ces valeurs sont NaN (ou gérer explicitement le warm-up).

---

## 6. Encodage des variables catégorielles (OBLIGATOIRE)

Transformation en **colonnes binaires** (one-hot) : 1 si la modalité est présente ce jour-là, 0 sinon.

### 6.1 Météo (`meteo_principale`)

Modalités à prévoir (nom des colonnes au choix, ex. minuscules + underscores) :

- Pluie, Froid, Gris, Soleil, Frais, Doux, Vent, Neige, Chaleurs, Canicule

Exemples de noms de colonnes : `meteo_pluie`, `meteo_froid`, `meteo_gris`, `meteo_soleil`, `meteo_frais`, `meteo_doux`, `meteo_vent`, `meteo_neige`, `meteo_chaleurs`, `meteo_canicule`.

*Adapter aux valeurs réellement présentes dans le CSV (ex. `Frais`, `Gris`, `Pluie` avec majuscule).*

### 6.2 Événements (`evenement_special`)

Modalités à prévoir :

- Epidémie de grippe  
- Epidémie de gastro  
- Pollen Allergène  
- Rentrée Scolaire  

Exemples de noms : `event_grippe`, `event_gastro`, `event_pollen`, `event_rentree`.  
*Dans le CSV les valeurs peuvent être du type `Epidemie_grippe` (avec underscore) : utiliser ces chaînes pour le mapping.*

---

## 7. Nettoyage et anti-fuite

- Supprimer les lignes où `y` est NaN (les 4 dernières après `shift(-4)`).
- Supprimer ou gérer les lignes où lags / rolling sont incomplets (début de série).
- **Ne jamais utiliser** :
  - une valeur future de `nombre_admissions`,
  - `y` comme feature.
- Tous les calculs (lags, rolling, calendar) doivent utiliser **uniquement l’information disponible au jour J**.

---

## 8. Séparation Train / Test (OBLIGATOIRE)

- **Split temporel uniquement** : pas de split aléatoire.
- **Recommandation** : **80 % premiers jours** = train, **20 % derniers jours** = test.  
  (Ex. ~2,2 ans train, ~0,5 an test sur 2022–2024.)
- Option pédagogique : `TimeSeriesSplit` (sklearn) pour validation croisée temporelle.

---

## 9. Baselines (À FAIRE AVANT LE ML)

Comparer les modèles ML à **au moins une** baseline ; recommandation : les **3** suivantes.

| Baseline              | Règle de prédiction      |
|-----------------------|---------------------------|
| Naïf J+4              | `y_pred = adm_lag_4`      |
| Saisonnier hebdo      | `y_pred = adm_lag_7`      |
| Moyenne glissante 7j  | `y_pred = adm_roll_mean_7`|
| **Règles (optionnel)**| Base (ex. `adm_roll_mean_7`) × mult_jour × mult_vacances × mult_saison × mult_événement (voir § 3.1) |

Évaluer chaque baseline avec les **mêmes métriques** que les modèles ML (MAE, MAPE ou sMAPE).

---

## 10. Métrique d’erreur “≤ 10 %”

La contrainte métier “erreur ≤ 10 %” doit être définie de façon unique pour le projet.

**Recommandation** : **MAPE** (Mean Absolute Percentage Error), en %.

- Formule :  
  `MAPE = mean(|y_true - y_pred| / y_true) * 100`  
  (gérer les cas `y_true == 0` : exclure ou capter le pourcentage.)
- Interprétation : “en moyenne, l’erreur relative est de X %”. Objectif : **MAPE ≤ 10 %**.

**Alternatives à documenter si tu en choisis une autre** :

- **sMAPE** : symétrique, borné ; plus robuste quand les valeurs sont proches de 0.
- **MAE normalisée** : e.g. `MAE / mean(y_true) * 100` pour avoir un “% moyen”.

Dans le rapport / code, **indiquer clairement** quelle métrique est utilisée pour le “≤ 10 %”.

---

## 11. Modèles ML à implémenter

- **RandomForestRegressor** (sklearn).
- **GradientBoostingRegressor** (sklearn), ou LightGBM si autorisé.
- Un **seul horizon** : J+4.
- **Un modèle par cible** (au minimum pour `nombre_admissions`).

---

## 12. Évaluation des modèles

**Métriques** :

- MAE  
- MAPE ou sMAPE (dont celle retenue pour la contrainte “≤ 10 %”)

**Sécurité (surestimation préférée)** :

- Appliquer une marge de **10 %** :  
  `prediction_safe = prediction * 1.10`  
- Documenter dans le rapport que les prédictions “sécurisées” sont ainsi définies.

**Visualisations utiles** :

- Prédiction vs réel (courbe dans le temps).
- Erreurs par période (ex. par mois ou par saison).
- Comparaison baseline vs ML (ex. courbes ou barres).

---

## 13. Ordre de développement recommandé

1. Charger les données et nettoyer (types, virgule décimale, `date` en datetime, tri par `date`).
2. Créer `y = nombre_admissions.shift(-4)`.
3. Créer lags et rolling sur `nombre_admissions` (puis variabilité / diff si besoin).
4. Créer les features calendrier (`is_weekend`, etc.).
5. Encoder météo et événements (one-hot).
6. Supprimer les lignes avec NaN (y ou features).
7. Split temporel 80 % / 20 %.
8. Implémenter et évaluer les 3 baselines.
9. Entraîner et évaluer Random Forest et Gradient Boosting.
10. Comparer baselines vs ML (métriques + visus).
11. Sauvegarder le modèle retenu (voir section 14).

---

## 14. Sauvegarde du modèle et livrable pour intégration

Tu développes le modèle de ton côté ; quelqu’un d’autre l’intégrera au projet (ex. front plus tard). Pour faciliter l’intégration :

- **Sauvegarder** :
  - Le **modèle** (ex. `joblib` ou `pickle`) : `RandomForestRegressor` ou `GradientBoostingRegressor` entraîné.
  - L’**encodage des variables** : liste des features utilisées à l’entraînement (ordre et noms), et si besoin le `OneHotEncoder` / le mapping météo et événements (pour reproduire les mêmes colonnes en prod).
- **Documenter** :
  - **Entrées** attendues pour une prédiction J+4 : date du jour J + toutes les features utilisées (ou comment les dériver à partir de la date et des données du jour).
  - **Sorties** : prédiction brute, prédiction sécurisée `prediction_safe = prediction * 1.10`.
- **Livrable suggéré** :
  - Un **script ou module** qui : charge le modèle, prend en entrée un vecteur de features (ou un dataframe d’une ligne), retourne `prediction` et `prediction_safe`.
  - Un **fichier de config ou README** listant les features dans l’ordre attendu et les éventuelles transformations (ex. noms des colonnes one-hot météo/événements).

Cela permettra à la personne qui intègre de brancher le modèle sans refaire la feature engineering à la main.

---

## 15. Résumé des choix documentés

| Sujet              | Choix |
|--------------------|-------|
| Public             | Professeur – Spé Data & IA |
| Contrainte erreur  | À définir explicitement ; recommandation : MAPE ≤ 10 % |
| Marge de sécurité  | 10 % : `prediction_safe = prediction * 1.10` |
| Météo              | 10 modalités (Pluie, Froid, Gris, Soleil, Frais, Doux, Vent, Neige, Chaleurs, Canicule) – one-hot |
| Événements         | 4 modalités (grippe, gastro, pollen, rentrée) – one-hot |
| Vacances           | Déjà dans le jeu : `vacances_scolaires` |
| Split              | Temporel 80 % train / 20 % test |
| Baselines          | Naïf lag_4, Saisonnier lag_7, Moyenne glissante 7j |
| Livrable modèle    | Modèle sérialisé + doc des entrées/sorties et des features pour intégration |
| Dashboard / front  | Hors périmètre pour l’instant |
| Type de doc        | Guide technique pour aiguiller le développement |

---

*Document à mettre à jour si les choix (métrique, split, noms de colonnes réels) changent pendant le développement.*
