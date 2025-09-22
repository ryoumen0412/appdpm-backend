"""
User Services

Business logic layer for user management operations.
"""

from app import db
from app.models import Usuario
from app.api.utils import paginate_query
from app.api.utils.errors import ValidationError, BusinessLogicError
from app.auth_utils import validate_rut, clean_rut, validate_password_strength


class UsuarioService:
    """
    Service class for user management operations.
    """
    
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
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            raise BusinessLogicError('Usuario no encontrado')
        return usuario
    
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
        # Validate required fields
        required_fields = ['rut_usuario', 'user_usuario', 'password', 'nivel_usuario']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'{field} es requerido')
        
        # Clean and validate RUT
        rut = clean_rut(data['rut_usuario'])
        if not validate_rut(rut):
            raise ValidationError('Formato de RUT inválido')
        
        # Check if user already exists
        if Usuario.query.filter_by(rut_usuario=rut).first():
            raise BusinessLogicError('Ya existe un usuario con este RUT')
        
        # Check if username already exists
        if Usuario.query.filter_by(user_usuario=data['user_usuario']).first():
            raise BusinessLogicError('Ya existe un usuario con este nombre de usuario')
        
        # Validate password strength
        is_valid, message = validate_password_strength(data['password'])
        if not is_valid:
            raise ValidationError(message)
        
        # Validate user level
        if data['nivel_usuario'] not in [1, 2, 3]:
            raise ValidationError('Nivel de usuario debe ser 1 (apoyo), 2 (encargado) o 3 (admin)')
        
        # Create new user
        usuario = Usuario(
            rut_usuario=rut,
            user_usuario=data['user_usuario'],
            nivel_usuario=data['nivel_usuario']
        )
        usuario.set_password(data['password'])
        
        db.session.add(usuario)
        db.session.commit()
        
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
        usuario = UsuarioService.get_usuario_by_id(usuario_id)
        
        # Update username if provided
        if 'user_usuario' in data:
            if data['user_usuario'] != usuario.user_usuario:
                # Check if new username already exists
                existing = Usuario.query.filter_by(user_usuario=data['user_usuario']).first()
                if existing and existing.id_usuario != usuario_id:
                    raise BusinessLogicError('Ya existe un usuario con este nombre de usuario')
                usuario.user_usuario = data['user_usuario']
        
        # Update user level if provided
        if 'nivel_usuario' in data:
            if data['nivel_usuario'] not in [1, 2, 3]:
                raise ValidationError('Nivel de usuario debe ser 1 (apoyo), 2 (encargado) o 3 (admin)')
            usuario.nivel_usuario = data['nivel_usuario']
        
        # Update password if provided
        if 'password' in data and data['password']:
            is_valid, message = validate_password_strength(data['password'])
            if not is_valid:
                raise ValidationError(message)
            usuario.set_password(data['password'])
        
        db.session.commit()
        return usuario
    
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
        usuario = UsuarioService.get_usuario_by_id(usuario_id)
        
        # Prevent self-deletion
        if usuario.id_usuario == current_user.id_usuario:
            raise BusinessLogicError('No puedes eliminar tu propio usuario')
        
        # Check for related records
        # Note: In real app, check for foreign key relationships
        # For now, allow deletion (cascade will handle relationships)
        
        db.session.delete(usuario)
        db.session.commit()
    
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