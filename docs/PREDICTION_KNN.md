# Prédiction avec K-NN Temporel et Facteur de Tendance

## 🎯 Problème résolu

**Problème initial** : Le modèle ML utilise des lags (admissions des jours précédents) pour faire des prédictions. Pour des dates en 2026, il utilisait les lags de décembre 2024, rendant les paramètres contextuels (météo, événements) quasi-inutiles.

**Solution implémentée** : Approche hybride ML + k-NN temporel avec facteur de tendance ajustable.

---

## 🔄 Fonctionnement

### **Mode automatique selon la date**

Le système détecte automatiquement si la date demandée est :
- **< 30 jours après dernière date historique** → Mode ML classique
- **> 30 jours après dernière date historique** → Mode k-NN avec lags synthétiques

### **Mode ML Classique** (date proche de l'historique)

1. Récupère la ligne de features pour la date exacte ou proche
2. Utilise les lags réels de l'historique
3. Applique les overrides météo/événement
4. Passe au modèle ML
5. Applique le facteur de tendance si configuré

### **Mode k-NN Temporel** (date éloignée de l'historique)

1. **Recherche de jours similaires** :
   - Compare la date cible avec tous les jours de l'historique (2022-2024)
   - Calcul de distance pondérée sur :
     - Jour de la semaine (poids 3.0)
     - Saison (poids 2.0)
     - Événement spécial (poids 2.5)
     - Conditions météo (poids 2.0)
     - Vacances scolaires (poids 1.5)
     - Température (poids 0.3, tolérance ±10°C)
   - Sélectionne les 10 jours les plus proches

2. **Génération de lags synthétiques** :
   - `adm_lag_1, 4, 7, 14, 28` = moyenne des admissions des jours similaires
   - `adm_roll_mean_7, 14, 28` = même moyenne
   - `adm_roll_std_7` = écart-type des jours similaires
   - `adm_diff_1, 7` = 0 (stabilité)

3. **Prédiction** :
   - Construit une ligne de features avec lags synthétiques
   - Applique les overrides météo/événement sur cette ligne
   - Passe au modèle ML
   - Applique le facteur de tendance

---

## 📈 Facteur de Tendance Temporelle

### **Calcul automatique**

```python
# Évolution 2022 → 2024
adm_2022 = moyenne(admissions_2022)
adm_2024 = moyenne(admissions_2024)

# Croissance annuelle
croissance = (adm_2024 / adm_2022) ^ (1/2) - 1

# Extrapolation vers 2026 (2 ans après 2024)
facteur_2026 = ((1 + croissance) ^ 2 - 1) * 100
```

### **Interface utilisateur**

- **Valeur automatique** : Affichée en info box avec détails du calcul
- **Checkbox** : "Utiliser tendance auto" (activée par défaut)
- **Slider personnalisé** : De -30% à +50%, disponible si checkbox décochée
- **Expander** : Détail du calcul pour transparence

### **Application**

```python
prediction_brute = model.predict(features)
prediction_ajustée = prediction_brute * (1 + facteur_tendance / 100)
```

Le facteur est appliqué **après** la prédiction du modèle ML, pour plus de transparence.

---

## 📊 Exemple d'utilisation

### Prédire le 15 février 2026

**Entrées utilisateur** :
- Date : 2026-02-15 (samedi)
- Température : 5°C
- Météo : Froid
- Événement : Épidémie grippe
- Vacances : Non

**Étapes système** :

1. **Détection** : 2026-02-15 est à 427 jours après dernier historique → Mode k-NN

2. **Recherche k-NN** :
   - Trouve 10 samedis de 2022-2024 avec :
     - Températures entre 0-10°C
     - Conditions froides
     - Épisodes grippaux
     - Hors vacances
     - En février/janvier/mars

3. **Lags synthétiques** :
   ```
   adm_lag_1 = 245 (moyenne des jours similaires)
   adm_lag_7 = 245
   adm_roll_mean_7 = 245
   ...
   ```

4. **Prédiction ML** : 258 admissions (brut)

5. **Tendance** : Facteur auto = +8.5% → 258 × 1.085 = **280 admissions**

---

## 🎨 Avantages de l'approche

✅ **Contextuel** : Les paramètres météo/événement impactent vraiment la prédiction  
✅ **Flexible** : Fonctionne pour n'importe quelle date future  
✅ **Transparent** : L'utilisateur comprend d'où vient la prédiction  
✅ **Ajustable** : Facteur de tendance modifiable selon expertise métier  
✅ **Robuste** : Bascule automatique entre modes ML/k-NN  
✅ **Éducatif** : Explications détaillées dans l'interface  

---

## 🔧 Fichiers modifiés

- **Nouveau** : `ML/smartcare_model/inference/similarity.py` - Fonctions k-NN et tendance
- **Modifié** : `ML/smartcare_model/inference/__init__.py` - Export des nouvelles fonctions
- **Modifié** : `ML/smartcare_model/pipeline.py` - Ajout à l'API publique
- **Modifié** : `app/pages/prediction.py` - Intégration complète de la logique

---

## 🚀 Prochaines améliorations possibles

- Ajuster les poids k-NN selon les performances observées
- Ajouter un mode "facteurs avancés" (démographie, politique de santé, etc.)
- Visualiser les jours similaires trouvés dans l'interface
- Permettre à l'utilisateur de choisir k (nombre de voisins)
- Sauvegarder les facteurs de tendance personnalisés par utilisateur
