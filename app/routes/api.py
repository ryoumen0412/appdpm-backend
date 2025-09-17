"""
API Routes Module

Este módulo contiene todas las rutas de la API REST para el sistema de gestión DPM.
Proporciona endpoints CRUD completos para todas las entidades del sistema, incluyendo
validación de datos, manejo de errores, autenticación y respuestas JSON estandarizadas.

Endpoints implementados:
- /api/auth/login: Autenticación de usuarios
- /api/auth/logout: Cerrar sesión
- /api/auth/register: Registro de nuevos usuarios
- /api/auth/profile: Obtener/actualizar perfil de usuario
- /api/auth/change-password: Cambiar contraseña
- /api/usuarios: CRUD para gestión de usuarios
- /api/personas-a-cargo: CRUD para personas responsables
- /api/personas-mayores: CRUD para usuarios del sistema
- /api/centros-comunitarios: CRUD para centros comunitarios
- /api/actividades: CRUD para actividades
- /api/talleres: CRUD para talleres
- /api/servicios: CRUD para servicios
- /api/trabajadores-apoyo: CRUD para trabajadores de apoyo
- /api/mantenciones: CRUD para mantenciones
- /api/participaciones: Gestión de participaciones (relaciones)
- /api/gestiones: Gestión de asignaciones (relaciones)
- /api/health: Endpoint de verificación de estado

"""

from flask import Blueprint, request, jsonify, session
from app import db
from sqlalchemy import or_
from app.models import (
    Usuario, PersonasACargo, PersonasMayores, CentrosComunitarios, 
    Actividades, Talleres, Servicios, TrabajadoresApoyo, 
    Mantenciones, Participa, Gestiona
)
from app.auth_utils import (
    token_required, admin_required, encargado_required, apoyo_required,
    can_create_users, can_delete_vital_records, can_update_records, can_update_participa_mantenciones,
    validate_rut, validate_password_strength, format_rut, clean_rut,
    login_user, logout_user, get_current_user_from_session
)
from datetime import datetime, date
from sqlalchemy import text, or_

# Crear blueprint para agrupar todas las rutas de la API
api_bp = Blueprint('api', __name__)

# =============================================================================
# RUTAS DE AUTENTICACIÓN
# =============================================================================

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Autenticar usuario en el sistema.
    
    Body (JSON):
        rut_usuario (str): RUT del usuario (requerido)
        password (str): Contraseña del usuario (requerido)
        
    Returns:
        JSON: Token de autenticación y datos del usuario
        
    Raises:
        400: Si faltan datos o credenciales inválidas
        401: Si las credenciales son incorrectas
        403: Si el usuario está inactivo
    """
    data = request.get_json()
    
    if not data or not data.get('rut_usuario') or not data.get('password'):
        return jsonify({'error': 'RUT y contraseña son requeridos'}), 400
    
    # Limpiar y validar RUT
    rut = clean_rut(data['rut_usuario'])
    if not validate_rut(rut):
        return jsonify({'error': 'Formato de RUT inválido'}), 400
    
    # Buscar usuario por RUT
    usuario = Usuario.query.filter_by(rut_usuario=rut).first()
    
    if not usuario:
        return jsonify({'error': 'Credenciales incorrectas'}), 401
    
    # Verificar contraseña
    if not usuario.check_password(data['password']):
        return jsonify({'error': 'Credenciales incorrectas'}), 401
    
    # Iniciar sesión
    response_data = login_user(usuario)
    return jsonify(response_data), 200


@api_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    Cerrar sesión del usuario actual.
    
    Returns:
        JSON: Mensaje de confirmación
    """
    response_data = logout_user()
    return jsonify(response_data), 200


