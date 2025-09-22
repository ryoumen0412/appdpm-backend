"""
Activities Routes

RESTful endpoints for activity and workshop management.
"""

from flask import Blueprint, request
from app.auth_utils import apoyo_required, can_update_records, can_delete_vital_records
from app.api.utils import (
    success_response, error_response, created_response,
    handle_validation_error, handle_business_logic_error, handle_db_error,
    get_request_args, ValidationError, BusinessLogicError
)
from .services import ActividadService, TallerService

actividades_bp = Blueprint('actividades', __name__, url_prefix='/api/actividades')


# ACTIVITY ROUTES
@actividades_bp.route('/', methods=['GET'])
@apoyo_required
def get_actividades(current_user):
    """
    Get paginated list of activities with optional filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)
        nombre (str): Filter by activity name
        centro (int): Filter by center ID
        fecha_inicio (str): Filter activities after this date (YYYY-MM-DD)
        fecha_fin (str): Filter activities before this date (YYYY-MM-DD)
        
    Returns:
        JSON: Paginated activities list
    """
    try:
        args = get_request_args(request)
        
        result = ActividadService.get_actividades(
            page=args.get('page', 1),
            per_page=min(args.get('per_page', 10), 100),
            nombre_filter=args.get('nombre'),
            centro_filter=args.get('centro'),
            fecha_inicio=args.get('fecha_inicio'),
            fecha_fin=args.get('fecha_fin')
        )
        
        return success_response(data=result)
        
    except Exception as e:
        return handle_db_error(e, "retrieving activities")


@actividades_bp.route('/<int:actividad_id>', methods=['GET'])
@apoyo_required
def get_actividad(current_user, actividad_id):
    """
    Get activity by ID.
    
    Path Parameters:
        actividad_id (int): Activity ID
        
    Returns:
        JSON: Activity data
    """
    try:
        actividad = ActividadService.get_actividad_by_id(actividad_id)
        return success_response(data=actividad.to_dict())
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "retrieving activity")


@actividades_bp.route('/', methods=['POST'])
@can_update_records
def create_actividad(current_user):
    """
    Create a new activity.
    
    Body (JSON):
        nombre_actividad (str): Activity name (required, max 100 chars)
        descripcion_actividad (str): Description (required, max 500 chars)
        fecha_inicio_actividad (str): Start date (optional, YYYY-MM-DD)
        fecha_fin_actividad (str): End date (optional, YYYY-MM-DD)
        id_centro (int): Community center ID (required)
        id_persona_a_cargo (int): Responsible person ID (optional)
        
    Returns:
        JSON: Created activity data
    """
    try:
        data = request.get_json() or {}
        actividad = ActividadService.create_actividad(data)
        
        return created_response(
            data=actividad.to_dict(),
            message="Actividad creada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating activity")


@actividades_bp.route('/<int:actividad_id>', methods=['PUT'])
@can_update_records
def update_actividad(current_user, actividad_id):
    """
    Update an activity.
    
    Path Parameters:
        actividad_id (int): Activity ID
        
    Body (JSON):
        nombre_actividad (str): Activity name (optional)
        descripcion_actividad (str): Description (optional)
        fecha_inicio_actividad (str): Start date (optional, YYYY-MM-DD)
        fecha_fin_actividad (str): End date (optional, YYYY-MM-DD)
        id_centro (int): Community center ID (optional)
        id_persona_a_cargo (int): Responsible person ID (optional)
        
    Returns:
        JSON: Updated activity data
    """
    try:
        data = request.get_json() or {}
        actividad = ActividadService.update_actividad(actividad_id, data)
        
        return success_response(
            data=actividad.to_dict(),
            message="Actividad actualizada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "updating activity")


@actividades_bp.route('/<int:actividad_id>', methods=['DELETE'])
@can_delete_vital_records
def delete_actividad(current_user, actividad_id):
    """
    Delete an activity.
    
    Path Parameters:
        actividad_id (int): Activity ID
        
    Returns:
        JSON: Deletion confirmation
    """
    try:
        ActividadService.delete_actividad(actividad_id)
        
        return success_response(
            message="Actividad eliminada exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "deleting activity")


# WORKSHOP ROUTES
@actividades_bp.route('/talleres', methods=['GET'])
@apoyo_required
def get_talleres(current_user):
    """
    Get paginated list of workshops with optional filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)
        nombre (str): Filter by workshop name
        actividad (int): Filter by activity ID
        
    Returns:
        JSON: Paginated workshops list
    """
    try:
        args = get_request_args(request)
        
        result = TallerService.get_talleres(
            page=args.get('page', 1),
            per_page=min(args.get('per_page', 10), 100),
            nombre_filter=args.get('nombre'),
            actividad_filter=args.get('actividad')
        )
        
        return success_response(data=result)
        
    except Exception as e:
        return handle_db_error(e, "retrieving workshops")


@actividades_bp.route('/talleres/<int:taller_id>', methods=['GET'])
@apoyo_required
def get_taller(current_user, taller_id):
    """
    Get workshop by ID.
    
    Path Parameters:
        taller_id (int): Workshop ID
        
    Returns:
        JSON: Workshop data
    """
    try:
        taller = TallerService.get_taller_by_id(taller_id)
        return success_response(data=taller.to_dict())
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "retrieving workshop")


@actividades_bp.route('/talleres', methods=['POST'])
@can_update_records
def create_taller(current_user):
    """
    Create a new workshop.
    
    Body (JSON):
        nombre_taller (str): Workshop name (required, max 100 chars)
        descripcion_taller (str): Description (optional, max 500 chars)
        id_actividad (int): Activity ID (required)
        id_persona_a_cargo (int): Responsible person ID (optional)
        
    Returns:
        JSON: Created workshop data
    """
    try:
        data = request.get_json() or {}
        taller = TallerService.create_taller(data)
        
        return created_response(
            data=taller.to_dict(),
            message="Taller creado exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating workshop")


@actividades_bp.route('/talleres/<int:taller_id>', methods=['PUT'])
@can_update_records
def update_taller(current_user, taller_id):
    """
    Update a workshop.
    
    Path Parameters:
        taller_id (int): Workshop ID
        
    Body (JSON):
        nombre_taller (str): Workshop name (optional)
        descripcion_taller (str): Description (optional)
        id_actividad (int): Activity ID (optional)
        id_persona_a_cargo (int): Responsible person ID (optional)
        
    Returns:
        JSON: Updated workshop data
    """
    try:
        data = request.get_json() or {}
        taller = TallerService.update_taller(taller_id, data)
        
        return success_response(
            data=taller.to_dict(),
            message="Taller actualizado exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "updating workshop")


@actividades_bp.route('/talleres/<int:taller_id>', methods=['DELETE'])
@can_delete_vital_records
def delete_taller(current_user, taller_id):
    """
    Delete a workshop.
    
    Path Parameters:
        taller_id (int): Workshop ID
        
    Returns:
        JSON: Deletion confirmation
    """
    try:
        TallerService.delete_taller(taller_id)
        
        return success_response(
            message="Taller eliminado exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "deleting workshop")