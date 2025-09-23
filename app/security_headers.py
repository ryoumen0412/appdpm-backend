"""
Security Headers Module

Este módulo implementa headers de seguridad críticos para proteger
la aplicación contra ataques comunes como:
- Clickjacking (X-Frame-Options)
- MIME sniffing (X-Content-Type-Options)
- XSS (Content-Security-Policy, X-XSS-Protection)
- Information leakage (Referrer-Policy)
- HTTPS enforcement (Strict-Transport-Security)
"""

from flask import current_app

class SecurityHeaders:
    """Clase para manejar headers de seguridad"""
    
    @staticmethod
    def get_security_headers():
        """
        Retorna diccionario con headers de seguridad apropiados
        según el entorno (desarrollo/producción).
        """
        is_production = current_app.config.get('FLASK_ENV') == 'production'
        
        headers = {
            # Prevenir clickjacking - no permitir iframe
            'X-Frame-Options': 'DENY',
            
            # Prevenir MIME sniffing - respetar Content-Type declarado
            'X-Content-Type-Options': 'nosniff',
            
            # XSS Protection para browsers antiguos
            'X-XSS-Protection': '1; mode=block',
            
            # Controlar información en referrer
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Política de permisos (Permissions Policy)
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            
            # Cache control para endpoints sensibles
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        # Content Security Policy - más estricta en producción
        if is_production:
            headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
            
            # HSTS solo en producción (requiere HTTPS)
            headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
            
        else:
            # CSP más permisiva en desarrollo
            headers['Content-Security-Policy'] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self' http://localhost:* ws://localhost:*; "
                "frame-ancestors 'none'; "
                "base-uri 'self'"
            )
        
        return headers
    
    @staticmethod
    def get_api_specific_headers():
        """Headers específicos para endpoints de API"""
        return {
            # API responses no deben ser cacheadas por defecto
            'Cache-Control': 'no-cache, no-store, must-revalidate, private',
            
            # Prevenir que el navegador trate de detectar el tipo de contenido
            'X-Content-Type-Options': 'nosniff',
            
            # Asegurar que las respuestas JSON no se interpreten como HTML
            'X-Download-Options': 'noopen',
            
            # Prevenir DNS prefetching en browsers
            'X-DNS-Prefetch-Control': 'off'
        }
    
    @staticmethod
    def apply_security_headers(response):
        """
        Aplica headers de seguridad a una respuesta Flask
        
        Args:
            response: Flask Response object
            
        Returns:
            Flask Response object con headers de seguridad
        """
        # Headers generales de seguridad
        security_headers = SecurityHeaders.get_security_headers()
        
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value
        
        return response
    
    @staticmethod
    def apply_auth_headers(response):
        """
        Headers específicos para endpoints de autenticación
        
        Args:
            response: Flask Response object
            
        Returns:
            Flask Response object con headers de auth
        """
        auth_headers = {
            # Prevenir caching de responses de auth
            'Cache-Control': 'no-cache, no-store, must-revalidate, private',
            'Pragma': 'no-cache',
            'Expires': '0',
            
            # Headers adicionales para auth
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY'
        }
        
        for header_name, header_value in auth_headers.items():
            response.headers[header_name] = header_value
            
        return response


def setup_security_headers(app):
    """
    Configura los headers de seguridad para toda la aplicación Flask
    
    Args:
        app: Flask application instance
    """
    
    @app.after_request
    def add_security_headers(response):
        """Middleware para agregar headers de seguridad a todas las respuestas"""
        from flask import request
        
        # Aplicar headers de seguridad generales
        response = SecurityHeaders.apply_security_headers(response)
        
        # Headers específicos para endpoints de API
        if request and '/api/' in request.path:
            api_headers = SecurityHeaders.get_api_specific_headers()
            for header_name, header_value in api_headers.items():
                response.headers[header_name] = header_value
        
        # Headers específicos para endpoints de autenticación
        if request and '/api/auth/' in request.path:
            response = SecurityHeaders.apply_auth_headers(response)
        
        return response
    
    # Log de configuración
    app.logger.info('Security headers configured successfully')
    app.logger.info('Headers include: X-Frame-Options, CSP, HSTS, X-Content-Type-Options')