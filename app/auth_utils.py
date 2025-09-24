"""
Authentication Utilities Module

Este módulo contiene utilidades para autenticación y autorización en el sistema DPM.
Incluye funciones para manejo de sesiones, generación de tokens JWT, decoradores
de autenticación y otras funciones relacionadas con la seguridad.

"""

import jwt
import secrets
import re
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify, session
from app.extensions import db
from app.models import Usuario

logger = logging.getLogger(__name__)


# =============================================================================
# VALIDACIÓN DE RUT
# =============================================================================

def validate_rut_format(rut):
    """
    Validar que el RUT tenga el formato correcto.
    Formatos aceptados:
    - XXXXXXXX-X (8 dígitos + guión + dígito verificador)
    - XXXXXXX-X (7 dígitos + guión + dígito verificador)
    
    Args:
        rut (str): RUT a validar
        
    Returns:
        bool: True si el formato es válido, False en caso contrario
    """
    if not rut or not isinstance(rut, str):
        return False
    
    # Patrón que acepta 7 u 8 dígitos + guión + dígito verificador (0-9 o k/K)
    pattern = r'^\d{7,8}-[\dkK]$'
    
    is_valid = bool(re.match(pattern, rut.strip()))
    
    if not is_valid:
        logger.debug(f"Formato de RUT inválido: {rut}")
    
    return is_valid


def normalize_rut(rut):
    """
    Normalizar RUT para consistencia (mantener formato original pero limpiar espacios)
    
    Args:
        rut (str): RUT a normalizar
        
    Returns:
        str: RUT normalizado o None si es inválido
    """
    if not rut:
        return None
    
    # Remover espacios en blanco
    normalized = rut.strip()
    
    # Validar formato
    if not validate_rut_format(normalized):
        return None
    
    return normalized


def is_valid_rut_length(rut_without_dash):
    """
    Verificar que la parte numérica del RUT tenga longitud válida
    
    Args:
        rut_without_dash (str): Parte numérica del RUT sin el guión
        
    Returns:
        bool: True si la longitud es válida (7 u 8 dígitos)
    """
    if not rut_without_dash.isdigit():
        return False
    
    return len(rut_without_dash) in [7, 8]


# =============================================================================
# GENERACIÓN DE TOKENS JWT
# =============================================================================

