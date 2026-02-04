"""Persistance des artefacts de modele."""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import joblib

from smartcare_model.config.constants import DEFAULT_MODEL_NAME
from smartcare_model.config.paths import ARTIFACTS_DIR


def save_artifacts(
    feature_cols: List[str],
    results: Dict[str, Dict[str, float]],
    trained_models: Dict[str, object],
    artifacts_dir: Path = ARTIFACTS_DIR,
) -> None:
    """Sauvegarder features, metriques et modeles entraines.

    Args:
        feature_cols: Liste ordonnee des features utilisees.
        results: Metriques par modele ou baseline.
        trained_models: Modeles entraines par nom.
        artifacts_dir: Dossier de sortie des artefacts.

    Side Effects:
        Ecrit des fichiers JSON et joblib dans ``artifacts_dir``.
    """
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    with open(artifacts_dir / "feature_columns.json", "w") as f:
        json.dump(feature_cols, f, indent=2)
    with open(artifacts_dir / "metrics.json", "w") as f:
        json.dump(results, f, indent=2)
    for name, model in trained_models.items():
        joblib.dump(model, artifacts_dir / f"{name}.joblib")


def load_feature_columns(artifacts_dir: Path = ARTIFACTS_DIR) -> List[str]:
    """Charger la liste de features persistees.

    Args:
        artifacts_dir: Dossier contenant ``feature_columns.json``.

    Returns:
        Liste ordonnee des colonnes features.

    Raises:
        FileNotFoundError: Si le fichier est absent.
    """
    path = artifacts_dir / "feature_columns.json"
    if not path.exists():
        raise FileNotFoundError("feature_columns.json not found. Run train_models() first.")
    with open(path, "r") as f:
        return json.load(f)


def load_artifacts(
    model_name: str = DEFAULT_MODEL_NAME,
    artifacts_dir: Path = ARTIFACTS_DIR,
) -> Tuple[object, List[str]]:
    """Charger un modele entraine et ses features.

    Args:
        model_name: Nom du modele a charger (par defaut: ``DEFAULT_MODEL_NAME``).
        artifacts_dir: Dossier contenant les artefacts.

    Returns:
        Tuple (modele, feature_columns).

    Raises:
        FileNotFoundError: Si l'artefact de modele est absent.
    """
    model_path = artifacts_dir / f"{model_name}.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"{model_path} not found. Train the model first.")
    model = joblib.load(model_path)
    feature_cols = load_feature_columns(artifacts_dir)
    return model, feature_cols
