"""
API Routes Registration Module

Este módulo registra todos los blueprints modulares de la API REST.
La estructura modular incluye:
- /api/auth/**: Módulo de autenticación
- /api/usuarios/**: Módulo de gestión de usuarios  
- /api/personas/**: Módulo de gestión de personas (mayores y a cargo)
- /api/centros/**: Módulo de centros comunitarios
- /api/actividades/**: Módulo de actividades y talleres
- /api/servicios/**: Módulo de servicios, mantenciones y relaciones
- /api/mantenciones/**: Módulo de mantenciones de centros
- /api/trabajadores-apoyo/**: Módulo de trabajadores de apoyo

Este archivo reemplaza el antiguo api.py monolítico.
"""

from flask import Blueprint
from app.api.auth import auth_bp
from app.api.usuarios import usuarios_bp
from app.api.personas import personas_mayores_bp, personas_a_cargo_bp
from app.api.centros import centros_bp
from app.api.actividades import actividades_bp
from app.api.servicios import servicios_bp
from app.api.mantenciones import mantenciones_bp
from app.api.trabajadores import trabajadores_bp

# Crear blueprint legacy vacío (puede ser eliminado en el futuro)
api_bp = Blueprint('api', __name__)

def register_api_blueprints(app):
    """
    Register all API blueprints with the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Authentication module
    app.register_blueprint(auth_bp)
    
    # User management module
    app.register_blueprint(usuarios_bp)
    
    # Personas modules
    app.register_blueprint(personas_mayores_bp)
    app.register_blueprint(personas_a_cargo_bp)
    
    # Community centers module
    app.register_blueprint(centros_bp)
    
    # Activities module
    app.register_blueprint(actividades_bp)
    
    # Services module
    app.register_blueprint(servicios_bp)
    
    # Maintenance module
    app.register_blueprint(mantenciones_bp)
    
    # Support workers module
    app.register_blueprint(trabajadores_bp)
    
    # Legacy blueprint (can be removed in future)
    app.register_blueprint(api_bp, url_prefix='/api')