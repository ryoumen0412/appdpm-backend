"""
Standardized Response Utilities

Provides consistent response formatting for all API endpoints.
"""

from flask import jsonify
from datetime import datetime


def success_response(data=None, message=None, status_code=200):
    """
    Create a standardized success response.
    
    Args:
        data: Response data (optional)
        message: Success message (optional)
        status_code: HTTP status code (default: 200)
        
    Returns:
        tuple: (jsonify(response), status_code)
    """
    response = {
        'success': True,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return jsonify(response), status_code


def error_response(message, status_code=400, details=None, error_code=None):
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code (default: 400)
        details: Additional error details (optional)
        error_code: Application-specific error code (optional)
        
    Returns:
        tuple: (jsonify(response), status_code)
    """
    response = {
        'success': False,
        'error': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    if error_code:
        response['error_code'] = error_code
    
    return jsonify(response), status_code


def paginated_response(items, pagination, message=None, status_code=200):
    """
    Create a standardized paginated response.
    
    Args:
        items: List of serialized items
        pagination: Pagination metadata
        message: Optional message
        status_code: HTTP status code (default: 200)
        
    Returns:
        tuple: (jsonify(response), status_code)
    """
    data = {
        'items': items,
        'pagination': pagination
    }
    
    return success_response(data=data, message=message, status_code=status_code)


def created_response(data, message="Resource created successfully"):
    """
    Convenience method for creation responses.
    """
    return success_response(data=data, message=message, status_code=201)


def deleted_response(message="Resource deleted successfully"):
    """
    Convenience method for deletion responses.
    """
    return success_response(message=message, status_code=200)