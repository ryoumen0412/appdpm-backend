"""
Activities Services

Business        # Validate name length
        if 'nombre' in data and data['nombre']:
            if len(data['nombre']) > 150:
                raise ValidationError('Nombre de actividad no puede exceder 150 caracteres')r activity and workshop management operations.
"""

from datetime import datetime
from app.extensions import db
from app.models import Actividades, Talleres, CentrosComunitarios, PersonasACargo
from app.api.utils import paginate_query
from app.api.utils.errors import ValidationError, BusinessLogicError


class ActividadService:
    """
    Service class for activity management operations.
    """
    
    @staticmethod
    def validate_actividad_data(data, is_update=False):
        """
        Validate activity data.
        
        Args:
            data: Activity data to validate
            is_update: Whether this is an update operation
            
        Raises:
            ValidationError: If validation fails
        """
        if not is_update:
            required_fields = ['nombre', 'fecha_inicio']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field.replace("_", " ").title()} es requerido')
        
        # Validate name length
        if 'nombre_actividad' in data and data['nombre_actividad']:
            if len(data['nombre_actividad']) > 100:
                raise ValidationError('Nombre de actividad no puede exceder 100 caracteres')
        
        # Validate description length
        if 'descripcion_actividad' in data and data['descripcion_actividad']:
            if len(data['descripcion_actividad']) > 500:
                raise ValidationError('Descripción no puede exceder 500 caracteres')
        
        # Validate center exists
        if 'id_centro' in data and data['id_centro']:
            centro = CentrosComunitarios.query.get(data['id_centro'])
            if not centro:
                raise ValidationError('Centro comunitario no encontrado')
        
        # Validate responsible person if provided
        if 'id_persona_a_cargo' in data and data['id_persona_a_cargo']:
            persona = PersonasACargo.query.get(data['id_persona_a_cargo'])
            if not persona:
                raise ValidationError('Persona a cargo no encontrada')
        
        # Validate dates if provided
        if 'fecha_inicio_actividad' in data and data['fecha_inicio_actividad']:
            try:
                fecha_inicio = datetime.strptime(data['fecha_inicio_actividad'], '%Y-%m-%d').date()
                # Check if start date is not too far in the past
                if (datetime.now().date() - fecha_inicio).days > 365:
                    raise ValidationError('Fecha de inicio no puede ser más de un año en el pasado')
            except ValueError:
                raise ValidationError('Formato de fecha de inicio inválido (YYYY-MM-DD)')
        
        if 'fecha_fin_actividad' in data and data['fecha_fin_actividad']:
            try:
                fecha_fin = datetime.strptime(data['fecha_fin_actividad'], '%Y-%m-%d').date()
                # Validate end date after start date if both provided
                if ('fecha_inicio_actividad' in data and data['fecha_inicio_actividad'] and
                    fecha_fin < datetime.strptime(data['fecha_inicio_actividad'], '%Y-%m-%d').date()):
                    raise ValidationError('Fecha de fin debe ser posterior a fecha de inicio')
            except ValueError:
                raise ValidationError('Formato de fecha de fin inválido (YYYY-MM-DD)')
    
    @staticmethod
    def get_actividades(page, per_page, nombre_filter=None, centro_filter=None, 
                       fecha_inicio=None, fecha_fin=None):
        """
        Get paginated list of activities with optional filters.
        
        Args:
            page: Page number
            per_page: Items per page
            nombre_filter: Filter by activity name
            centro_filter: Filter by center ID
            fecha_inicio: Filter activities after this date
            fecha_fin: Filter activities before this date
            
        Returns:
            dict: Paginated activity data
        """
        query = Actividades.query
        
        # Apply filters
        if nombre_filter:
            query = query.filter(Actividades.nombre.ilike(f'%{nombre_filter}%'))
        
        if fecha_inicio:
            try:
                fecha = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                query = query.filter(Actividades.fecha_inicio >= fecha)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        if fecha_fin:
            try:
                fecha = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                query = query.filter(Actividades.fecha_termino <= fecha)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        # Order by start date descending
        query = query.order_by(Actividades.fecha_inicio.desc())
        
        return paginate_query(query, page, per_page)
    
    @staticmethod
    def get_actividad_by_id(actividad_id):
        """
        Get activity by ID.
        
        Args:
            actividad_id: Activity ID
            
        Returns:
            Actividades: Activity instance
            
        Raises:
            BusinessLogicError: If activity not found
        """
        actividad = Actividades.query.get(actividad_id)
        if not actividad:
            raise BusinessLogicError('Actividad no encontrada')
        return actividad
    
    @staticmethod
    def create_actividad(data):
        """
        Create a new activity.
        
        Args:
            data: Activity data
            
        Returns:
            Actividades: Created activity instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        # Validate data
        ActividadService.validate_actividad_data(data)
        
        # Parse dates
        fecha_inicio = None
        fecha_fin = None
        
        if data.get('fecha_inicio_actividad'):
            fecha_inicio = datetime.strptime(data['fecha_inicio_actividad'], '%Y-%m-%d').date()
        
        if data.get('fecha_fin_actividad'):
            fecha_fin = datetime.strptime(data['fecha_fin_actividad'], '%Y-%m-%d').date()
        
        # Create activity
        actividad = Actividades(
            nombre=data['nombre'],
            fecha_inicio=fecha_inicio,
            fecha_termino=fecha_fin,
            persona_a_cargo=data.get('persona_a_cargo'),
            observaciones=data.get('observaciones')
        )
        
        db.session.add(actividad)
        db.session.commit()
        
        return actividad
    
    @staticmethod
    def update_actividad(actividad_id, data):
        """
        Update an activity.
        
        Args:
            actividad_id: Activity ID
            data: Update data
            
        Returns:
            Actividades: Updated activity instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        actividad = ActividadService.get_actividad_by_id(actividad_id)
        
        # Validate data
        ActividadService.validate_actividad_data(data, is_update=True)
        
        # Update fields
        if 'nombre_actividad' in data:
            actividad.nombre_actividad = data['nombre_actividad']
        if 'descripcion_actividad' in data:
            actividad.descripcion_actividad = data['descripcion_actividad']
        if 'id_centro' in data:
            actividad.id_centro = data['id_centro']
        if 'id_persona_a_cargo' in data:
            actividad.id_persona_a_cargo = data['id_persona_a_cargo']
        
        # Update dates
        if 'fecha_inicio_actividad' in data:
            if data['fecha_inicio_actividad']:
                actividad.fecha_inicio_actividad = datetime.strptime(
                    data['fecha_inicio_actividad'], '%Y-%m-%d'
                ).date()
            else:
                actividad.fecha_inicio_actividad = None
        
        if 'fecha_fin_actividad' in data:
            if data['fecha_fin_actividad']:
                actividad.fecha_fin_actividad = datetime.strptime(
                    data['fecha_fin_actividad'], '%Y-%m-%d'
                ).date()
            else:
                actividad.fecha_fin_actividad = None
        
        db.session.commit()
        return actividad
    
    @staticmethod
    def delete_actividad(actividad_id):
        """
        Delete an activity.
        
        Args:
            actividad_id: Activity ID to delete
            
        Raises:
            BusinessLogicError: If business rules are violated
        """
        actividad = ActividadService.get_actividad_by_id(actividad_id)
        
        # Check for related workshops
        talleres_count = Talleres.query.filter_by(id_actividad=actividad_id).count()
        if talleres_count > 0:
            raise BusinessLogicError(
                f'No se puede eliminar la actividad porque tiene {talleres_count} taller(es) asociado(s)'
            )
        
        db.session.delete(actividad)
        db.session.commit()
    
    @staticmethod
    def get_actividades_by_centro(centro_id):
        """
        Get activities by community center.
        
        Args:
            centro_id: Center ID
            
        Returns:
            list: List of activities
        """
        return Actividades.query.filter_by(id_centro=centro_id).order_by(
            Actividades.fecha_inicio_actividad.desc()
        ).all()


