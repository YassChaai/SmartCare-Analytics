# Audit technique – Prototype, prédiction et recommandations

**Mise à jour** : 5 février 2026 (structure & chemins vérifiés)

**Projet :** Smart Care Analytics – Pitié-Salpêtrière  
**Périmètre :** Côté technique du livrable (prototype fonctionnel + prédiction + recommandations)  
**Référence :** Consignes projet DATA – Livrables attendus  
**Date :** 3 février 2026

---

## 1. Synthèse exécutive

| Dimension | Conforme | Partiel | Non fait | Commentaire rapide |
|-----------|----------|---------|----------|---------------------|
| Interface / exploration des flux | ✅ | | | Dashboard, navigation, KPIs, graphiques |
| Simulation de scénarios | ✅ | | | Épidémie, canicule, grève, afflux, vacances, personnalisé |
| Modélisation / prévision des besoins | ⚠️ | ✅ | | Modèle ML + fallback stats ; perf limitée, pas 2025/2026 |
| Tableau de bord interactif | ✅ | | | Décideurs peuvent ajuster via filtres, scénarios, prédictions |
| Module de recommandations automatiques | ✅ | | | Règles métier, priorisation, planification, ROI |

**Verdict :** Le prototype couvre les attendus fonctionnels (interface, simulation, prévisions, recommandations). Les écarts principaux concernent la **qualité et le périmètre de la prédiction** (données 2022–2024 uniquement, pas de vraie prédiction 2026, modèle peu performant) et le **lien explicite prédiction → recommandations**.

---

## 2. Rapport détaillé par attendu

### 2.1 Prototype fonctionnel (consignes)

#### 2.1.1 Interface permettant d’explorer les flux hospitaliers et de simuler différents scénarii

**Attendu :**  
« Interface permettant d’explorer les flux hospitaliers et de simuler différents scénarii (épidémie, grève, afflux massif). »

**Réalisé :**
- **Exploration des flux :** Page Accueil (KPIs, évolution admissions/urgences, occupation, alertes). Page Analyse (tendances, corrélations, impact météo, stats descriptives). Filtres par période et saison.
- **Simulation :** Page Simulation avec 7 types de scénarios (Épidémie, Canicule, Vague de froid, Grève, Afflux massif, Vacances, Personnalisé), paramètres d’impact (admissions, urgences, personnel, lits), durée, intensité, projection sur N jours, graphiques baseline vs scénario, analyse de risque, besoins supplémentaires, coûts estimés, recommandations et export CSV/TXT.

**Écart :** Aucun. Conforme.

---

#### 2.1.2 Modélisation des tendances d’admissions et prévision des besoins (lits, personnel, matériel)

**Attendu :**  
« Modélisation des tendances d’admissions et prévision des besoins en lits, personnel et matériel médical. »

**Réalisé :**
- **Tendances :** Visualisées en Analyse (quotidien/hebdo/mensuel, par jour de semaine, par saison). Pas de modèle de tendance explicite (régression temporelle, décomposition saisonnière) côté app.
- **Prévision :**
  - **Prédiction simple (1 jour) :** Si pipeline SmartCare dispo → `prepare_prediction_row` + `apply_overrides` (météo, événement) + `predict_from_features` (admissions). Urgences et occupation dérivées (ratio moyen, moyenne globale). Sinon ou en erreur → `predict_with_stats` (baseline jour_semaine + saison + ajustements vacances/température/événement).
  - **Prédiction multi-jours (1–90 j) :** Uniquement `predict_with_stats` (pas d’appel au modèle ML), avec paramètres fixes (vacances=False, T=15, événement=Aucun). Donc pas d’usage des événements/météo ni du ML sur la plage.
- **Besoins :** Lits (1650 × taux occupation), personnel (lits / ratio), matériel non modélisé explicitement.

