# 📖 Guide d'Utilisation - Dashboard Smart Care

## 🎯 Introduction

Ce dashboard permet d'analyser l'activité de l'hôpital Pitié-Salpêtrière, de simuler des scénarios d'affluence, de prédire l'activité future et d'obtenir des recommandations automatiques.

**Données** : 3 ans d'historique (2022-2024) avec 1098 jours de données quotidiennes.

---

## 🚀 Lancement du Dashboard

### Méthode 1 : Avec Pipenv (Recommandé)

```bash
cd "c:\Users\evan_\Desktop\SCProject\SmartCare-Analytics"
pipenv shell
streamlit run app/app.py
```

### Méthode 2 : Avec l'environnement virtuel

```bash
cd "c:\Users\evan_\Desktop\SCProject\SmartCare-Analytics"
.\.venv\Scripts\activate
streamlit run app/app.py
```

### Méthode 3 : Direct avec pipenv

```bash
cd "c:\Users\evan_\Desktop\SCProject\SmartCare-Analytics"
pipenv run streamlit run app/app.py
```

**Le dashboard s'ouvre automatiquement dans votre navigateur** à l'adresse : `http://localhost:8501`

---

## 📱 Interface Générale

```
┌──────────────────────────────────────────────────────────┐
│  🏥 SMART CARE - Pitié-Salpêtrière                      │
├──────────────────────────────────────────────────────────┤
│ NAVBAR (haut)             │  CONTENU PRINCIPAL (bas)    │
│                           │                              │
│ 🏠 Accueil                │  [Graphiques, KPIs, etc.]   │
│ 📊 Analyse Exploratoire   │                              │
│ 🎯 Simulation Scénarios   │                              │
│ 🔮 Prédiction             │                              │
│ 💡 Recommandations        │                              │
└───────────────────────────┴──────────────────────────────┘
```

**Navigation** : Cliquez sur un bouton dans la barre de navigation horizontale en haut.

---

## 🏠 Page 1 : Accueil

**Objectif** : Vue d'ensemble de l'activité hospitalière avec KPIs et alertes.

### Section 1 : Indicateurs Clés (KPIs)

```
┌────────────┬────────────┬────────────┬────────────┐
│ 73.5%      │    345     │    1025    │   92.8%    │
│ Occupation │ Admissions │  Urgences  │ Personnel  │
│   ▲ +2.3%  │   ▼ -12    │   ▲ +45    │   ▼ -1.2%  │
└────────────┴────────────┴────────────┴────────────┘
```

**Interprétation** :
- **Taux d'occupation** : % de lits occupés (🔴 >85% critique, 🟠 75-85% élevé, 🟢 <75% normal)
- **Admissions** : Nombre moyen d'admissions/jour sur 7 derniers jours
- **Passages urgences** : Nombre moyen/jour
- **Personnel** : Taux de couverture (médecins + infirmiers + aides-soignants)

**Flèches** :
- ▲ Vert : Augmentation favorable
- ▼ Rouge : Diminution ou augmentation défavorable

### Section 2 : Évolutions Mensuelles

Deux graphiques linéaires montrant les tendances sur les 6 derniers mois :
- **Admissions** : Tendance des admissions
- **Urgences** : Tendance des passages urgences

**Utilisation** : 
- Survolez les points pour voir les valeurs exactes
- Identifiez les pics et les creux
- Comparez les mois entre eux

### Section 3 : Distribution de l'Occupation

Histogramme montrant la **répartition des taux d'occupation** :
- Axe X : Taux d'occupation (0-100%)
- Axe Y : Nombre de jours
- **Zone verte** : <75% (normal)
- **Zone orange** : 75-85% (élevé)
- **Zone rouge** : >85% (critique)

**Exemple d'interprétation** : 
"150 jours à 70-75% d'occupation, 50 jours à >85% (critique)"

### Section 4 : Alertes et Événements

Trois colonnes d'alertes :

#### 🔴 Alertes Occupation
```
┌─────────────────────────────┐
│ 🔴 ALERTE OCCUPATION        │
│                             │
│ Occupation actuelle: 87.3%  │
│ ⚠️ Plan blanc recommandé    │
└─────────────────────────────┘
```

#### 📅 Événements Actifs
```
┌─────────────────────────────┐
│ 📅 ÉVÉNEMENTS EN COURS      │
│                             │
│ 🦠 Épidémie de grippe       │
│    Impact: +16%             │
└─────────────────────────────┘
```

#### 👥 Alertes Personnel
```
┌─────────────────────────────┐
│ 👥 PERSONNEL                │
│                             │
│ 🟢 Couverture normale       │
│    Taux: 92.5%              │
└─────────────────────────────┘
```

