"""
Rate Limiting Utilities

Custom rate limiting functions and decorators for the DPM backend.
"""

from functools import wraps
from flask import request, jsonify, current_app
from app import limiter
import time
import hashlib

def get_user_id_from_token():
    """
    Extract user ID from JWT token for user-specific rate limiting.
    
    Returns:
        str: User ID if token is valid, IP address otherwise
    """
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            from app.auth_utils import verify_auth_token
            payload = verify_auth_token(token)
            if payload:
                return f"user:{payload.get('user_id')}"
    except:
        pass
    
    # Fallback to IP address
    return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

def create_rate_limit_key(identifier):
    """
    Create a consistent rate limit key.
    
    Args:
        identifier (str): User identifier or IP
        
    Returns:
        str: Hashed key for rate limiting
    """
    endpoint = request.endpoint or 'unknown'
    return hashlib.md5(f"{identifier}:{endpoint}".encode()).hexdigest()

def sensitive_operation_limit(max_attempts=3, window_minutes=60):
    """
    Decorator for sensitive operations with strict rate limiting.
    
    Args:
        max_attempts (int): Maximum attempts allowed
        window_minutes (int): Time window in minutes
        
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Apply the rate limit
            limit_string = f"{max_attempts} per {window_minutes} minute{'s' if window_minutes > 1 else ''}"
            
            @limiter.limit(limit_string, key_func=get_user_id_from_token)
            def limited_function():
                return f(*args, **kwargs)
            
            return limited_function()
        
        return decorated_function
    return decorator

def public_endpoint_limit(max_requests=100, window_minutes=60):
    """
    Decorator for public endpoints with IP-based rate limiting.
    
    Args:
        max_requests (int): Maximum requests allowed
        window_minutes (int): Time window in minutes
        
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limit_string = f"{max_requests} per {window_minutes} minute{'s' if window_minutes > 1 else ''}"
            
            @limiter.limit(limit_string)
            def limited_function():
                return f(*args, **kwargs)
            
            return limited_function()
        
        return decorated_function
    return decorator

def get_rate_limit_status():
    """
    Get current rate limit status for monitoring.
    
    Returns:
        dict: Rate limit statistics
    """
    try:
        # This would require Redis for proper implementation
        return {
            "rate_limiting_enabled": True,
            "storage_type": current_app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
            "default_limits": current_app.config.get('RATELIMIT_DEFAULT', '1000 per hour'),
            "headers_enabled": current_app.config.get('RATELIMIT_HEADERS_ENABLED', True)
        }
    except Exception as e:
        current_app.logger.error(f"Error getting rate limit status: {e}")
        return {"rate_limiting_enabled": False, "error": str(e)}

# Rate limiting exemption for health checks and monitoring
def is_health_check_request():
    """
    Check if the request is a health check or monitoring request.
    
    Returns:
        bool: True if this is a health check request
    """
    health_endpoints = ['/health', '/api/health', '/status', '/ping']
    return request.path in health_endpoints

def custom_rate_limit_key():
    """
    Custom key function for rate limiting that considers user authentication.
    
    Returns:
        str: Rate limiting key
    """
    if is_health_check_request():
        return "health_check"
    
    # For authenticated requests, use user ID
    user_id = get_user_id_from_token()
    if user_id.startswith('user:'):
        return user_id
    
    # For unauthenticated requests, use IP address
    return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

# Error handler for rate limit exceeded
def rate_limit_handler(e):
    """
    Custom handler for rate limit exceeded errors.
    
    Args:
        e: RateLimitExceeded exception
        
    Returns:
        tuple: JSON response and status code
    """
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later.",
        "retry_after": getattr(e, 'retry_after', None),
        "limit": getattr(e, 'limit', None),
        "per": getattr(e, 'per', None)
    }), 429