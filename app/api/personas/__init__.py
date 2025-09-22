"""
Personas Module

Handles all person-related endpoints including:
- Personas a cargo (caregivers)
- Personas mayores (elderly people)
"""

from .personas_mayores_routes import personas_mayores_bp
from .personas_a_cargo_routes import personas_a_cargo_bp

__all__ = ['personas_mayores_bp', 'personas_a_cargo_bp']