**Actions** : Les alertes critiques (🔴) nécessitent une action immédiate.

---

## 📊 Page 2 : Analyse Exploratoire

**Objectif** : Explorer les données en profondeur avec filtres et visualisations.

### Zone de Filtres (en haut de page)

```
┌─────────────────────┐
│ 📅 Plage de dates   │
│ Du: 2022-01-01      │
│ Au: 2024-12-31      │
│                     │
│ 🌸 Saison           │
│ ☑ Toutes            │
│ ☐ Hiver             │
│ ☐ Printemps         │
│ ☐ Été               │
│ ☐ Automne           │
└─────────────────────┘
```

**Utilisation** : Sélectionnez une plage de dates et/ou une saison pour filtrer toutes les analyses.
Les filtres sont intégrés dans la page (pas de sidebar).

### Onglet 1 : Tendances Temporelles

#### Sélection de métrique
```
┌────────────────────────────┐
│ Métrique à analyser:       │
│ [▼ Nombre d'admissions   ] │
└────────────────────────────┘
```

**Métriques disponibles** :
- Nombre d'admissions
- Passages urgences
- Taux d'occupation des lits
- Nombre d'hospitalisations
- Nombre de sorties

#### Granularité
```
┌──────────────────────┐
│ [Jour] [Semaine] [Mois]│
└──────────────────────┘
```

**Utilisation** :
- **Jour** : Voir l'évolution quotidienne (détails fins)
- **Semaine** : Tendance hebdomadaire (moyenne)
- **Mois** : Vue macro (tendances long terme)

#### Graphiques

1. **Évolution Temporelle** : Ligne montrant la métrique sur la période
2. **Analyse par Jour de la Semaine** : Bar chart (Lundi-Dimanche)
3. **Analyse par Saison** : Bar chart (Hiver, Printemps, Été, Automne)

**Exemple d'insight** :
- "Les admissions sont 25% plus élevées en hiver"
- "Les lundis ont +30% de passages urgences vs dimanche"

### Onglet 2 : Corrélations

#### Matrice de Corrélations

```
                  Admissions  Urgences  Occupation
Admissions            1.00      0.65       0.72
Urgences              0.65      1.00       0.58
Occupation            0.72      0.58       1.00
```

**Lecture** :
- **1.00** : Corrélation parfaite (même variable)
- **0.65-0.72** : Corrélation forte positive
- **0.0-0.3** : Corrélation faible
- **Négatif** : Corrélation inverse

**Couleurs** :
- 🔴 Rouge foncé : Forte corrélation positive
- 🔵 Bleu foncé : Forte corrélation négative
- ⚪ Blanc : Pas de corrélation

#### Top 10 Corrélations

Tableau listant les 10 paires de variables les plus corrélées.

**Exemple** :
```
Variable 1              Variable 2           Corrélation
Admissions              Taux occupation         0.72
Température moyenne     Urgences                0.45
```

**Utilisation** : Identifiez les liens entre variables pour comprendre les facteurs d'influence.

### Onglet 3 : Impact Météo

#### Graphique 1 : Scatter Plot
- **Axe X** : Température moyenne
- **Axe Y** : Nombre d'admissions
- **Couleur** : Type de météo (Ensoleillé, Nuageux, Pluie, etc.)

**Utilisation** : Survolez les points pour voir les détails. Observez si les températures extrêmes augmentent les admissions.

#### Graphique 2 : Admissions moyennes par météo

Bar chart montrant le nombre moyen d'admissions pour chaque type de météo.

**Exemple d'insight** :
- "Par temps de canicule : 425 admissions/jour (vs 345 en temps normal)"
- "Par temps froid : 380 admissions/jour"

### Onglet 4 : Statistiques Descriptives

#### Tableau de Synthèse

```
Métrique        Moyenne   Médiane   Écart-type   Min    Max
Admissions        345      342         45        236    477
Urgences         1025     1020         82        920   1250
Occupation       73.5%    74.0%       8.2%      49%    95%
```

**Lecture** :
- **Moyenne** : Valeur moyenne sur la période
- **Médiane** : Valeur centrale (50% des jours au-dessus/en-dessous)
- **Écart-type** : Variabilité (plus élevé = plus de fluctuations)
- **Min/Max** : Valeurs extrêmes observées

#### Graphiques de Distribution

Histogrammes montrant la répartition des valeurs pour chaque métrique.

