"""
Authentication Module

Handles all authentication-related endpoints including:
- User login/logout
- User registration
- Profile management
- Password changes
- Token verification
"""

from .routes import auth_bp

__all__ = ['auth_bp']