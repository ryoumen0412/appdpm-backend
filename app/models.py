"""
Database Models Module

Este módulo contiene todas las definiciones de modelos de datos para el sistema
de gestión DPM (Dirección de Personas Mayores). Los modelos están construidos
usando SQLAlchemy ORM y representan las entidades principales del sistema.

Modelos incluidos:
- PersonasACargo: Personal responsable de actividades y servicios
- PersonasMayores: Usuarios principales del sistema (adultos mayores)
- CentrosComunitarios: Centros donde se realizan las actividades
- Actividades: Actividades organizadas para personas mayores
- Talleres: Talleres educativos y recreativos
- Servicios: Servicios prestados a la comunidad
- TrabajadoresApoyo: Personal de apoyo en los centros
- Mantenciones: Registros de mantenimiento de infraestructura
- Participa: Relación many-to-many para participación en actividades
- Gestiona: Relación many-to-many para gestión de actividades

"""

from app.extensions import db
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

# =============================================================================
# MODELO: USUARIOS (AUTENTICACIÓN)
# =============================================================================

class Usuario(db.Model):
    """
    Modelo para representar usuarios del sistema con autenticación.
    
    Este modelo gestiona la autenticación y autorización de usuarios que
    pueden acceder al sistema.
    
    Attributes:
        id_usuario (int): ID único del usuario (clave primaria, SERIAL)
        rut_usuario (str): RUT del usuario (VARCHAR(12), UNIQUE)
        user_usuario (str): Nombre de usuario (VARCHAR(150))
        passwd_usuario (str): Hash de la contraseña del usuario (VARCHAR(255))
        nivel_usuario (int): Nivel de acceso del usuario (3-admin, 2-encargado, 1-apoyo)
    
    """
    
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rut_usuario = db.Column(db.String(12), unique=True, nullable=False)
    user_usuario = db.Column(db.String(150), nullable=False)
    passwd_usuario = db.Column(db.String(255), nullable=False)
    nivel_usuario = db.Column(db.Integer, nullable=False)
    
    # Constraint para validar niveles de usuario
    __table_args__ = (
        db.CheckConstraint("nivel_usuario IN (1, 2, 3)", name='check_nivel_usuario'),
    )
    
    def __repr__(self):
        return f'<Usuario {self.rut_usuario}: {self.user_usuario}>'
    
    def set_password(self, password):
        """
        Generar hash seguro de la contraseña usando Werkzeug.
        
        Args:
            password (str): Contraseña en texto plano
            
        Raises:
            ValueError: Si la contraseña excede los límites permitidos
        """
        if len(password) > 128:  # Límite razonable para contraseña original
            raise ValueError("La contraseña no puede exceder 128 caracteres")
        self.passwd_usuario = generate_password_hash(password, method='scrypt')
    
    def check_password(self, password):
        """
        Verificar contraseña contra el hash almacenado.
        
        Args:
            password (str): Contraseña en texto plano a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        return check_password_hash(self.passwd_usuario, password)
    
    def update_last_login(self):
        """
        Actualizar timestamp del último login.
        
        NOTA: Este método no hace nada ya que last_login no existe en el modelo actual.
        """
        pass
    
    def is_admin(self):
        """Verificar si el usuario es administrador."""
        return self.nivel_usuario == 3
    
    def is_encargado(self):
        """Verificar si el usuario es encargado o administrador."""
        return self.nivel_usuario >= 2
    
    def is_apoyo(self):
        """Verificar si el usuario tiene al menos nivel de apoyo."""
        return self.nivel_usuario >= 1
    
    def get_nivel_nombre(self):
        """Obtener nombre del nivel de usuario."""
        niveles = {3: 'Admin', 2: 'Encargado', 1: 'Apoyo'}
        return niveles.get(self.nivel_usuario, 'Desconocido')
    
    def can_create_users(self):
        """Verificar si puede crear usuarios (solo admin)."""
        return self.is_admin()
    
    def can_delete_vital_records(self):
        """Verificar si puede eliminar registros vitales (solo admin)."""
        return self.is_admin()
    
    def can_update_all_records(self):
        """Verificar si puede actualizar todos los registros (encargado+)."""
        return self.is_encargado()
    
    def can_update_participa_mantenciones(self):
        """Verificar si puede actualizar participa y mantenciones (apoyo+)."""
        return self.is_apoyo()
    
    def can_view_all_data(self):
        """Verificar si puede ver toda la data (todos los niveles pueden)."""
        return self.is_apoyo()  # Todos los usuarios autenticados pueden ver
    
    def get_permissions_summary(self):
        """Obtener resumen de permisos del usuario."""
        return {
            'can_view_data': self.can_view_all_data(),
            'can_create_users': self.can_create_users(),
            'can_delete_vital_records': self.can_delete_vital_records(),
            'can_update_all_records': self.can_update_all_records(),
            'can_update_participa_mantenciones': self.can_update_participa_mantenciones(),
            'nivel_nombre': self.get_nivel_nombre(),
            'nivel_numero': self.nivel_usuario
        }
    
    def to_dict(self, include_sensitive=False):
        """Convertir modelo a diccionario."""
        data = {
            'id_usuario': self.id_usuario,
            'rut_usuario': self.rut_usuario,
            'user_usuario': self.user_usuario,
            'nivel_usuario': self.nivel_usuario,
            'nivel_nombre': self.get_nivel_nombre()
        }
        
        # Solo incluir información sensible si se solicita explícitamente
        if include_sensitive:
            data['passwd_usuario'] = self.passwd_usuario
            
        return data

# =============================================================================
# MODELO: PERSONAS A CARGO
# =============================================================================

class PersonasACargo(db.Model):
    """
    Modelo para representar a las personas responsables de coordinar
    actividades, talleres y servicios dentro del sistema DPM.
    
    Estas personas son los coordinadores y responsables que gestionan
    las diferentes actividades ofrecidas a la comunidad de personas mayores.
    
    Attributes:
        rut (str): RUT único de la persona (clave primaria)
        nombre (str): Nombre de la persona
        apellido (str): Apellido de la persona
        correo_electronico (str): Email de contacto (opcional)
        telefono (str): Número telefónico (opcional)
        fecha_nacimiento (date): Fecha de nacimiento (opcional)
        created_at (datetime): Fecha y hora de creación del registro
        updated_at (datetime): Fecha y hora de última actualización
    
    Relationships:
        actividades: Lista de actividades que gestiona esta persona
        talleres: Lista de talleres que gestiona esta persona
        servicios: Lista de servicios que gestiona esta persona
    """
    __tablename__ = 'personas_a_cargo'
    
    # Campos principales
    rut = db.Column(db.String(12), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(150), nullable=False)
    correo_electronico = db.Column(db.String(150))
    telefono = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.Date)
    
    # Campos de auditoría
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow) 
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones con otras entidades
    actividades = db.relationship('Actividades', backref='persona_responsable', lazy=True)
    talleres = db.relationship('Talleres', backref='persona_responsable', lazy=True)
    servicios = db.relationship('Servicios', backref='persona_responsable', lazy=True)
    
    def __repr__(self):
        """Representación string del objeto para debugging"""
        return f'<PersonasACargo {self.rut}: {self.nombre} {self.apellido}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización JSON.
        
        Returns:
            dict: Diccionario con todos los campos del modelo
        """
        return {
            'rut': self.rut,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'correo_electronico': self.correo_electronico,
            'telefono': self.telefono,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# =============================================================================
# MODELO: CENTROS COMUNITARIOS
# =============================================================================

class CentrosComunitarios(db.Model):
    """
    Modelo para representar los centros comunitarios donde se realizan
    las actividades, talleres y servicios del sistema DPM.
    
    Los centros comunitarios son las ubicaciones físicas donde se
    desarrollan las actividades para personas mayores y donde trabajan
    los equipos de apoyo.
    
    Attributes:
        id (int): Identificador único del centro (clave primaria)
        nombre (str): Nombre del centro comunitario
        direccion (str): Dirección física del centro (opcional)
        sector (str): Sector o zona geográfica donde se ubica (opcional)
        created_at (datetime): Fecha y hora de creación del registro
        updated_at (datetime): Fecha y hora de última actualización
    
    Relationships:
        trabajadores: Lista de trabajadores de apoyo asignados al centro
        mantenciones: Lista de mantenciones realizadas en el centro
    """
    __tablename__ = 'centros_comunitarios'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    direccion = db.Column(db.String(200))
    sector = db.Column(db.String(100))
    
    # Campos de auditoría
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones con otras entidades
    trabajadores = db.relationship('TrabajadoresApoyo', backref='centro', lazy=True)
    mantenciones = db.relationship('Mantenciones', backref='centro', lazy=True)
    
    def __repr__(self):
        """Representación string del objeto para debugging"""
        return f'<CentroComunitario {self.id}: {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'direccion': self.direccion,
            'sector': self.sector,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PersonasMayores(db.Model):
    __tablename__ = 'personas_mayores'
    
    rut = db.Column(db.String(12), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150), nullable=False)
    genero = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.Date)
    direccion = db.Column(db.String(200))
    sector = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(150))
    cedula_discapacidad = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participaciones = db.relationship('Participa', backref='persona', lazy=True)
    
    def __repr__(self):
        return f'<PersonaMayor {self.rut}: {self.nombre} {self.apellidos}>'
    
    def to_dict(self):
        return {
            'rut': self.rut,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'genero': self.genero,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'direccion': self.direccion,
            'sector': self.sector,
            'telefono': self.telefono,
            'email': self.email,
            'cedula_discapacidad': self.cedula_discapacidad,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Actividades(db.Model):
    __tablename__ = 'actividades'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_termino = db.Column(db.Date)
    persona_a_cargo = db.Column(db.String(12), db.ForeignKey('personas_a_cargo.rut', ondelete='SET NULL', onupdate='CASCADE'))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Actividad {self.id}: {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_termino': self.fecha_termino.isoformat() if self.fecha_termino else None,
            'persona_a_cargo': self.persona_a_cargo,
            'observaciones': self.observaciones,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Talleres(db.Model):
    __tablename__ = 'talleres'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_termino = db.Column(db.Date)
    persona_a_cargo = db.Column(db.String(12), db.ForeignKey('personas_a_cargo.rut', ondelete='SET NULL', onupdate='CASCADE'))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Taller {self.id}: {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_termino': self.fecha_termino.isoformat() if self.fecha_termino else None,
            'persona_a_cargo': self.persona_a_cargo,
            'observaciones': self.observaciones,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Servicios(db.Model):
    __tablename__ = 'servicios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    lugar = db.Column(db.String(200))
    direccion_servicio = db.Column(db.String(200))
    persona_a_cargo = db.Column(db.String(12), db.ForeignKey('personas_a_cargo.rut', ondelete='SET NULL', onupdate='CASCADE'))
    fecha = db.Column(db.Date)
    estado = db.Column(db.String(50))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Servicio {self.id}: {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'lugar': self.lugar,
            'direccion_servicio': self.direccion_servicio,
            'persona_a_cargo': self.persona_a_cargo,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'estado': self.estado,
            'observaciones': self.observaciones,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TrabajadoresApoyo(db.Model):
    __tablename__ = 'trabajadores_apoyo'
    
    rut = db.Column(db.String(12), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150))
    cargo = db.Column(db.String(100))
    id_centro = db.Column(db.Integer, db.ForeignKey('centros_comunitarios.id', ondelete='SET NULL', onupdate='CASCADE'))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TrabajadorApoyo {self.rut}: {self.nombre} {self.apellidos}>'
    
    def to_dict(self):
        return {
            'rut': self.rut,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'cargo': self.cargo,
            'id_centro': self.id_centro,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Mantenciones(db.Model):
    __tablename__ = 'mantenciones'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    id_centro = db.Column(db.Integer, db.ForeignKey('centros_comunitarios.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    detalle = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    adjuntos = db.Column(db.Text)
    quienes_realizaron = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Mantencion {self.id}: {self.fecha}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'id_centro': self.id_centro,
            'detalle': self.detalle,
            'observaciones': self.observaciones,
            'adjuntos': self.adjuntos,
            'quienes_realizaron': self.quienes_realizaron,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Tabla de relaciones: Participa (Personas Mayores -> Actividades/Talleres/Servicios)
class Participa(db.Model):
    __tablename__ = 'participa'
    
    rut_persona = db.Column(db.String(12), db.ForeignKey('personas_mayores.rut', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    tipo = db.Column(db.String(20), nullable=False, primary_key=True)  # 'actividad', 'taller', 'servicio'
    id_actividad_taller_servicio = db.Column(db.Integer, nullable=False, primary_key=True)
    fecha_participacion = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        db.CheckConstraint("tipo IN ('actividad', 'taller', 'servicio')", name='check_tipo_participa'),
    )
    
    def __repr__(self):
        return f'<Participa {self.rut_persona}: {self.tipo} {self.id_actividad_taller_servicio}>'
    
    def to_dict(self):
        return {
            'rut_persona': self.rut_persona,
            'tipo': self.tipo,
            'id_actividad_taller_servicio': self.id_actividad_taller_servicio,
            'fecha_participacion': self.fecha_participacion.isoformat() if self.fecha_participacion else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Tabla de relaciones: Gestiona (Personas a Cargo -> Actividades/Talleres/Servicios)
class Gestiona(db.Model):
    __tablename__ = 'gestiona'
    
    rut_persona_a_cargo = db.Column(db.String(12), db.ForeignKey('personas_a_cargo.rut', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    tipo = db.Column(db.String(20), nullable=False, primary_key=True)  # 'actividad', 'taller', 'servicio'
    id_actividad_taller_servicio = db.Column(db.Integer, nullable=False, primary_key=True)
    fecha_asignacion = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        db.CheckConstraint("tipo IN ('actividad', 'taller', 'servicio')", name='check_tipo_gestiona'),
    )
    
    def __repr__(self):
        return f'<Gestiona {self.rut_persona_a_cargo}: {self.tipo} {self.id_actividad_taller_servicio}>'
    
    def to_dict(self):
        return {
            'rut_persona_a_cargo': self.rut_persona_a_cargo,
            'tipo': self.tipo,
            'id_actividad_taller_servicio': self.id_actividad_taller_servicio,
            'fecha_asignacion': self.fecha_asignacion.isoformat() if self.fecha_asignacion else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    