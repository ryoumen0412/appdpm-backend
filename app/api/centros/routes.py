"""
Community Centers Routes

RESTful endpoints for community center management.
"""

from flask import Blueprint, request
from app.auth_utils import apoyo_required, can_update_records, can_delete_vital_records
from app.api.utils import (
    success_response, error_response, created_response,
    handle_validation_error, handle_business_logic_error, handle_db_error,
    get_request_args, ValidationError, BusinessLogicError
)
from .services import CentroService

centros_bp = Blueprint('centros', __name__, url_prefix='/api/centros')


@centros_bp.route('/', methods=['GET'])
@apoyo_required
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
    try:
        args = get_request_args(request)
        
        result = CentroService.get_centros(
            page=args.get('page', 1),
            per_page=min(args.get('per_page', 10), 100),
            nombre_filter=args.get('nombre'),
            sector_filter=args.get('sector'),
            direccion_filter=args.get('direccion')
        )
        
        return success_response(data=result)
        
    except Exception as e:
        return handle_db_error(e, "retrieving community centers")


@centros_bp.route('/<int:centro_id>', methods=['GET'])
@apoyo_required
def get_centro(current_user, centro_id):
    """
    Get community center by ID.
    
    Path Parameters:
        centro_id (int): Center ID
        
    Returns:
        JSON: Center data
    """
    try:
        centro = CentroService.get_centro_by_id(centro_id)
        return success_response(data=centro.to_dict())
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "retrieving community center")


@centros_bp.route('/', methods=['POST'])
@can_update_records
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
    try:
        data = request.get_json() or {}
        centro = CentroService.create_centro(data)
        
        return created_response(
            data=centro.to_dict(),
            message="Centro comunitario creado exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating community center")


@centros_bp.route('/<int:centro_id>', methods=['PUT'])
@can_update_records
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
    try:
        data = request.get_json() or {}
        centro = CentroService.update_centro(centro_id, data)
        
        return success_response(
            data=centro.to_dict(),
            message="Centro comunitario actualizado exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "updating community center")


@centros_bp.route('/<int:centro_id>', methods=['DELETE'])
@can_delete_vital_records
def delete_centro(current_user, centro_id):
    """
    Delete a community center.
    
    Path Parameters:
        centro_id (int): Center ID
        
    Returns:
        JSON: Deletion confirmation
    """
    try:
        CentroService.delete_centro(centro_id)
        
        return success_response(
            message="Centro comunitario eliminado exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "deleting community center")


@centros_bp.route('/sectores', methods=['GET'])
@apoyo_required
def get_sectores(current_user):
    """
    Get list of unique sectors.
    
    Returns:
        JSON: List of sector names
    """
    try:
        sectores = CentroService.get_sectores_list()
        return success_response(data={'sectores': sectores})
        
    except Exception as e:
        return handle_db_error(e, "retrieving sectors")


@centros_bp.route('/stats', methods=['GET'])
@apoyo_required
def get_centro_stats(current_user):
    """
    Get community center statistics.
    
    Returns:
        JSON: Center statistics
    """
    try:
        stats = CentroService.get_centro_stats()
        return success_response(data=stats)
        
    except Exception as e:
        return handle_db_error(e, "retrieving center statistics")