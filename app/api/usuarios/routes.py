"""
User Management Routes

RESTful endpoints for complete user administration.
"""

from flask import Blueprint, request
from app.auth_utils import admin_required, can_manage_users
from app.extensions import limiter
from app.api.utils import (
    success_response, created_response,
    get_request_args, ValidationError,
    # Decorators
    handle_crud_errors, require_json, validate_request_data,
    validate_pagination_params, log_api_call
)
from .services import UsuarioService

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')


@usuarios_bp.route('/', methods=['GET'])
@can_manage_users
@handle_crud_errors("usuario", "listar")
@validate_pagination_params
@log_api_call
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
    args = get_request_args(request)
    
    result = UsuarioService.get_usuarios(
        page=args.get('page', 1),
        per_page=min(args.get('per_page', 10), 100),
        rut_filter=args.get('rut'),
        username_filter=args.get('username'),
        nivel_filter=args.get('nivel')
    )
    
    return success_response(data=result)


@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
@can_manage_users
@handle_crud_errors("usuario", "obtener")
@log_api_call
def get_usuario(current_user, usuario_id):
    """
    Get user by ID.
    
    Path Parameters:
        usuario_id (int): User ID
        
    Returns:
        JSON: User data
    """
    usuario = UsuarioService.get_usuario_by_id(usuario_id)
    return success_response(data=usuario.to_dict())


@usuarios_bp.route('/', methods=['POST'])
@limiter.limit("10 per hour")
@admin_required
@handle_crud_errors("usuario", "crear")
@require_json
@validate_request_data(['rut_usuario', 'user_usuario', 'password'], ['nivel_usuario'])
@log_api_call
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
    data = request.get_json()
    usuario = UsuarioService.create_usuario(data)
    
    return created_response(
        data=usuario.to_dict(),
        message="Usuario creado exitosamente"
    )


@usuarios_bp.route('/<int:usuario_id>', methods=['PUT'])
@admin_required
@handle_crud_errors("usuario", "actualizar")
@require_json
@validate_request_data([], ['user_usuario', 'nivel_usuario', 'password'])
@log_api_call
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
    data = request.get_json()
    usuario = UsuarioService.update_usuario(usuario_id, data)
    
    return success_response(
        data=usuario.to_dict(),
        message="Usuario actualizado exitosamente"
    )


@usuarios_bp.route('/<int:usuario_id>', methods=['DELETE'])
@admin_required
@handle_crud_errors("usuario", "eliminar")
@log_api_call
def delete_usuario(current_user, usuario_id):
    """
    Delete a user (admin only).
    
    Path Parameters:
        usuario_id (int): User ID
        
    Returns:
        JSON: Deletion confirmation
    """
    UsuarioService.delete_usuario(usuario_id, current_user)
    
    return success_response(
        message="Usuario eliminado exitosamente"
    )


@usuarios_bp.route('/<int:usuario_id>/reset-password', methods=['POST'])
@limiter.limit("5 per hour")
@admin_required
@handle_crud_errors("usuario", "restablecer contraseña")
@require_json
@validate_request_data(['new_password'])
@log_api_call
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
    data = request.get_json()
    new_password = data.get('new_password')
    
    UsuarioService.reset_password(usuario_id, new_password)
    
    return success_response(
        message="Contraseña restablecida exitosamente"
    )


@usuarios_bp.route('/stats', methods=['GET'])
@can_manage_users
@handle_crud_errors("estadísticas de usuario", "obtener")
@log_api_call
def get_user_stats(current_user):
    """
    Get user statistics.
    
    Returns:
        JSON: User statistics
    """
    stats = UsuarioService.get_user_stats()
    return success_response(data=stats)