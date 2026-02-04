"""
Persistance des résultats de prédiction pour la page Recommandations.
Sauvegarde dans un fichier JSON (data/last_prediction_for_recommendations.json)
pour survivre aux rechargements de page.
"""

import json
from pathlib import Path
from datetime import datetime, date
import pandas as pd

_BASE = Path(__file__).resolve().parent.parent.parent
PREDICTION_FILE = _BASE / "data" / "last_prediction_for_recommendations.json"


def _serialize(obj):
    """Sérialise les types non-JSON (date, datetime, numpy)."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, (pd.Timestamp,)):
        return obj.isoformat()
    if hasattr(obj, "item") and callable(getattr(obj, "item")):
        return obj.item()
    if isinstance(obj, pd.DataFrame):
        df = obj.copy()
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).astype(str)
        return df.to_dict(orient="records")
    return obj


def save_prediction_for_recommendations(data: dict) -> bool:
    """Sauvegarde les résultats de prédiction dans un fichier JSON."""
    try:
        serialized = {}
        for k, v in data.items():
            if v is None:
                serialized[k] = None
            elif isinstance(v, (datetime, date, pd.Timestamp)):
                serialized[k] = _serialize(v)
            elif isinstance(v, pd.DataFrame):
                serialized[k] = _serialize(v)
            elif hasattr(v, "item") and callable(getattr(v, "item")):
                serialized[k] = v.item()
            else:
                serialized[k] = v
        PREDICTION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PREDICTION_FILE, "w", encoding="utf-8") as f:
            json.dump(serialized, f, ensure_ascii=False, indent=2, default=str)
        return True
    except Exception:
        return False


def load_prediction_for_recommendations() -> dict | None:
    """Charge les résultats de prédiction depuis le fichier JSON."""
    try:
        if not PREDICTION_FILE.exists():
            return None
        with open(PREDICTION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "pred_df" in data and isinstance(data["pred_df"], list):
            data["pred_df"] = pd.DataFrame(data["pred_df"])
            if "date" in data["pred_df"].columns:
                data["pred_df"]["date"] = pd.to_datetime(data["pred_df"]["date"])
        if "pred_date" in data and isinstance(data["pred_date"], str):
            data["pred_date"] = pd.to_datetime(data["pred_date"]).date()
        if "start_date" in data and isinstance(data["start_date"], str):
            data["start_date"] = pd.to_datetime(data["start_date"]).date()
        return data
    except Exception:
        return None
