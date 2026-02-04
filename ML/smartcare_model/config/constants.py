"""Constantes partagees pour l'entrainement et l'inference."""

DATA_FILENAME_HINT = "daily_hospital_context_2022-2026_generated.csv"
DEFAULT_MODEL_NAME = "gradient_boosting"
TARGET_COL = "y"

NUMERIC_COLUMNS = [
    "temperature_moyenne",
    "temperature_min",
    "temperature_max",
    "indice_chaleur",
    "indice_froid",
    "taux_occupation_lits",
    "taux_couverture_personnel",
    "impact_evenement_estime",
]
