"""Utilitaires Prophet pour la prediction multi-jours."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Optional

import numpy as np
import pandas as pd
import joblib
import re

from smartcare_model.config.paths import ARTIFACTS_DIR
from smartcare_model.data.loading import load_raw_dataframe
from smartcare_model.evaluation.metrics import evaluate

try:
    from prophet import Prophet
    from prophet.serialize import model_from_json, model_to_json
except Exception as exc:  # pragma: no cover - dependance optionnelle en runtime
    Prophet = None
    model_from_json = None
    model_to_json = None
    _PROPHET_IMPORT_ERROR = exc
else:
    _PROPHET_IMPORT_ERROR = None


def _require_prophet() -> None:
    if Prophet is None or model_to_json is None or model_from_json is None:
        raise ImportError(
            "Prophet n'est pas disponible. Installez la dependance `prophet` "
            "puis relancez l'entrainement."
        ) from _PROPHET_IMPORT_ERROR


def _ensure_cmdstan_installed() -> None:
    """Verifier que CmdStan est installe via cmdstanpy."""
    try:
        import cmdstanpy
        import importlib.resources as importlib_resources
        from prophet.models import CmdStanPyBackend

        local_root = importlib_resources.files("prophet") / "stan_model"
        local_cmdstan = local_root / f"cmdstan-{CmdStanPyBackend.CMDSTAN_VERSION}"
        if local_cmdstan.exists():
            makefile = local_cmdstan / "makefile"
            if not makefile.exists():
                cmdstanpy.install_cmdstan(
                    version=CmdStanPyBackend.CMDSTAN_VERSION,
                    dir=str(local_root),
                    overwrite=True,
                    progress=True,
                )
            cmdstanpy.set_cmdstan_path(str(local_cmdstan))
            return

        cmdstanpy.cmdstan_path()
    except Exception as exc:
        raise RuntimeError(
            "CmdStan est manquant ou invalide. Lancez `python -m cmdstanpy.install_cmdstan` "
            "puis relancez l'entrainement."
        ) from exc


def _monthly_mode(series: pd.Series) -> str:
    """Retourner le mode d'une serie, ou une chaine vide si absent."""
    modes = series.dropna().mode()
    if not modes.empty:
        return str(modes.iloc[0])
    return ""


def _sanitize_holiday_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip())
    cleaned = cleaned.strip("_")
    return cleaned.lower() if cleaned else "event"


