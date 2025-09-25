"""
User Services

Business logic layer for user management operations.
"""

from app.extensions import db
from app.models import Usuario
from app.api.utils import paginate_query, BaseCRUDService
from app.api.utils.errors import ValidationError, BusinessLogicError
from app.auth_utils import validate_rut, normalize_rut, validate_password_strength


class UsuarioService(BaseCRUDService):
    """
    Service class for user management operations.
    """
    
    # BaseCRUDService properties
    @property
    def model_class(self):
        return Usuario
    
    @property
    def entity_name(self):
        return 'Usuario'
    
    @property
    def id_field(self):
        return 'id_usuario'
    
    @staticmethod
    def get_usuarios(page, per_page, rut_filter=None, username_filter=None, nivel_filter=None):
        """
        Get paginated list of users with optional filters.
        
        Args:
            page: Page number
            per_page: Items per page
            rut_filter: Filter by RUT
            username_filter: Filter by username
            nivel_filter: Filter by user level
            
        Returns:
            dict: Paginated user data
        """
        query = Usuario.query
        
        # Apply filters
        if rut_filter:
            query = query.filter(Usuario.rut_usuario.ilike(f'%{rut_filter}%'))
        
        if username_filter:
            query = query.filter(Usuario.user_usuario.ilike(f'%{username_filter}%'))
        
        if nivel_filter is not None:
            query = query.filter(Usuario.nivel_usuario == nivel_filter)
        
        # Order by ID for consistent pagination
        query = query.order_by(Usuario.id_usuario)
        
        return paginate_query(query, page, per_page)
    
    @staticmethod
    def get_usuario_by_id(usuario_id):
        """
        Get user by ID.
        
        Args:
            usuario_id: User ID
            
        Returns:
            Usuario: User instance
            
        Raises:
            BusinessLogicError: If user not found
        """
        service = UsuarioService()
        return service.get_by_id(usuario_id)
    
    @staticmethod
    def create_usuario(data):
        """
        Create a new user.
        
        Args:
            data: User data
            
        Returns:
            Usuario: Created user instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        service = UsuarioService()
        return service.create(data)
    
    # BaseCRUDService abstract methods implementation
    def validate_create_data(self, data):
        """Validate data for user creation."""
        # Validate required fields
        required_fields = ['rut_usuario', 'user_usuario', 'password', 'nivel_usuario']
        self.validate_required_fields(data, required_fields)
        
        # Normalize and validate RUT
        rut = normalize_rut(data['rut_usuario'])
        if not rut:
            raise ValidationError('Formato de RUT inválido')
        data['rut_usuario'] = rut  # Update with normalized RUT
        
        # Check if user already exists by RUT
        if not self.check_unique_field('rut_usuario', rut):
            raise BusinessLogicError('Ya existe un usuario con este RUT')
        
        # Check if username already exists
        if not self.check_unique_field('user_usuario', data['user_usuario']):
            raise BusinessLogicError('Ya existe un usuario con este nombre de usuario')
        
        # Validate password strength
        is_valid, message = validate_password_strength(data['password'])
        if not is_valid:
            raise ValidationError(message)
        
        # Validate user level
        if data['nivel_usuario'] not in [1, 2, 3]:
            raise ValidationError('Nivel de usuario debe ser 1 (apoyo), 2 (encargado) o 3 (admin)')
    
    def build_entity(self, data):
        """Build user instance from data."""
        # Create new user
        usuario = Usuario(
            rut_usuario=data['rut_usuario'],
            user_usuario=data['user_usuario'],
            nivel_usuario=data['nivel_usuario']
        )
        
        # Set password (this will hash it)
        usuario.set_password(data['password'])
        
        return usuario
    
    @staticmethod
    def update_usuario(usuario_id, data):
        """
        Update a user.
        
        Args:
            usuario_id: User ID
            data: Update data
            
        Returns:
            Usuario: Updated user instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        service = UsuarioService()
        return service.update(usuario_id, data)
    
    def validate_update_data(self, data, entity):
        """Validate data for user update."""
        # Update username if provided
        if 'user_usuario' in data:
            if data['user_usuario'] != entity.user_usuario:
                # Check if new username already exists
                if not self.check_unique_field('user_usuario', data['user_usuario'], exclude_id=entity.id_usuario):
                    raise BusinessLogicError('Ya existe un usuario con este nombre de usuario')
        
        # Validate user level if provided
        if 'nivel_usuario' in data:
            if data['nivel_usuario'] not in [1, 2, 3]:
                raise ValidationError('Nivel de usuario debe ser 1 (apoyo), 2 (encargado) o 3 (admin)')
        
        # Validate password if provided
        if 'password' in data and data['password']:
            is_valid, message = validate_password_strength(data['password'])
            if not is_valid:
                raise ValidationError(message)
    
    def update_entity_fields(self, entity, data):
        """Update user fields with new data."""
        # Update username if provided
        if 'user_usuario' in data:
            entity.user_usuario = data['user_usuario']
        
        # Update user level if provided
        if 'nivel_usuario' in data:
            entity.nivel_usuario = data['nivel_usuario']
        
        # Update password if provided
        if 'password' in data and data['password']:
            entity.set_password(data['password'])
    
    @staticmethod
    def delete_usuario(usuario_id, current_user):
        """
        Delete a user.
        
        Args:
            usuario_id: User ID to delete
            current_user: Current authenticated user
            
        Raises:
            BusinessLogicError: If business rules are violated
        """
        service = UsuarioService()
        usuario = service.get_by_id(usuario_id)
        
        # Prevent self-deletion
        if usuario.id_usuario == current_user.id_usuario:
            raise BusinessLogicError('No puedes eliminar tu propio usuario')
        
        # Use base class delete method
        return service.delete(usuario_id)
    
    def validate_delete(self, entity):
        """Validate if user can be deleted."""
        # Check for related records
        # Note: In real app, check for foreign key relationships
        # For now, allow deletion (cascade will handle relationships)
        pass
    
    @staticmethod
    def reset_password(usuario_id, new_password):
        """
        Reset user password (admin only).
        
        Args:
            usuario_id: User ID
            new_password: New password
            
        Returns:
            Usuario: Updated user instance
            
        Raises:
            ValidationError: If validation fails
        """
        usuario = UsuarioService.get_usuario_by_id(usuario_id)
        
        # Validate new password
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            raise ValidationError(message)
        
        # Set new password
        usuario.set_password(new_password)
        db.session.commit()
        
        return usuario
    
    @staticmethod
    def get_user_stats():
        """
        Get user statistics.
        
        Returns:
            dict: User statistics
        """
        total_users = Usuario.query.count()
        users_by_level = {
            'apoyo': Usuario.query.filter_by(nivel_usuario=1).count(),
            'encargado': Usuario.query.filter_by(nivel_usuario=2).count(),
            'admin': Usuario.query.filter_by(nivel_usuario=3).count()
        }
        
        return {
            'total_users': total_users,
            'users_by_level': users_by_level
        }