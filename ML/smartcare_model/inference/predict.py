"""Utilitaires d'inference pour generer des predictions."""

from typing import Dict, Optional, List

import pandas as pd


def prepare_prediction_row(
    feature_df: pd.DataFrame,
    feature_cols: List[str],
    target_date: Optional[str] = None,
) -> pd.DataFrame:
    """Selectionner la ligne de prediction depuis un DataFrame de features.

    Args:
        feature_df: DataFrame de features contenant la colonne ``date``.
        feature_cols: Liste ordonnee des colonnes attendues par le modele.
        target_date: Date optionnelle (YYYY-MM-DD) pour selectionner une ligne.

    Returns:
        DataFrame a une ligne, pret pour la prediction.

    Raises:
        ValueError: Si ``target_date`` est fourni mais absent des donnees.
    """
    df = feature_df.dropna(subset=feature_cols).copy()
    if target_date:
        date = pd.to_datetime(target_date)
        row = df[df["date"] == date]
        if row.empty:
            raise ValueError(f"No data found for date {target_date}.")
        return row.tail(1)
    return df.tail(1)


def apply_overrides(
    row: pd.DataFrame,
    feature_cols: List[str],
    meteo: Optional[str] = None,
    event: Optional[str] = None,
) -> pd.DataFrame:
    """Appliquer des overrides one-hot meteo ou evenement.

    Args:
        row: DataFrame a une ligne utilise pour la prediction.
        feature_cols: Liste ordonnee des colonnes.
        meteo: Valeur meteo optionnelle (suffixe sans ``meteo_``).
        event: Valeur evenement optionnelle (suffixe sans ``event_``).

    Returns:
        DataFrame mis a jour avec les overrides demandes.
    """
    row = row.copy()
    if meteo:
        meteo_col = f"meteo_{meteo}"
        meteo_cols = [c for c in feature_cols if c.startswith("meteo_")]
        for col in meteo_cols:
            row[col] = 0
        if meteo_col in row.columns:
            row[meteo_col] = 1
    if event:
        event_col = f"event_{event}"
        event_cols = [c for c in feature_cols if c.startswith("event_")]
        for col in event_cols:
            row[col] = 0
        if event_col in row.columns:
            row[event_col] = 1
    return row


def predict_from_features(
    row: pd.DataFrame,
    model,
    feature_cols: List[str],
    safety_margin: float = 0.10,
) -> Dict[str, float]:
    """Generer la prediction et une estimation securisee.

    Args:
        row: DataFrame a une ligne pour la prediction.
        model: Modele entraine implementant ``predict``.
        feature_cols: Liste ordonnee des colonnes features.
        safety_margin: Marge en pourcentage pour ``prediction_safe``.

    Returns:
        Dictionnaire avec prediction brute, prediction securisee, et date.
    """
    X = row[feature_cols].astype(float)
    pred = float(model.predict(X)[0])
    return {
        "prediction": pred,
        "prediction_safe": pred * (1 + safety_margin),
        "date_J": row["date"].iloc[0].date(),
    }
