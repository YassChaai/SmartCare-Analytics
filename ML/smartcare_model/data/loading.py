"""Utilitaires de chargement des donnees brutes."""

import os
from pathlib import Path
from typing import List

import pandas as pd

from smartcare_model.config.constants import DATA_FILENAME_HINT, NUMERIC_COLUMNS
from smartcare_model.config.paths import RAW_DIR


def _to_float(series: pd.Series) -> pd.Series:
    """Convertir des chaines numeriques avec virgule en float.

    Args:
        series: Serie a convertir en valeurs numeriques.

    Returns:
        Serie numerique avec valeurs invalides en NaN.
    """
    return pd.to_numeric(series.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def _get_data_path(raw_dir: Path = RAW_DIR, filename_hint: str = DATA_FILENAME_HINT) -> Path:
    """Resoudre le chemin du dataset brut via un indice de nom de fichier.

    Args:
        raw_dir: Dossier contenant les CSV bruts.
        filename_hint: Sous-chaine attendue dans le nom de fichier.

    Returns:
        Chemin vers le premier fichier correspondant.

    Raises:
        FileNotFoundError: Si aucun fichier ne correspond dans ``raw_dir``.
    """
    matches: List[str] = [f for f in os.listdir(raw_dir) if filename_hint in f]
    if not matches:
        raise FileNotFoundError(
            f"No file containing '{filename_hint}' found in {raw_dir}"
        )
    return raw_dir / matches[0]


def load_raw_dataframe() -> pd.DataFrame:
    """Charger et nettoyer le dataset brut.

    Etapes:
    - Lecture du CSV depuis ``RAW_DIR``.
    - Parsing de la colonne ``date`` en datetime.
    - Tri des donnees par date.
    - Conversion des colonnes numeriques avec virgule.

    Returns:
        DataFrame nettoye, pret pour le feature engineering.
    """
    df = pd.read_csv(_get_data_path())
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df = df.sort_values("date").reset_index(drop=True)

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = _to_float(df[col])
    return df