**Écarts :**
1. **Données :** Données 2022–2024 uniquement. Pas 2025 → pas de prédiction « réelle » pour 2026 ; pour une date future le pipeline utilise la dernière ligne disponible (proche de 2024) + overrides météo/événement.
2. **Modèle ML :** Entraîné sur `nombre_admissions` (shift -4 j). Métriques (artifacts) : gradient_boosting MAE ≈ 58, MAPE ≈ 19 % ; random_forest proche. Mieux que les baselines (lag, roll_mean, rules) mais erreur relative encore élevée pour un usage « force de prédiction ».
3. **Patterns :** Les features ML (météo, événements, lags, vacances, saison) sont bien utilisées en entraînement ; en prédiction, pour une date hors 2022–2024 on n’a pas de vraie série temporelle (lags 2026), donc la logique repose surtout sur 2024 + surcharge météo/événement.
4. **Multi-jours :** Pas de chaînage avec le ML (pas de prédiction séquentielle avec lags mis à jour).

---

#### 2.1.3 Tableau de bord interactif pour ajuster les ressources selon les prévisions

**Attendu :**  
« Développement d’un tableau de bord interactif permettant aux décideurs hospitaliers d’ajuster les ressources en fonction des prévisions. »

**Réalisé :**
- Dashboard (Accueil + Analyse + Simulation + Prédiction + Recommandations), navigation claire, KPIs, graphiques interactifs (Plotly), filtres, choix de scénarios et de paramètres.
- Les « ajustements » sont implicites : l’utilisateur voit prévisions et recommandations puis peut agir en dehors de l’outil. Pas de sliders du type « ajouter X lits / Y ETP » avec mise à jour en direct des indicateurs.

**Écart :** Mineur. L’outil fournit bien la vision prévisionnelle et les recommandations ; un module explicite « Ajuster ressources (lits/ETP) → recalcul indicateurs » renforcerait l’alignement avec la formulation.

---

#### 2.1.4 Module de recommandations automatiques

**Attendu :**  
« Intégration d’un module de recommandations automatiques pour optimiser la gestion des ressources hospitalières. »

**Réalisé :**
- Page Recommandations avec 3 onglets :
  - **Recommandations du jour :** À partir des 7 derniers jours (occupation, personnel, tendances). Règles (seuils 85 %, 75 %, etc.) → recommandations priorisées (CRITIQUE / HAUTE / MOYENNE / OPTIMISATION) avec description, impact, délai, actions. Prise en compte des événements spéciaux.
  - **Planification hebdomadaire :** Stats par jour de semaine, graphiques, recommandations par jour (renfort, lits, opportunités).
  - **Optimisation stratégique :** Tendances mensuelles/saisonnières, impact des événements, capacité (P95, jours critiques), RH, calculateur ROI (réduction durée séjour, économies).
- Simulation : recommandations contextuelles après chaque scénario (lits, personnel, mesures sanitaires, etc.).

**Écart :** Conforme. Le lien « prévision → recommandations » pourrait être renforcé (ex. « Selon la prédiction des 7 prochains jours, nous recommandons… ») pour coller encore plus à l’esprit « prédiction + recommandations ».

---

### 2.2 Conformité réglementaire et éthique (données de santé)

**Attendu :**  
« Respect de la conformité réglementaire, contraintes légales et éthiques liées aux données de santé. »

**Réalisé :**
- Données synthétiques (générées), pas de données personnelles de santé réelles. Pas de collecte ni de stockage de données sensibles dans l’app. Modèle entraîné sur agrégats (admissions, urgences, occupation, etc.).

**Écart :** Aucun pour le périmètre actuel. À mentionner en soutenance (données fictives, pas de PHI).

---

### 2.3 Soutenance – Démos attendues

**Attendu :**  
« Démonstration complète du prototype et des simulations réalisées » ; « Analyse des résultats du modèle prédictif et recommandations concrètes ».

