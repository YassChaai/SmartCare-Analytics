"""Module pour rechercher des jours similaires dans l'historique (k-NN temporel)."""

from typing import List, Dict, Optional
import pandas as pd
import numpy as np


def find_similar_days(
    feature_df: pd.DataFrame,
    target_date: pd.Timestamp,
    target_features: Dict[str, any],
    k: int = 10,
    weights: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """Trouver les k jours les plus similaires dans l'historique.
    
    Args:
        feature_df: DataFrame historique avec features.
        target_date: Date cible pour la prédiction.
        target_features: Dict des features contextuelles (meteo, saison, jour, temperature, etc.).
        k: Nombre de jours similaires à retourner.
        weights: Poids optionnels pour chaque feature dans le calcul de distance.
    
    Returns:
        DataFrame avec les k jours les plus similaires (triés par distance).
    """
    if weights is None:
        # Poids par défaut : plus de poids sur jour_semaine et saison
        weights = {
            "jour_semaine": 3.0,
            "saison": 2.0,
            "vacances_scolaires": 1.5,
            "temperature": 0.3,
            "meteo": 2.0,
            "evenement": 2.5,
        }
    
    # Extraire le jour de semaine et la saison de la date cible
    jour_map = {
        0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
        4: "Vendredi", 5: "Samedi", 6: "Dimanche"
    }
    target_jour = jour_map[target_date.weekday()]
    
    month = target_date.month
    if month in [12, 1, 2]:
        target_saison = "Hiver"
    elif month in [3, 4, 5]:
        target_saison = "Printemps"
    elif month in [6, 7, 8]:
        target_saison = "Été"
    else:
        target_saison = "Automne"
    
    # Copier le dataframe pour calcul de distance
    df = feature_df.copy()
    
    # Calculer les distances
    distances = np.zeros(len(df))
    
    # Distance sur jour de la semaine (0 si même jour, 1 sinon)
    if "jour_semaine" in df.columns:
        jour_distance = (df["jour_semaine"] != target_jour).astype(float)
        distances += jour_distance * weights["jour_semaine"]
    
    # Distance sur saison
    if "saison" in df.columns:
        saison_distance = (df["saison"] != target_saison).astype(float)
        distances += saison_distance * weights["saison"]
    
    # Distance sur vacances scolaires
    if "vacances_scolaires" in df.columns and "vacances" in target_features:
        vacances_distance = (df["vacances_scolaires"] != target_features["vacances"]).astype(float)
        distances += vacances_distance * weights["vacances_scolaires"]
    
    # Distance sur température (euclidienne normalisée)
    if "temperature_moyenne" in df.columns and "temperature" in target_features:
        temp_diff = np.abs(df["temperature_moyenne"] - target_features["temperature"])
        # Normaliser : tolérance de ±10°C = distance de 1
        temp_distance = temp_diff / 10.0
        distances += temp_distance * weights["temperature"]
    
    # Distance sur météo (one-hot matching)
    if "meteo" in target_features:
        meteo_cols = [c for c in df.columns if c.startswith("meteo_")]
        if meteo_cols:
            # Trouver la météo active pour chaque jour
            meteo_match = np.zeros(len(df))
            target_meteo_col = f"meteo_{target_features['meteo']}"
            if target_meteo_col in df.columns:
                meteo_match = df[target_meteo_col].fillna(0).values
            # Distance = 0 si match, 1 sinon
            meteo_distance = 1 - meteo_match
            distances += meteo_distance * weights["meteo"]
    
    # Distance sur événement spécial
    if "evenement" in target_features:
        event_cols = [c for c in df.columns if c.startswith("event_")]
        if event_cols:
            event_match = np.zeros(len(df))
            target_event_col = f"event_{target_features['evenement']}"
            if target_event_col in df.columns:
                event_match = df[target_event_col].fillna(0).values
            event_distance = 1 - event_match
            distances += event_distance * weights["evenement"]
    
    # Ajouter la colonne distance
    df["similarity_distance"] = distances
    
    # Trier par distance et retourner les k plus proches
    similar_days = df.nsmallest(k, "similarity_distance")
    
    return similar_days


def compute_synthetic_lags(
    similar_days: pd.DataFrame,
    lag_periods: List[int] = [1, 4, 7, 14, 28],
    window_sizes: List[int] = [7, 14, 28],
) -> Dict[str, float]:
    """Calculer des lags synthétiques basés sur les jours similaires.
    
    Args:
        similar_days: DataFrame des jours similaires trouvés par find_similar_days.
        lag_periods: Liste des périodes de lag à calculer.
        window_sizes: Liste des tailles de fenêtre pour rolling means.
    
    Returns:
        Dict avec les valeurs de lags synthétiques.
    """
    # Moyenne des admissions des jours similaires
    base_admissions = similar_days["nombre_admissions"].mean()
    
    synthetic_lags = {}
    
    # Lags simples (utiliser la moyenne)
    for lag in lag_periods:
        synthetic_lags[f"adm_lag_{lag}"] = base_admissions
    
    # Rolling means (utiliser la moyenne aussi)
    for window in window_sizes:
        synthetic_lags[f"adm_roll_mean_{window}"] = base_admissions
    
    # Rolling std (utiliser l'écart-type des jours similaires)
    synthetic_lags["adm_roll_std_7"] = similar_days["nombre_admissions"].std()
    
    # Différences (approximer à 0 pour stabilité)
    synthetic_lags["adm_diff_1"] = 0.0
    synthetic_lags["adm_diff_7"] = 0.0
    
    return synthetic_lags


def calculate_historical_trend(
    df: pd.DataFrame,
    start_year: int = 2022,
    end_year: int = 2024,
) -> Dict[str, float]:
    """Calculer la tendance historique d'évolution des admissions.
    
    Args:
        df: DataFrame historique avec colonnes 'annee' et 'nombre_admissions'.
        start_year: Année de début pour le calcul.
        end_year: Année de fin pour le calcul.
    
    Returns:
        Dict avec le facteur de tendance annuelle et les statistiques.
    """
    # Vérifier que les colonnes nécessaires existent
    if "annee" not in df.columns or "nombre_admissions" not in df.columns:
        return {
            "tendance_annuelle_pct": 0.0,
            "facteur_2026_pct": 0.0,
            "adm_moyenne_start": 0.0,
            "adm_moyenne_end": 0.0,
        }
    
    # Calculer les moyennes par année
    df_start = df[df["annee"] == start_year]
    df_end = df[df["annee"] == end_year]
    
    if len(df_start) == 0 or len(df_end) == 0:
        return {
            "tendance_annuelle_pct": 0.0,
            "facteur_2026_pct": 0.0,
            "adm_moyenne_start": 0.0,
            "adm_moyenne_end": 0.0,
        }
    
    adm_start = df_start["nombre_admissions"].mean()
    adm_end = df_end["nombre_admissions"].mean()
    
    # Calculer la croissance annuelle
    n_years = end_year - start_year
    if n_years > 0 and adm_start > 0:
        croissance_annuelle = (adm_end / adm_start) ** (1 / n_years) - 1
    else:
        croissance_annuelle = 0.0
    
    # Extrapoler vers 2026 (2 ans après 2024)
    facteur_2026 = ((1 + croissance_annuelle) ** 2 - 1) * 100
    
    return {
        "tendance_annuelle_pct": croissance_annuelle * 100,
        "facteur_2026_pct": facteur_2026,
        "adm_moyenne_start": adm_start,
        "adm_moyenne_end": adm_end,
    }
