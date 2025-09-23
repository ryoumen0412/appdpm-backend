"""
Configuration Module

Este módulo contiene las configuraciones de la aplicación Flask, incluyendo
configuraciones de base de datos, claves secretas y otros parámetros de entorno.

Las configuraciones se cargan desde variables de entorno para mantener la
seguridad y permitir diferentes configuraciones entre entornos (desarrollo,
producción, testing).

"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

class Config:
    """
    Clase de configuración principal para la aplicación Flask.
    
    Esta clase centraliza todas las configuraciones necesarias para el
    funcionamiento de la aplicación, incluyendo configuraciones de base
    de datos, seguridad, autenticación y otras extensiones.
    
    Attributes:
        SECRET_KEY (str): Clave secreta para encriptación y sesiones
        JWT_SECRET_KEY (str): Clave secreta específica para JWT
        JWT_ACCESS_TOKEN_EXPIRES (int): Tiempo de expiración de tokens en segundos
        SESSION_TYPE (str): Tipo de almacenamiento de sesiones
        SESSION_PERMANENT (bool): Si las sesiones son permanentes por defecto
        PERMANENT_SESSION_LIFETIME (int): Duración de sesiones permanentes en segundos
        DB_HOST (str): Host del servidor de base de datos
        DB_PORT (str): Puerto del servidor de base de datos
        DB_NAME (str): Nombre de la base de datos
        DB_USER (str): Usuario de la base de datos
        DB_PASSWORD (str): Contraseña de la base de datos
        SQLALCHEMY_DATABASE_URI (str): URI completa de conexión a PostgreSQL
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Desactivar tracking de modificaciones
    """
    
    # Configuración de seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Configuración de autenticación JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora por defecto
    
    # Configuración de CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Configuración de sesiones
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('SESSION_LIFETIME', 1800))  # 30 minutos por defecto
    
    # Configuraciones de base de datos PostgreSQL
    # Se obtienen desde variables de entorno con valores por defecto
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'dpm_db')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
    
    # Construcción de la URI de conexión a PostgreSQL
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # Configuraciones de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Desactivar para mejorar rendimiento
    
    # Configuración de Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '1000 per hour')
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_SWALLOW_ERRORS = True  # No fallar si Redis no está disponible