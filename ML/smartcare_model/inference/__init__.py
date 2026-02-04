"""Points d'entree d'inference."""

from smartcare_model.inference.predict import (
    apply_overrides,
    predict_from_features,
    prepare_prediction_row,
)
from smartcare_model.inference.similarity import (
    calculate_historical_trend,
    compute_synthetic_lags,
    find_similar_days,
)

__all__ = [
    "apply_overrides",
    "predict_from_features",
    "prepare_prediction_row",
    "calculate_historical_trend",
    "compute_synthetic_lags",
    "find_similar_days",
]
