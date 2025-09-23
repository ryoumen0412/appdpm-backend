"""
Maintenance Services

Business logic layer for maintenance management operations.
"""

from app.extensions import db
from app.models import Mantenciones, CentrosComunitarios
from app.api.utils import paginate_query
from app.api.utils.errors import ValidationError, BusinessLogicError
from datetime import datetime


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
            required_fields = ['fecha', 'id_centro']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field.replace("_", " ").title()} es requerido')
        
        # Validate center exists
        if 'id_centro' in data and data['id_centro']:
            centro = CentrosComunitarios.query.get(data['id_centro'])
            if not centro:
                raise ValidationError('Centro comunitario no encontrado')
        
        # Validate date format
        if 'fecha' in data and data['fecha']:
            try:
                if isinstance(data['fecha'], str):
                    datetime.strptime(data['fecha'], '%Y-%m-%d')
            except ValueError:
                raise ValidationError('Formato de fecha inválido. Use YYYY-MM-DD')
    
    @staticmethod
    def get_mantenciones(page=1, per_page=10, centro_filter=None, fecha_desde=None, fecha_hasta=None):
        """
        Get paginated list of maintenance records with optional filters.
        
        Args:
            page: Page number
            per_page: Items per page  
            centro_filter: Filter by center ID
            fecha_desde: Filter maintenance from this date
            fecha_hasta: Filter maintenance until this date
            
        Returns:
            dict: Paginated maintenance data
        """
        query = Mantenciones.query
        
        # Apply filters
        if centro_filter:
            try:
                centro_id = int(centro_filter)
                query = query.filter(Mantenciones.id_centro == centro_id)
            except ValueError:
                pass  # Invalid center ID, ignore filter
        
        if fecha_desde:
            try:
                fecha = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                query = query.filter(Mantenciones.fecha >= fecha)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        if fecha_hasta:
            try:
                fecha = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                query = query.filter(Mantenciones.fecha <= fecha)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        # Order by date descending
        query = query.order_by(Mantenciones.fecha.desc())
        
        return paginate_query(query, page, per_page)
    
    @staticmethod
    def get_mantencion_by_id(mantencion_id):
        """
        Get maintenance record by ID.
        
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
        Create a new maintenance record.
        
        Args:
            data: Maintenance data
            
        Returns:
            Mantenciones: Created maintenance instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate data
        MantencionService.validate_mantencion_data(data)
        
        # Parse date if it's a string
        fecha = data['fecha']
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Create maintenance record
        mantencion = Mantenciones(
            fecha=fecha,
            id_centro=data['id_centro'],
            detalle=data.get('detalle'),
            observaciones=data.get('observaciones'),
            adjuntos=data.get('adjuntos'),
            quienes_realizaron=data.get('quienes_realizaron')
        )
        
        db.session.add(mantencion)
        db.session.commit()
        
        return mantencion
    
    @staticmethod
    def update_mantencion(mantencion_id, data):
        """
        Update a maintenance record.
        
        Args:
            mantencion_id: Maintenance ID
            data: Update data
            
        Returns:
            Mantenciones: Updated maintenance instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        mantencion = MantencionService.get_mantencion_by_id(mantencion_id)
        
        # Validate data
        MantencionService.validate_mantencion_data(data, is_update=True)
        
        # Update fields
        if 'fecha' in data:
            fecha = data['fecha']
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            mantencion.fecha = fecha
        
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
        return mantencion
    
    @staticmethod
    def delete_mantencion(mantencion_id):
        """
        Delete a maintenance record.
        
        Args:
            mantencion_id: Maintenance ID to delete
            
        Raises:
            BusinessLogicError: If maintenance not found or cannot be deleted
        """
        mantencion = MantencionService.get_mantencion_by_id(mantencion_id)
        
        db.session.delete(mantencion)
        db.session.commit()
    
    @staticmethod
    def get_mantenciones_by_centro(centro_id):
        """
        Get all maintenance records for a specific center.
        
        Args:
            centro_id: Center ID
            
        Returns:
            list: List of maintenance records
        """
        return Mantenciones.query.filter_by(id_centro=centro_id).order_by(
            Mantenciones.fecha.desc()
        ).all()