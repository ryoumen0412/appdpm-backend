"""
Services Routes

RESTful endpoints for services, maintenance, and relationship management.
"""

from flask import Blueprint, request
from app.auth_utils import apoyo_required, can_update_records, can_delete_vital_records
from app.api.utils import (
    success_response, error_response, created_response,
    handle_validation_error, handle_business_logic_error, handle_db_error,
    get_request_args, ValidationError, BusinessLogicError
)
from app.api.utils.decorators import validate_rut_parameter
from .services import ServicioService, RelacionService
from app.api.mantenciones.services import MantencionService
from app.api.trabajadores.services import TrabajadorApoyoService

servicios_bp = Blueprint('servicios', __name__, url_prefix='/api/servicios')


# SERVICES ROUTES
@servicios_bp.route('/', methods=['GET'])
@apoyo_required
def get_servicios(current_user):
    """
    Get paginated list of services with optional filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)
        nombre (str): Filter by service name
        
    Returns:
        JSON: Paginated services list
    """
    try:
        args = get_request_args(request)
        
        result = ServicioService.get_servicios(
            page=args.get('page', 1),
            per_page=min(args.get('per_page', 10), 100),
            nombre_filter=args.get('nombre')
        )
        
        return success_response(data=result)
        
    except Exception as e:
        return handle_db_error(e, "retrieving services")


@servicios_bp.route('/<int:servicio_id>', methods=['GET'])
@apoyo_required
def get_servicio(current_user, servicio_id):
    """
    Get service by ID.
    
    Path Parameters:
        servicio_id (int): Service ID
        
    Returns:
        JSON: Service data
    """
    try:
        servicio = ServicioService.get_servicio_by_id(servicio_id)
        return success_response(data=servicio.to_dict())
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "retrieving service")


@servicios_bp.route('/', methods=['POST'])
@can_update_records
def create_servicio(current_user):
    """
    Create a new service.
    
    Body (JSON):
        nombre_servicio (str): Service name (required, max 100 chars)
        descripcion_servicio (str): Description (required, max 500 chars)
        
    Returns:
        JSON: Created service data
    """
    try:
        data = request.get_json() or {}
        servicio = ServicioService.create_servicio(data)
        
        return created_response(
            data=servicio.to_dict(),
            message="Servicio creado exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating service")


