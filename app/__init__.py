import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from sqlalchemy import text
from .config import Config
from .extensions import db, migrate, cors, limiter
from .security_headers import setup_security_headers

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Disable strict slashes to avoid 308 redirects
    app.url_map.strict_slashes = False
    
    try:
        app.config.from_object(config_class)
        _validate_config(app.config)
        _init_extensions(app)
        _configure_logging(app)
        _register_blueprints(app)
        _register_error_handlers(app)
        _init_database(app)
        _setup_security(app)
        
        app.logger.info('Application factory completed')
        return app
    except Exception as e:
        if app:
            app.logger.error(f'App factory failed: {str(e)}')
        raise RuntimeError(f'Failed to create application: {str(e)}')
    
def _validate_config(config):
    required_keys = [
        'SECRET_KEY',
        'SQLALCHEMY_DATABASE_URI',
        'JWT_SECRET_KEY'
    ]
    
    for key in required_keys:
        if not config.get(key):
            raise RuntimeError(F'Missing required configuration: {key}')
        
def _init_extensions(app):
    try:
        db.init_app(app)
        migrate.init_app(app, db)
        limiter.init_app(app)
        
        # CORS configuration - allow all origins for development
        app.logger.info('CORS configured to allow all origins (development mode)')
        
        cors.init_app(app, resources={
            r"/*": {
                "origins": "*",  # Allow all origins
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "expose_headers": ["Content-Type", "Authorization"],
                "supports_credentials": False,  # Must be False when origins is "*"
                "max_age": 3600
            }
        })
    
    except Exception as e:
        raise RuntimeError(f'Extension initialization failed: {str(e)}')

def _configure_logging(app):
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/backend.log',
            maxBytes=10240000,
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Backend startup')
        
    else:
        app.logger.setLevel(logging.DEBUG)
        
def _register_blueprints(app):
    try:
        # Import new modular blueprint registration function
        from .routes.api import register_api_blueprints
        
        # Register all modular blueprints
        register_api_blueprints(app)
        
        app.logger.info('All modular API blueprints registered successfully')
        
        @app.route('/health')
        @app.route('/api/health') # Compatibilidad con scripts de testing
        def health_check():
            try:
                db.session.execute(text('SELECT 1'))
                return jsonify({
                    'status': 'healthy',
                    'database': 'connected',
                    'version': app.config.get('APP_VERSION', '1.0.0'),
                    'modules': ['auth', 'usuarios', 'personas', 'centros', 'actividades', 'servicios']
                }), 200
            except Exception as e:
                app.logger.error(f'Health check failed: {str(e)}')
                return jsonify({
                    'status': 'unhealthy',
                    'database': 'disconnected',
                    'error': 'Database connection failed'
                }), 503
    
    except ImportError as e:
        raise RuntimeError(f'Blueprint registration failed: {str(e)}')

def _register_error_handlers(app):
    
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f'Bad request: {error}')
        return jsonify({
            'error': 'Bad request',
            'message': 'The request could not be understood by the server'
        }), 400
        
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
        
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions'
        }), 403
        
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(f'Rate limit exceeded: {e}')
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': f'Rate limit exceeded: {e.description}'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal server error: {error}')
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

def _init_database(app):
    if app.config.get('ENVIRONMENT') == 'development':
        with app.app_context():
            try:

                from . import models
                    
                db.session.execute(text('SELECT 1'))
                    
                db.create_all()
                app.logger.info('Database tables initialized successfully')
                    
            except Exception as e:
                app.logger.error(f'Database initialization failed: {str(e)}')
                raise ConnectionError(f'Database setup failed: {str(e)}')
    else:
        app.logger.info('Skipping database initialization in production (use migrations)')

def _setup_security(app):
    """Configurar headers de seguridad y otras medidas de seguridad"""
    try:
        # Configurar headers de seguridad
        setup_security_headers(app)
        app.logger.info('Security headers configured successfully')
        
    except Exception as e:
        app.logger.error(f'Security setup failed: {str(e)}')
        raise RuntimeError(f'Security configuration failed: {str(e)}')
            
__all__ = ['create_app', 'db']