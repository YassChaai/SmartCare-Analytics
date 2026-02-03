import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
DATA_FILENAME_HINT = "daily_hospital_context_2022-2024_generated.csv"

ARTIFACTS_DIR = BASE_DIR / "artifacts"
DEFAULT_MODEL_NAME = "gradient_boosting"
TARGET_COL = "y"


def _to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def _get_data_path() -> Path:
    matches = [f for f in os.listdir(RAW_DIR) if DATA_FILENAME_HINT in f]
    if not matches:
        raise FileNotFoundError(
            f"No file containing '{DATA_FILENAME_HINT}' found in {RAW_DIR}"
        )
    return RAW_DIR / matches[0]


def load_raw_dataframe() -> pd.DataFrame:
    df = pd.read_csv(_get_data_path())
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df = df.sort_values("date").reset_index(drop=True)

    numeric_cols = [
        "temperature_moyenne",
        "temperature_min",
        "temperature_max",
        "indice_chaleur",
        "indice_froid",
        "taux_occupation_lits",
        "taux_couverture_personnel",
        "impact_evenement_estime",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = _to_float(df[col])
    return df


def _add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df["is_weekend"] = (df["date"].dt.weekday >= 5).astype(int)
    df["is_holiday"] = df["vacances_scolaires"].astype(int)
    df["veille_holiday"] = df["is_holiday"].shift(-1).fillna(0).astype(int)
    df["lendemain_holiday"] = df["is_holiday"].shift(1).fillna(0).astype(int)
    return df


def _add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
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
    df[TARGET_COL] = df["nombre_admissions"].shift(-4)
    return df


def _one_hot_encode(df: pd.DataFrame) -> pd.DataFrame:
    return pd.get_dummies(
        df,
        columns=["meteo_principale", "evenement_special"],
        prefix=["meteo", "event"],
        dummy_na=False,
    )


def build_feature_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df = _add_target(df)
    df = _add_calendar_features(df)
    df = _add_lag_features(df)
    df = _add_rule_multiplier_features(df)
    df = _one_hot_encode(df)
    return df


def _select_feature_columns(df: pd.DataFrame) -> List[str]:
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


def _train_test_split(df: pd.DataFrame, train_ratio: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
    split_idx = int(len(df) * train_ratio)
    return df.iloc[:split_idx], df.iloc[split_idx:]


def _mape(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mask = y_true != 0
    if not mask.any():
        return np.nan
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def _smape(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    mask = denominator != 0
    if not mask.any():
        return np.nan
    return np.mean(np.abs(y_true[mask] - y_pred[mask]) / denominator[mask]) * 100


def _evaluate(y_true, y_pred) -> Dict[str, float]:
    return {
        "mae": mean_absolute_error(y_true, y_pred),
        "mape": _mape(y_true, y_pred),
        "smape": _smape(y_true, y_pred),
    }


def save_artifacts(
    feature_cols: List[str],
    results: Dict[str, Dict[str, float]],
    trained_models: Dict[str, object],
    artifacts_dir: Path = ARTIFACTS_DIR,
) -> None:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    with open(artifacts_dir / "feature_columns.json", "w") as f:
        json.dump(feature_cols, f, indent=2)
    with open(artifacts_dir / "metrics.json", "w") as f:
        json.dump(results, f, indent=2)
    for name, model in trained_models.items():
        joblib.dump(model, artifacts_dir / f"{name}.joblib")


def train_models(
    train_ratio: float = 0.8,
    artifacts_dir: Path = ARTIFACTS_DIR,
) -> Dict[str, Dict[str, float]]:
    raw_df = load_raw_dataframe()
    feature_df = build_feature_dataframe(raw_df)
    feature_cols = _select_feature_columns(feature_df)
    feature_df = feature_df.dropna(subset=[TARGET_COL] + feature_cols).reset_index(drop=True)

    train_df, test_df = _train_test_split(feature_df, train_ratio=train_ratio)

    X_train, y_train = train_df[feature_cols], train_df[TARGET_COL]
    X_test, y_test = test_df[feature_cols], test_df[TARGET_COL]

    baselines = {
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

    results: Dict[str, Dict[str, float]] = {}
    for name, preds in baselines.items():
        results[name] = _evaluate(y_test, preds)

    models = {
        "random_forest": RandomForestRegressor(
            n_estimators=300,
            random_state=42,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
    }

    trained_models: Dict[str, object] = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        results[name] = _evaluate(y_test, preds)
        trained_models[name] = model

    save_artifacts(feature_cols, results, trained_models, artifacts_dir=artifacts_dir)
    return results


def load_feature_columns(artifacts_dir: Path = ARTIFACTS_DIR) -> List[str]:
    path = artifacts_dir / "feature_columns.json"
    if not path.exists():
        raise FileNotFoundError("feature_columns.json not found. Run train_models() first.")
    with open(path, "r") as f:
        return json.load(f)


def load_artifacts(
    model_name: str = DEFAULT_MODEL_NAME,
    artifacts_dir: Path = ARTIFACTS_DIR,
):
    model_path = artifacts_dir / f"{model_name}.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"{model_path} not found. Train the model first.")
    model = joblib.load(model_path)
    feature_cols = load_feature_columns(artifacts_dir)
    return model, feature_cols


def prepare_prediction_row(
    feature_df: pd.DataFrame,
    feature_cols: List[str],
    target_date: Optional[str] = None,
) -> pd.DataFrame:
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
    X = row[feature_cols].astype(float)
    pred = float(model.predict(X)[0])
    return {
        "prediction": pred,
        "prediction_safe": pred * (1 + safety_margin),
        "date_J": row["date"].iloc[0].date(),
    }