def build_prophet_holidays(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Construire un DataFrame de jours speciaux pour Prophet."""
    df = raw_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    holiday_rows = []

    if "vacances_scolaires" in df.columns:
        vac_mask = pd.to_numeric(df["vacances_scolaires"], errors="coerce").fillna(0) == 1
        for date in df.loc[vac_mask, "date"]:
            holiday_rows.append({"ds": date, "holiday": "vacances_scolaires"})

    if "evenement_special" in df.columns:
        for date, evt in df[["date", "evenement_special"]].dropna().itertuples(index=False):
            evt_str = str(evt)
            if evt_str.lower() in ("aucun", "none", "nan"):
                continue
            holiday_rows.append(
                {"ds": date, "holiday": f"event_{_sanitize_holiday_name(evt_str)}"}
            )

    if not holiday_rows:
        return pd.DataFrame(columns=["ds", "holiday"])

    holidays = pd.DataFrame(holiday_rows)
    holidays["ds"] = pd.to_datetime(holidays["ds"])
    return holidays


def build_prophet_train_frame(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Construire le DataFrame d'entrainement pour Prophet.

    Args:
        raw_df: DataFrame brut (charge depuis le CSV).

    Returns:
        DataFrame avec colonnes `ds`, `y` et regressseurs numeriques/one-hot.
    """
    df = raw_df.copy()
    df = df.sort_values("date").reset_index(drop=True)

    base_cols = [
        "date",
        "nombre_admissions",
        "temperature_moyenne",
        "temperature_min",
        "temperature_max",
        "indice_chaleur",
        "indice_froid",
        "lits_total",
        "lits_occupes",
        "taux_occupation_lits",
        "nb_medecins_disponibles",
        "nb_infirmiers_disponibles",
        "nb_aides_soignants_disponibles",
        "taux_couverture_personnel",
        "vacances_scolaires",
        "meteo_principale",
        "evenement_special",
    ]
    existing_cols = [c for c in base_cols if c in df.columns]
    df = df[existing_cols].copy()

    df = df.rename(columns={"date": "ds", "nombre_admissions": "y"})

    for num_col in [
        "temperature_moyenne",
        "temperature_min",
        "temperature_max",
        "indice_chaleur",
        "indice_froid",
        "lits_total",
        "lits_occupes",
        "taux_occupation_lits",
        "nb_medecins_disponibles",
        "nb_infirmiers_disponibles",
        "nb_aides_soignants_disponibles",
        "taux_couverture_personnel",
        "vacances_scolaires",
    ]:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce").fillna(0)

    cat_cols = [
        c
        for c in ["meteo_principale", "evenement_special"]
        if c in df.columns
    ]
    if cat_cols:
        prefixes = ["meteo" if c == "meteo_principale" else "event" for c in cat_cols]
        df = pd.get_dummies(
            df,
            columns=cat_cols,
            prefix=prefixes,
            dummy_na=False,
        )
    return df


def _build_prophet_model(
    holidays: Optional[pd.DataFrame],
    seasonality_mode: str,
    changepoint_prior_scale: float,
    seasonality_prior_scale: float,
) -> "Prophet":
    model = Prophet(
        seasonality_mode=seasonality_mode,
        changepoint_prior_scale=changepoint_prior_scale,
        seasonality_prior_scale=seasonality_prior_scale,
        holidays=holidays if holidays is not None and not holidays.empty else None,
    )
    model.add_seasonality(name="monthly", period=30.5, fourier_order=5)
    return model


def _default_tuning_grid() -> List[Dict[str, float | str]]:
    return [
        {"seasonality_mode": "additive", "changepoint_prior_scale": 0.05, "seasonality_prior_scale": 5.0},
        {"seasonality_mode": "additive", "changepoint_prior_scale": 0.1, "seasonality_prior_scale": 10.0},
        {"seasonality_mode": "additive", "changepoint_prior_scale": 0.2, "seasonality_prior_scale": 10.0},
        {"seasonality_mode": "multiplicative", "changepoint_prior_scale": 0.05, "seasonality_prior_scale": 5.0},
        {"seasonality_mode": "multiplicative", "changepoint_prior_scale": 0.1, "seasonality_prior_scale": 10.0},
        {"seasonality_mode": "multiplicative", "changepoint_prior_scale": 0.2, "seasonality_prior_scale": 10.0},
        {"seasonality_mode": "multiplicative", "changepoint_prior_scale": 0.3, "seasonality_prior_scale": 15.0},
        {"seasonality_mode": "multiplicative", "changepoint_prior_scale": 0.5, "seasonality_prior_scale": 20.0},
    ]


def train_prophet_model(
    train_ratio: float = 0.8,
    artifacts_dir: Path = ARTIFACTS_DIR,
    tune: bool = False,
    param_grid: Optional[List[Dict[str, float | str]]] = None,
) -> dict:
    """Entrainer un modele Prophet et sauvegarder les artefacts."""
    _require_prophet()
    _ensure_cmdstan_installed()
    raw_df = load_raw_dataframe()
    train_df = build_prophet_train_frame(raw_df)

    train_df = train_df.dropna(subset=["y"]).reset_index(drop=True)
    regressor_cols = [c for c in train_df.columns if c not in ("ds", "y")]
    if "vacances_scolaires" in regressor_cols:
        regressor_cols.remove("vacances_scolaires")
    if regressor_cols:
        train_df = train_df.dropna(subset=regressor_cols).reset_index(drop=True)

    split_idx = int(len(train_df) * train_ratio)
    train_data = train_df.iloc[:split_idx].copy()
    test_data = train_df.iloc[split_idx:].copy()

    train_data["y"] = pd.to_numeric(train_data["y"], errors="coerce")
    test_data["y"] = pd.to_numeric(test_data["y"], errors="coerce")
    train_data[regressor_cols] = train_data[regressor_cols].astype(float)
    test_data[regressor_cols] = test_data[regressor_cols].astype(float)

    holidays = build_prophet_holidays(raw_df)

    best_model = None
    best_metrics = None
    best_params: Optional[Dict[str, float | str]] = None
    best_score = float("inf")
    tuning_results: List[Dict[str, object]] = []

    if tune:
        grid = param_grid or _default_tuning_grid()
        for params in grid:
            model = _build_prophet_model(
                holidays,
                seasonality_mode=str(params["seasonality_mode"]),
                changepoint_prior_scale=float(params["changepoint_prior_scale"]),
                seasonality_prior_scale=float(params["seasonality_prior_scale"]),
            )
            for col in regressor_cols:
                model.add_regressor(col)
            try:
                model.fit(train_data[["ds", "y"] + regressor_cols])
                forecast = model.predict(test_data[["ds"] + regressor_cols])
                metrics = evaluate(test_data["y"], forecast["yhat"])
                tuning_results.append({"params": params, "metrics": metrics})
                score = 0.5 * metrics.get("mape", float("inf")) + 0.5 * metrics.get("smape", float("inf"))
                if best_metrics is None:
                    best_metrics = metrics
                    best_model = model
                    best_params = params
                    best_score = score
                else:
                    if score < best_score:
                        best_metrics = metrics
                        best_model = model
                        best_params = params
                        best_score = score
            except Exception as exc:
                tuning_results.append({"params": params, "error": str(exc)})
        if best_model is None:
            raise RuntimeError("Aucune configuration Prophet n'a pu être entraînée.")
        model = best_model
        metrics = best_metrics
    else:
        default_params = {
            "seasonality_mode": "multiplicative",
            "changepoint_prior_scale": 0.1,
            "seasonality_prior_scale": 10.0,
        }
        model = _build_prophet_model(
            holidays,
            seasonality_mode=default_params["seasonality_mode"],
            changepoint_prior_scale=default_params["changepoint_prior_scale"],
            seasonality_prior_scale=default_params["seasonality_prior_scale"],
        )
        for col in regressor_cols:
            model.add_regressor(col)
        model.fit(train_data[["ds", "y"] + regressor_cols])
        forecast = model.predict(test_data[["ds"] + regressor_cols])
        metrics = evaluate(test_data["y"], forecast["yhat"])
        best_params = default_params

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model_json": model_to_json(model), "regressors": regressor_cols},
        artifacts_dir / "prophet.joblib",
    )

    metrics_path = artifacts_dir / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = {}
    existing["prophet"] = metrics
    if best_params is not None:
        existing["prophet_params"] = best_params
    if tuning_results:
        existing["prophet_tuning"] = tuning_results
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    return {"prophet": metrics}


