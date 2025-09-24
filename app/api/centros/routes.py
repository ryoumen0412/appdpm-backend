"""
Community Centers Routes

RESTful endpoints for community center management.
"""

from flask import Blueprint, request
from app.auth_utils import apoyo_required, can_update_records, can_delete_vital_records
from app.api.utils import (
    success_response, created_response,
    get_request_args,
    # Decorators
    handle_crud_errors, require_json, validate_request_data,
    validate_pagination_params, log_api_call
)
from .services import CentroService

centros_bp = Blueprint('centros', __name__, url_prefix='/api/centros')


@centros_bp.route('/', methods=['GET'])
@apoyo_required
@handle_crud_errors("centro comunitario", "listar")
@validate_pagination_params
@log_api_call
def get_centros(current_user):
    """
    Get paginated list of community centers with optional filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)
        nombre (str): Filter by center name
        sector (str): Filter by sector
        direccion (str): Filter by address
        
    Returns:
        JSON: Paginated centers list
    """
    args = get_request_args(request)
    
    result = CentroService.get_centros(
        page=args.get('page', 1),
        per_page=min(args.get('per_page', 10), 100),
        nombre_filter=args.get('nombre'),
        sector_filter=args.get('sector'),
        direccion_filter=args.get('direccion')
    )
    
    return success_response(data=result)


@centros_bp.route('/<int:centro_id>', methods=['GET'])
@apoyo_required
@handle_crud_errors("centro comunitario", "obtener")
@log_api_call
def get_centro(current_user, centro_id):
    """
    Get community center by ID.
    
    Path Parameters:
        centro_id (int): Center ID
        
    Returns:
        JSON: Center data
    """
    centro = CentroService.get_centro_by_id(centro_id)
    return success_response(data=centro.to_dict())


@centros_bp.route('/', methods=['POST'])
@can_update_records
@handle_crud_errors("centro comunitario", "crear")
@require_json
@validate_request_data(
    ['nombre_centro', 'direccion_centro', 'sector_centro'],
    ['telefono_centro', 'email_centro', 'capacidad_centro']
)
@log_api_call
def create_centro(current_user):
    """
    Create a new community center.
    
    Body (JSON):
        nombre_centro (str): Center name (required, max 100 chars)
        direccion_centro (str): Address (required, max 200 chars)
        sector_centro (str): Sector (required, max 50 chars)
        telefono_centro (str): Phone number (optional, max 20 chars)
        email_centro (str): Email address (optional, max 100 chars)
        capacidad_centro (int): Capacity (optional, positive number)
        
    Returns:
        JSON: Created center data
    """
    data = request.get_json()
    centro = CentroService.create_centro(data)
    
    return created_response(
        data=centro.to_dict(),
        message="Centro comunitario creado exitosamente"
    )


@centros_bp.route('/<int:centro_id>', methods=['PUT'])
@can_update_records
@handle_crud_errors("centro comunitario", "actualizar")
@require_json
@validate_request_data(
    [],
    ['nombre_centro', 'direccion_centro', 'sector_centro', 'telefono_centro', 'email_centro', 'capacidad_centro']
)
@log_api_call
def update_centro(current_user, centro_id):
    """
    Update a community center.
    
    Path Parameters:
        centro_id (int): Center ID
        
    Body (JSON):
        nombre_centro (str): Center name (optional)
        direccion_centro (str): Address (optional)
        sector_centro (str): Sector (optional)
        telefono_centro (str): Phone number (optional)
        email_centro (str): Email address (optional)
        capacidad_centro (int): Capacity (optional)
        
    Returns:
        JSON: Updated center data
    """
    data = request.get_json()
    centro = CentroService.update_centro(centro_id, data)
    
    return success_response(
        data=centro.to_dict(),
        message="Centro comunitario actualizado exitosamente"
    )


@centros_bp.route('/<int:centro_id>', methods=['DELETE'])
@can_delete_vital_records
@handle_crud_errors("centro comunitario", "eliminar")
@log_api_call
def delete_centro(current_user, centro_id):
    """
    Delete a community center.
    
    Path Parameters:
        centro_id (int): Center ID
        
    Returns:
        JSON: Deletion confirmation
    """
    CentroService.delete_centro(centro_id)
    
    return success_response(
        message="Centro comunitario eliminado exitosamente"
    )


@centros_bp.route('/sectores', methods=['GET'])
@apoyo_required
@handle_crud_errors("sectores", "obtener")
@log_api_call
def get_sectores(current_user):
    """
    Get list of unique sectors.
    
    Returns:
        JSON: List of sector names
    """
    sectores = CentroService.get_sectores_list()
    return success_response(data={'sectores': sectores})


@centros_bp.route('/stats', methods=['GET'])
@apoyo_required
@handle_crud_errors("estadísticas de centros", "obtener")
@log_api_call
def get_centro_stats(current_user):
    """
    Get community center statistics.
    
    Returns:
        JSON: Center statistics
    """
    stats = CentroService.get_centro_stats()
    return success_response(data=stats)