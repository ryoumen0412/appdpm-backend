"""
User Management Routes

RESTful endpoints for complete user administration.
"""

from flask import Blueprint, request
from app.auth_utils import admin_required, can_manage_users
from app.api.utils import (
    success_response, error_response, created_response,
    handle_validation_error, handle_business_logic_error, handle_db_error,
    get_request_args, ValidationError, BusinessLogicError
)
from .services import UsuarioService

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')


@usuarios_bp.route('/', methods=['GET'])
@can_manage_users
def get_usuarios(current_user):
    """
    Get paginated list of users with optional filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)
        rut (str): Filter by RUT
        username (str): Filter by username
        nivel (int): Filter by user level (1-3)
        
    Returns:
        JSON: Paginated user list
    """
    try:
        args = get_request_args(request)
        
        result = UsuarioService.get_usuarios(
            page=args.get('page', 1),
            per_page=min(args.get('per_page', 10), 100),
            rut_filter=args.get('rut'),
            username_filter=args.get('username'),
            nivel_filter=args.get('nivel')
        )
        
        return success_response(data=result)
        
    except Exception as e:
        return handle_db_error(e, "retrieving users")


@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
@can_manage_users
def get_usuario(current_user, usuario_id):
    """
    Get user by ID.
    
    Path Parameters:
        usuario_id (int): User ID
        
    Returns:
        JSON: User data
    """
    try:
        usuario = UsuarioService.get_usuario_by_id(usuario_id)
        return success_response(data=usuario.to_dict())
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "retrieving user")


@usuarios_bp.route('/', methods=['POST'])
@admin_required
def create_usuario(current_user):
    """
    Create a new user (admin only).
    
    Body (JSON):
        rut_usuario (str): User's RUT (required)
        user_usuario (str): Username (required)
        password (str): Password (required)
        nivel_usuario (int): Access level (1-support, 2-manager, 3-admin)
        
    Returns:
        JSON: Created user data
    """
    try:
        data = request.get_json() or {}
        usuario = UsuarioService.create_usuario(data)
        
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


@usuarios_bp.route('/<int:usuario_id>', methods=['PUT'])
@admin_required
def update_usuario(current_user, usuario_id):
    """
    Update a user (admin only).
    
    Path Parameters:
        usuario_id (int): User ID
        
    Body (JSON):
        user_usuario (str): Username (optional)
        nivel_usuario (int): Access level (optional)
        password (str): New password (optional)
        
    Returns:
        JSON: Updated user data
    """
    try:
        data = request.get_json() or {}
        usuario = UsuarioService.update_usuario(usuario_id, data)
        
        return success_response(
            data=usuario.to_dict(),
            message="Usuario actualizado exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "updating user")


@usuarios_bp.route('/<int:usuario_id>', methods=['DELETE'])
@admin_required
def delete_usuario(current_user, usuario_id):
    """
    Delete a user (admin only).
    
    Path Parameters:
        usuario_id (int): User ID
        
    Returns:
        JSON: Deletion confirmation
    """
    try:
        UsuarioService.delete_usuario(usuario_id, current_user)
        
        return success_response(
            message="Usuario eliminado exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "deleting user")


@usuarios_bp.route('/<int:usuario_id>/reset-password', methods=['POST'])
@admin_required
def reset_password(current_user, usuario_id):
    """
    Reset user password (admin only).
    
    Path Parameters:
        usuario_id (int): User ID
        
    Body (JSON):
        new_password (str): New password (required)
        
    Returns:
        JSON: Reset confirmation
    """
    try:
        data = request.get_json() or {}
        new_password = data.get('new_password')
        
        if not new_password:
            raise ValidationError('Nueva contraseña es requerida')
        
        UsuarioService.reset_password(usuario_id, new_password)
        
        return success_response(
            message="Contraseña restablecida exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "resetting password")


@usuarios_bp.route('/stats', methods=['GET'])
@can_manage_users
def get_user_stats(current_user):
    """
    Get user statistics.
    
    Returns:
        JSON: User statistics
    """
    try:
        stats = UsuarioService.get_user_stats()
        return success_response(data=stats)
        
    except Exception as e:
        return handle_db_error(e, "retrieving user statistics")