def load_prophet_artifacts(
    artifacts_dir: Path = ARTIFACTS_DIR,
) -> Tuple["Prophet", List[str]]:
    """Charger le modele Prophet et la liste des regressseurs."""
    _require_prophet()
    joblib_path = artifacts_dir / "prophet.joblib"
    if joblib_path.exists():
        payload = joblib.load(joblib_path)
        model_json = payload.get("model_json")
        regressor_cols = payload.get("regressors", [])
        if model_json is None:
            raise ValueError("prophet.joblib is missing model_json.")
        return model_from_json(model_json), regressor_cols

    raise FileNotFoundError(f"{joblib_path} not found. Train Prophet first.")


def build_prophet_future_frame(
    dates: Iterable[pd.Timestamp],
    raw_df: pd.DataFrame,
    regressor_cols: List[str],
) -> pd.DataFrame:
    """Construire les regressseurs futurs pour Prophet."""
    future = pd.DataFrame({"ds": pd.to_datetime(list(dates))})

    hist = raw_df.copy()
    hist["date"] = pd.to_datetime(hist["date"])
    hist["month"] = hist["date"].dt.month

    numeric_cols = [
        "temperature_moyenne",
        "temperature_min",
        "temperature_max",
        "indice_chaleur",
        "indice_froid",
        "lits_total",
        "lits_occupes",
        "taux_occupation_lits",
        "nb_medecins_disponibles",
        "nb_infirmiers_disponibles",
        "nb_aides_soignants_disponibles",
        "taux_couverture_personnel",
        "vacances_scolaires",
    ]
    numeric_cols = [c for c in numeric_cols if c in hist.columns]
    monthly_means = hist.groupby("month")[numeric_cols].mean()
    overall_means = hist[numeric_cols].mean()

    for col in numeric_cols:
        future[col] = (
            future["ds"].dt.month.map(monthly_means[col]).fillna(overall_means[col])
        )

    if "meteo_principale" in hist.columns:
        meteo_by_month = hist.groupby("month")["meteo_principale"].apply(_monthly_mode)
        meteo_global = _monthly_mode(hist["meteo_principale"]) or "Aucun"
        future["meteo_principale"] = (
            future["ds"].dt.month.map(meteo_by_month).replace("", np.nan).fillna(meteo_global)
        )

    event_default = "Aucun"
    if "evenement_special" in hist.columns:
        event_values = hist["evenement_special"].dropna().astype(str)
        if "Aucun" not in event_values.unique():
            event_default = _monthly_mode(event_values) or "Aucun"
        future["evenement_special"] = event_default

    cat_cols = [
        c
        for c in ["meteo_principale", "evenement_special"]
        if c in future.columns
    ]
    if cat_cols:
        prefixes = ["meteo" if c == "meteo_principale" else "event" for c in cat_cols]
        future = pd.get_dummies(
            future,
            columns=cat_cols,
            prefix=prefixes,
            dummy_na=False,
        )

    for col in regressor_cols:
        if col not in future.columns:
            future[col] = 0.0

    future = future[["ds"] + regressor_cols]
    future[regressor_cols] = future[regressor_cols].astype(float)
    return future


def forecast_prophet(model: "Prophet", future_df: pd.DataFrame) -> pd.DataFrame:
    """Generer les previsions Prophet pour un DataFrame futur."""
    _require_prophet()
    return model.predict(future_df)
