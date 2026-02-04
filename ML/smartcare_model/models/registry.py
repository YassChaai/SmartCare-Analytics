"""Registry des modeles.

Ce module est la source unique des modeles utilises a l'entrainement.
"""

from typing import Dict

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor

from smartcare_model.models.interfaces import ModelProtocol


def build_models() -> Dict[str, ModelProtocol]:
    """Instancier et retourner les modeles supportes.

    Returns:
        Dictionnaire {nom_modele: instance_modele}.
    """
    return {
        "random_forest": RandomForestRegressor(
            n_estimators=300,
            random_state=42,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
    }
