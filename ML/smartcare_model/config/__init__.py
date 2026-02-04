"""Couche de configuration: chemins et constantes."""

from smartcare_model.config.constants import (
    DATA_FILENAME_HINT,
    DEFAULT_MODEL_NAME,
    NUMERIC_COLUMNS,
    TARGET_COL,
)
from smartcare_model.config.paths import ARTIFACTS_DIR, DATA_DIR, ML_ROOT, RAW_DIR

__all__ = [
    "ARTIFACTS_DIR",
    "DATA_DIR",
    "DATA_FILENAME_HINT",
    "DEFAULT_MODEL_NAME",
    "ML_ROOT",
    "NUMERIC_COLUMNS",
    "RAW_DIR",
    "TARGET_COL",
]
