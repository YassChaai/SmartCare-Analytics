"""Metriques d'evaluation pour la prediction d'admissions."""

from typing import Dict

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def mape(y_true, y_pred) -> float:
    """Calculer le MAPE (Mean Absolute Percentage Error).

    Args:
        y_true: Valeurs reelles.
        y_pred: Valeurs predites.

    Returns:
        Valeur MAPE en pourcentage, ou NaN si toutes les valeurs reelles sont nulles.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mask = y_true != 0
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def smape(y_true, y_pred) -> float:
    """Calculer le sMAPE (Symmetric Mean Absolute Percentage Error).

    Args:
        y_true: Valeurs reelles.
        y_pred: Valeurs predites.

    Returns:
        Valeur sMAPE en pourcentage, ou NaN si le denominateur est nul.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    mask = denominator != 0
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs(y_true[mask] - y_pred[mask]) / denominator[mask]) * 100)


def evaluate(y_true, y_pred) -> Dict[str, float]:
    """Calculer les metriques d'evaluation pour un vecteur de prediction.

    Args:
        y_true: Valeurs reelles.
        y_pred: Valeurs predites.

    Returns:
        Dictionnaire contenant MAE, RMSE, MAPE et sMAPE.
    """
    return {
        "mae": mean_absolute_error(y_true, y_pred),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mape": mape(y_true, y_pred),
        "smape": smape(y_true, y_pred),
    }


# Alias retro-compatibilite.
_mape = mape
_smape = smape
_evaluate = evaluate
