"""
Services Management Services

Business logic layer for services and relationship management operations.
"""

from datetime import datetime
from app.extensions import db
from app.models import (
    Servicios, Participa, Gestiona,
    PersonasMayores, PersonasACargo, CentrosComunitarios
)
from app.api.utils import paginate_query, BaseCRUDService
from app.api.utils.errors import ValidationError, BusinessLogicError


class ServicioService(BaseCRUDService):
    """
    Service class for service management operations.
    """
    
    # BaseCRUDService properties
    @property
    def model_class(self):
        return Servicios
    
    @property
    def entity_name(self):
        return 'Servicio'
    
    @property
    def id_field(self):
        return 'id_servicio'
    
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
        service = ServicioService()
        return service.get_by_id(servicio_id)
    
    @staticmethod
    def create_servicio(data):
        """
        Create a new service.
        
        Args:
            data: Service data
            
        Returns:
            Servicios: Created service instance
            
        Raises:
            ValidationError: If validation fails
        """
        service = ServicioService()
        return service.create(data)
    
    # BaseCRUDService abstract methods implementation
    def validate_create_data(self, data):
        """Validate data for service creation."""
        ServicioService.validate_servicio_data(data)
    
    def build_entity(self, data):
        """Build service instance from data."""
        return Servicios(
            nombre_servicio=data.get('nombre_servicio'),
            descripcion_servicio=data.get('descripcion_servicio')
        )
    
    @staticmethod
    def update_servicio(servicio_id, data):
        """
        Update a service.
        
        Args:
            servicio_id: Service ID
            data: Updated service data
            
        Returns:
            Servicios: Updated service instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If service not found
        """
        service = ServicioService()
        return service.update(servicio_id, data)
    
    def validate_update_data(self, data, entity):
        """Validate data for service update."""
        ServicioService.validate_servicio_data(data, is_update=True)
    
    def update_entity_fields(self, entity, data):
        """Update service fields with new data."""
        if 'nombre_servicio' in data:
            entity.nombre_servicio = data['nombre_servicio']
        
        if 'descripcion_servicio' in data:
            entity.descripcion_servicio = data['descripcion_servicio']
    
    @staticmethod
    def delete_servicio(servicio_id):
        """
        Delete a service.
        
        Args:
            servicio_id: Service ID to delete
            
        Raises:
            BusinessLogicError: If service not found
        """
        service = ServicioService()
        return service.delete(servicio_id)


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