**Exemple** : 
- Si la distribution est **centrée** : valeurs stables
- Si la distribution est **étalée** : forte variabilité
- Si **bimodale** : deux régimes distincts (ex: semaine vs weekend)

---

## 🎯 Page 3 : Simulation de Scénarios

**Objectif** : Projeter l'impact d'un événement sur l'activité hospitalière.

### Étape 1 : Choisir un Scénario

```
┌──────────────────────────────────┐
│ Type de scénario:                │
│ [▼ 🦠 Épidémie (grippe/covid) ] │
└──────────────────────────────────┘
```

**Scénarios prédéfinis** :

| Scénario | Description | Utilisation |
|----------|-------------|-------------|
| 🦠 **Épidémie** | Grippe, Covid, gastro | Hiver, saison grippale |
| 🔥 **Canicule** | Température >35°C | Été, vagues de chaleur |
| ❄️ **Vague de froid** | Température <0°C | Hiver, grand froid |
| 🚫 **Grève** | Personnel en grève | Mouvement social |
| 🚨 **Afflux massif** | Accident, attentat | Urgence immédiate |
| 📅 **Vacances** | Période de vacances | Juillet-Août, Noël |
| 🎯 **Personnalisé** | Paramètres manuels | Cas spécifique |

### Étape 2 : Configuration du Scénario

```
┌──────────────────────────────────┐
│ 📅 Date de début                 │
│    [03/02/2026]                  │
│                                  │
│ ⏱️ Durée de l'événement          │
│    [━━━━━━━●━━━━] 30 jours      │
│                                  │
│ 📊 Intensité                     │
│    [━━━━━━●━━━━━] 0.7           │
└──────────────────────────────────┘
```

**Paramètres** :
- **Date de début** : Quand commence le scénario
- **Durée** : Nombre de jours (1-90)
- **Intensité** : 0 = faible, 1 = maximale

### Étape 3 : Ajuster les Impacts (Mode Avancé)

Pour chaque scénario, vous pouvez ajuster :

```
┌─────────────────────────────────────┐
│ 📈 Impact sur les admissions        │
│    [━━━━━━━●━━━] +30%              │
│                                     │
│ 🚑 Impact sur les urgences          │
│    [━━━━━━━●━━━] +20%              │
│                                     │
│ 👥 Personnel disponible             │
│    [━━━━━━━━━━●] -5%               │
│                                     │
│ 🛏️ Pression sur les lits            │
│    [━━━━━━━●━━━] +15%              │
└─────────────────────────────────────┘
```

**Valeurs prédéfinies par scénario** :
- **Épidémie** : +30% admissions, +20% urgences, -5% personnel, +15% pression lits
- **Canicule** : +15% admissions, +40% urgences, 0% personnel, +20% pression
- **Grève** : 0% admissions, 0% urgences, -40% personnel, +10% pression

### Étape 4 : Lancer la Simulation

Cliquez sur **"🎬 Lancer la Simulation"**

### Résultats de la Simulation

#### 1. Métriques Clés

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   Baseline   │  Projection  │  Variation   │   Maximum    │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Admissions   │              │              │              │
│    345       │     449      │   +30.1%     │     485      │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Urgences     │              │              │              │
│   1025       │    1230      │   +20.0%     │    1310      │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Occupation   │              │              │              │
│   73.5%      │    88.2%     │   +14.7 pts  │    93.5%     │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Personnel    │              │              │              │
│   92.8%      │    88.2%     │    -4.6 pts  │    85.0%     │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**Légende** :
- **Baseline** : Valeur actuelle (référence)
- **Projection** : Valeur moyenne pendant le scénario
- **Variation** : Écart par rapport à la baseline
- **Maximum** : Pic le plus élevé attendu

#### 2. Graphiques de Projection

Quatre graphiques montrant l'évolution jour par jour :

1. **Admissions** : Ligne baseline (gris) vs projection (bleu)
2. **Urgences** : Ligne baseline vs projection
3. **Occupation** : Ligne baseline vs projection + **ligne rouge** (seuil critique 85%)
4. **Personnel** : Ligne baseline vs projection + **ligne rouge** (seuil minimum 85%)

**Lecture** :
- La courbe est **progressive** : pic au milieu de l'événement, retour progressif à la normale
- Les **zones rouges** indiquent des dépassements de seuils critiques

#### 3. Analyse des Risques

```
┌────────────────────────────────────────┐
│ 🔴 NIVEAU DE RISQUE : CRITIQUE         │
└────────────────────────────────────────┘

⚠️ Points d'attention :
• Occupation maximale : 93.5% (> seuil critique 85%)
• Personnel minimal : 85.0% (= seuil critique)
• 18 jours avec occupation > 85%
• Pic attendu : Jour 15 (18/02/2026)
```