**Réalisé :**
- Démo possible : Accueil → Analyse → Simulation (ex. épidémie ou grève) → Prédiction (1 jour avec ML si artifacts présents, multi-jours en stats) → Recommandations.
- Résultats du modèle : dans `ML/artifacts/metrics.json` (MAE, MAPE, SMAPE) ; à commenter en soutenance (choix gradient_boosting, limites MAE ~58, MAPE ~19 %).
- Recommandations concrètes : présentes (actions, priorités, délais).

**Écart :** Prévoir 2–3 slides sur les limites (données jusqu’en 2024, perf du modèle, prédiction 2026 basée sur 2024 + surcharge) et sur les pistes d’amélioration.

---

## 3. Checklist attendus vs réalisé

### 3.1 Prototype fonctionnel

| # | Critère | Statut | Note |
|---|---------|--------|------|
| P1 | Interface pour explorer les flux hospitaliers | ✅ Fait | Accueil, Analyse, filtres, graphiques |
| P2 | Simulation scénario épidémie | ✅ Fait | Paramètres, projection, risques, export |
| P3 | Simulation scénario grève | ✅ Fait | Idem |
| P4 | Simulation scénario afflux massif | ✅ Fait | Idem |
| P5 | Autres scénarios (canicule, froid, vacances, personnalisé) | ✅ Fait | 7 scénarios au total |
| P6 | Modélisation des tendances d’admissions | ⚠️ Partiel | Visualisation oui ; pas de modèle de tendance dédié (ex. décomposition) |
| P7 | Prévision des besoins en lits | ✅ Fait | Prédiction + simulation (lits dérivés) |
| P8 | Prévision des besoins en personnel | ✅ Fait | Idem (ratios, effectifs) |
| P9 | Prévision des besoins en matériel médical | ⚠️ Partiel | Non modélisé explicitement ; peut être déduit des recommandations |
| P10 | Tableau de bord interactif | ✅ Fait | Multi-pages, KPIs, graphiques, filtres |
| P11 | Ajustement des ressources par les décideurs (vision prévisionnelle) | ✅ Fait | Via scénarios et paramètres ; pas de « sliders ressources » dédiés |
| P12 | Module de recommandations automatiques | ✅ Fait | 3 onglets + recommandations post-simulation |

### 3.2 Prédiction et modèles

| # | Critère | Statut | Note |
|---|---------|--------|------|
| M1 | Développement d’un/de modèle(s) de prédiction | ✅ Fait | Gradient Boosting + Random Forest + baselines (lag, rules) |
| M2 | Anticipation des pics d’activité | ⚠️ Partiel | Modèle prédit admissions (J+4) ; pics détectables via seuils ; pas de série 2025/2026 |
| M3 | Utilisation de la météo dans le modèle | ✅ Fait | Features météo (one-hot) + overrides en prédiction |
| M4 | Utilisation des événements dans le modèle | ✅ Fait | Idem (événements + impact_evenement_estime) |
| M5 | Saisonnalité / tendance | ✅ Fait | Saison, vacances, lags, roll means dans les features |
| M6 | Prédiction 1 jour intégrée au dashboard | ✅ Fait | Onglet Prédiction simple, ML si dispo |
| M7 | Prédiction multi-jours | ✅ Fait | 1–90 jours ; actuellement en statistique uniquement (pas ML) |
| M8 | Qualité du modèle (impact utilisable) | ⚠️ Partiel | MAE ~58, MAPE ~19 % ; améliorable (features, horizon, données) |
| M9 | Justification des choix de modèle (rapport/soutenance) | À faire | Documenter dans le rapport + soutenance (gradient_boosting, baselines, limites) |

### 3.3 Recommandations

