"""
Support Workers Services

Business logic layer for support worker management operations.
"""

from app.extensions import db
from app.models import TrabajadoresApoyo, CentrosComunitarios
from app.api.utils import paginate_query, BaseCRUDService
from app.api.utils.errors import ValidationError, BusinessLogicError
import re


class TrabajadorApoyoService(BaseCRUDService):
    """
    Service class for support worker management operations.
    """
    
    # BaseCRUDService properties
    @property
    def model_class(self):
        return TrabajadoresApoyo
    
    @property
    def entity_name(self):
        return 'Trabajador de apoyo'
    
    @property
    def id_field(self):
        return 'rut'
    
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
            required_fields = ['rut', 'nombre']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field.replace("_", " ").title()} es requerido')
        
        # Validate RUT format
        if 'rut' in data and data['rut']:
            rut = data['rut'].replace('.', '').replace('-', '')
            if not re.match(r'^\d{7,8}[0-9Kk]$', rut):
                raise ValidationError('Formato de RUT inválido')
        
        # Validate name length
        if 'nombre' in data and data['nombre']:
            if len(data['nombre']) > 100:
                raise ValidationError('Nombre no puede exceder 100 caracteres')
        
        # Validate apellidos length
        if 'apellidos' in data and data['apellidos']:
            if len(data['apellidos']) > 150:
                raise ValidationError('Apellidos no pueden exceder 150 caracteres')
        
        # Validate cargo length
        if 'cargo' in data and data['cargo']:
            if len(data['cargo']) > 100:
                raise ValidationError('Cargo no puede exceder 100 caracteres')
        
        # Validate center exists
        if 'id_centro' in data and data['id_centro']:
            centro = CentrosComunitarios.query.get(data['id_centro'])
            if not centro:
                raise ValidationError('Centro comunitario no encontrado')
    
    @staticmethod
    def get_trabajadores(page=1, per_page=10, nombre_filter=None, centro_filter=None, cargo_filter=None):
        """
        Get paginated list of support workers with optional filters.
        
        Args:
            page: Page number
            per_page: Items per page
            nombre_filter: Filter by worker name
            centro_filter: Filter by center ID
            cargo_filter: Filter by position/role
            
        Returns:
            dict: Paginated worker data
        """
        query = TrabajadoresApoyo.query
        
        # Apply filters
        if nombre_filter:
            query = query.filter(
                (TrabajadoresApoyo.nombre.ilike(f'%{nombre_filter}%')) |
                (TrabajadoresApoyo.apellidos.ilike(f'%{nombre_filter}%'))
            )
        
        if centro_filter:
            try:
                centro_id = int(centro_filter)
                query = query.filter(TrabajadoresApoyo.id_centro == centro_id)
            except ValueError:
                pass  # Invalid center ID, ignore filter
        
        if cargo_filter:
            query = query.filter(TrabajadoresApoyo.cargo.ilike(f'%{cargo_filter}%'))
        
        # Order by name
        query = query.order_by(TrabajadoresApoyo.nombre, TrabajadoresApoyo.apellidos)
        
        return paginate_query(query, page, per_page)
    
    @staticmethod
    def get_trabajador_by_rut(rut):
        """
        Get support worker by RUT.
        Soporta formatos XXXXXXX-X y XXXXXXXX-X
        
        Args:
            rut: Worker RUT (con guión)
            
        Returns:
            TrabajadoresApoyo: Worker instance
            
        Raises:
            BusinessLogicError: If worker not found
        """
        from app.auth_utils import normalize_rut
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Normalize and validate RUT format
        normalized_rut = normalize_rut(rut)
        if not normalized_rut:
            logger.warning(f"Formato de RUT inválido: {rut}")
            raise BusinessLogicError('Formato de RUT inválido')
        
        # Search worker by normalized RUT (which is the primary key)
        service = TrabajadorApoyoService()
        
        try:
            trabajador = service.get_by_id(normalized_rut)
            logger.info(f"Trabajador encontrado: {normalized_rut}")
            return trabajador
        except BusinessLogicError:
            logger.warning(f"Trabajador con RUT {normalized_rut} no encontrado")
            raise BusinessLogicError('Trabajador de apoyo no encontrado')
    
    @staticmethod
    def create_trabajador(data):
        """
        Create a new support worker.
        
        Args:
            data: Worker data
            
        Returns:
            TrabajadoresApoyo: Created worker instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        service = TrabajadorApoyoService()
        return service.create(data)
    
    # BaseCRUDService abstract methods implementation
    def validate_create_data(self, data):
        """Validate data for worker creation."""
        # Validate data
        TrabajadorApoyoService.validate_trabajador_data(data)
        
        # Clean RUT
        rut_clean = data['rut'].replace('.', '').replace('-', '')
        data['rut'] = rut_clean  # Update with cleaned RUT
        
        # Check if worker already exists
        if not self.check_unique_field('rut', rut_clean):
            raise BusinessLogicError('Ya existe un trabajador con este RUT')
    
    def build_entity(self, data):
        """Build worker instance from data."""
        return TrabajadoresApoyo(
            rut=data['rut'],
            nombre=data['nombre'],
            apellidos=data.get('apellidos'),
            cargo=data.get('cargo'),
            id_centro=data.get('id_centro')
        )
    
    @staticmethod
    def update_trabajador(rut, data):
        """
        Update a support worker.
        
        Args:
            rut: Worker RUT
            data: Update data
            
        Returns:
            TrabajadoresApoyo: Updated worker instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        # Clean RUT
        rut_clean = rut.replace('.', '').replace('-', '')
        
        service = TrabajadorApoyoService()
        return service.update(rut_clean, data)
    
    def validate_update_data(self, data, entity):
        """Validate data for worker update."""
        TrabajadorApoyoService.validate_trabajador_data(data, is_update=True)
    
    def update_entity_fields(self, entity, data):
        """Update worker fields with new data."""
        # Update fields (RUT cannot be changed)
        if 'nombre' in data:
            entity.nombre = data['nombre']
        if 'apellidos' in data:
            entity.apellidos = data['apellidos']
        if 'cargo' in data:
            entity.cargo = data['cargo']
        if 'id_centro' in data:
            entity.id_centro = data['id_centro']
    
    @staticmethod
    def delete_trabajador(rut):
        """
        Delete a support worker.
        
        Args:
            rut: Worker RUT to delete
            
        Raises:
            BusinessLogicError: If worker not found or cannot be deleted
        """
        # Clean RUT
        rut_clean = rut.replace('.', '').replace('-', '')
        
        service = TrabajadorApoyoService()
        return service.delete(rut_clean)
    
    @staticmethod
    def get_trabajadores_by_centro(centro_id):
        """
        Get all support workers for a specific center.
        
        Args:
            centro_id: Center ID
            
        Returns:
            list: List of workers for the center
        """
        return TrabajadoresApoyo.query.filter_by(id_centro=centro_id).order_by(
            TrabajadoresApoyo.nombre, TrabajadoresApoyo.apellidos
        ).all()