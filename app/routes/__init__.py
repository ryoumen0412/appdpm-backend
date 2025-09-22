"""
Routes Package - Centralized Blueprint Management

This package manages both legacy and modular blueprints.
Legacy routes will be gradually migrated to the new modular structure.
"""
from .api import api_bp

# Import new modular blueprints
from ..api.personas import personas_mayores_bp, personas_a_cargo_bp

# Lista de todos los blueprints disponibles
__all__ = [
    'api_bp',  # Legacy - will be deprecated
    'personas_mayores_bp', 
    'personas_a_cargo_bp'
]