**Niveaux de risque** :
- 🟢 **FAIBLE** : Tous les indicateurs dans les normes
- 🟠 **MODÉRÉ** : Un indicateur proche du seuil critique
- 🔴 **CRITIQUE** : Un ou plusieurs indicateurs au-delà du seuil

#### 4. Besoins Supplémentaires

```
┌──────────────────────────────────────────┐
│ 🛏️ LITS SUPPLÉMENTAIRES                  │
│    +45 lits nécessaires                  │
│                                          │
│ 👥 PERSONNEL SUPPLÉMENTAIRE              │
│    +12 médecins                          │
│    +28 infirmiers                        │
│    +18 aides-soignants                   │
│                                          │
│ 💰 COÛT ESTIMÉ                           │
│    Journalier : 37,500 €                 │
│    Total (30j) : 1,125,000 €             │
└──────────────────────────────────────────┘
```

**Calculs** :
- **Lits** : 500 €/lit/jour
- **Personnel** : 300 €/personne/jour

#### 5. Recommandations Automatiques

Liste d'actions prioritaires générées automatiquement :

```
✅ ACTIONS RECOMMANDÉES

🔴 PRIORITÉ CRITIQUE
• Activer le plan blanc niveau 1
• Rappeler personnel de garde
• Identifier lits mobilisables en chirurgie ambulatoire

🟠 PRIORITÉ HAUTE
• Renforcer équipes aux urgences (+2 médecins/shift)
• Préparer ouverture de 45 lits supplémentaires
• Communication SAMU pour répartition des patients

🟡 PRIORITÉ MOYENNE
• Accélérer sorties des patients stabilisés
• Annuler interventions non-urgentes
• Veille quotidienne renforcée
```

**Utilisation** : Suivez les recommandations dans l'ordre de priorité (🔴 → 🟠 → 🟡).

### Étape 5 : Exporter les Résultats

Deux boutons d'export :

```
[📥 Télécharger CSV]   [📄 Télécharger Rapport]
```

- **CSV** : Données jour par jour (date, admissions, urgences, occupation, personnel)
- **Rapport TXT** : Synthèse complète avec métriques, risques, besoins, recommandations

**Utilisation** : Utilisez le CSV pour des analyses supplémentaires dans Excel/Python, et le rapport pour présenter aux décideurs.

---

## 🔮 Page 4 : Prédiction

**Objectif** : Prédire l'activité hospitalière future.

### Onglet 1 : Prédiction Simple (1 jour)

#### Étape 1 : Sélectionner une date

```
┌─────────────────────────┐
│ 📅 Date à prédire       │
│    [15/02/2026]         │
└─────────────────────────┘
```

**Auto-calculé** :
- Jour de la semaine : Dimanche
- Saison : Hiver
- Vacances scolaires : Non

#### Étape 2 : Paramètres Contextuels

```
┌──────────────────────────────────┐
│ 🌡️ Température moyenne (°C)      │
│    [━━━━━━●━━━━] 15°C           │
│                                  │
│ ☁️ Météo principale              │
│    [▼ Nuageux              ]     │
│                                  │
│ 📅 Événement spécial             │
│    [▼ Aucun                ]     │
└──────────────────────────────────┘
```

**Événements disponibles** : Aucun, Épidémie grippe, Canicule, Vague de froid, Pollution, Événement majeur

#### Étape 3 : Lancer la Prédiction

Cliquez sur **"🔮 Prédire"**

#### Résultats

```
┌────────────────────────────────────────┐
│ PRÉDICTIONS POUR LE 15/02/2026        │
├────────────────────────────────────────┤
│ 📊 Admissions prévues                  │
│     328 ± 35                           │
│     (Intervalle : 293 - 363)           │
│                                        │
│ 🚑 Passages urgences                   │
│     985 ± 82                           │
│     (Intervalle : 903 - 1067)          │
│                                        │
│ 🛏️ Taux occupation                     │
│     71.2% ± 6.5%                       │
│     (Intervalle : 64.7% - 77.7%)       │
│                                        │
│ 🆚 Comparaison baseline                │
│     Admissions : -5% vs moyenne        │
│     Urgences : -3% vs moyenne          │
└────────────────────────────────────────┘
```

**Légende** :
- **±** : Marge d'erreur (écart-type)
- **Intervalle** : Intervalle de confiance à 95%
- **Comparaison baseline** : Écart par rapport à la moyenne historique

#### Besoins Estimés

