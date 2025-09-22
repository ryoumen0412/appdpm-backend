"""
Users Module

Handles complete user management operations including:
- User CRUD operations
- User listing and search
- User permission management
- User status management
"""

from .routes import usuarios_bp

__all__ = ['usuarios_bp']