def generate_auth_token(usuario, expires_in=3600):
    """
    Generar token JWT para autenticación del usuario.
    
    Args:
        usuario (Usuario): Instancia del modelo Usuario
        expires_in (int): Tiempo de expiración en segundos (default: 1 hora)
    
    Returns:
        str: Token JWT firmado
    """
    payload = {
        'user_id': usuario.id_usuario,
        'rut': usuario.rut_usuario,
        'nivel': usuario.nivel_usuario,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def verify_auth_token(token):
    """
    Verificar y decodificar token JWT.
    
    Args:
        token (str): Token JWT a verificar
    
    Returns:
        dict or None: Payload del token si es válido, None si es inválido
    """
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido


def generate_session_token():
    """
    Generar token de sesión aleatorio.
    
    Returns:
        str: Token de sesión de 32 caracteres
    """
    return secrets.token_urlsafe(32)


# =============================================================================
# DECORADORES DE AUTENTICACIÓN
# =============================================================================

def token_required(f):
    """
    Decorador para endpoints que requieren autenticación por token JWT.
    
    Usage:
        @token_required
        def protected_endpoint():
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar token en headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer TOKEN"
            except IndexError:
                return jsonify({'error': 'Token malformado'}), 401
        
        if not token:
            return jsonify({'error': 'Token de autenticación requerido'}), 401
        
        try:
            payload = verify_auth_token(token)
            if payload is None:
                return jsonify({'error': 'Token inválido o expirado'}), 401
            
            # Obtener usuario actual
            current_user = Usuario.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'error': 'Usuario no encontrado'}), 401
            
            # Pasar usuario al endpoint
            return f(current_user, *args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': 'Error al verificar token'}), 401
    
    return decorated


def admin_required(f):
    """
    Decorador para endpoints que requieren nivel de administrador.
    
    Usage:
        @admin_required
        def admin_endpoint():
            pass
    """
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Acceso denegado: se requieren privilegios de administrador'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def encargado_required(f):
    """
    Decorador para endpoints que requieren nivel de encargado o superior.
    
    Usage:
        @encargado_required
        def encargado_endpoint():
            pass
    """
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_encargado():
            return jsonify({'error': 'Acceso denegado: se requieren privilegios de encargado o superior'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def apoyo_required(f):
    """
    Decorador para endpoints que requieren al menos nivel de apoyo.
    
    Usage:
        @apoyo_required
        def apoyo_endpoint():
            pass
    """
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_apoyo():
            return jsonify({'error': 'Acceso denegado: se requiere autenticación'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def can_create_users(f):
    """
    Decorador para endpoints que requieren permisos para crear usuarios (solo admin).
    """
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Acceso denegado: solo administradores pueden crear usuarios'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def can_manage_users(f):
    """
    Decorador para endpoints que requieren permisos para gestionar usuarios (admin y encargado).
    Permite listar, ver detalles y realizar operaciones básicas de gestión de usuarios.
    """
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not (current_user.is_admin() or current_user.is_encargado()):
            return jsonify({'error': 'Acceso denegado: se requieren permisos de administrador o encargado'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def can_delete_vital_records(f):
    """
    Decorador para endpoints que requieren permisos para eliminar registros vitales (solo admin).
    Tablas vitales: personas_a_cargo, personas_mayores, centros_comunitarios, etc.
    """
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Acceso denegado: solo administradores pueden eliminar registros vitales'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def can_update_records(f):
    """
    Decorador para endpoints que requieren permisos para actualizar registros (encargado+).
    """
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_encargado():
            return jsonify({'error': 'Acceso denegado: se requieren privilegios de encargado o superior'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def can_update_participa_mantenciones(f):
    """
    Decorador para endpoints que requieren permisos para actualizar participa y mantenciones (apoyo+).
    """
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_apoyo():
            return jsonify({'error': 'Acceso denegado: se requiere autenticación'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


# =============================================================================
# FUNCIONES DE VALIDACIÓN
# =============================================================================

def validate_rut(rut):
    """
    Validar formato de RUT chileno.
    
    Args:
        rut (str): RUT a validar
    
    Returns:
        bool: True si el RUT es válido
    """
    if not rut or len(rut) < 8:
        return False
    
    # Remover puntos y guiones
    rut = rut.replace('.', '').replace('-', '').upper()
    
    if len(rut) < 8 or len(rut) > 9:
        return False
    
    # Separar número y dígito verificador
    numero = rut[:-1]
    dv = rut[-1]
    
    # Validar que el número sean solo dígitos
    if not numero.isdigit():
        return False
    
    # Calcular dígito verificador
    suma = 0
    multiplicador = 2
    
    for digit in reversed(numero):
        suma += int(digit) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    return dv == dv_calculado


def validate_password_strength(password):
    """
    Validar fortaleza de contraseña.
    
    Args:
        password (str): Contraseña a validar
    
    Returns:
        tuple: (bool, str) - (es_válida, mensaje_error)
    """
    if not password:
        return False, "La contraseña es requerida"
    
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if len(password) > 128:
        return False, "La contraseña no puede exceder 128 caracteres"
    
    # Verificar que contenga al menos una letra y un número
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not has_letter:
        return False, "La contraseña debe contener al menos una letra"
    
    if not has_number:
        return False, "La contraseña debe contener al menos un número"
    
    return True, "Contraseña válida"


# =============================================================================
# FUNCIONES DE SESIÓN
# =============================================================================

def login_user(usuario):
    """
    Iniciar sesión de usuario.
    
    Args:
        usuario (Usuario): Instancia del modelo Usuario
    
    Returns:
        dict: Datos de respuesta con token y información del usuario
    """
    # Actualizar timestamp de último login
    usuario.update_last_login()
    
    # Generar token JWT
    token = generate_auth_token(usuario)
    
    # Guardar información en sesión de Flask
    session['user_id'] = usuario.id_usuario
    session['user_rut'] = usuario.rut_usuario
    session['user_nivel'] = usuario.nivel_usuario
    
    return {
        'message': 'Inicio de sesión exitoso',
        'token': token,
        'user': usuario.to_dict(),
        'expires_in': 3600  # 1 hora
    }


def logout_user():
    """
    Cerrar sesión de usuario.
    
    Returns:
        dict: Mensaje de confirmación
    """
    # Limpiar sesión de Flask
    session.pop('user_id', None)
    session.pop('user_rut', None)
    session.pop('user_nivel', None)
    
    return {'message': 'Sesión cerrada exitosamente'}


def get_current_user_from_session():
    """
    Obtener usuario actual desde la sesión de Flask.
    
    Returns:
        Usuario or None: Instancia del usuario actual o None si no hay sesión
    """
    user_id = session.get('user_id')
    if user_id:
        return Usuario.query.get(user_id)
    return None


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def format_rut(rut):
    """
    Formatear RUT chileno con puntos y guión.
    
    Args:
        rut (str): RUT sin formato
    
    Returns:
        str: RUT formateado (ej: 12.345.678-9)
    """
    if not rut:
        return ""
    
    # Limpiar RUT
    rut = rut.replace('.', '').replace('-', '').upper()
    
    if len(rut) < 8:
        return rut
    
    # Separar número y dígito verificador
    numero = rut[:-1]
    dv = rut[-1]
    
    # Formatear con puntos
    formatted = ""
    for i, digit in enumerate(reversed(numero)):
        if i > 0 and i % 3 == 0:
            formatted = "." + formatted
        formatted = digit + formatted
    
    return f"{formatted}-{dv}"


def clean_rut(rut):
    """
    Limpiar RUT removiendo puntos y guiones.
    
    Args:
        rut (str): RUT con o sin formato
    
    Returns:
        str: RUT limpio
    """
    if not rut:
        return ""
    
    return rut.replace('.', '').replace('-', '').upper()
