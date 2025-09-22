"""
Activities Module

Handles activity and workshop management operations including:
- Activity CRUD operations
- Workshop management
- Date and time scheduling
- Responsible person assignment
- Community center association
"""

from .routes import actividades_bp

__all__ = ['actividades_bp']