"""
Base CRUD Service for common database operations.

This module provides a base class with common CRUD operations that can be
inherited by specific service classes to reduce code duplication.
"""

from abc import ABC, abstractmethod
from app.extensions import db
from .errors import BusinessLogicError, ValidationError


class BaseCRUDService(ABC):
    """
    Abstract base class for CRUD services.
    
    This class provides common database operations that are used across
    multiple service classes. Subclasses must define the model_class
    and entity_name properties.
    """
    
    @property
    @abstractmethod
    def model_class(self):
        """
        The SQLAlchemy model class for this service.
        
        Returns:
            class: The model class (e.g., Usuario, Mantenciones)
        """
        pass
    
    @property
    @abstractmethod
    def entity_name(self):
        """
        Human-readable name for the entity (for error messages).
        
        Returns:
            str: Entity name (e.g., 'Usuario', 'Mantención')
        """
        pass
    
    @property
    @abstractmethod
    def id_field(self):
        """
        The primary key field name for the model.
        
        Returns:
            str: Primary key field name (e.g., 'id_usuario', 'id_mantencion')
        """
        pass
    
    def get_by_id(self, entity_id):
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Model instance
            
        Raises:
            BusinessLogicError: If entity not found
        """
        entity = self.model_class.query.get(entity_id)
        if not entity:
            raise BusinessLogicError(f'{self.entity_name} no encontrado')
        return entity
    
    def create(self, data):
        """
        Create a new entity.
        
        Args:
            data: Entity data dictionary
            
        Returns:
            Model instance: Created entity
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        # Validate data using subclass method
        self.validate_create_data(data)
        
        # Create entity using subclass method
        entity = self.build_entity(data)
        
        # Save to database
        db.session.add(entity)
        db.session.commit()
        
        return entity
    
    def update(self, entity_id, data):
        """
        Update an entity.
        
        Args:
            entity_id: Entity ID
            data: Update data dictionary
            
        Returns:
            Model instance: Updated entity
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        # Get existing entity
        entity = self.get_by_id(entity_id)
        
        # Validate update data using subclass method
        self.validate_update_data(data, entity)
        
        # Update entity using subclass method
        self.update_entity_fields(entity, data)
        
        # Save changes
        db.session.commit()
        
        return entity
    
    def delete(self, entity_id):
        """
        Delete an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            BusinessLogicError: If entity not found or cannot be deleted
        """
        # Get existing entity
        entity = self.get_by_id(entity_id)
        
        # Perform pre-delete validation using subclass method
        self.validate_delete(entity)
        
        # Delete entity
        db.session.delete(entity)
        db.session.commit()
        
        return True
    
    # Abstract methods that subclasses must implement
    
    @abstractmethod
    def validate_create_data(self, data):
        """
        Validate data for entity creation.
        
        Args:
            data: Data to validate
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    @abstractmethod
    def build_entity(self, data):
        """
        Build entity instance from data.
        
        Args:
            data: Entity data
            
        Returns:
            Model instance: New entity (not yet saved)
        """
        pass
    
    @abstractmethod
    def validate_update_data(self, data, entity):
        """
        Validate data for entity update.
        
        Args:
            data: Update data
            entity: Existing entity instance
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    @abstractmethod
    def update_entity_fields(self, entity, data):
        """
        Update entity fields with new data.
        
        Args:
            entity: Entity instance to update
            data: Update data
        """
        pass
    
    def validate_delete(self, entity):
        """
        Validate if entity can be deleted.
        
        Default implementation allows deletion. Override if needed.
        
        Args:
            entity: Entity instance to delete
            
        Raises:
            BusinessLogicError: If entity cannot be deleted
        """
        pass
    
    # Helper methods for common operations
    
    def check_unique_field(self, field_name, value, exclude_id=None):
        """
        Check if a field value is unique.
        
        Args:
            field_name: Field name to check
            value: Value to check for uniqueness
            exclude_id: ID to exclude from the check (for updates)
            
        Returns:
            bool: True if unique, False otherwise
        """
        query = self.model_class.query.filter(
            getattr(self.model_class, field_name) == value
        )
        
        if exclude_id is not None:
            id_field = getattr(self.model_class, self.id_field)
            query = query.filter(id_field != exclude_id)
        
        return query.first() is None
    
    def validate_required_fields(self, data, required_fields):
        """
        Validate that required fields are present in data.
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Raises:
            ValidationError: If any required field is missing
        """
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'{field} es requerido')