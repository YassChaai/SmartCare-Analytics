"""Utilitaires de selection des features."""

from typing import List

import pandas as pd

from smartcare_model.config.constants import TARGET_COL


def select_feature_columns(df: pd.DataFrame) -> List[str]:
    """Selectionner les colonnes numeriques utilisees en train/inference.

    Exclut la cible, les admissions brutes et la date.

    Args:
        df: DataFrame de features.

    Returns:
        Liste des colonnes utilisees comme entrees modele.
    """
    exclude_cols = {
        TARGET_COL,
        "date",
        "nombre_admissions",
    }
    return [
        col
        for col in df.columns
        if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col])
    ]


# Alias retro-compatibilite pour l'ancien nom interne.
_select_feature_columns = select_feature_columns