```
🛏️ Lits nécessaires : 1175 / 1650
👥 Personnel minimal requis :
   - Médecins : 53
   - Infirmiers : 220
   - Aides-soignants : 195
```

#### Graphique de Comparaison

Histogramme comparant la prédiction à la distribution historique :
- **Barre verte** : Prédiction pour le jour
- **Courbe grise** : Distribution historique des jours similaires

**Utilisation** : Si la barre verte est dans la zone dense de la courbe grise, la prédiction est "normale". Si elle est dans la queue de distribution, c'est un jour atypique.

### Onglet 2 : Prédiction Multi-jours

#### Étape 1 : Sélectionner une plage

```
┌─────────────────────────┐
│ 📅 Date de début        │
│    [05/02/2026]         │
│                         │
│ 📅 Date de fin          │
│    [04/03/2026]         │
│                         │
│ → Durée : 28 jours      │
└─────────────────────────┘
```

**Limite** : Maximum 90 jours

#### Étape 2 : Options Avancées (Optionnel)

```
┌─────────────────────────────────────┐
│ ⚙️ Options avancées                 │
│                                     │
│ ☑ Prendre en compte la saisonnalité │
│ ☑ Inclure la tendance               │
│                                     │
│ Niveau de confiance :               │
│ [━━━━━━━━━●] 95%                   │
└─────────────────────────────────────┘
```

**Options** :
- **Saisonnalité** : Applique les variations saisonnières observées dans l'historique
- **Tendance** : Intègre la tendance à long terme (croissance/décroissance)
- **Niveau de confiance** : Largeur des intervalles de confiance (80-99%)

#### Étape 3 : Générer les Prédictions

Cliquez sur **"🔮 Générer prédictions"**

#### Résultats

##### 1. Graphique d'Évolution

Deux courbes :
- **Admissions** (bleu)
- **Passages urgences** (rouge)

Avec **bandes d'incertitude** (zones transparentes) représentant l'intervalle de confiance.

##### 2. Graphique d'Occupation

- **Ligne bleue** : Taux d'occupation prédit
- **Ligne rouge pointillée** : Seuil critique (85%)
- **Zone rouge** : Jours au-dessus du seuil

##### 3. Statistiques de la Période

```
┌────────────────────────────────────┐
│ Admissions moyennes : 342 ± 38     │
│ Urgences moyennes : 1015 ± 87      │
│ Occupation moyenne : 72.8% ± 7.2%  │
│ Occupation maximale : 89.5%        │
└────────────────────────────────────┘
```

##### 4. Jours Critiques

```
⚠️ JOURS CRITIQUES DÉTECTÉS

🔴 18/02/2026 : Occupation 87.2%
🔴 25/02/2026 : Occupation 89.5%
🔴 28/02/2026 : Occupation 86.8%

→ 3 jours critiques sur 28 (10.7%)
```

**Action** : Planifiez des ressources supplémentaires pour ces jours.

##### 5. Export

```
[📥 Télécharger CSV prédictions]
```

**Contenu du CSV** :
- Date, Jour semaine, Admissions prévues, Urgences prévues, Occupation prévue, Intervalle min, Intervalle max

### Onglet 3 : Upload Modèle ML

**Objectif** : Importer le modèle `.pkl` créé par votre collègue.

#### Zone de Upload

```
┌────────────────────────────────────┐
│ 📤 Uploader votre modèle ML        │
│                                    │
│ [Choisir un fichier .pkl]          │
│                                    │
│ ou glisser-déposer ici             │
└────────────────────────────────────┘
```

**Étapes** :
1. Cliquez sur "Choisir un fichier"
2. Sélectionnez le fichier `model_prediction.pkl`
3. Attendez la confirmation "✅ Modèle importé avec succès"
4. Cliquez sur **"🔄 Recharger l'application"**

**Après l'import** :
- L'application utilisera automatiquement le modèle ML pour toutes les prédictions
- Le modèle statistique de secours ne sera plus utilisé
- Un indicateur "🤖 Modèle ML actif" apparaîtra dans l'interface

#### Documentation pour le Modèle

Section détaillant les features attendues par le modèle et un exemple de code pour sauvegarder le modèle au bon format.

---

## 💡 Page 5 : Recommandations

**Objectif** : Obtenir des recommandations automatiques pour optimiser la gestion hospitalière.

### Onglet 1 : Recommandations du Jour

#### Section 1 : État Actuel

```
┌──────────────┬──────────────┬──────────────┐
│ Occupation   │  Personnel   │   Tendance   │
├──────────────┼──────────────┼──────────────┤
│ 🔴 87.3%     │ 🟢 92.5%     │ ↗️ +5.2%     │
│ CRITIQUE     │ NORMAL       │ HAUSSE       │
└──────────────┴──────────────┴──────────────┘
```

