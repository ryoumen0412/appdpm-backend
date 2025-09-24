"""
Maintenance Routes

RESTful endpoints for maintenance management.
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
from .services import MantencionService

mantenciones_bp = Blueprint('mantenciones', __name__, url_prefix='/api/mantenciones')


@mantenciones_bp.route('/', methods=['GET'])
@apoyo_required
@handle_crud_errors("mantención", "listar")
@validate_pagination_params
@log_api_call
def get_mantenciones(current_user):
    """
    Get paginated list of maintenance records with optional filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)
        centro (int): Filter by center ID
        fecha_desde (str): Filter maintenance from this date (YYYY-MM-DD)
        fecha_hasta (str): Filter maintenance until this date (YYYY-MM-DD)
        
    Returns:
        JSON: Paginated maintenance list
    """
    args = get_request_args(request)
    
    result = MantencionService.get_mantenciones(
        page=args.get('page', 1),
        per_page=min(args.get('per_page', 10), 100),
        centro_filter=args.get('centro'),
        fecha_desde=args.get('fecha_desde'),
        fecha_hasta=args.get('fecha_hasta')
    )
    
    return success_response(data=result)


@mantenciones_bp.route('/<int:mantencion_id>', methods=['GET'])
@apoyo_required
@handle_crud_errors("mantención", "obtener")
@log_api_call
def get_mantencion(current_user, mantencion_id):
    """
    Get maintenance record by ID.
    
    Path Parameters:
        mantencion_id (int): Maintenance ID
        
    Returns:
        JSON: Maintenance record data
    """
    mantencion = MantencionService.get_mantencion_by_id(mantencion_id)
    
    return success_response(
        data=mantencion.to_dict(),
        message="Mantención encontrada"
    )


@mantenciones_bp.route('/', methods=['POST'])
@can_update_records
@handle_crud_errors("mantención", "crear")
@require_json
@validate_request_data(
    ['fecha', 'id_centro'],
    ['detalle', 'observaciones', 'adjuntos', 'quienes_realizaron']
)
@log_api_call
def create_mantencion(current_user):
    """
    Create a new maintenance record.
    
    Body (JSON):
        fecha (str): Maintenance date (YYYY-MM-DD) (required)
        id_centro (int): Center ID (required)
        detalle (str): Maintenance details (optional)
        observaciones (str): Observations (optional)
        adjuntos (str): Attachments info (optional)
        quienes_realizaron (str): Who performed the maintenance (optional)
        
    Returns:
        JSON: Created maintenance record data
    """
    data = request.get_json()
    mantencion = MantencionService.create_mantencion(data)
    
    return created_response(
        data=mantencion.to_dict(),
        message="Mantención creada exitosamente"
    )


@mantenciones_bp.route('/<int:mantencion_id>', methods=['PUT'])
@can_update_records
@handle_crud_errors("mantención", "actualizar")
@require_json
@validate_request_data(
    [],
    ['fecha', 'id_centro', 'detalle', 'observaciones', 'adjuntos', 'quienes_realizaron']
)
@log_api_call
def update_mantencion(current_user, mantencion_id):
    """
    Update a maintenance record.
    
    Path Parameters:
        mantencion_id (int): Maintenance ID
        
    Body (JSON): Fields to update
        
    Returns:
        JSON: Updated maintenance record data
    """
    data = request.get_json()
    mantencion = MantencionService.update_mantencion(mantencion_id, data)
    
    return success_response(
        data=mantencion.to_dict(),
        message="Mantención actualizada exitosamente"
    )


@mantenciones_bp.route('/<int:mantencion_id>', methods=['DELETE'])
@can_delete_vital_records
@handle_crud_errors("mantención", "eliminar")
@log_api_call
def delete_mantencion(current_user, mantencion_id):
    """
    Delete a maintenance record.
    
    Path Parameters:
        mantencion_id (int): Maintenance ID
        
    Returns:
        JSON: Deletion confirmation
    """
    MantencionService.delete_mantencion(mantencion_id)
    
    return success_response(
        message="Mantención eliminada exitosamente"
    )


@mantenciones_bp.route('/centro/<int:centro_id>', methods=['GET'])
@apoyo_required
@handle_crud_errors("mantenciones por centro", "obtener")
@log_api_call
def get_mantenciones_by_centro(current_user, centro_id):
    """
    Get all maintenance records for a specific center.
    
    Path Parameters:
        centro_id (int): Center ID
        
    Returns:
        JSON: List of maintenance records for the center
    """
    mantenciones = MantencionService.get_mantenciones_by_centro(centro_id)
    
    return success_response(
        data=[m.to_dict() for m in mantenciones],
        message=f"Mantenciones del centro {centro_id} obtenidas exitosamente"
    )