@api_bp.route('/auth/register', methods=['POST'])
@can_create_users  # Solo administradores pueden crear usuarios
def register(current_user):
    """
    Registrar un nuevo usuario en el sistema.
    
    Body (JSON):
        rut_usuario (str): RUT del usuario (requerido)
        user_usuario (str): Nombre de usuario (requerido)
        password (str): Contraseña del usuario (requerido, máximo 50 caracteres)
        nivel_usuario (int): Nivel de acceso (3-admin, 2-encargado, 1-apoyo)
        
    Returns:
        JSON: Datos del usuario creado
        
    Raises:
        400: Si faltan datos o hay errores de validación
        409: Si el usuario ya existe
    """
    data = request.get_json()
    
    # Validar datos requeridos
    required_fields = ['rut_usuario', 'user_usuario', 'password', 'nivel_usuario']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} es requerido'}), 400
    
    # Limpiar y validar RUT
    rut = clean_rut(data['rut_usuario'])
    if not validate_rut(rut):
        return jsonify({'error': 'Formato de RUT inválido'}), 400
    
    # Verificar que no existe usuario con este RUT
    if Usuario.query.filter_by(rut_usuario=rut).first():
        return jsonify({'error': 'Ya existe un usuario con este RUT'}), 409
    
    # Validar contraseña
    is_valid, message = validate_password_strength(data['password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Validar nivel de usuario
    if data['nivel_usuario'] not in [1, 2, 3]:
        return jsonify({'error': 'Nivel de usuario debe ser 1 (apoyo), 2 (encargado) o 3 (admin)'}), 400
    
    try:
        # Crear nuevo usuario
        usuario = Usuario(
            rut_usuario=rut,
            user_usuario=data['user_usuario'],
            nivel_usuario=data['nivel_usuario']
        )
        usuario.set_password(data['password'])
        
        db.session.add(usuario)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'user': usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear usuario'}), 500


@api_bp.route('/auth/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Obtener perfil del usuario actual.
    
    Returns:
        JSON: Datos completos del usuario actual
    """
    return jsonify({
        'user': current_user.to_dict(),
        'permissions': current_user.get_permissions_summary()
    }), 200


@api_bp.route('/auth/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    Actualizar perfil del usuario actual.
    
    Body (JSON):
        user_usuario (str): Nuevo nombre de usuario (opcional)
        
    Returns:
        JSON: Datos actualizados del usuario
    """
    data = request.get_json()
    
    try:
        if 'user_usuario' in data:
            current_user.user_usuario = data['user_usuario']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar perfil'}), 500


@api_bp.route('/auth/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """
    Cambiar contraseña del usuario actual.
    
    Body (JSON):
        current_password (str): Contraseña actual
        new_password (str): Nueva contraseña
        
    Returns:
        JSON: Mensaje de confirmación
    """
    data = request.get_json()
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Contraseña actual y nueva son requeridas'}), 400
    
    # Verificar contraseña actual
    if not current_user.check_password(data['current_password']):
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401
    
    # Validar nueva contraseña
    is_valid, message = validate_password_strength(data['new_password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
    try:
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Contraseña cambiada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al cambiar contraseña'}), 500


# =============================================================================
# RUTAS DE GESTIÓN DE USUARIOS (ADMIN)
# =============================================================================

@api_bp.route('/usuarios', methods=['GET'])
@encargado_required
def get_usuarios(current_user):
    """
    Obtener lista de todos los usuarios (solo encargados y admins).
    
    Query Parameters:
        page (int): Número de página (opcional)
        per_page (int): Usuarios por página (opcional, máximo 100)
        search (str): Buscar por RUT o nombre de usuario (opcional)
        nivel (int): Filtrar por nivel de usuario (opcional)
        
    Returns:
        JSON: Lista paginada de usuarios
    """
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Construir query base
        query = Usuario.query
        
        # Filtro de búsqueda
        search = request.args.get('search')
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                Usuario.rut_usuario.ilike(search_term),
                Usuario.user_usuario.ilike(search_term)
            ))
        
        # Filtro por nivel
        nivel = request.args.get('nivel', type=int)
        if nivel and nivel in [1, 2, 3]:
            query = query.filter_by(nivel_usuario=nivel)
        
        # Ordenar por ID (más recientes primero)
        query = query.order_by(Usuario.id_usuario.desc())
        
        # Paginar resultados
        usuarios = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'usuarios': [usuario.to_dict() for usuario in usuarios.items],
            'pagination': {
                'page': page,
                'pages': usuarios.pages,
                'per_page': per_page,
                'total': usuarios.total,
                'has_next': usuarios.has_next,
                'has_prev': usuarios.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error al obtener usuarios'}), 500


@api_bp.route('/usuarios/<int:user_id>', methods=['GET'])
@encargado_required
def get_usuario(current_user, user_id):
    """
    Obtener usuario específico por ID.
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        JSON: Datos completos del usuario
    """
    usuario = Usuario.query.get_or_404(user_id)
    return jsonify({'user': usuario.to_dict()}), 200


@api_bp.route('/usuarios/<int:user_id>', methods=['PUT'])
@admin_required
def update_usuario(current_user, user_id):
    """
    Actualizar usuario específico (solo administradores).
    
    Args:
        user_id (int): ID del usuario
        
    Body (JSON):
        user_usuario (str): Nuevo nombre de usuario (opcional)
        nivel_usuario (int): Nuevo nivel (opcional)
        
    Returns:
        JSON: Datos actualizados del usuario
    """
    usuario = Usuario.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        if 'user_usuario' in data:
            usuario.user_usuario = data['user_usuario']
        
        if 'nivel_usuario' in data:
            if data['nivel_usuario'] not in [1, 2, 3]:
                return jsonify({'error': 'Nivel de usuario debe ser 1 (apoyo), 2 (encargado) o 3 (admin)'}), 400
            usuario.nivel_usuario = data['nivel_usuario']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario actualizado exitosamente',
            'user': usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar usuario'}), 500


@api_bp.route('/usuarios/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_usuario(current_user, user_id):
    """
    Eliminar usuario específico (solo administradores).
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        JSON: Mensaje de confirmación
    """
    if user_id == current_user.id_usuario:
        return jsonify({'error': 'No puedes eliminar tu propio usuario'}), 400
    
    usuario = Usuario.query.get_or_404(user_id)
    
    try:
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar usuario'}), 500


# =============================================================================
# RUTAS EXISTENTES (PERSONAS A CARGO, ETC.)
# =============================================================================

@api_bp.route('/personas-a-cargo', methods=['GET'])
@apoyo_required  # Todos pueden ver
def get_personas_a_cargo(current_user):
    """
    Obtener todas las personas a cargo del sistema.
    
    Returns:
        JSON: Lista de todas las personas a cargo con sus datos completos
    """
    personas = PersonasACargo.query.all()
    return jsonify([persona.to_dict() for persona in personas])

@api_bp.route('/personas-a-cargo/<string:rut>', methods=['GET'])
@apoyo_required  # Todos pueden ver
def get_persona_a_cargo(current_user, rut):
    """
    Obtener una persona a cargo específica por su RUT.
    
    Args:
        rut (str): RUT de la persona a cargo
        
    Returns:
        JSON: Datos completos de la persona a cargo
        
    Raises:
        404: Si no se encuentra la persona con el RUT especificado
    """
    persona = PersonasACargo.query.get_or_404(rut)
    return jsonify(persona.to_dict())

@api_bp.route('/personas-a-cargo', methods=['POST'])
@admin_required  # Solo admin puede crear registros vitales
def create_persona_a_cargo(current_user):
    """
    Crear una nueva persona a cargo en el sistema.
    
    Body (JSON):
        rut (str): RUT único de la persona (requerido)
        nombre (str): Nombre de la persona (requerido)
        apellido (str): Apellido de la persona (requerido)
        correo_electronico (str): Email de contacto (opcional)
        telefono (str): Número telefónico (opcional)
        fecha_nacimiento (str): Fecha de nacimiento en formato ISO (opcional)
        
    Returns:
        JSON: Datos de la persona creada con código 201
        
    Raises:
        400: Si faltan campos requeridos o hay errores de validación
        500: Si hay errores en la base de datos
    """
    data = request.get_json()
    
    # Validar datos requeridos
    if not data.get('rut') or not data.get('nombre') or not data.get('apellido'):
        return jsonify({'error': 'RUT, nombre y apellido son requeridos'}), 400
    
    try:
        persona = PersonasACargo(
            rut=data['rut'],
            nombre=data['nombre'],
            apellido=data['apellido'],
            correo_electronico=data.get('correo_electronico'),
            telefono=data.get('telefono'),
            fecha_nacimiento=data.get('fecha_nacimiento')
        )
        
        db.session.add(persona)
        db.session.commit()
        
        return jsonify(persona.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear la persona a cargo', 'details': str(e)}), 500

@api_bp.route('/personas-a-cargo/<string:rut>', methods=['PUT'])
@can_update_records  # Encargado+ puede actualizar
def update_persona_a_cargo(current_user, rut):
    """Actualizar una persona a cargo"""
    persona = PersonasACargo.query.get_or_404(rut)
    data = request.get_json()
    
    try:
        if 'nombre' in data:
            persona.nombre = data['nombre']
        if 'apellido' in data:
            persona.apellido = data['apellido']
        if 'correo_electronico' in data:
            persona.correo_electronico = data['correo_electronico']
        if 'telefono' in data:
            persona.telefono = data['telefono']
        if 'fecha_nacimiento' in data:
            persona.fecha_nacimiento = data['fecha_nacimiento']
        
        db.session.commit()
        return jsonify(persona.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar la persona a cargo', 'details': str(e)}), 500

@api_bp.route('/personas-a-cargo/<string:rut>', methods=['DELETE'])
@can_delete_vital_records  # Solo admin puede eliminar registros vitales
def delete_persona_a_cargo(current_user, rut):
    """Eliminar una persona a cargo"""
    persona = PersonasACargo.query.get_or_404(rut)
    
    try:
        db.session.delete(persona)
        db.session.commit()
        return jsonify({'message': 'Persona a cargo eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar la persona a cargo', 'details': str(e)}), 500

@api_bp.route('/personas-mayores', methods=['GET'])
@apoyo_required  # Todos pueden ver
def get_personas_mayores(current_user):
    """
    Obtener personas mayores con paginación y búsqueda
    
    Query Parameters:
        - page (int): Número de página (default: 1)
        - per_page (int): Registros por página (default: 50, max: 100)
        - search (str): Búsqueda por RUT, nombre o apellidos
        - sector (str): Filtro por sector
        - genero (str): Filtro por género
    
    Returns:
        JSON con datos paginados y metadatos
    """
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)  # Máximo 100 por página
        
        # Parámetros de búsqueda y filtros
        search = request.args.get('search', '').strip()
        sector = request.args.get('sector', '').strip()
        genero = request.args.get('genero', '').strip()
        
        # Construir query base
        query = PersonasMayores.query
        
        # Aplicar filtros de búsqueda
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    PersonasMayores.rut.ilike(search_filter),
                    PersonasMayores.nombre.ilike(search_filter),
                    PersonasMayores.apellidos.ilike(search_filter)
                )
            )
        
        # Aplicar filtros específicos
        if sector:
            query = query.filter(PersonasMayores.sector.ilike(f"%{sector}%"))
            
        if genero:
            query = query.filter(PersonasMayores.genero == genero)
        
        # Ordenar por apellidos, nombre
        query = query.order_by(PersonasMayores.apellidos, PersonasMayores.nombre)
        
        # Ejecutar paginación
        personas_paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Preparar respuesta
        response = {
            'data': [persona.to_dict() for persona in personas_paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': personas_paginated.total,
                'pages': personas_paginated.pages,
                'has_prev': personas_paginated.has_prev,
                'has_next': personas_paginated.has_next,
                'prev_num': personas_paginated.prev_num,
                'next_num': personas_paginated.next_num
            },
            'filters': {
                'search': search,
                'sector': sector,
                'genero': genero
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': 'Error al obtener personas mayores', 'details': str(e)}), 500

@api_bp.route('/personas-mayores/<string:rut>', methods=['GET'])
def get_persona_mayor(rut):
    """Obtener una persona mayor por RUT"""
    persona = PersonasMayores.query.get_or_404(rut)
    return jsonify(persona.to_dict())

@api_bp.route('/personas-mayores', methods=['POST'])
def create_persona_mayor():
    """Crear una nueva persona mayor"""
    data = request.get_json()
    
    if not data.get('rut') or not data.get('nombre') or not data.get('apellidos'):
        return jsonify({'error': 'RUT, nombre y apellidos son requeridos'}), 400
    
    try:
        persona = PersonasMayores(
            rut=data['rut'],
            nombre=data['nombre'],
            apellidos=data['apellidos'],
            genero=data.get('genero'),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            direccion=data.get('direccion'),
            sector=data.get('sector'),
            telefono=data.get('telefono'),
            email=data.get('email'),
            cedula_discapacidad=data.get('cedula_discapacidad', False)
        )
        
        db.session.add(persona)
        db.session.commit()
        
        return jsonify(persona.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear la persona mayor', 'details': str(e)}), 500

@api_bp.route('/personas-mayores/<string:rut>', methods=['PUT'])
def update_persona_mayor(rut):
    """Actualizar una persona mayor"""
    persona = PersonasMayores.query.get_or_404(rut)
    data = request.get_json()
    
    try:
        if 'nombre' in data:
            persona.nombre = data['nombre']
        if 'apellidos' in data:
            persona.apellidos = data['apellidos']
        if 'genero' in data:
            persona.genero = data['genero']
        if 'fecha_nacimiento' in data:
            persona.fecha_nacimiento = data['fecha_nacimiento']
        if 'direccion' in data:
            persona.direccion = data['direccion']
        if 'sector' in data:
            persona.sector = data['sector']
        if 'telefono' in data:
            persona.telefono = data['telefono']
        if 'email' in data:
            persona.email = data['email']
        if 'cedula_discapacidad' in data:
            persona.cedula_discapacidad = data['cedula_discapacidad']
        
        db.session.commit()
        return jsonify(persona.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar la persona mayor', 'details': str(e)}), 500

@api_bp.route('/personas-mayores/<string:rut>', methods=['DELETE'])
def delete_persona_mayor(rut):
    """Eliminar una persona mayor"""
    persona = PersonasMayores.query.get_or_404(rut)
    
    try:
        db.session.delete(persona)
        db.session.commit()
        return jsonify({'message': 'Persona mayor eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar la persona mayor', 'details': str(e)}), 500

@api_bp.route('/centros-comunitarios', methods=['GET'])
def get_centros_comunitarios():
    """Obtener todos los centros comunitarios"""
    centros = CentrosComunitarios.query.all()
    return jsonify([centro.to_dict() for centro in centros])

@api_bp.route('/centros-comunitarios/<int:centro_id>', methods=['GET'])
def get_centro_comunitario(centro_id):
    """Obtener un centro comunitario por ID"""
    centro = CentrosComunitarios.query.get_or_404(centro_id)
    return jsonify(centro.to_dict())

@api_bp.route('/centros-comunitarios', methods=['POST'])
def create_centro_comunitario():
    """Crear un nuevo centro comunitario"""
    data = request.get_json()
    
    if not data.get('nombre'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    try:
        centro = CentrosComunitarios(
            nombre=data['nombre'],
            direccion=data.get('direccion'),
            sector=data.get('sector')
        )
        
        db.session.add(centro)
        db.session.commit()
        
        return jsonify(centro.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear el centro comunitario', 'details': str(e)}), 500

@api_bp.route('/centros-comunitarios/<int:centro_id>', methods=['PUT'])
def update_centro_comunitario(centro_id):
    """Actualizar un centro comunitario"""
    centro = CentrosComunitarios.query.get_or_404(centro_id)
    data = request.get_json()
    
    try:
        if 'nombre' in data:
            centro.nombre = data['nombre']
        if 'direccion' in data:
            centro.direccion = data['direccion']
        if 'sector' in data:
            centro.sector = data['sector']
        
        db.session.commit()
        return jsonify(centro.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar el centro comunitario', 'details': str(e)}), 500

@api_bp.route('/centros-comunitarios/<int:centro_id>', methods=['DELETE'])
def delete_centro_comunitario(centro_id):
    """Eliminar un centro comunitario"""
    centro = CentrosComunitarios.query.get_or_404(centro_id)
    
    try:
        db.session.delete(centro)
        db.session.commit()
        return jsonify({'message': 'Centro comunitario eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar el centro comunitario', 'details': str(e)}), 500

@api_bp.route('/actividades', methods=['GET'])
def get_actividades():
    """Obtener todas las actividades"""
    actividades = Actividades.query.all()
    return jsonify([actividad.to_dict() for actividad in actividades])

@api_bp.route('/actividades/<int:actividad_id>', methods=['GET'])
def get_actividad(actividad_id):
    """Obtener una actividad por ID"""
    actividad = Actividades.query.get_or_404(actividad_id)
    return jsonify(actividad.to_dict())

@api_bp.route('/actividades', methods=['POST'])
def create_actividad():
    """Crear una nueva actividad"""
    data = request.get_json()
    
    if not data.get('nombre') or not data.get('fecha_inicio'):
        return jsonify({'error': 'El nombre y fecha de inicio son requeridos'}), 400
    
    try:
        actividad = Actividades(
            nombre=data['nombre'],
            fecha_inicio=data['fecha_inicio'],
            fecha_termino=data.get('fecha_termino'),
            persona_a_cargo=data.get('persona_a_cargo'),
            observaciones=data.get('observaciones')
        )
        
        db.session.add(actividad)
        db.session.commit()
        
        return jsonify(actividad.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear la actividad', 'details': str(e)}), 500

@api_bp.route('/actividades/<int:actividad_id>', methods=['PUT'])
@can_update_records  # Encargado+ puede actualizar
def update_actividad(current_user, actividad_id):
    """Actualizar una actividad"""
    actividad = Actividades.query.get_or_404(actividad_id)
    data = request.get_json()
    
    try:
        if 'nombre' in data:
            actividad.nombre = data['nombre']
        if 'fecha_inicio' in data:
            actividad.fecha_inicio = data['fecha_inicio']
        if 'fecha_termino' in data:
            actividad.fecha_termino = data['fecha_termino']
        if 'persona_a_cargo' in data:
            actividad.persona_a_cargo = data['persona_a_cargo']
        if 'observaciones' in data:
            actividad.observaciones = data['observaciones']
        
        db.session.commit()
        return jsonify(actividad.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar la actividad', 'details': str(e)}), 500

@api_bp.route('/actividades/<int:actividad_id>', methods=['DELETE'])
@can_delete_vital_records  # Solo admin puede eliminar registros vitales
def delete_actividad(current_user, actividad_id):
    """Eliminar una actividad"""
    actividad = Actividades.query.get_or_404(actividad_id)
    
    try:
        db.session.delete(actividad)
        db.session.commit()
        return jsonify({'message': 'Actividad eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar la actividad', 'details': str(e)}), 500

@api_bp.route('/talleres', methods=['GET'])
@apoyo_required  # Todos pueden ver
def get_talleres(current_user):
    """Obtener todos los talleres"""
    talleres = Talleres.query.all()
    return jsonify([taller.to_dict() for taller in talleres])

@api_bp.route('/talleres/<int:taller_id>', methods=['GET'])
@apoyo_required  # Todos pueden ver
def get_taller(current_user, taller_id):
    """Obtener un taller por ID"""
    taller = Talleres.query.get_or_404(taller_id)
    return jsonify(taller.to_dict())

@api_bp.route('/talleres', methods=['POST'])
def create_taller():
    """Crear un nuevo taller"""
    data = request.get_json()
    
    if not data.get('nombre') or not data.get('fecha_inicio'):
        return jsonify({'error': 'El nombre y fecha de inicio son requeridos'}), 400
    
    try:
        taller = Talleres(
            nombre=data['nombre'],
            fecha_inicio=data['fecha_inicio'],
            fecha_termino=data.get('fecha_termino'),
            persona_a_cargo=data.get('persona_a_cargo'),
            observaciones=data.get('observaciones')
        )
        
        db.session.add(taller)
        db.session.commit()
        
        return jsonify(taller.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear el taller', 'details': str(e)}), 500

@api_bp.route('/talleres/<int:taller_id>', methods=['PUT'])
def update_taller(taller_id):
    """Actualizar un taller"""
    taller = Talleres.query.get_or_404(taller_id)
    data = request.get_json()
    
    try:
        if 'nombre' in data:
            taller.nombre = data['nombre']
        if 'fecha_inicio' in data:
            taller.fecha_inicio = data['fecha_inicio']
        if 'fecha_termino' in data:
            taller.fecha_termino = data['fecha_termino']
        if 'persona_a_cargo' in data:
            taller.persona_a_cargo = data['persona_a_cargo']
        if 'observaciones' in data:
            taller.observaciones = data['observaciones']
        
        db.session.commit()
        return jsonify(taller.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar el taller', 'details': str(e)}), 500

@api_bp.route('/talleres/<int:taller_id>', methods=['DELETE'])
def delete_taller(taller_id):
    """Eliminar un taller"""
    taller = Talleres.query.get_or_404(taller_id)
    
    try:
        db.session.delete(taller)
        db.session.commit()
        return jsonify({'message': 'Taller eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar el taller', 'details': str(e)}), 500

@api_bp.route('/servicios', methods=['GET'])
def get_servicios():
    """Obtener todos los servicios"""
    servicios = Servicios.query.all()
    return jsonify([servicio.to_dict() for servicio in servicios])

@api_bp.route('/servicios/<int:servicio_id>', methods=['GET'])
def get_servicio(servicio_id):
    """Obtener un servicio por ID"""
    servicio = Servicios.query.get_or_404(servicio_id)
    return jsonify(servicio.to_dict())

@api_bp.route('/servicios', methods=['POST'])
def create_servicio():
    """Crear un nuevo servicio"""
    data = request.get_json()
    
    if not data.get('nombre'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    try:
        servicio = Servicios(
            nombre=data['nombre'],
            lugar=data.get('lugar'),
            direccion_servicio=data.get('direccion_servicio'),
            persona_a_cargo=data.get('persona_a_cargo'),
            fecha=data.get('fecha'),
            estado=data.get('estado'),
            observaciones=data.get('observaciones')
        )
        
        db.session.add(servicio)
        db.session.commit()
        
        return jsonify(servicio.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear el servicio', 'details': str(e)}), 500

@api_bp.route('/servicios/<int:servicio_id>', methods=['PUT'])
def update_servicio(servicio_id):
    """Actualizar un servicio"""
    servicio = Servicios.query.get_or_404(servicio_id)
    data = request.get_json()
    
    try:
        if 'nombre' in data:
            servicio.nombre = data['nombre']
        if 'lugar' in data:
            servicio.lugar = data['lugar']
        if 'direccion_servicio' in data:
            servicio.direccion_servicio = data['direccion_servicio']
        if 'persona_a_cargo' in data:
            servicio.persona_a_cargo = data['persona_a_cargo']
        if 'fecha' in data:
            servicio.fecha = data['fecha']
        if 'estado' in data:
            servicio.estado = data['estado']
        if 'observaciones' in data:
            servicio.observaciones = data['observaciones']
        
        db.session.commit()
        return jsonify(servicio.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar el servicio', 'details': str(e)}), 500

@api_bp.route('/servicios/<int:servicio_id>', methods=['DELETE'])
def delete_servicio(servicio_id):
    """Eliminar un servicio"""
    servicio = Servicios.query.get_or_404(servicio_id)
    
    try:
        db.session.delete(servicio)
        db.session.commit()
        return jsonify({'message': 'Servicio eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar el servicio', 'details': str(e)}), 500

@api_bp.route('/trabajadores-apoyo', methods=['GET'])
def get_trabajadores_apoyo():
    """Obtener todos los trabajadores de apoyo"""
    trabajadores = TrabajadoresApoyo.query.all()
    return jsonify([trabajador.to_dict() for trabajador in trabajadores])

@api_bp.route('/trabajadores-apoyo/<string:rut>', methods=['GET'])
def get_trabajador_apoyo(rut):
    """Obtener un trabajador de apoyo por RUT"""
    trabajador = TrabajadoresApoyo.query.get_or_404(rut)
    return jsonify(trabajador.to_dict())

@api_bp.route('/trabajadores-apoyo', methods=['POST'])
def create_trabajador_apoyo():
    """Crear un nuevo trabajador de apoyo"""
    data = request.get_json()
    
    if not data.get('rut') or not data.get('nombre'):
        return jsonify({'error': 'RUT y nombre son requeridos'}), 400
    
    try:
        trabajador = TrabajadoresApoyo(
            rut=data['rut'],
            nombre=data['nombre'],
            apellidos=data.get('apellidos'),
            cargo=data.get('cargo'),
            id_centro=data.get('id_centro')
        )
        
        db.session.add(trabajador)
        db.session.commit()
        
        return jsonify(trabajador.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear el trabajador de apoyo', 'details': str(e)}), 500

@api_bp.route('/trabajadores-apoyo/<string:rut>', methods=['PUT'])
def update_trabajador_apoyo(rut):
    """Actualizar un trabajador de apoyo"""
    trabajador = TrabajadoresApoyo.query.get_or_404(rut)
    data = request.get_json()
    
    try:
        if 'nombre' in data:
            trabajador.nombre = data['nombre']
        if 'apellidos' in data:
            trabajador.apellidos = data['apellidos']
        if 'cargo' in data:
            trabajador.cargo = data['cargo']
        if 'id_centro' in data:
            trabajador.id_centro = data['id_centro']
        
        db.session.commit()
        return jsonify(trabajador.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar el trabajador de apoyo', 'details': str(e)}), 500

@api_bp.route('/trabajadores-apoyo/<string:rut>', methods=['DELETE'])
def delete_trabajador_apoyo(rut):
    """Eliminar un trabajador de apoyo"""
    trabajador = TrabajadoresApoyo.query.get_or_404(rut)
    
    try:
        db.session.delete(trabajador)
        db.session.commit()
        return jsonify({'message': 'Trabajador de apoyo eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar el trabajador de apoyo', 'details': str(e)}), 500

@api_bp.route('/mantenciones', methods=['GET'])
def get_mantenciones():
    """Obtener todas las mantenciones"""
    mantenciones = Mantenciones.query.all()
    return jsonify([mantencion.to_dict() for mantencion in mantenciones])

@api_bp.route('/mantenciones/<int:mantencion_id>', methods=['GET'])
def get_mantencion(mantencion_id):
    """Obtener una mantención por ID"""
    mantencion = Mantenciones.query.get_or_404(mantencion_id)
    return jsonify(mantencion.to_dict())

@api_bp.route('/mantenciones', methods=['POST'])
def create_mantencion():
    """Crear una nueva mantención"""
    data = request.get_json()
    
    if not data.get('fecha') or not data.get('id_centro'):
        return jsonify({'error': 'La fecha y el ID del centro son requeridos'}), 400
    
    try:
        mantencion = Mantenciones(
            fecha=data['fecha'],
            id_centro=data['id_centro'],
            detalle=data.get('detalle'),
            observaciones=data.get('observaciones'),
            adjuntos=data.get('adjuntos'),
            quienes_realizaron=data.get('quienes_realizaron')
        )
        
        db.session.add(mantencion)
        db.session.commit()
        
        return jsonify(mantencion.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear la mantención', 'details': str(e)}), 500

@api_bp.route('/mantenciones/<int:mantencion_id>', methods=['PUT'])
def update_mantencion(mantencion_id):
    """Actualizar una mantención"""
    mantencion = Mantenciones.query.get_or_404(mantencion_id)
    data = request.get_json()
    
    try:
        if 'fecha' in data:
            mantencion.fecha = data['fecha']
        if 'id_centro' in data:
            mantencion.id_centro = data['id_centro']
        if 'detalle' in data:
            mantencion.detalle = data['detalle']
        if 'observaciones' in data:
            mantencion.observaciones = data['observaciones']
        if 'adjuntos' in data:
            mantencion.adjuntos = data['adjuntos']
        if 'quienes_realizaron' in data:
            mantencion.quienes_realizaron = data['quienes_realizaron']
        
        db.session.commit()
        return jsonify(mantencion.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar la mantención', 'details': str(e)}), 500

@api_bp.route('/mantenciones/<int:mantencion_id>', methods=['DELETE'])
def delete_mantencion(mantencion_id):
    """Eliminar una mantención"""
    mantencion = Mantenciones.query.get_or_404(mantencion_id)
    
    try:
        db.session.delete(mantencion)
        db.session.commit()
        return jsonify({'message': 'Mantención eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar la mantención', 'details': str(e)}), 500

@api_bp.route('/participaciones', methods=['GET'])
def get_participaciones():
    """Obtener todas las participaciones"""
    participaciones = Participa.query.all()
    return jsonify([participacion.to_dict() for participacion in participaciones])

@api_bp.route('/participaciones/<string:rut_persona>', methods=['GET'])
def get_participaciones_persona(rut_persona):
    """Obtener todas las participaciones de una persona mayor"""
    participaciones = Participa.query.filter_by(rut_persona=rut_persona).all()
    return jsonify([participacion.to_dict() for participacion in participaciones])

@api_bp.route('/participaciones', methods=['POST'])
def create_participacion():
    """Crear una nueva participación"""
    data = request.get_json()
    
    required_fields = ['rut_persona', 'tipo', 'id_actividad_taller_servicio']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'RUT persona, tipo e ID son requeridos'}), 400
    
    if data['tipo'] not in ['actividad', 'taller', 'servicio']:
        return jsonify({'error': 'Tipo debe ser: actividad, taller o servicio'}), 400
    
    try:
        participacion = Participa(
            rut_persona=data['rut_persona'],
            tipo=data['tipo'],
            id_actividad_taller_servicio=data['id_actividad_taller_servicio'],
            fecha_participacion=data.get('fecha_participacion')
        )
        
        db.session.add(participacion)
        db.session.commit()
        
        return jsonify(participacion.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear la participación', 'details': str(e)}), 500

@api_bp.route('/participaciones/<string:rut_persona>/<string:tipo>/<int:id_actividad>', methods=['DELETE'])
def delete_participacion(rut_persona, tipo, id_actividad):
    """Eliminar una participación específica"""
    participacion = Participa.query.filter_by(
        rut_persona=rut_persona,
        tipo=tipo,
        id_actividad_taller_servicio=id_actividad
    ).first_or_404()
    
    try:
        db.session.delete(participacion)
        db.session.commit()
        return jsonify({'message': 'Participación eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar la participación', 'details': str(e)}), 500

@api_bp.route('/gestiones', methods=['GET'])
def get_gestiones():
    """Obtener todas las gestiones"""
    gestiones = Gestiona.query.all()
    return jsonify([gestion.to_dict() for gestion in gestiones])

@api_bp.route('/gestiones/<string:rut_persona_a_cargo>', methods=['GET'])
def get_gestiones_persona(rut_persona_a_cargo):
    """Obtener todas las gestiones de una persona a cargo"""
    gestiones = Gestiona.query.filter_by(rut_persona_a_cargo=rut_persona_a_cargo).all()
    return jsonify([gestion.to_dict() for gestion in gestiones])

@api_bp.route('/gestiones', methods=['POST'])
def create_gestion():
    """Crear una nueva gestión"""
    data = request.get_json()
    
    required_fields = ['rut_persona_a_cargo', 'tipo', 'id_actividad_taller_servicio']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'RUT persona a cargo, tipo e ID son requeridos'}), 400
    
    if data['tipo'] not in ['actividad', 'taller', 'servicio']:
        return jsonify({'error': 'Tipo debe ser: actividad, taller o servicio'}), 400
    
    try:
        gestion = Gestiona(
            rut_persona_a_cargo=data['rut_persona_a_cargo'],
            tipo=data['tipo'],
            id_actividad_taller_servicio=data['id_actividad_taller_servicio'],
            fecha_asignacion=data.get('fecha_asignacion')
        )
        
        db.session.add(gestion)
        db.session.commit()
        
        return jsonify(gestion.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear la gestión', 'details': str(e)}), 500

@api_bp.route('/gestiones/<string:rut_persona_a_cargo>/<string:tipo>/<int:id_actividad>', methods=['DELETE'])
def delete_gestion(rut_persona_a_cargo, tipo, id_actividad):
    """Eliminar una gestión específica"""
    gestion = Gestiona.query.filter_by(
        rut_persona_a_cargo=rut_persona_a_cargo,
        tipo=tipo,
        id_actividad_taller_servicio=id_actividad
    ).first_or_404()
    
    try:
        db.session.delete(gestion)
        db.session.commit()
        return jsonify({'message': 'Gestión eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar la gestión', 'details': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de verificación de estado de la API.
    
    Verifica que la API esté funcionando correctamente y que la conexión
    a la base de datos esté disponible.
    
    Returns:
        JSON: Estado de la API y información del sistema
        
    Responses:
        200: API funcionando correctamente
        503: Error en la base de datos o servicio no disponible
    """
    try:
        # Verificar conexión a la base de datos
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'message': 'API funcionando correctamente',
            'database': 'connected',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': 'Error en el servicio',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503