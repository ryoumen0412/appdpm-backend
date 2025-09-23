"""
Error Handling Utilities

Provides common error handling patterns and custom exceptions.
"""

import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.extensions import db
from .responses import error_response

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """
    Custom exception for validation errors.
    """
    def __init__(self, message, field=None, code=None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.code = code


class BusinessLogicError(Exception):
    """
    Custom exception for business logic violations.
    """
    def __init__(self, message, code=None):
        super().__init__(message)
        self.message = message
        self.code = code


def handle_db_error(error, operation="database operation"):
    """
    Handle database errors consistently.
    
    Args:
        error: The database error that occurred
        operation: Description of the operation that failed
        
    Returns:
        tuple: (jsonify(error_response), status_code)
    """
    db.session.rollback()
    
    if isinstance(error, IntegrityError):
        logger.warning(f"Integrity error during {operation}: {str(error)}")
        
        # Common integrity constraint violations
        error_msg = str(error.orig).lower()
        if 'unique' in error_msg or 'duplicate' in error_msg:
            return error_response(
                "Resource already exists with these values",
                status_code=409,
                error_code="DUPLICATE_RESOURCE"
            )
        elif 'foreign key' in error_msg:
            return error_response(
                "Referenced resource does not exist",
                status_code=400,
                error_code="INVALID_REFERENCE"
            )
        else:
            return error_response(
                "Data integrity constraint violation",
                status_code=400,
                error_code="INTEGRITY_ERROR"
            )
    
    elif isinstance(error, SQLAlchemyError):
        logger.error(f"Database error during {operation}: {str(error)}")
        return error_response(
            f"Database error during {operation}",
            status_code=500,
            error_code="DATABASE_ERROR"
        )
    
    else:
        logger.error(f"Unexpected error during {operation}: {str(error)}")
        return error_response(
            f"Unexpected error during {operation}",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )


def handle_validation_error(error):
    """
    Handle validation errors consistently.
    
    Args:
        error: ValidationError instance
        
    Returns:
        tuple: (jsonify(error_response), status_code)
    """
    details = {}
    if error.field:
        details['field'] = error.field
    
    return error_response(
        error.message,
        status_code=400,
        details=details,
        error_code=error.code or "VALIDATION_ERROR"
    )


def handle_business_logic_error(error):
    """
    Handle business logic errors consistently.
    
    Args:
        error: BusinessLogicError instance
        
    Returns:
        tuple: (jsonify(error_response), status_code)
    """
    return error_response(
        error.message,
        status_code=422,
        error_code=error.code or "BUSINESS_LOGIC_ERROR"
    )