"""
Services Management Services

Bus        if 'nombre' in data and data['nombre']:
            if len(data['nombre']) > 150:
                raise ValidationError('Nombre de servicio no puede exceder 150 caracteres')ss logic layer for services, maintenance, and relationship management operations.
"""

from datetime import datetime
from app import db
from app.models import (
    Servicios, Mantenciones, TrabajadoresApoyo, Participa, Gestiona,
    PersonasMayores, PersonasACargo, CentrosComunitarios
)
from app.api.utils import paginate_query
from app.api.utils.errors import ValidationError, BusinessLogicError


class ServicioService:
    """
    Service class for service management operations.
    """
    
    @staticmethod
    def validate_servicio_data(data, is_update=False):
        """
        Validate service data.
        
        Args:
            data: Service data to validate
            is_update: Whether this is an update operation
            
        Raises:
            ValidationError: If validation fails
        """
        if not is_update:
            required_fields = ['nombre']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field.replace("_", " ").title()} es requerido')
        
        # Validate name length
        if 'nombre_servicio' in data and data['nombre_servicio']:
            if len(data['nombre_servicio']) > 100:
                raise ValidationError('Nombre del servicio no puede exceder 100 caracteres')
        
        # Validate description length
        if 'descripcion_servicio' in data and data['descripcion_servicio']:
            if len(data['descripcion_servicio']) > 500:
                raise ValidationError('Descripción no puede exceder 500 caracteres')
    
    @staticmethod
    def get_servicios(page, per_page, nombre_filter=None):
        """
        Get paginated list of services with optional filters.
        
        Args:
            page: Page number
            per_page: Items per page
            nombre_filter: Filter by service name
            
        Returns:
            dict: Paginated service data
        """
        query = Servicios.query
        
        # Apply filters
        if nombre_filter:
            query = query.filter(Servicios.nombre.ilike(f'%{nombre_filter}%'))
        
        # Order by name
        query = query.order_by(Servicios.nombre)
        
        return paginate_query(query, page, per_page)
    
    @staticmethod
    def get_servicio_by_id(servicio_id):
        """
        Get service by ID.
        
        Args:
            servicio_id: Service ID
            
        Returns:
            Servicios: Service instance
            
        Raises:
            BusinessLogicError: If service not found
        """
        servicio = Servicios.query.get(servicio_id)
        if not servicio:
            raise BusinessLogicError('Servicio no encontrado')
        return servicio
    
    @staticmethod
    def create_servicio(data):
        """
        Create a new service.
        
        Args:
            data: Service data
            
        Returns:
            Servicios: Created service instance
        """
        # Validate data
        ServicioService.validate_servicio_data(data)
        
        # Create service
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
        
        return servicio
    
    @staticmethod
    def update_servicio(servicio_id, data):
        """
        Update a service.
        
        Args:
            servicio_id: Service ID
            data: Update data
            
        Returns:
            Servicios: Updated service instance
        """
        servicio = ServicioService.get_servicio_by_id(servicio_id)
        
        # Validate data
        ServicioService.validate_servicio_data(data, is_update=True)
        
        # Update fields
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
        return servicio
    
    @staticmethod
    def delete_servicio(servicio_id):
        """
        Delete a service.
        
        Args:
            servicio_id: Service ID to delete
        """
        servicio = ServicioService.get_servicio_by_id(servicio_id)
        
        db.session.delete(servicio)
        db.session.commit()