**Indicateurs de couleur** :
- 🔴 CRITIQUE : Action immédiate requise
- 🟠 ATTENTION : Surveillance renforcée
- 🟢 NORMAL : Situation maîtrisée

#### Section 2 : Recommandations Prioritaires

Les recommandations sont triées par priorité :

##### 🔴 PRIORITÉ CRITIQUE (Action immédiate : 0-4h)

```
▶️ Saturation des lits - Plan blanc à envisager

Le taux d'occupation actuel (87.3%) dépasse le seuil 
critique de 85%. Risque élevé de refus d'admission.

📊 Impact : Réduction des refus d'admission, amélioration 
           de la qualité des soins

⏱️ Délai : Immédiat (0-4h)

✅ Actions concrètes :
   • Activer le plan blanc niveau 1
   • Identifier les lits mobilisables (chirurgie ambulatoire)
   • Préparer l'ouverture de lits supplémentaires
   • Accélérer les sorties des patients stabilisés
   • Communication SAMU pour répartition des patients
```

##### 🟠 PRIORITÉ HAUTE (Action rapide : 4-24h)

```
▶️ Tendance occupation à la hausse

Augmentation de 5.2% détectée sur les 7 derniers jours.
Risque de saturation dans les prochaines 48-72h.

📊 Impact : Anticipation de la saturation
⏱️ Délai : Court terme (24-72h)

✅ Actions concrètes :
   • Préparer plan de contingence
   • Augmenter la veille quotidienne
   • Prévoir des ressources additionnelles
   • Anticiper les besoins en personnel
```

##### 🟡 PRIORITÉ MOYENNE (Action préventive : 1-7 jours)

```
▶️ Surveillance renforcée recommandée

L'occupation est dans la zone haute mais stable.
Maintenir une vigilance accrue.

📊 Impact : Prévention de la saturation
⏱️ Délai : Moyen terme (1-2 semaines)

✅ Actions concrètes :
   • Suivi quotidien des indicateurs
   • Préparation des lits additionnels
   • Communication renforcée avec les services
```

##### 🔵 OPTIMISATION (Amélioration continue)

```
▶️ Optimiser les plannings chirurgicaux

Les conditions actuelles permettent d'optimiser 
l'utilisation des ressources.

📊 Impact : Efficience opérationnelle
⏱️ Délai : Moyen terme (1-2 semaines)

✅ Actions concrètes :
   • Programmer les interventions reportées
   • Former le personnel sur les nouvelles procédures
   • Effectuer la maintenance préventive des équipements
```

#### Section 3 : Recommandations Contextuelles

En fonction des événements actifs :

```
🦠 RECOMMANDATIONS SPÉCIFIQUES - ÉPIDÉMIE

✅ Mettre en place des mesures d'isolement
✅ Renforcer les stocks d'EPI (masques, gants)
✅ Activer le protocole hygiène renforcée
✅ Communication préventive au personnel
```

### Onglet 2 : Planification Hebdomadaire

#### Section 1 : Analyse par Jour

Graphiques en barres avec barres d'erreur :
- **Admissions moyennes** par jour de la semaine
- **Taux d'occupation moyen** par jour

**Exemple de lecture** :
```
Lundi    : 385 ± 42 admissions (occupation 78%)
Mardi    : 370 ± 38 admissions (occupation 76%)
...
Dimanche : 280 ± 35 admissions (occupation 65%)
```

#### Section 2 : Recommandations par Jour

Accordéons pour chaque jour de la semaine :

```
▼ 📅 Lundi (Activité HAUTE - 385 admissions)

🔴 PRIORITÉS
• Renforcer les urgences dès 6h du matin
• Prévoir +2 médecins aux admissions
• Préparer 30 lits supplémentaires
• Coordination renforcée avec le SAMU

🟡 PRÉVENTIF
• Brief équipes à 7h sur la charge attendue
• Vérifier disponibilité des lits la veille
```

```
▼ 📅 Dimanche (Activité BASSE - 280 admissions)

🟢 OPPORTUNITÉS
• Programmer les interventions non-urgentes
• Effectuer la maintenance des équipements
• Formation du personnel (ateliers pratiques)
• Revue des dossiers complexes
```

#### Section 3 : Synthèse Hebdomadaire

