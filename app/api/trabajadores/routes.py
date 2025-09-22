"""
Support Workers Routes

RESTful endpoints for support worker management.
"""

from flask import Blueprint, request
from app.auth_utils import apoyo_required, can_update_records, can_delete_vital_records
from app.api.utils import (
    success_response, error_response, created_response,
    handle_validation_error, handle_business_logic_error, handle_db_error,
    get_request_args, ValidationError, BusinessLogicError
)
from .services import TrabajadorApoyoService

trabajadores_bp = Blueprint('trabajadores', __name__, url_prefix='/api/trabajadores-apoyo')


@trabajadores_bp.route('/', methods=['GET'])
@apoyo_required
def get_trabajadores(current_user):
    """
    Get paginated list of support workers with optional filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)
        nombre (str): Filter by worker name or last name
        centro (int): Filter by center ID
        cargo (str): Filter by position/role
        
    Returns:
        JSON: Paginated support workers list
    """
    try:
        args = get_request_args(request)
        
        result = TrabajadorApoyoService.get_trabajadores(
            page=args.get('page', 1),
            per_page=min(args.get('per_page', 10), 100),
            nombre_filter=args.get('nombre'),
            centro_filter=args.get('centro'),
            cargo_filter=args.get('cargo')
        )
        
        return success_response(data=result)
        
    except Exception as e:
        return handle_db_error(e, "retrieving support workers")


@trabajadores_bp.route('/<string:rut>', methods=['GET'])
@apoyo_required
def get_trabajador(current_user, rut):
    """
    Get support worker by RUT.
    
    Path Parameters:
        rut (str): Worker RUT
        
    Returns:
        JSON: Support worker data
    """
    try:
        trabajador = TrabajadorApoyoService.get_trabajador_by_rut(rut)
        
        return success_response(
            data=trabajador.to_dict(),
            message="Trabajador de apoyo encontrado"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "retrieving support worker")


@trabajadores_bp.route('/', methods=['POST'])
@can_update_records
def create_trabajador(current_user):
    """
    Create a new support worker.
    
    Body (JSON):
        rut (str): Worker RUT (required)
        nombre (str): Worker name (required)
        apellidos (str): Worker last names (optional)
        cargo (str): Worker position/role (optional)
        id_centro (int): Center ID (optional)
        
    Returns:
        JSON: Created support worker data
    """
    try:
        data = request.get_json() or {}
        trabajador = TrabajadorApoyoService.create_trabajador(data)
        
        return created_response(
            data=trabajador.to_dict(),
            message="Trabajador de apoyo creado exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating support worker")


@trabajadores_bp.route('/<string:rut>', methods=['PUT'])
@can_update_records
def update_trabajador(current_user, rut):
    """
    Update a support worker.
    
    Path Parameters:
        rut (str): Worker RUT
        
    Body (JSON): Fields to update (RUT cannot be changed)
        
    Returns:
        JSON: Updated support worker data
    """
    try:
        data = request.get_json() or {}
        trabajador = TrabajadorApoyoService.update_trabajador(rut, data)
        
        return success_response(
            data=trabajador.to_dict(),
            message="Trabajador de apoyo actualizado exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "updating support worker")


@trabajadores_bp.route('/<string:rut>', methods=['DELETE'])
@can_delete_vital_records
def delete_trabajador(current_user, rut):
    """
    Delete a support worker.
    
    Path Parameters:
        rut (str): Worker RUT
        
    Returns:
        JSON: Deletion confirmation
    """
    try:
        TrabajadorApoyoService.delete_trabajador(rut)
        
        return success_response(
            message="Trabajador de apoyo eliminado exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "deleting support worker")


@trabajadores_bp.route('/centro/<int:centro_id>', methods=['GET'])
@apoyo_required
def get_trabajadores_by_centro(current_user, centro_id):
    """
    Get all support workers for a specific center.
    
    Path Parameters:
        centro_id (int): Center ID
        
    Returns:
        JSON: List of support workers for the center
    """
    try:
        trabajadores = TrabajadorApoyoService.get_trabajadores_by_centro(centro_id)
        
        return success_response(
            data=[t.to_dict() for t in trabajadores],
            message=f"Trabajadores del centro {centro_id} obtenidos exitosamente"
        )
        
    except Exception as e:
        return handle_db_error(e, "retrieving center support workers")