"""Chemins de fichiers pour les donnees ML et les artefacts."""

from pathlib import Path

# /ml/smartcare_model/config/paths.py -> parents[2] == /ml
ML_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = ML_ROOT.parent
DATA_DIR = ML_ROOT / "data"
PROJECT_RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR = PROJECT_RAW_DIR if PROJECT_RAW_DIR.exists() else (DATA_DIR / "raw")
ARTIFACTS_DIR = ML_ROOT / "artifacts"