class MantencionService:
    """
    Service class for maintenance management operations.
    """
    
    @staticmethod
    def validate_mantencion_data(data, is_update=False):
        """
        Validate maintenance data.
        
        Args:
            data: Maintenance data to validate
            is_update: Whether this is an update operation
            
        Raises:
            ValidationError: If validation fails
        """
        if not is_update:
            required_fields = ['nombre_mantencion', 'descripcion_mantencion']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field.replace("_", " ").title()} es requerido')
        
        # Validate name length
        if 'nombre_mantencion' in data and data['nombre_mantencion']:
            if len(data['nombre_mantencion']) > 100:
                raise ValidationError('Nombre de mantención no puede exceder 100 caracteres')
        
        # Validate description length
        if 'descripcion_mantencion' in data and data['descripcion_mantencion']:
            if len(data['descripcion_mantencion']) > 500:
                raise ValidationError('Descripción no puede exceder 500 caracteres')
        
        # Validate date if provided
        if 'fecha_mantencion' in data and data['fecha_mantencion']:
            try:
                datetime.strptime(data['fecha_mantencion'], '%Y-%m-%d')
            except ValueError:
                raise ValidationError('Formato de fecha inválido (YYYY-MM-DD)')
    
    @staticmethod
    def get_mantenciones(page, per_page, nombre_filter=None, fecha_filter=None):
        """
        Get paginated list of maintenances with optional filters.
        
        Args:
            page: Page number
            per_page: Items per page
            nombre_filter: Filter by maintenance name
            fecha_filter: Filter by date
            
        Returns:
            dict: Paginated maintenance data
        """
        query = Mantenciones.query
        
        # Apply filters
        if nombre_filter:
            query = query.filter(Mantenciones.nombre_mantencion.ilike(f'%{nombre_filter}%'))
        
        if fecha_filter:
            try:
                fecha = datetime.strptime(fecha_filter, '%Y-%m-%d').date()
                query = query.filter(Mantenciones.fecha_mantencion == fecha)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        # Order by date descending
        query = query.order_by(Mantenciones.fecha_mantencion.desc())
        
        return paginate_query(query, page, per_page)
    
    @staticmethod
    def get_mantencion_by_id(mantencion_id):
        """
        Get maintenance by ID.
        
        Args:
            mantencion_id: Maintenance ID
            
        Returns:
            Mantenciones: Maintenance instance
            
        Raises:
            BusinessLogicError: If maintenance not found
        """
        mantencion = Mantenciones.query.get(mantencion_id)
        if not mantencion:
            raise BusinessLogicError('Mantención no encontrada')
        return mantencion
    
    @staticmethod
    def create_mantencion(data):
        """
        Create a new maintenance.
        
        Args:
            data: Maintenance data
            
        Returns:
            Mantenciones: Created maintenance instance
        """
        # Validate data
        MantencionService.validate_mantencion_data(data)
        
        # Parse date
        fecha_mantencion = None
        if data.get('fecha_mantencion'):
            fecha_mantencion = datetime.strptime(data['fecha_mantencion'], '%Y-%m-%d').date()
        
        # Create maintenance
        mantencion = Mantenciones(
            nombre_mantencion=data['nombre_mantencion'],
            descripcion_mantencion=data['descripcion_mantencion'],
            fecha_mantencion=fecha_mantencion
        )
        
        db.session.add(mantencion)
        db.session.commit()
        
        return mantencion
    
    @staticmethod
    def update_mantencion(mantencion_id, data):
        """
        Update a maintenance.
        
        Args:
            mantencion_id: Maintenance ID
            data: Update data
            
        Returns:
            Mantenciones: Updated maintenance instance
        """
        mantencion = MantencionService.get_mantencion_by_id(mantencion_id)
        
        # Validate data
        MantencionService.validate_mantencion_data(data, is_update=True)
        
        # Update fields
        if 'nombre_mantencion' in data:
            mantencion.nombre_mantencion = data['nombre_mantencion']
        if 'descripcion_mantencion' in data:
            mantencion.descripcion_mantencion = data['descripcion_mantencion']
        if 'fecha_mantencion' in data:
            if data['fecha_mantencion']:
                mantencion.fecha_mantencion = datetime.strptime(
                    data['fecha_mantencion'], '%Y-%m-%d'
                ).date()
            else:
                mantencion.fecha_mantencion = None
        
        db.session.commit()
        return mantencion
    
    @staticmethod
    def delete_mantencion(mantencion_id):
        """
        Delete a maintenance.
        
        Args:
            mantencion_id: Maintenance ID to delete
        """
        mantencion = MantencionService.get_mantencion_by_id(mantencion_id)
        
        db.session.delete(mantencion)
        db.session.commit()


class TrabajadorApoyoService:
    """
    Service class for support worker management operations.
    """
    
    @staticmethod
    def validate_trabajador_data(data, is_update=False):
        """
        Validate support worker data.
        
        Args:
            data: Worker data to validate
            is_update: Whether this is an update operation
            
        Raises:
            ValidationError: If validation fails
        """
        if not is_update:
            required_fields = ['nombre_trabajador', 'cargo_trabajador']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field.replace("_", " ").title()} es requerido')
        
        # Validate name length
        if 'nombre_trabajador' in data and data['nombre_trabajador']:
            if len(data['nombre_trabajador']) > 100:
                raise ValidationError('Nombre del trabajador no puede exceder 100 caracteres')
        
        # Validate position length
        if 'cargo_trabajador' in data and data['cargo_trabajador']:
            if len(data['cargo_trabajador']) > 100:
                raise ValidationError('Cargo no puede exceder 100 caracteres')
    
    @staticmethod
    def get_trabajadores_apoyo(page, per_page, nombre_filter=None, cargo_filter=None):
        """
        Get paginated list of support workers with optional filters.
        
        Args:
            page: Page number
            per_page: Items per page
            nombre_filter: Filter by worker name
            cargo_filter: Filter by position
            
        Returns:
            dict: Paginated worker data
        """
        query = TrabajadoresApoyo.query
        
        # Apply filters
        if nombre_filter:
            query = query.filter(TrabajadoresApoyo.nombre_trabajador.ilike(f'%{nombre_filter}%'))
        
        if cargo_filter:
            query = query.filter(TrabajadoresApoyo.cargo_trabajador.ilike(f'%{cargo_filter}%'))
        
        # Order by name
        query = query.order_by(TrabajadoresApoyo.nombre_trabajador)
        
        return paginate_query(query, page, per_page)
    
    @staticmethod
    def get_trabajador_by_id(trabajador_id):
        """
        Get support worker by ID.
        
        Args:
            trabajador_id: Worker ID
            
        Returns:
            TrabajadoresApoyo: Worker instance
            
        Raises:
            BusinessLogicError: If worker not found
        """
        trabajador = TrabajadoresApoyo.query.get(trabajador_id)
        if not trabajador:
            raise BusinessLogicError('Trabajador de apoyo no encontrado')
        return trabajador
    
    @staticmethod
    def create_trabajador(data):
        """
        Create a new support worker.
        
        Args:
            data: Worker data
            
        Returns:
            TrabajadoresApoyo: Created worker instance
        """
        # Validate data
        TrabajadorApoyoService.validate_trabajador_data(data)
        
        # Create worker
        trabajador = TrabajadoresApoyo(
            nombre_trabajador=data['nombre_trabajador'],
            cargo_trabajador=data['cargo_trabajador']
        )
        
        db.session.add(trabajador)
        db.session.commit()
        
        return trabajador
    
    @staticmethod
    def update_trabajador(trabajador_id, data):
        """
        Update a support worker.
        
        Args:
            trabajador_id: Worker ID
            data: Update data
            
        Returns:
            TrabajadoresApoyo: Updated worker instance
        """
        trabajador = TrabajadorApoyoService.get_trabajador_by_id(trabajador_id)
        
        # Validate data
        TrabajadorApoyoService.validate_trabajador_data(data, is_update=True)
        
        # Update fields
        if 'nombre_trabajador' in data:
            trabajador.nombre_trabajador = data['nombre_trabajador']
        if 'cargo_trabajador' in data:
            trabajador.cargo_trabajador = data['cargo_trabajador']
        
        db.session.commit()
        return trabajador
    
    @staticmethod
    def delete_trabajador(trabajador_id):
        """
        Delete a support worker.
        
        Args:
            trabajador_id: Worker ID to delete
        """
        trabajador = TrabajadorApoyoService.get_trabajador_by_id(trabajador_id)
        
        db.session.delete(trabajador)
        db.session.commit()


