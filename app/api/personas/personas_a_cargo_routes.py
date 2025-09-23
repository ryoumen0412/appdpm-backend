"""
Personas a Cargo Routes

RESTful endpoints for managing caregivers in the system.
"""

from flask import Blueprint, request
from app.extensions import db
from app.models import PersonasACargo
from app.auth_utils import apoyo_required, admin_required, can_update_records, can_delete_vital_records
from app.api.utils import (
    success_response, error_response, created_response, deleted_response,
    handle_db_error, handle_validation_error, handle_business_logic_error,
    ValidationError, BusinessLogicError
)
from .services import PersonasACargoService

personas_a_cargo_bp = Blueprint(
    'personas_a_cargo', 
    __name__, 
    url_prefix='/api/personas-a-cargo'
)


@personas_a_cargo_bp.route('', methods=['GET'])
@apoyo_required
def list_personas_a_cargo(current_user):
    """
    Get all personas a cargo.
    
    Returns:
        JSON: List of all caregivers
    """
    try:
        personas = PersonasACargo.query.all()
        return success_response(
            data=[persona.to_dict() for persona in personas]
        )
        
    except Exception as e:
        return handle_db_error(e, "retrieving personas a cargo")


@personas_a_cargo_bp.route('/<string:rut>', methods=['GET'])
@apoyo_required
def get_persona_a_cargo(current_user, rut):
    """
    Get a specific persona a cargo by RUT.
    
    Args:
        rut (str): RUT of the caregiver
        
    Returns:
        JSON: Caregiver data
    """
    try:
        persona = PersonasACargo.query.get_or_404(rut)
        return success_response(data=persona.to_dict())
        
    except Exception as e:
        return handle_db_error(e, "retrieving persona a cargo")


@personas_a_cargo_bp.route('', methods=['POST'])
@admin_required
def create_persona_a_cargo(current_user):
    """
    Create a new persona a cargo (admin only).
    
    Body (JSON):
        rut (str): RUT (required)
        nombre (str): First name (required)
        apellido (str): Last name (required)
        correo_electronico (str): Email (optional)
        telefono (str): Phone (optional)
        fecha_nacimiento (str): Birth date YYYY-MM-DD (optional)
        
    Returns:
        JSON: Created caregiver data
    """
    try:
        data = request.get_json() or {}
        persona = PersonasACargoService.create_persona_a_cargo(data)
        
        return created_response(
            data=persona.to_dict(),
            message="Persona a cargo creada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except BusinessLogicError as e:
        return handle_business_logic_error(e)
    except Exception as e:
        return handle_db_error(e, "creating persona a cargo")


@personas_a_cargo_bp.route('/<string:rut>', methods=['PUT'])
@can_update_records
def update_persona_a_cargo(current_user, rut):
    """
    Update an existing persona a cargo.
    
    Args:
        rut (str): RUT of the caregiver to update
        
    Body (JSON):
        Any of the fields from create (except rut)
        
    Returns:
        JSON: Updated caregiver data
    """
    try:
        data = request.get_json() or {}
        persona = PersonasACargoService.update_persona_a_cargo(rut, data)
        
        return success_response(
            data=persona.to_dict(),
            message="Persona a cargo actualizada exitosamente"
        )
        
    except ValidationError as e:
        return handle_validation_error(e)
    except Exception as e:
        return handle_db_error(e, "updating persona a cargo")


@personas_a_cargo_bp.route('/<string:rut>', methods=['DELETE'])
@can_delete_vital_records
def delete_persona_a_cargo(current_user, rut):
    """
    Delete a persona a cargo (admin only).
    
    Args:
        rut (str): RUT of the caregiver to delete
        
    Returns:
        JSON: Success confirmation
    """
    try:
        persona = PersonasACargo.query.get_or_404(rut)
        
        db.session.delete(persona)
        db.session.commit()
        
        return deleted_response("Persona a cargo eliminada exitosamente")
        
    except Exception as e:
        return handle_db_error(e, "deleting persona a cargo")