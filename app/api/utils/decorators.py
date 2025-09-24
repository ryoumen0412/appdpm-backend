"""
API Decorators

Decorators for centralized error handling, validation, and logging.
"""

from functools import wraps
from flask import request, jsonify
import traceback
import logging

from .errors import ValidationError, BusinessLogicError
from .responses import success_response
from .errors import handle_validation_error, handle_business_logic_error, handle_db_error


def handle_api_errors(operation_description="operación"):
    """
    Decorador para manejo centralizado de errores en endpoints de API.
    
    Args:
        operation_description (str): Descripción de la operación para logging y mensajes de error
        
    Usage:
        @handle_api_errors("crear usuario")
        def create_user():
            # lógica del endpoint
            return result
            
    Returns:
        Decorated function with automatic error handling
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                return result
                
            except ValidationError as e:
                logging.warning(f"Error de validación en {operation_description}: {str(e)}")
                return handle_validation_error(e)
                
            except BusinessLogicError as e:
                logging.warning(f"Error de lógica de negocio en {operation_description}: {str(e)}")
                return handle_business_logic_error(e)
                
            except Exception as e:
                logging.error(f"Error inesperado en {operation_description}: {str(e)}")
                logging.error(f"Traceback: {traceback.format_exc()}")
                return handle_db_error(e, operation_description)
                
        return wrapper
    return decorator


def handle_crud_errors(entity_name, operation_type):
    """
    Decorador especializado para operaciones CRUD con mensajes más específicos.
    
    Args:
        entity_name (str): Nombre de la entidad (ej: "usuario", "centro")
        operation_type (str): Tipo de operación ("crear", "actualizar", "eliminar", "obtener", "listar")
        
    Usage:
        @handle_crud_errors("usuario", "crear")
        def create_user():
            # lógica del endpoint
            return result
            
    Returns:
        Decorated function with automatic CRUD error handling
    """
    operation_description = f"{operation_type} {entity_name}"
    
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                return result
                
            except ValidationError as e:
                logging.warning(f"Error de validación al {operation_description}: {str(e)}")
                return handle_validation_error(e)
                
            except BusinessLogicError as e:
                logging.warning(f"Error de lógica de negocio al {operation_description}: {str(e)}")
                return handle_business_logic_error(e)
                
            except Exception as e:
                logging.error(f"Error inesperado al {operation_description}: {str(e)}")
                logging.error(f"Traceback: {traceback.format_exc()}")
                return handle_db_error(e, operation_description)
                
        return wrapper
    return decorator


def require_json(f):
    """
    Decorador para validar que el request tenga Content-Type JSON.
    
    Usage:
        @require_json
        def create_something():
            data = request.get_json()
            # lógica del endpoint
            
    Returns:
        Decorated function that validates JSON content type
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type debe ser application/json',
                'message': 'El endpoint requiere datos en formato JSON'
            }), 400
        return f(*args, **kwargs)
    return wrapper


def validate_request_data(required_fields=None, optional_fields=None):
    """
    Decorador para validar datos de entrada del request.
    
    Args:
        required_fields (list): Lista de campos requeridos
        optional_fields (list): Lista de campos opcionales permitidos
        
    Usage:
        @validate_request_data(['nombre', 'email'], ['telefono', 'direccion'])
        def create_user():
            data = request.get_json()
            # data ya está validado
            
    Returns:
        Decorated function with automatic request data validation
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'error': 'No se proporcionaron datos',
                    'message': 'El cuerpo de la petición está vacío'
                }), 400
            
            # Validar campos requeridos
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data or not data[field]]
                if missing_fields:
                    return jsonify({
                        'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}',
                        'message': 'Algunos campos obligatorios no fueron proporcionados'
                    }), 400
            
            # Validar campos no permitidos
            if required_fields or optional_fields:
                allowed_fields = set((required_fields or []) + (optional_fields or []))
                invalid_fields = [field for field in data.keys() if field not in allowed_fields]
                if invalid_fields:
                    return jsonify({
                        'error': f'Campos no permitidos: {", ".join(invalid_fields)}',
                        'message': 'Se enviaron campos que no están permitidos para esta operación'
                    }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def log_api_call(f):
    """
    Decorador para logging automático de llamadas a la API.
    
    Usage:
        @log_api_call
        def some_endpoint():
            # lógica del endpoint
            
    Returns:
        Decorated function with automatic API call logging
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Log request
        logging.info(
            f"API Request: {request.method} {request.path} - "
            f"IP: {request.remote_addr} - "
            f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
        )
        
        # Execute function
        result = f(*args, **kwargs)
        
        # Log response
        status_code = getattr(result, 'status_code', 'Unknown')
        logging.info(f"API Response: {request.method} {request.path} - Status: {status_code}")
        
        return result
    return wrapper


def validate_pagination_params(f):
    """
    Decorador para validar y normalizar parámetros de paginación.
    
    Usage:
        @validate_pagination_params
        def get_paginated_data():
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            # page y per_page ya están validados
            
    Returns:
        Decorated function with validated pagination parameters
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Validar página
        page = request.args.get('page', 1, type=int)
        if page < 1:
            return jsonify({
                'error': 'Número de página inválido',
                'message': 'El número de página debe ser mayor a 0'
            }), 400
        
        # Validar elementos por página
        per_page = request.args.get('per_page', 10, type=int)
        if per_page < 1 or per_page > 100:
            return jsonify({
                'error': 'Cantidad de elementos por página inválida',
                'message': 'Debe estar entre 1 y 100 elementos por página'
            }), 400
        
        return f(*args, **kwargs)
    return wrapper


def require_auth(f):
    """
    Decorador para requerir autenticación en endpoints.
    
    Usage:
        @require_auth
        def protected_endpoint():
            # lógica del endpoint protegido
            
    Returns:
        Decorated function that requires authentication
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Esta implementación sería específica según el sistema de auth usado
        # Por ahora, solo es un placeholder
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'error': 'Autenticación requerida',
                'message': 'Este endpoint requiere autenticación'
            }), 401
        
        return f(*args, **kwargs)
    return wrapper


def handle_file_upload_errors(allowed_extensions=None, max_file_size=None):
    """
    Decorador para manejo de errores en uploads de archivos.
    
    Args:
        allowed_extensions (list): Extensiones permitidas (ej: ['.pdf', '.jpg'])
        max_file_size (int): Tamaño máximo en bytes
        
    Usage:
        @handle_file_upload_errors(['.pdf', '.jpg'], 5*1024*1024)  # 5MB
        def upload_file():
            # lógica de upload
            
    Returns:
        Decorated function with file upload validation
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'file' not in request.files:
                return jsonify({
                    'error': 'No se proporcionó archivo',
                    'message': 'Debe incluir un archivo en la petición'
                }), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'error': 'Nombre de archivo vacío',
                    'message': 'El archivo debe tener un nombre válido'
                }), 400
            
            # Validar extensión
            if allowed_extensions:
                import os
                _, ext = os.path.splitext(file.filename.lower())
                if ext not in allowed_extensions:
                    return jsonify({
                        'error': f'Tipo de archivo no permitido',
                        'message': f'Solo se permiten archivos: {", ".join(allowed_extensions)}'
                    }), 400
            
            # Validar tamaño (si se puede determinar)
            if max_file_size and hasattr(file, 'content_length') and file.content_length:
                if file.content_length > max_file_size:
                    return jsonify({
                        'error': 'Archivo demasiado grande',
                        'message': f'El archivo no debe exceder {max_file_size} bytes'
                    }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator