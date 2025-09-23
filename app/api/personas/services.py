"""
Personas Services

Business logic layer for person-related operations.
"""

from sqlalchemy import or_
from app.extensions import db
from app.models import PersonasMayores, PersonasACargo
from app.api.utils.errors import ValidationError, BusinessLogicError
from app.auth_utils import validate_rut, clean_rut
from datetime import datetime, date


class PersonasMayoresService:
    """
    Service class for PersonasMayores operations.
    """
    
    @staticmethod
    def build_search_query(search=None, sector=None, genero=None):
        """
        Build filtered query for personas mayores.
        
        Args:
            search: Search term for RUT, nombre, apellidos
            sector: Filter by sector
            genero: Filter by gender
            
        Returns:
            Query: Filtered SQLAlchemy query
        """
        query = PersonasMayores.query
        
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(or_(
                PersonasMayores.rut.ilike(search_term),
                PersonasMayores.nombre.ilike(search_term),
                PersonasMayores.apellidos.ilike(search_term)
            ))
        
        if sector:
            query = query.filter(PersonasMayores.sector.ilike(f"%{sector.strip()}%"))
        
        if genero:
            query = query.filter(PersonasMayores.genero == genero)
        
        return query.order_by(PersonasMayores.apellidos, PersonasMayores.nombre)
    
    @staticmethod
    def validate_persona_mayor_data(data, is_update=False):
        """
        Validate persona mayor data.
        
        Args:
            data: Dict with person data
            is_update: Whether this is an update operation
            
        Raises:
            ValidationError: If validation fails
        """
        if not is_update:
            # Required fields for creation
            required_fields = ['rut', 'nombre', 'apellidos']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field} es requerido', field=field)
        
        # Validate RUT if provided
        if 'rut' in data:
            rut = clean_rut(data['rut'])
            if not validate_rut(rut):
                raise ValidationError('Formato de RUT inválido', field='rut')
            data['rut'] = rut  # Update with cleaned RUT
        
        # Validate email format if provided
        if data.get('email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                raise ValidationError('Formato de email inválido', field='email')
        
        # Validate fecha_nacimiento if provided
        if data.get('fecha_nacimiento'):
            try:
                if isinstance(data['fecha_nacimiento'], str):
                    data['fecha_nacimiento'] = datetime.strptime(
                        data['fecha_nacimiento'], '%Y-%m-%d'
                    ).date()
            except ValueError:
                raise ValidationError(
                    'Formato de fecha inválido. Use YYYY-MM-DD', 
                    field='fecha_nacimiento'
                )
    
    @staticmethod
    def create_persona_mayor(data):
        """
        Create a new persona mayor.
        
        Args:
            data: Dict with person data
            
        Returns:
            PersonasMayores: Created person instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        PersonasMayoresService.validate_persona_mayor_data(data)
        
        # Check if RUT already exists
        existing = PersonasMayores.query.filter_by(rut=data['rut']).first()
        if existing:
            raise BusinessLogicError('Ya existe una persona mayor con este RUT')
        
        persona = PersonasMayores(
            rut=data['rut'],
            nombre=data['nombre'],
            apellidos=data['apellidos'],
            genero=data.get('genero'),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            direccion=data.get('direccion'),
            sector=data.get('sector'),
            telefono=data.get('telefono'),
            email=data.get('email'),
            cedula_discapacidad=data.get('cedula_discapacidad', False)
        )
        
        db.session.add(persona)
        db.session.commit()
        
        return persona
    
    @staticmethod
    def update_persona_mayor(rut, data):
        """
        Update an existing persona mayor.
        
        Args:
            rut: RUT of the person to update
            data: Dict with updated data
            
        Returns:
            PersonasMayores: Updated person instance
            
        Raises:
            ValidationError: If validation fails
        """
        persona = PersonasMayores.query.get_or_404(rut)
        
        PersonasMayoresService.validate_persona_mayor_data(data, is_update=True)
        
        # Update fields
        updatable_fields = [
            'nombre', 'apellidos', 'genero', 'fecha_nacimiento',
            'direccion', 'sector', 'telefono', 'email', 'cedula_discapacidad'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(persona, field, data[field])
        
        db.session.commit()
        
        return persona


class PersonasACargoService:
    """
    Service class for PersonasACargo operations.
    """
    
    @staticmethod
    def validate_persona_a_cargo_data(data, is_update=False):
        """
        Validate persona a cargo data.
        """
        if not is_update:
            required_fields = ['rut', 'nombre', 'apellido']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field} es requerido', field=field)
        
        # Validate RUT if provided
        if 'rut' in data:
            rut = clean_rut(data['rut'])
            if not validate_rut(rut):
                raise ValidationError('Formato de RUT inválido', field='rut')
            data['rut'] = rut
        
        # Validate email format if provided
        if data.get('correo_electronico'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['correo_electronico']):
                raise ValidationError('Formato de email inválido', field='correo_electronico')
        
        # Validate fecha_nacimiento if provided
        if data.get('fecha_nacimiento'):
            try:
                if isinstance(data['fecha_nacimiento'], str):
                    data['fecha_nacimiento'] = datetime.strptime(
                        data['fecha_nacimiento'], '%Y-%m-%d'
                    ).date()
            except ValueError:
                raise ValidationError(
                    'Formato de fecha inválido. Use YYYY-MM-DD', 
                    field='fecha_nacimiento'
                )
    
    @staticmethod
    def create_persona_a_cargo(data):
        """
        Create a new persona a cargo.
        """
        PersonasACargoService.validate_persona_a_cargo_data(data)
        
        # Check if RUT already exists
        existing = PersonasACargo.query.filter_by(rut=data['rut']).first()
        if existing:
            raise BusinessLogicError('Ya existe una persona a cargo con este RUT')
        
        persona = PersonasACargo(
            rut=data['rut'],
            nombre=data['nombre'],
            apellido=data['apellido'],
            correo_electronico=data.get('correo_electronico'),
            telefono=data.get('telefono'),
            fecha_nacimiento=data.get('fecha_nacimiento')
        )
        
        db.session.add(persona)
        db.session.commit()
        
        return persona
    
    @staticmethod
    def update_persona_a_cargo(rut, data):
        """
        Update an existing persona a cargo.
        """
        persona = PersonasACargo.query.get_or_404(rut)
        
        PersonasACargoService.validate_persona_a_cargo_data(data, is_update=True)
        
        # Update fields
        updatable_fields = [
            'nombre', 'apellido', 'correo_electronico', 
            'telefono', 'fecha_nacimiento'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(persona, field, data[field])
        
        db.session.commit()
        
        return persona