```
📊 SYNTHÈSE DE LA SEMAINE

Jours à forte activité : Lundi, Mardi, Jeudi
Jours calmes : Mercredi, Samedi, Dimanche

🎯 Stratégie recommandée :
• Concentration des ressources Lun-Mar-Jeu
• Planification des congés Mer-Sam-Dim
• Interventions programmées Sam-Dim
```

### Onglet 3 : Optimisation Stratégique

#### Section 1 : Tendances Long Terme

##### Graphique 1 : Évolution Mensuelle

Ligne montrant l'évolution sur 3 ans des :
- Admissions totales/mois
- Urgences totales/mois

**Utilisation** : Identifiez les tendances de croissance ou décroissance.

##### Graphique 2 : Patterns Saisonniers

Bar chart par saison :
```
Hiver     : ████████████████ 425 adm/jour
Printemps : ███████████░░░░░ 360 adm/jour
Été       : ██████████░░░░░░ 320 adm/jour
Automne   : ████████████░░░░ 380 adm/jour
```

#### Section 2 : Impact des Événements

Tableau des événements spéciaux avec leur impact :

```
Événement             Occurrences  Impact Admissions  Impact Urgences
Épidémie grippe            45           +16%              +22%
Canicule                   12           +12%              +35%
Vague de froid             15           +10%              +18%
Pollution                   8           +5%               +15%
```

**Utilisation** : Préparez-vous en fonction des événements à venir.

#### Section 3 : Analyse de Capacité

```
📊 ANALYSE DE CAPACITÉ (3 ans)

🛏️ Lits
   Occupation moyenne : 73.5%
   Occupation maximale : 95.2%
   Jours critiques (>85%) : 127 jours (11.6%)
   
👥 Personnel
   Couverture moyenne : 92.3%
   Jours sous-staffés (<85%) : 43 jours (3.9%)
```

**Recommandations automatiques** :

```
⚠️ RECOMMANDATIONS CAPACITÉ

📌 11.6% de jours critiques > 10% (seuil acceptable)
   → Augmentation de capacité recommandée : +80 lits
   → Coût estimé : 14.6M € (construction + équipement)
   → Réduction attendue jours critiques : -75%

📌 3.9% de jours sous-staffés < 5% (acceptable)
   → Situation RH maîtrisée
   → Maintenir les effectifs actuels
```

#### Section 4 : Optimisation RH

```
👥 ANALYSE RESSOURCES HUMAINES

Personnel actuel :
• Médecins : 58 (moyenne disponibles)
• Infirmiers : 228
• Aides-soignants : 205

Ratios observés :
• 1 médecin pour 28.4 patients
• 1 infirmier pour 7.2 patients
• 1 aide-soignant pour 8.1 patients

🎯 Recommandations :
• Recruter 3 médecins supplémentaires (cible : 1/25)
• Maintenir effectifs infirmiers (ratio optimal)
• Recruter 10 aides-soignants (cible : 1/7)
```

#### Section 5 : Calculateur ROI

Widget interactif pour calculer le retour sur investissement :

```
┌────────────────────────────────────────┐
│ 💰 CALCULATEUR DE ROI                  │
├────────────────────────────────────────┤
│ Réduction des jours critiques :       │
│ [━━━━━●━━━━━] 50%                     │
│                                        │
│ 💡 Résultats :                         │
│    Jours critiques évités : 64         │
│    Économies refus admission : 320K €  │
│    Économies lits urgence : 128K €     │
│    ROI total annuel : 448,000 €        │
│                                        │
│ ⏱️ Retour sur investissement : 2.3 ans│
└────────────────────────────────────────┘
```

**Utilisation** : Bougez le slider pour voir l'impact financier de différents scénarios d'optimisation.

#### Section 6 : Scénarios d'Optimisation

Cartes présentant différentes stratégies :

```
┌─────────────────────────────────────────┐
│ 📋 SCÉNARIO 1 : Optimisation Capacité   │
├─────────────────────────────────────────┤
│ Investissement : 14.6M €                │
│ Actions : +80 lits, rénovation          │
│ Bénéfices annuels : 620K €              │
│ ROI : 23.5 ans                          │
│                                         │
│ ✅ Recommandé si : Croissance activité  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 📋 SCÉNARIO 2 : Optimisation RH         │
├─────────────────────────────────────────┤
│ Investissement : 1.2M €/an              │
│ Actions : +13 personnels                │
│ Bénéfices annuels : 280K €              │
│ ROI : 4.3 ans                           │
│                                         │
│ ✅ Recommandé si : Sous-staffing >5%    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 📋 SCÉNARIO 3 : Optimisation Processus  │
├─────────────────────────────────────────┤
│ Investissement : 500K € (logiciels)     │
│ Actions : Digitalisation, IA            │
│ Bénéfices annuels : 450K €              │
│ ROI : 1.1 an                            │
│                                         │
│ ✅ Recommandé : Impact rapide et élevé  │
└─────────────────────────────────────────┘
```

