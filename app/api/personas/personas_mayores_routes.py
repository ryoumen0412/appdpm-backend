"""
Personas Mayores Routes

RESTful endpoints for managing elderly people in the system.
"""

from flask import Blueprint, request
from app import db
from app.models import PersonasMayores
from app.auth_utils import apoyo_required, can_update_records, can_delete_vital_records
from app.api.utils import (
    paginate_query, success_response, error_response, 
    created_response, deleted_response, handle_db_error,
    handle_validation_error, handle_business_logic_error,
    ValidationError, BusinessLogicError
)
from .services import PersonasMayoresService

personas_mayores_bp = Blueprint(
    'personas_mayores', 
    __name__, 
    url_prefix='/api/personas-mayores'
)


@personas_mayores_bp.route('', methods=['GET'])
@apoyo_required
def list_personas_mayores(current_user):
    """
    Get paginated list of personas mayores with filters.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 50, max: 100)
        search (str): Search in RUT, nombre, apellidos
        sector (str): Filter by sector
        genero (str): Filter by gender
        
    Returns:
        JSON: Paginated list with metadata
    """
    try:
        # Get filter parameters
        search = request.args.get('search', '').strip()
        sector = request.args.get('sector', '').strip()
        genero = request.args.get('genero', '').strip()
        
        # Build filtered query
        query = PersonasMayoresService.build_search_query(
            search=search, 
            sector=sector, 
            genero=genero
        )
        
        # Paginate results
        result = paginate_query(query)
        
        # Add filter information to response
        result['filters'] = {
            'search': search,
            'sector': sector,
            'genero': genero
        }
        
        return success_response(data=result)
        
    except Exception as e:
        return handle_db_error(e, "retrieving personas mayores")


@personas_mayores_bp.route('/<string:rut>', methods=['GET'])
@apoyo_required
def get_persona_mayor(current_user, rut):
    """
    Get a specific persona mayor by RUT.
    
    Args:
        rut (str): RUT of the person
        
    Returns:
        JSON: Person data
    """
    try:
        persona = PersonasMayores.query.get_or_404(rut)
        return success_response(data=persona.to_dict())
        
    except Exception as e:
        return handle_db_error(e, "retrieving persona mayor")


@personas_mayores_bp.route('', methods=['POST'])
@can_update_records
def create_persona_mayor(current_user):
    """
    Create a new persona mayor.
    
    Body (JSON):
        rut (str): RUT (required)
        nombre (str): First name (required)
        apellidos (str): Last names (required)
        genero (str): Gender (optional)
        fecha_nacimiento (str): Birth date YYYY-MM-DD (optional)
        direccion (str): Address (optional)
        sector (str): Sector (optional)
        telefono (str): Phone (optional)
        email (str): Email (optional)
        cedula_discapacidad (bool): Disability certificate (optional, default: false)
        
    Returns:
        JSON: Created person data
    """
    try:
        data = request.get_json() or {}
        persona = PersonasMayoresService.create_persona_mayor(data)
        
        return created_response(
            data=persona.to_dict(),
            message="Persona mayor creada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating persona mayor")


@personas_mayores_bp.route('/<string:rut>', methods=['PUT'])
@can_update_records
def update_persona_mayor(current_user, rut):
    """
    Update an existing persona mayor.
    
    Args:
        rut (str): RUT of the person to update
        
    Body (JSON):
        Any of the fields from create (except rut)
        
    Returns:
        JSON: Updated person data
    """
    try:
        data = request.get_json() or {}
        persona = PersonasMayoresService.update_persona_mayor(rut, data)
        
        return success_response(
            data=persona.to_dict(),
            message="Persona mayor actualizada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except Exception as e:
        return handle_db_error(e, "updating persona mayor")


@personas_mayores_bp.route('/<string:rut>', methods=['DELETE'])
@can_delete_vital_records
def delete_persona_mayor(current_user, rut):
    """
    Delete a persona mayor.
    
    Args:
        rut (str): RUT of the person to delete
        
    Returns:
        JSON: Success confirmation
    """
    try:
        persona = PersonasMayores.query.get_or_404(rut)
        
        db.session.delete(persona)
        db.session.commit()
        
        return deleted_response("Persona mayor eliminada exitosamente")
        
    except Exception as e:
        return handle_db_error(e, "deleting persona mayor")