@servicios_bp.route('/<int:servicio_id>', methods=['PUT'])
@can_update_records
def update_servicio(current_user, servicio_id):
    """
    Update a service.
    
    Path Parameters:
        servicio_id (int): Service ID
        
    Body (JSON):
        nombre_servicio (str): Service name (optional)
        descripcion_servicio (str): Description (optional)
        
    Returns:
        JSON: Updated service data
    """
    try:
        data = request.get_json() or {}
        servicio = ServicioService.update_servicio(servicio_id, data)
        
        return success_response(
            data=servicio.to_dict(),
            message="Servicio actualizado exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "updating service")


@servicios_bp.route('/<int:servicio_id>', methods=['DELETE'])
@can_delete_vital_records
def delete_servicio(current_user, servicio_id):
    """
    Delete a service.
    
    Path Parameters:
        servicio_id (int): Service ID
        
    Returns:
        JSON: Deletion confirmation
    """
    try:
        ServicioService.delete_servicio(servicio_id)
        
        return success_response(
            message="Servicio eliminado exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "deleting service")


# MAINTENANCE ROUTES
@servicios_bp.route('/mantenciones', methods=['GET'])
@apoyo_required
def get_mantenciones(current_user):
    """
    Get paginated list of maintenances with optional filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)
        centro (int): Filter by center ID
        fecha_desde (str): Filter maintenance from this date (YYYY-MM-DD)
        fecha_hasta (str): Filter maintenance until this date (YYYY-MM-DD)
        
    Returns:
        JSON: Paginated maintenances list
    """
    try:
        args = get_request_args(request)
        
        result = MantencionService.get_mantenciones(
            page=args.get('page', 1),
            per_page=min(args.get('per_page', 10), 100),
            centro_filter=args.get('centro'),
            fecha_desde=args.get('fecha_desde'),
            fecha_hasta=args.get('fecha_hasta')
        )
        
        return success_response(data=result)
        
    except Exception as e:
        return handle_db_error(e, "retrieving maintenances")


@servicios_bp.route('/mantenciones/<int:mantencion_id>', methods=['GET'])
@apoyo_required
def get_mantencion(current_user, mantencion_id):
    """
    Get maintenance by ID.
    
    Path Parameters:
        mantencion_id (int): Maintenance ID
        
    Returns:
        JSON: Maintenance data
    """
    try:
        mantencion = MantencionService.get_mantencion_by_id(mantencion_id)
        return success_response(data=mantencion.to_dict())
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "retrieving maintenance")


@servicios_bp.route('/mantenciones', methods=['POST'])
@can_update_records
def create_mantencion(current_user):
    """
    Create a new maintenance.
    
    Body (JSON):
        nombre_mantencion (str): Maintenance name (required, max 100 chars)
        descripcion_mantencion (str): Description (required, max 500 chars)
        fecha_mantencion (str): Maintenance date (optional, YYYY-MM-DD)
        
    Returns:
        JSON: Created maintenance data
    """
    try:
        data = request.get_json() or {}
        mantencion = MantencionService.create_mantencion(data)
        
        return created_response(
            data=mantencion.to_dict(),
            message="Mantención creada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating maintenance")


@servicios_bp.route('/mantenciones/<int:mantencion_id>', methods=['PUT'])
@can_update_records
def update_mantencion(current_user, mantencion_id):
    """
    Update a maintenance.
    
    Path Parameters:
        mantencion_id (int): Maintenance ID
        
    Body (JSON):
        nombre_mantencion (str): Maintenance name (optional)
        descripcion_mantencion (str): Description (optional)
        fecha_mantencion (str): Maintenance date (optional, YYYY-MM-DD)
        
    Returns:
        JSON: Updated maintenance data
    """
    try:
        data = request.get_json() or {}
        mantencion = MantencionService.update_mantencion(mantencion_id, data)
        
        return success_response(
            data=mantencion.to_dict(),
            message="Mantención actualizada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "updating maintenance")


@servicios_bp.route('/mantenciones/<int:mantencion_id>', methods=['DELETE'])
@can_delete_vital_records
def delete_mantencion(current_user, mantencion_id):
    """
    Delete a maintenance.
    
    Path Parameters:
        mantencion_id (int): Maintenance ID
        
    Returns:
        JSON: Deletion confirmation
    """
    try:
        MantencionService.delete_mantencion(mantencion_id)
        
        return success_response(
            message="Mantención eliminada exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "deleting maintenance")


# SUPPORT WORKERS ROUTES
@servicios_bp.route('/trabajadores-apoyo', methods=['GET'])
@apoyo_required
def get_trabajadores_apoyo(current_user):
    """
    Get paginated list of support workers with optional filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)
        nombre (str): Filter by worker name
        cargo (str): Filter by position
        
    Returns:
        JSON: Paginated workers list
    """
    try:
        args = get_request_args(request)
        
        result = TrabajadorApoyoService.get_trabajadores(
            page=args.get('page', 1),
            per_page=min(args.get('per_page', 10), 100),
            nombre_filter=args.get('nombre'),
            cargo_filter=args.get('cargo')
        )
        
        return success_response(data=result)
        
    except Exception as e:
        return handle_db_error(e, "retrieving support workers")


@servicios_bp.route('/trabajadores-apoyo/<string:trabajador_rut>', methods=['GET'])
@apoyo_required
@validate_rut_parameter
def get_trabajador_apoyo(current_user, trabajador_rut):
    """
    Get support worker by RUT.
    
    Path Parameters:
        trabajador_rut (string): Worker RUT
        
    Returns:
        JSON: Worker data
    """
    try:
        trabajador = TrabajadorApoyoService.get_trabajador_by_rut(trabajador_rut)
        return success_response(data=trabajador.to_dict())
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "retrieving support worker")


@servicios_bp.route('/trabajadores-apoyo', methods=['POST'])
@can_update_records
def create_trabajador_apoyo(current_user):
    """
    Create a new support worker.
    
    Body (JSON):
        nombre_trabajador (str): Worker name (required, max 100 chars)
        cargo_trabajador (str): Position (required, max 100 chars)
        
    Returns:
        JSON: Created worker data
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


@servicios_bp.route('/trabajadores-apoyo/<int:trabajador_id>', methods=['PUT'])
@can_update_records
def update_trabajador_apoyo(current_user, trabajador_id):
    """
    Update a support worker.
    
    Path Parameters:
        trabajador_id (int): Worker ID
        
    Body (JSON):
        nombre_trabajador (str): Worker name (optional)
        cargo_trabajador (str): Position (optional)
        
    Returns:
        JSON: Updated worker data
    """
    try:
        data = request.get_json() or {}
        trabajador = TrabajadorApoyoService.update_trabajador(trabajador_id, data)
        
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


@servicios_bp.route('/trabajadores-apoyo/<int:trabajador_id>', methods=['DELETE'])
@can_delete_vital_records
def delete_trabajador_apoyo(current_user, trabajador_id):
    """
    Delete a support worker.
    
    Path Parameters:
        trabajador_id (int): Worker ID
        
    Returns:
        JSON: Deletion confirmation
    """
    try:
        TrabajadorApoyoService.delete_trabajador(trabajador_id)
        
        return success_response(
            message="Trabajador de apoyo eliminado exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "deleting support worker")


# RELATIONSHIP ROUTES
@servicios_bp.route('/participaciones', methods=['POST'])
@can_update_records
def create_participacion(current_user):
    """
    Create a participation relationship.
    
    Body (JSON):
        id_persona_mayor (int): Elderly person ID (required)
        id_actividad (int): Activity ID (required)
        
    Returns:
        JSON: Created participation data
    """
    try:
        data = request.get_json() or {}
        
        if not data.get('id_persona_mayor') or not data.get('id_actividad'):
            raise ValidationError('ID de persona mayor e ID de actividad son requeridos')
        
        participacion = RelacionService.create_participacion(
            data['id_persona_mayor'],
            data['id_actividad']
        )
        
        return created_response(
            data=participacion.to_dict(),
            message="Participación creada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating participation")


@servicios_bp.route('/participaciones/<int:persona_mayor_id>/<int:actividad_id>', methods=['DELETE'])
@can_delete_vital_records
def delete_participacion(current_user, persona_mayor_id, actividad_id):
    """
    Delete a participation relationship.
    
    Path Parameters:
        persona_mayor_id (int): Elderly person ID
        actividad_id (int): Activity ID
        
    Returns:
        JSON: Deletion confirmation
    """
    try:
        RelacionService.delete_participacion(persona_mayor_id, actividad_id)
        
        return success_response(
            message="Participación eliminada exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "deleting participation")


@servicios_bp.route('/gestiones', methods=['POST'])
@can_update_records
def create_gestion(current_user):
    """
    Create a management relationship.
    
    Body (JSON):
        id_persona_a_cargo (int): Person in charge ID (required)
        id_centro (int): Community center ID (required)
        
    Returns:
        JSON: Created management data
    """
    try:
        data = request.get_json() or {}
        
        if not data.get('id_persona_a_cargo') or not data.get('id_centro'):
            raise ValidationError('ID de persona a cargo e ID de centro son requeridos')
        
        gestion = RelacionService.create_gestion(
            data['id_persona_a_cargo'],
            data['id_centro']
        )
        
        return created_response(
            data=gestion.to_dict(),
            message="Gestión creada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating management")


@servicios_bp.route('/gestiones/<int:persona_a_cargo_id>/<int:centro_id>', methods=['DELETE'])
@can_delete_vital_records
def delete_gestion(current_user, persona_a_cargo_id, centro_id):
    """
    Delete a management relationship.
    
    Path Parameters:
        persona_a_cargo_id (int): Person in charge ID
        centro_id (int): Community center ID
        
    Returns:
        JSON: Deletion confirmation
    """
    try:
        RelacionService.delete_gestion(persona_a_cargo_id, centro_id)
        
        return success_response(
            message="Gestión eliminada exitosamente"
        )
        
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "deleting management")