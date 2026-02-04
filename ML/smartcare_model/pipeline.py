"""Facade retro-compatible pour le pipeline ML.

Ce module conserve l'API publique historique tout en deleguant
aux sous-modules refactorises.
"""

from smartcare_model.artifacts.store import load_artifacts, load_feature_columns, save_artifacts
from smartcare_model.config.constants import DATA_FILENAME_HINT, DEFAULT_MODEL_NAME, TARGET_COL
from smartcare_model.config.paths import ARTIFACTS_DIR, ML_ROOT, RAW_DIR
from smartcare_model.data.loading import load_raw_dataframe
from smartcare_model.features.engineering import build_feature_dataframe
from smartcare_model.features.selection import _select_feature_columns
from smartcare_model.inference.predict import (
    apply_overrides,
    predict_from_features,
    prepare_prediction_row,
)
from smartcare_model.inference.similarity import (
    calculate_historical_trend,
    compute_synthetic_lags,
    evaluate_knn_quality,
    find_similar_days,
)
from smartcare_model.training.trainer import train_models

BASE_DIR = ML_ROOT

__all__ = [
    "ARTIFACTS_DIR",
    "BASE_DIR",
    "DATA_FILENAME_HINT",
    "DEFAULT_MODEL_NAME",
    "RAW_DIR",
    "TARGET_COL",
    "apply_overrides",
    "build_feature_dataframe",
    "calculate_historical_trend",
    "compute_synthetic_lags",
    "evaluate_knn_quality",
    "find_similar_days",
    "load_artifacts",
    "load_feature_columns",
    "load_raw_dataframe",
    "predict_from_features",
    "prepare_prediction_row",
    "save_artifacts",
    "train_models",
    "_select_feature_columns",
]
