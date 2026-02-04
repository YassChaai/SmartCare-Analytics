"""Chemins de fichiers pour les donnees ML et les artefacts."""

from pathlib import Path

# /ml/smartcare_model/config/paths.py -> parents[2] == /ml
ML_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ML_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
ARTIFACTS_DIR = ML_ROOT / "artifacts"