class RelacionService:
    """
    Service class for relationship management (Participa and Gestiona).
    """
    
    @staticmethod
    def create_participacion(persona_mayor_id, actividad_id):
        """
        Create a participation relationship.
        
        Args:
            persona_mayor_id: Elderly person ID
            actividad_id: Activity ID
            
        Returns:
            Participa: Created participation instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If relationship already exists
        """
        # Validate entities exist
        if not PersonasMayores.query.get(persona_mayor_id):
            raise ValidationError('Persona mayor no encontrada')
        
        # Note: We'll need to import Actividades here or check differently
        # For now, assume the relationship is valid if entities exist
        
        # Check if relationship already exists
        existing = Participa.query.filter_by(
            id_persona_mayor=persona_mayor_id,
            id_actividad=actividad_id
        ).first()
        
        if existing:
            raise BusinessLogicError('Esta persona ya participa en esta actividad')
        
        # Create participation
        participacion = Participa(
            id_persona_mayor=persona_mayor_id,
            id_actividad=actividad_id
        )
        
        db.session.add(participacion)
        db.session.commit()
        
        return participacion
    
    @staticmethod
    def delete_participacion(persona_mayor_id, actividad_id):
        """
        Delete a participation relationship.
        
        Args:
            persona_mayor_id: Elderly person ID
            actividad_id: Activity ID
            
        Raises:
            BusinessLogicError: If relationship not found
        """
        participacion = Participa.query.filter_by(
            id_persona_mayor=persona_mayor_id,
            id_actividad=actividad_id
        ).first()
        
        if not participacion:
            raise BusinessLogicError('Participación no encontrada')
        
        db.session.delete(participacion)
        db.session.commit()
    
    @staticmethod
    def create_gestion(persona_a_cargo_id, centro_id):
        """
        Create a management relationship.
        
        Args:
            persona_a_cargo_id: Person in charge ID
            centro_id: Community center ID
            
        Returns:
            Gestiona: Created management instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If relationship already exists
        """
        # Validate entities exist
        if not PersonasACargo.query.get(persona_a_cargo_id):
            raise ValidationError('Persona a cargo no encontrada')
        
        if not CentrosComunitarios.query.get(centro_id):
            raise ValidationError('Centro comunitario no encontrado')
        
        # Check if relationship already exists
        existing = Gestiona.query.filter_by(
            id_persona_a_cargo=persona_a_cargo_id,
            id_centro=centro_id
        ).first()
        
        if existing:
            raise BusinessLogicError('Esta persona ya gestiona este centro')
        
        # Create management
        gestion = Gestiona(
            id_persona_a_cargo=persona_a_cargo_id,
            id_centro=centro_id
        )
        
        db.session.add(gestion)
        db.session.commit()
        
        return gestion
    
    @staticmethod
    def delete_gestion(persona_a_cargo_id, centro_id):
        """
        Delete a management relationship.
        
        Args:
            persona_a_cargo_id: Person in charge ID
            centro_id: Community center ID
            
        Raises:
            BusinessLogicError: If relationship not found
        """
        gestion = Gestiona.query.filter_by(
            id_persona_a_cargo=persona_a_cargo_id,
            id_centro=centro_id
        ).first()
        
        if not gestion:
            raise BusinessLogicError('Gestión no encontrada')
        
        db.session.delete(gestion)
        db.session.commit()