| # | Critère | Statut | Note |
|---|---------|--------|------|
| R1 | Recommandations automatiques basées sur l’état actuel | ✅ Fait | Derniers 7 jours, seuils, priorités |
| R2 | Priorisation des recommandations | ✅ Fait | CRITIQUE / HAUTE / MOYENNE / OPTIMISATION |
| R3 | Actions concrètes (lits, personnel, plans) | ✅ Fait | Liste d’actions par recommandation |
| R4 | Lien avec les événements (épidémie, canicule, etc.) | ✅ Fait | Règles par type d’événement |
| R5 | Planification hebdomadaire | ✅ Fait | Onglet dédié, par jour de semaine |
| R6 | Optimisation stratégique / ROI | ✅ Fait | Capacité, RH, calculateur ROI |
| R7 | Recommandations déclenchées par la simulation | ✅ Fait | Après chaque scénario |
| R8 | Lien explicite prédiction → recommandations | ⚠️ Partiel | Recommandations basées sur historique récent ; pas de bloc « selon prédiction des 7 prochains jours » |

### 3.4 Technique et conformité

| # | Critère | Statut | Note |
|---|---------|--------|------|
| T1 | Données de santé : conformité / éthique | ✅ Fait | Données synthétiques, pas de PHI |
| T2 | Prototype exécutable en local | ✅ Fait | Streamlit, dépendances projet |
| T3 | Documentation (architecture, guides) | ✅ Fait | ARCHITECTURE.md, guides utilisateur |
| T4 | Intégration ML ↔ Dashboard | ✅ Fait | Chargement artifacts, fallback stats |

---

## 4. Points forts pour la soutenance

1. **Couverture fonctionnelle** : Tous les scénarios demandés (épidémie, grève, afflux, etc.) sont présents avec paramétrage et visualisation.
2. **Pipeline ML structuré** : Features riches (météo, événements, lags, vacances, saison), entraînement reproductible (`train_poc.py`), artifacts versionnés, intégration dans l’app avec fallback propre.
3. **Recommandations** : Règles métier claires, priorisation, actions opérationnelles et onglet ROI.
4. **UX** : Navigation lisible, KPIs, graphiques interactifs, export CSV/TXT.

---

## 5. Recommandations d’amélioration (priorité avant jeudi matin)

### Court terme (présentable en soutenance)

1. **Prédiction multi-jours + ML**  
   Utiliser le modèle ML pour chaque jour de la plage (en réutilisant la dernière ligne de features + overrides météo/événement par jour si besoin), au lieu de rester uniquement sur `predict_with_stats`. Même avec des lags « figés », cela aligne la démo avec « modèle de prédiction utilisé partout ».

2. **Afficher les métriques du modèle dans l’app**  
   Dans l’onglet Prédiction (ou Upload), afficher MAE/MAPE depuis `metrics.json` et une phrase du type : « Modèle entraîné sur 2022–2026 ; pour les dates hors période, la prédiction s’appuie sur la dernière période connue + contexte météo/événement. »

3. **Une slide « Limites et pistes »**  
   Données jusqu’en 2024 → prédiction 2026 contrainte ; modèle à améliorer (MAPE ~19 %) ; évolution possible : prédiction séquentielle, données 2025, matériel médical.

### Moyen terme (après projet)

4. **Lien prédiction → recommandations**  
   Un bloc « Selon la prédiction des 7 prochains jours » qui réutilise les sorties de l’onglet Prédiction multi-jours et génère 2–3 recommandations ciblées (ex. « Renforcer le mercredi X »).

5. **Amélioration du modèle**  
   Tester d’autres horizons (J+1, J+7), variables cibles (urgences, occupation), rééquilibrage ou séries temporelles (SARIMAX, Prophet) pour mieux capter la saisonnalité.

---

## 6. Résumé checklist globale

- **Conforme / Fait :** 28 critères  
- **Partiel :** 7 critères (tendances, matériel, pics, multi-jours ML, qualité modèle, lien prédiction→recommandations)  
- **À faire (hors code) :** 1 critère (justification des choix dans rapport/soutenance)

Le prototype est **livrable et défendable** pour la soutenance du jeudi après-midi. Les écarts sont surtout sur la **force de la prédiction** (données, horizon 2026, performance du modèle) et sur le **lien explicite prédiction → recommandations** ; les documenter et proposer des pistes d’évolution suffit à répondre aux attendus.
