"""
Support Workers Module

This module handles support worker management operations.
"""

from .routes import trabajadores_bp
from .services import TrabajadorApoyoService

__all__ = ['trabajadores_bp', 'TrabajadorApoyoService']