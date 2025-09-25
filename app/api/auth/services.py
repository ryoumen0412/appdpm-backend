"""
Authentication Services

Business logic layer for authentication operations.
"""

from app.extensions import db
from app.models import Usuario
from app.api.utils.errors import ValidationError, BusinessLogicError
from app.auth_utils import (
    validate_rut_format, normalize_rut, clean_rut, validate_password_strength,
    login_user as auth_login_user, logout_user as auth_logout_user
)


class AuthService:
    """
    Service class for authentication operations.
    """
    
    @staticmethod
    def authenticate_user(rut_usuario, password):
        """
        Authenticate user with RUT and password.
        
        Args:
            rut_usuario: User's RUT
            password: User's password
            
        Returns:
            dict: Authentication response data
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If authentication fails
        """
        if not rut_usuario or not password:
            raise ValidationError('RUT y contraseña son requeridos')
        
        # Normalize and validate RUT format
        normalized_rut = normalize_rut(rut_usuario)
        if not normalized_rut:
            raise ValidationError('Formato de RUT inválido. Use formato XXXXXXX-X o XXXXXXXX-X')
        
        # Clean RUT for database lookup (remove dashes and dots)
        clean_rut_for_db = clean_rut(normalized_rut)
        
        # Find user by RUT
        usuario = Usuario.query.filter_by(rut_usuario=clean_rut_for_db).first()
        if not usuario:
            raise BusinessLogicError('Credenciales incorrectas')
        
        # Verify password
        if not usuario.check_password(password):
            raise BusinessLogicError('Credenciales incorrectas')
        
        # Login user and return response
        return auth_login_user(usuario)
    
    @staticmethod
    def register_user(data, current_user):
        """
        Register a new user (admin only).
        
        Args:
            data: User registration data
            current_user: Current authenticated user
            
        Returns:
            Usuario: Created user instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        # Validate required fields
        required_fields = ['rut_usuario', 'user_usuario', 'password', 'nivel_usuario']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'{field} es requerido')
        
        # Normalize and validate RUT format
        normalized_rut = normalize_rut(data['rut_usuario'])
        if not normalized_rut:
            raise ValidationError('Formato de RUT inválido. Use formato XXXXXXX-X o XXXXXXXX-X')
        
        # Check if user already exists
        if Usuario.query.filter_by(rut_usuario=normalized_rut).first():
            raise BusinessLogicError('Ya existe un usuario con este RUT')
        
        # Validate password strength
        is_valid, message = validate_password_strength(data['password'])
        if not is_valid:
            raise ValidationError(message)
        
        # Validate user level
        if data['nivel_usuario'] not in [1, 2, 3]:
            raise ValidationError('Nivel de usuario debe ser 1 (apoyo), 2 (encargado) o 3 (admin)')
        
        # Create new user
        usuario = Usuario(
            rut_usuario=normalized_rut,
            user_usuario=data['user_usuario'],
            nivel_usuario=data['nivel_usuario']
        )
        usuario.set_password(data['password'])
        
        db.session.add(usuario)
        db.session.commit()
        
        return usuario
    
    @staticmethod
    def update_profile(usuario, data):
        """
        Update user profile.
        
        Args:
            usuario: User instance to update
            data: Update data
            
        Returns:
            Usuario: Updated user instance
        """
        if 'user_usuario' in data:
            usuario.user_usuario = data['user_usuario']
        
        db.session.commit()
        return usuario
    
    @staticmethod
    def change_password(usuario, current_password, new_password):
        """
        Change user password.
        
        Args:
            usuario: User instance
            current_password: Current password
            new_password: New password
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If current password is wrong
        """
        if not current_password or not new_password:
            raise ValidationError('Contraseña actual y nueva son requeridas')
        
        # Verify current password
        if not usuario.check_password(current_password):
            raise BusinessLogicError('Contraseña actual incorrecta')
        
        # Validate new password
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            raise ValidationError(message)
        
        # Update password
        usuario.set_password(new_password)
        db.session.commit()
    
    @staticmethod
    def logout_user():
        """
        Logout current user.
        
        Returns:
            dict: Logout response
        """
        return auth_logout_user()