class TallerService:
    """
    Service class for workshop management operations.
    """
    
    @staticmethod
    def validate_taller_data(data, is_update=False):
        """
        Validate workshop data.
        
        Args:
            data: Workshop data to validate
            is_update: Whether this is an update operation
            
        Raises:
            ValidationError: If validation fails
        """
        if not is_update:
            required_fields = ['nombre', 'fecha_inicio']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field.replace("_", " ").title()} es requerido')
        
        # Validate name length
        if 'nombre' in data and data['nombre']:
            if len(data['nombre']) > 150:
                raise ValidationError('Nombre del taller no puede exceder 150 caracteres')
        
        # Validate responsible person if provided
        if 'persona_a_cargo' in data and data['persona_a_cargo']:
            from app.models import PersonasACargo
            persona = PersonasACargo.query.get(data['persona_a_cargo'])
            if not persona:
                raise ValidationError('Persona a cargo no encontrada')
    
    @staticmethod
    def get_talleres(page, per_page, nombre_filter=None, actividad_filter=None):
        """
        Get paginated list of workshops with optional filters.
        
        Args:
            page: Page number
            per_page: Items per page
            nombre_filter: Filter by workshop name
            actividad_filter: Filter by activity ID
            
        Returns:
            dict: Paginated workshop data
        """
        query = Talleres.query
        
        # Apply filters
        if nombre_filter:
            query = query.filter(Talleres.nombre.ilike(f'%{nombre_filter}%'))
        
        # Order by name
        query = query.order_by(Talleres.nombre)
        
        return paginate_query(query, page, per_page)
    
    @staticmethod
    def get_taller_by_id(taller_id):
        """
        Get workshop by ID.
        
        Args:
            taller_id: Workshop ID
            
        Returns:
            Talleres: Workshop instance
            
        Raises:
            BusinessLogicError: If workshop not found
        """
        taller = Talleres.query.get(taller_id)
        if not taller:
            raise BusinessLogicError('Taller no encontrado')
        return taller
    
    @staticmethod
    def create_taller(data):
        """
        Create a new workshop.
        
        Args:
            data: Workshop data
            
        Returns:
            Talleres: Created workshop instance
        """
        # Validate data
        TallerService.validate_taller_data(data)
        
        # Create workshop
        # Parse dates if they are strings
        fecha_inicio = data['fecha_inicio']
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        
        fecha_termino = data.get('fecha_termino')
        if fecha_termino and isinstance(fecha_termino, str):
            fecha_termino = datetime.strptime(fecha_termino, '%Y-%m-%d').date()
        
        taller = Talleres(
            nombre=data['nombre'],
            fecha_inicio=fecha_inicio,
            fecha_termino=fecha_termino,
            persona_a_cargo=data.get('persona_a_cargo'),
            observaciones=data.get('observaciones')
        )
        
        db.session.add(taller)
        db.session.commit()
        
        return taller
    
    @staticmethod
    def update_taller(taller_id, data):
        """
        Update a workshop.
        
        Args:
            taller_id: Workshop ID
            data: Update data
            
        Returns:
            Talleres: Updated workshop instance
        """
        taller = TallerService.get_taller_by_id(taller_id)
        
        # Validate data
        TallerService.validate_taller_data(data, is_update=True)
        
        # Update fields
        if 'nombre' in data:
            taller.nombre = data['nombre']
        if 'fecha_inicio' in data:
            fecha_inicio = data['fecha_inicio']
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            taller.fecha_inicio = fecha_inicio
        if 'fecha_termino' in data:
            fecha_termino = data['fecha_termino']
            if fecha_termino and isinstance(fecha_termino, str):
                fecha_termino = datetime.strptime(fecha_termino, '%Y-%m-%d').date()
            taller.fecha_termino = fecha_termino
        if 'persona_a_cargo' in data:
            taller.persona_a_cargo = data['persona_a_cargo']
        if 'observaciones' in data:
            taller.observaciones = data['observaciones']
        if 'descripcion_taller' in data:
            taller.descripcion_taller = data['descripcion_taller']
        if 'id_actividad' in data:
            taller.id_actividad = data['id_actividad']
        if 'id_persona_a_cargo' in data:
            taller.id_persona_a_cargo = data['id_persona_a_cargo']
        
        db.session.commit()
        return taller
    
    @staticmethod
    def delete_taller(taller_id):
        """
        Delete a workshop.
        
        Args:
            taller_id: Workshop ID to delete
        """
        taller = TallerService.get_taller_by_id(taller_id)
        
        db.session.delete(taller)
        db.session.commit()