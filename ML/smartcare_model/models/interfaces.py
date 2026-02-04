"""Interfaces de modeles pour garantir une API commune."""

from typing import Protocol

import pandas as pd


class ModelProtocol(Protocol):
    """Interface commune attendue par l'entrainement et l'inference.

    Les implementations doivent supporter ``fit`` et ``predict``. La
    persistance est geree par la couche artifacts (joblib).
    """

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "ModelProtocol":
        """Entrainer le modele sur les donnees."""

    def predict(self, X: pd.DataFrame):
        """Generer des predictions a partir des features."""
