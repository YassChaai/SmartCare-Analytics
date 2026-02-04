"""Pipeline d'entrainement des modeles de prediction."""

from typing import Dict, Tuple

import pandas as pd

from smartcare_model.artifacts.store import save_artifacts
from smartcare_model.config.constants import TARGET_COL
from smartcare_model.config.paths import ARTIFACTS_DIR
from smartcare_model.data.loading import load_raw_dataframe
from smartcare_model.evaluation.metrics import evaluate
from smartcare_model.features.engineering import build_feature_dataframe
from smartcare_model.features.selection import select_feature_columns
from smartcare_model.models.registry import build_models


def _train_test_split(
    df: pd.DataFrame, train_ratio: float = 0.8
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Effectuer un split chronologique train/test.

    Args:
        df: DataFrame de features trie par date.
        train_ratio: Ratio utilise pour l'entrainement (debut de serie).

    Returns:
        Tuple (train_df, test_df).
    """
    split_idx = int(len(df) * train_ratio)
    return df.iloc[:split_idx], df.iloc[split_idx:]


def _build_baselines(test_df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Construire les predictions baseline sur le test.

    Args:
        test_df: DataFrame test contenant lags et multiplicateurs.

    Returns:
        Dictionnaire {nom_baseline: predictions}.
    """
    return {
        "baseline_lag_4": test_df["adm_lag_4"],
        "baseline_lag_7": test_df["adm_lag_7"],
        "baseline_roll_mean_7": test_df["adm_roll_mean_7"],
        "baseline_rules": (
            test_df["adm_roll_mean_7"]
            * test_df["mult_jour_semaine"]
            * test_df["mult_vacances"]
            * test_df["mult_saison"]
            * test_df["mult_evenement"]
        ),
    }


def train_models(
    train_ratio: float = 0.8,
    artifacts_dir=ARTIFACTS_DIR,
) -> Dict[str, Dict[str, float]]:
    """Entrainer les modeles, evaluer, et persister les artefacts.

    Args:
        train_ratio: Ratio du dataset utilise pour l'entrainement.
        artifacts_dir: Dossier de sortie des artefacts.

    Returns:
        Dictionnaire des metriques par modele ou baseline.

    Side Effects:
        Ecrit metrics, feature_columns et modeles sur disque.
    """
    raw_df = load_raw_dataframe()
    feature_df = build_feature_dataframe(raw_df)
    feature_cols = select_feature_columns(feature_df)
    feature_df = feature_df.dropna(subset=[TARGET_COL] + feature_cols).reset_index(drop=True)

    train_df, test_df = _train_test_split(feature_df, train_ratio=train_ratio)

    X_train, y_train = train_df[feature_cols], train_df[TARGET_COL]
    X_test, y_test = test_df[feature_cols], test_df[TARGET_COL]

    results: Dict[str, Dict[str, float]] = {}
    baselines = _build_baselines(test_df)
    for name, preds in baselines.items():
        results[name] = evaluate(y_test, preds)

    models = build_models()

    trained_models: Dict[str, object] = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        results[name] = evaluate(y_test, preds)
        trained_models[name] = model

    save_artifacts(feature_cols, results, trained_models, artifacts_dir=artifacts_dir)
    return results
