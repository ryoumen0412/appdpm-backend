"""
Community Centers Services

Business logic layer for community center management operations.
"""

from app.extensions import db
from app.models import CentrosComunitarios
from app.api.utils import paginate_query, BaseCRUDService
from app.api.utils.errors import ValidationError, BusinessLogicError
import re


class CentroService(BaseCRUDService):
    """
    Service class for community center management operations.
    """
    
    # BaseCRUDService properties
    @property
    def model_class(self):
        return CentrosComunitarios
    
    @property
    def entity_name(self):
        return 'Centro comunitario'
    
    @property
    def id_field(self):
        return 'id_centro'
    
    @staticmethod
    def validate_centro_data(data, is_update=False):
        """
        Validate community center data.
        
        Args:
            data: Center data to validate
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
        if 'nombre' in data and data['nombre']:
            if len(data['nombre']) > 150:
                raise ValidationError('Nombre del centro no puede exceder 150 caracteres')
        
        # Validate address length
        if 'direccion' in data and data['direccion']:
            if len(data['direccion']) > 200:
                raise ValidationError('Dirección no puede exceder 200 caracteres')
        
        # Validate sector
        if 'sector' in data and data['sector']:
            if len(data['sector']) > 100:
                raise ValidationError('Sector no puede exceder 100 caracteres')
        
        # Validate phone if provided
        if 'telefono_centro' in data and data['telefono_centro']:
            phone = data['telefono_centro'].strip()
            if phone and not re.match(r'^[\d\s\-\+\(\)]+$', phone):
                raise ValidationError('Formato de teléfono inválido')
            if len(phone) > 20:
                raise ValidationError('Teléfono no puede exceder 20 caracteres')
        
        # Validate email if provided
        if 'email_centro' in data and data['email_centro']:
            email = data['email_centro'].strip().lower()
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if email and not re.match(email_pattern, email):
                raise ValidationError('Formato de email inválido')
            if len(email) > 100:
                raise ValidationError('Email no puede exceder 100 caracteres')
        
        # Validate capacity if provided
        if 'capacidad_centro' in data and data['capacidad_centro'] is not None:
            try:
                capacity = int(data['capacidad_centro'])
                if capacity < 0:
                    raise ValidationError('Capacidad debe ser un número positivo')
                if capacity > 10000:
                    raise ValidationError('Capacidad no puede exceder 10,000 personas')
            except (ValueError, TypeError):
                raise ValidationError('Capacidad debe ser un número válido')
    
    @staticmethod
    def get_centros(page, per_page, nombre_filter=None, sector_filter=None, direccion_filter=None):
        """
        Get paginated list of community centers with optional filters.
        
        Args:
            page: Page number
            per_page: Items per page
            nombre_filter: Filter by center name
            sector_filter: Filter by sector
            direccion_filter: Filter by address
            
        Returns:
            dict: Paginated center data
        """
        query = CentrosComunitarios.query
        
        # Apply filters
        if nombre_filter:
            query = query.filter(CentrosComunitarios.nombre.ilike(f'%{nombre_filter}%'))
        
        if sector_filter:
            query = query.filter(CentrosComunitarios.sector.ilike(f'%{sector_filter}%'))
        
        if direccion_filter:
            query = query.filter(CentrosComunitarios.direccion.ilike(f'%{direccion_filter}%'))
        
        # Order by name for consistent pagination
        query = query.order_by(CentrosComunitarios.nombre)
        
        return paginate_query(query, page, per_page)
    
    @staticmethod
    def get_centro_by_id(centro_id):
        """
        Get community center by ID.
        
        Args:
            centro_id: Center ID
            
        Returns:
            CentrosComunitarios: Center instance
            
        Raises:
            BusinessLogicError: If center not found
        """
        service = CentroService()
        return service.get_by_id(centro_id)
    
    @staticmethod
    def create_centro(data):
        """
        Create a new community center.
        
        Args:
            data: Center data
            
        Returns:
            CentrosComunitarios: Created center instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        service = CentroService()
        return service.create(data)
    
    # BaseCRUDService abstract methods implementation
    def validate_create_data(self, data):
        """Validate data for center creation."""
        # Validate data
        CentroService.validate_centro_data(data)
        
        # Check if center name already exists
        if not self.check_unique_field('nombre', data['nombre']):
            raise BusinessLogicError('Ya existe un centro con este nombre')
    
    def build_entity(self, data):
        """Build center instance from data."""
        # Create center
        centro = CentrosComunitarios(
            nombre=data['nombre'],
            direccion=data.get('direccion'),
            sector=data.get('sector')
        )
        
        return centro
    
    @staticmethod
    def update_centro(centro_id, data):
        """
        Update a community center.
        
        Args:
            centro_id: Center ID
            data: Update data
            
        Returns:
            CentrosComunitarios: Updated center instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        service = CentroService()
        return service.update(centro_id, data)
    
    def validate_update_data(self, data, entity):
        """Validate data for center update."""
        # Validate data
        CentroService.validate_centro_data(data, is_update=True)
        
        # Check name uniqueness if changing
        if 'nombre' in data and data['nombre'] != entity.nombre:
            if not self.check_unique_field('nombre', data['nombre'], exclude_id=entity.id_centro):
                raise BusinessLogicError('Ya existe un centro con este nombre')
    
    def update_entity_fields(self, entity, data):
        """Update center fields with new data."""
        # Update fields
        if 'nombre' in data:
            entity.nombre = data['nombre']
        if 'direccion' in data:
            entity.direccion = data['direccion']
        if 'sector' in data:
            entity.sector = data['sector']
    
    @staticmethod
    def delete_centro(centro_id):
        """
        Delete a community center.
        
        Args:
            centro_id: Center ID to delete
            
        Raises:
            BusinessLogicError: If business rules are violated
        """
        service = CentroService()
        return service.delete(centro_id)
    
    def validate_delete(self, entity):
        """Validate if center can be deleted."""
        # Check for related records (activities, etc.)
        # For now, allow deletion (cascade will handle relationships)
        pass
    
    @staticmethod
    def get_sectores_list():
        """
        Get list of unique sectors.
        
        Returns:
            list: List of sector names
        """
        sectores = db.session.query(CentrosComunitarios.sector_centro).distinct().all()
        return [sector[0] for sector in sectores if sector[0]]
    
    @staticmethod
    def get_centro_stats():
        """
        Get community center statistics.
        
        Returns:
            dict: Center statistics
        """
        total_centers = CentrosComunitarios.query.count()
        centers_by_sector = {}
        
        sectores_data = db.session.query(
            CentrosComunitarios.sector_centro,
            db.func.count(CentrosComunitarios.id_centro)
        ).group_by(CentrosComunitarios.sector_centro).all()
        
        for sector, count in sectores_data:
            centers_by_sector[sector or 'Sin sector'] = count
        
        # Calculate total capacity
        total_capacity = db.session.query(
            db.func.sum(CentrosComunitarios.capacidad_centro)
        ).scalar() or 0
        
        return {
            'total_centers': total_centers,
            'centers_by_sector': centers_by_sector,
            'total_capacity': total_capacity
        }