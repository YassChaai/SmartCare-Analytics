"""Pipeline de feature engineering pour la prediction d'admissions."""

from typing import List

import numpy as np
import pandas as pd

from smartcare_model.config.constants import TARGET_COL


def _add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajouter des features de calendrier.

    Args:
        df: DataFrame contenant ``date`` et ``vacances_scolaires``.

    Returns:
        DataFrame avec les features calendrier ajoutees.
    """
    df["is_weekend"] = (df["date"].dt.weekday >= 5).astype(int)
    df["is_holiday"] = df["vacances_scolaires"].astype(int)
    df["veille_holiday"] = df["is_holiday"].shift(-1).fillna(0).astype(int)
    df["lendemain_holiday"] = df["is_holiday"].shift(1).fillna(0).astype(int)
    return df


def _add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajouter des lags et stats glissantes sur les admissions.

    Args:
        df: DataFrame contenant ``nombre_admissions``.

    Returns:
        DataFrame avec lags, moyennes glissantes, ecart-type, et differences.
    """
    for lag in [1, 4, 7, 14, 28]:
        df[f"adm_lag_{lag}"] = df["nombre_admissions"].shift(lag)

    for window in [7, 14, 28]:
        df[f"adm_roll_mean_{window}"] = (
            df["nombre_admissions"].shift(1).rolling(window).mean()
        )

    df["adm_roll_std_7"] = df["nombre_admissions"].shift(1).rolling(7).std()
    df["adm_diff_1"] = df["nombre_admissions"].diff(1)
    df["adm_diff_7"] = df["nombre_admissions"].diff(7)
    return df


def _add_rule_multiplier_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajouter des multiplicateurs issus des regles metier.

    Args:
        df: DataFrame contenant calendar, saison, meteo et evenements.

    Returns:
        DataFrame avec multiplicateurs de regles.
    """
    jour_map = {
        "Lundi": 1.10,
        "Mardi": 1.05,
        "Mercredi": 1.00,
        "Jeudi": 1.00,
        "Vendredi": 0.95,
        "Samedi": 0.85,
        "Dimanche": 0.80,
    }
    saison_map = {
        "Hiver": 1.15,
        "Printemps": 1.00,
        "Ete": 0.90,
        "Été": 0.90,
        "Automne": 1.05,
    }

    df["mult_jour_semaine"] = df["jour_semaine"].map(jour_map).fillna(1.0)
    df["mult_saison"] = df["saison"].map(saison_map).fillna(1.0)
    df["mult_vacances"] = np.where(df["vacances_scolaires"] == 1, 0.90, 1.00)

    df["mult_canicule"] = np.select(
        [df["temperature_max"] >= 35, df["temperature_max"] >= 30],
        [1.25, 1.10],
        default=1.00,
    )

    df["mult_evenement"] = 1.0 + df.get("impact_evenement_estime", 0).fillna(0)
    return df


def _add_target(df: pd.DataFrame) -> pd.DataFrame:
    """Creer la cible J+4.

    Args:
        df: DataFrame contenant ``nombre_admissions``.

    Returns:
        DataFrame avec la colonne cible ``y``.
    """
    df[TARGET_COL] = df["nombre_admissions"].shift(-4)
    return df


def _one_hot_encode(df: pd.DataFrame) -> pd.DataFrame:
    """Encoder en one-hot les colonnes meteo et evenements.

    Args:
        df: DataFrame contenant les colonnes categorielles.

    Returns:
        DataFrame avec colonnes one-hot ajoutees.
    """
    return pd.get_dummies(
        df,
        columns=["meteo_principale", "evenement_special"],
        prefix=["meteo", "event"],
        dummy_na=False,
    )


def build_feature_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Executer le pipeline complet de feature engineering.

    Args:
        raw_df: DataFrame brut charge depuis le CSV.

    Returns:
        DataFrame enrichi avec features et cible.
    """
    df = raw_df.copy()
    df = _add_target(df)
    df = _add_calendar_features(df)
    df = _add_lag_features(df)
    df = _add_rule_multiplier_features(df)
    df = _one_hot_encode(df)
    return df