---

## ⚙️ Paramètres et Configuration

### Modifier les Seuils d'Alerte

Les seuils sont définis dans `app.py` :

```python
# Ligne ~200
if current_occupation > 0.85:  # Seuil critique occupation
    status = "CRITIQUE"
    
if current_staff < 0.85:  # Seuil minimum personnel
    status = "CRITIQUE"
```

**Pour modifier** : Éditez ces valeurs et relancez l'application.

### Changer les Coûts de Simulation

Dans `pages/simulation.py` :

```python
# Ligne ~320
cost_per_bed = 500  # €/lit/jour
cost_per_staff = 300  # €/personnel/jour
```

---

## 🐛 Résolution de Problèmes

### Le Dashboard ne se Lance Pas

```bash
# Vérifier que Streamlit est installé
pip list | grep streamlit

# Réinstaller si nécessaire
pip install --upgrade streamlit
```

### Erreur de Chargement des Données

```
FileNotFoundError: Jeu de données - Smart Care - *.csv
```

**Solution** : Vérifiez que vous êtes dans le bon répertoire :
```bash
cd "c:\Users\evan_\Desktop\SCProject\SmartCare-Analytics"
ls  # Doit afficher data/raw/
```

### Le Modèle ML n'est Pas Détecté

**Symptôme** : "⚠️ Modèle ML non disponible" affiché

**Solution** :
1. Vérifiez la présence des artefacts dans `ML/artifacts/` (ex. `gradient_boosting.joblib`, `feature_columns.json`, `metrics.json`)
2. Dans l'onglet "Uploader Modèle ML", cliquez sur "🔄 Recharger l'application"

### Graphiques ne S'affichent Pas

**Solution** : 
```bash
pip install --upgrade plotly
```

### Performances Lentes

**Cause** : Cache désactivé ou données trop volumineuses

**Solution** : 
- Le cache est actif (`@st.cache_data`)
- Réduisez la plage de dates dans les filtres

---

## 📱 Raccourcis Clavier

- **R** : Recharger l'application
- **C** : Effacer le cache
- **Ctrl + K** : Ouvrir la palette de commandes
- **Ctrl + Click** sur un lien : Ouvrir dans un nouvel onglet

---

## 💡 Conseils d'Utilisation

### Pour une Présentation

1. **Commencez par Accueil** : Vue d'ensemble
2. **Montrez une Simulation** : Scénario épidémie sur 30 jours
3. **Prédiction** : 7 jours à venir
4. **Recommandations** : Actions concrètes

### Pour une Analyse Approfondie

1. **Analyse Exploratoire** : Identifiez les patterns
2. **Corrélations** : Trouvez les facteurs d'influence
3. **Simulation** : Testez plusieurs scénarios
4. **Recommandations Stratégiques** : ROI et optimisation

### Pour une Utilisation Quotidienne

1. **Accueil** : Check rapide des KPIs et alertes
2. **Recommandations du Jour** : Actions prioritaires
3. **Prédiction Simple** : Prévoir le lendemain

---

## 🎓 Aller Plus Loin

### Personnaliser les Analyses

Ajoutez vos propres calculs dans les pages :
```python
# Exemple : Ajouter un nouveau KPI
custom_metric = df['nombre_admissions'] / df['lits_total']
st.metric("Taux d'admission", f"{custom_metric.mean():.2f}")
```

### Créer un Nouveau Scénario

Éditez `pages/simulation.py` :
```python
# Ligne ~50
scenario_type = st.selectbox("Type", [
    "🦠 Épidémie",
    # ...
    "🆕 Mon Nouveau Scénario"  # Ajoutez ici
])
```

### Exporter vers PowerPoint

1. Faites des captures d'écran des graphiques
2. Utilisez les exports CSV pour créer des graphiques Excel
3. Utilisez les rapports TXT comme base pour les présentations

---

## 📞 Support

Pour toute question :
1. Consultez d'abord les guides :
   - [GUIDE_STREAMLIT.md](GUIDE_STREAMLIT.md) : Comprendre Streamlit
   - [ARCHITECTURE.md](ARCHITECTURE.md) : Structure de l'app
2. Vérifiez les commentaires dans le code
3. Testez avec des données réduites pour déboguer

---

**Bon usage du Dashboard Smart Care ! 🏥✨**

Projet réalisé dans le cadre du projet DATA - EPITECH Promo 2026
