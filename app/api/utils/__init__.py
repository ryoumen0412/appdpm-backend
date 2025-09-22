"""
API Utilities Package

Provides common utilities for API routes including:
- Pagination helpers
- Standardized response formatting
- Error handling utilities
- Request argument parsing
"""

from flask import request

from .pagination import paginate_query, create_pagination_response
from .responses import (
    success_response, error_response, paginated_response,
    created_response, deleted_response
)
from .errors import (
    handle_db_error, ValidationError, BusinessLogicError,
    handle_validation_error, handle_business_logic_error
)


def get_request_args(request_obj):
    """
    Extract and parse request arguments for API endpoints.
    
    Args:
        request_obj: Flask request object
        
    Returns:
        dict: Parsed request arguments with appropriate types
    """
    args = {}
    
    # Pagination parameters
    if 'page' in request_obj.args:
        try:
            args['page'] = int(request_obj.args.get('page', 1))
        except (ValueError, TypeError):
            args['page'] = 1
    
    if 'per_page' in request_obj.args:
        try:
            args['per_page'] = int(request_obj.args.get('per_page', 10))
        except (ValueError, TypeError):
            args['per_page'] = 10
    
    # Filter parameters (string filters)
    string_filters = [
        'nombre', 'rut', 'username', 'sector', 'direccion', 'cargo',
        'email', 'telefono', 'fecha', 'fecha_inicio', 'fecha_fin',
        'centro', 'actividad', 'nivel'
    ]
    
    for filter_name in string_filters:
        if filter_name in request_obj.args:
            value = request_obj.args.get(filter_name)
            if value and value.strip():
                # Try to convert 'nivel' to int
                if filter_name == 'nivel':
                    try:
                        args[filter_name] = int(value)
                    except (ValueError, TypeError):
                        pass  # Invalid level, ignore
                else:
                    args[filter_name] = value.strip()
    
    return args


__all__ = [
    'paginate_query', 'create_pagination_response',
    'success_response', 'error_response', 'paginated_response',
    'created_response', 'deleted_response',
    'handle_db_error', 'ValidationError', 'BusinessLogicError',
    'handle_validation_error', 'handle_business_logic_error',
    'get_request_args'
]