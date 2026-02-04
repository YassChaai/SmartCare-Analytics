"""Definitions et registry des modeles."""

from smartcare_model.models.interfaces import ModelProtocol
from smartcare_model.models.registry import build_models

__all__ = ["ModelProtocol", "build_models"]
