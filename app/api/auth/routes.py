"""
Authentication Routes

RESTful endpoints for user authentication and account management.
"""

from flask import Blueprint, request
from app.auth_utils import token_required, can_create_users
from app.api.utils import (
    success_response, error_response, created_response,
    handle_validation_error, handle_business_logic_error, handle_db_error,
    ValidationError, BusinessLogicError
)
from .services import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user in the system.
    
    Body (JSON):
        rut_usuario (str): User's RUT (required)
        password (str): User's password (required)
        
    Returns:
        JSON: Authentication token and user data
        
    Responses:
        200: Authentication successful
        400: Validation error
        401: Authentication failed
    """
    try:
        data = request.get_json() or {}
        response_data = AuthService.authenticate_user(
            data.get('rut_usuario'),
            data.get('password')
        )
        
        return success_response(
            data=response_data,
            message="Autenticación exitosa"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "authenticating user")


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    Logout current user.
    
    Returns:
        JSON: Logout confirmation
    """
    try:
        response_data = AuthService.logout_user()
        return success_response(
            data=response_data,
            message="Sesión cerrada exitosamente"
        )
        
    except Exception as e:
        return handle_db_error(e, "logging out user")


@auth_bp.route('/register', methods=['POST'])
@can_create_users
def register(current_user):
    """
    Register a new user (admin only).
    
    Body (JSON):
        rut_usuario (str): User's RUT (required)
        user_usuario (str): Username (required)
        password (str): Password (required, max 50 chars)
        nivel_usuario (int): Access level (1-support, 2-manager, 3-admin)
        
    Returns:
        JSON: Created user data
        
    Responses:
        201: User created successfully
        400: Validation error
        409: User already exists
    """
    try:
        data = request.get_json() or {}
        usuario = AuthService.register_user(data, current_user)
        
        return created_response(
            data=usuario.to_dict(),
            message="Usuario creado exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating user")


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Get current user's profile.
    
    Returns:
        JSON: User profile data with permissions
    """
    try:
        return success_response(
            data={
                'user': current_user.to_dict(),
                'permissions': current_user.get_permissions_summary()
            }
        )
        
    except Exception as e:
        return handle_db_error(e, "retrieving user profile")


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    Update current user's profile.
    
    Body (JSON):
        user_usuario (str): New username (optional)
        
    Returns:
        JSON: Updated user data
    """
    try:
        data = request.get_json() or {}
        usuario = AuthService.update_profile(current_user, data)
        
        return success_response(
            data=usuario.to_dict(),
            message="Perfil actualizado exitosamente"
        )
        
    except Exception as e:
        return handle_db_error(e, "updating user profile")


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """
    Change current user's password.
    
    Body (JSON):
        current_password (str): Current password (required)
        new_password (str): New password (required)
        
    Returns:
        JSON: Success confirmation
    """
    try:
        data = request.get_json() or {}
        
        AuthService.change_password(
            current_user,
            data.get('current_password'),
            data.get('new_password')
        )
        
        return success_response(
            message="Contraseña cambiada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "changing password")