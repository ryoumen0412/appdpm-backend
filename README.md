# DPM Backend API - Documentación Técnica

## Descripción General

Sistema de gestión para Departamento de Personas Mayores (DPM) desarrollado con Flask y arquitectura modular. La API REST proporciona endpoints para la gestión integral de personas mayores, centros comunitarios, actividades, servicios y personal de apoyo.

## Estado del Sistema

**Estado Actual**: Operativo
**Última Verificación**: 23 de Septiembre, 2025
**Integridad del Código**: 8.8/10 - Excelente
**Estado de Seguridad**: Implementado y verificado

## Arquitectura del Sistema

### Estructura Modular

El sistema utiliza una arquitectura modular basada en blueprints de Flask, organizando la funcionalidad en módulos independientes:

```md
app/api/
├── auth/ # Autenticación y autorización
├── usuarios/ # Gestión de usuarios del sistema
├── personas/ # Gestión de personas mayores y a cargo
├── centros/ # Centros comunitarios
├── actividades/ # Actividades y talleres
├── servicios/ # Servicios y relaciones
├── mantenciones/ # Mantenciones de centros
└── trabajadores/ # Trabajadores de apoyo
```

### Patrón de Arquitectura

Cada módulo sigue el patrón MVC adaptado para APIs REST:

- **routes.py**: Controladores HTTP (endpoints)
- **services.py**: Lógica de negocio y validaciones
- **models.py**: Modelos de datos (SQLAlchemy)
- **utils/**: Utilidades compartidas (respuestas, errores, paginación)

## Requisitos del Sistema

### Dependencias Principales

- **Python**: 3.8+
- **Flask**: 2.3.3
- **SQLAlchemy**: 3.0.5
- **PostgreSQL**: 12+
- **Flask-Migrate**: 4.0.5
- **Flask-Limiter**: 3.5.0
- **psycopg2-binary**: 2.9.7

### Instalación

1. **Clonar el repositorio**

```bash
git clone <repository-url>
cd appdpm-clone/backend
```

2. **Crear entorno virtual**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Crear archivo `.env` en el directorio backend:

```env
DB_HOST=100.126.196.33
DB_PORT=5432
DB_NAME=db_dpm
DB_USER=dbadmin
DB_PASSWORD=hola123
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=e73f6bc7d677d03655fee282b492f2038d761cd9ded0bf7077ea181e23b39ea5
CORS_ORIGINS=http://localhost:8081,http://localhost:19006,http://localhost:3000,http://localhost:19000
```

5. **Inicializar base de datos**

```bash
flask db upgrade
python create_test_user.py  # Crear usuario de prueba
```

6. **Ejecutar aplicación**

```bash
python run.py
```

## Configuración de Base de Datos

### Modelos de Datos

El sistema utiliza los siguientes modelos principales:

- **Usuario**: Usuarios del sistema con roles y permisos
- **PersonasMayores**: Personas mayores beneficiarias
- **PersonasACargo**: Personas responsables de los beneficiarios
- **CentrosComunitarios**: Centros donde se realizan actividades
- **Actividades**: Actividades programadas
- **Talleres**: Talleres específicos
- **Servicios**: Servicios proporcionados
- **Mantenciones**: Mantenimientos de centros
- **TrabajadoresApoyo**: Personal de apoyo

### Migraciones

```bash
# Crear nueva migración
flask db migrate -m "Descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir migración
flask db downgrade
```

## Sistema de Autenticación

### Niveles de Acceso

1. **Nivel 1 (Apoyo)**: Acceso de solo lectura
2. **Nivel 2 (Encargado)**: Acceso de lectura y escritura
3. **Nivel 3 (Admin)**: Acceso completo incluyendo gestión de usuarios

### Endpoints de Autenticación

- `POST /api/auth/login`: Inicio de sesión
- `GET /api/auth/profile`: Perfil del usuario autenticado
- `POST /api/auth/logout`: Cerrar sesión
- `POST /api/auth/register`: Registrar nuevo usuario (solo admin)
- `POST /api/auth/change-password`: Cambiar contraseña

### Uso de Tokens JWT

```python
# Headers requeridos para endpoints protegidos
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

## Endpoints de la API

### Formato de Respuesta Estándar

```json
{
  "success": true|false,
  "data": {},
  "message": "Mensaje descriptivo",
  "timestamp": "2025-09-22T16:30:00.000000",
  "error_code": "CODIGO_ERROR" // Solo en errores
}
```

### Módulos y Endpoints

#### 1. Usuarios (`/api/usuarios`)

- `GET /`: Lista paginada de usuarios
- `GET /{id}`: Usuario específico
- `POST /`: Crear usuario
- `PUT /{id}`: Actualizar usuario
- `DELETE /{id}`: Eliminar usuario

#### 2. Personas Mayores (`/api/personas-mayores`)

- `GET /`: Lista paginada con filtros
- `GET /{rut}`: Persona específica por RUT
- `POST /`: Registrar nueva persona
- `PUT /{rut}`: Actualizar información
- `DELETE /{rut}`: Eliminar registro

#### 3. Personas a Cargo (`/api/personas-a-cargo`)

- `GET /`: Lista paginada
- `GET /{rut}`: Persona específica
- `POST /`: Crear registro
- `PUT /{rut}`: Actualizar
- `DELETE /{rut}`: Eliminar

#### 4. Centros Comunitarios (`/api/centros`)

- `GET /`: Lista de centros
- `GET /{id}`: Centro específico
- `POST /`: Crear centro
- `PUT /{id}`: Actualizar centro
- `DELETE /{id}`: Eliminar centro

#### 5. Actividades (`/api/actividades`)

- `GET /`: Lista de actividades
- `GET /{id}`: Actividad específica
- `POST /`: Crear actividad
- `PUT /{id}`: Actualizar actividad
- `DELETE /{id}`: Eliminar actividad

#### 6. Talleres (`/api/actividades/talleres`)

- `GET /`: Lista de talleres
- `GET /{id}`: Taller específico
- `POST /`: Crear taller
- `PUT /{id}`: Actualizar taller
- `DELETE /{id}`: Eliminar taller

#### 7. Servicios (`/api/servicios`)

- `GET /`: Lista de servicios
- `GET /{id}`: Servicio específico
- `POST /`: Crear servicio
- `PUT /{id}`: Actualizar servicio
- `DELETE /{id}`: Eliminar servicio

#### 8. Mantenciones (`/api/mantenciones`)

- `GET /`: Lista de mantenciones
- `GET /{id}`: Mantención específica
- `POST /`: Crear mantención
- `PUT /{id}`: Actualizar mantención
- `DELETE /{id}`: Eliminar mantención
- `GET /centro/{id}`: Mantenciones por centro

#### 9. Trabajadores de Apoyo (`/api/trabajadores-apoyo`)

- `GET /`: Lista de trabajadores
- `GET /{rut}`: Trabajador específico
- `POST /`: Crear trabajador
- `PUT /{rut}`: Actualizar trabajador
- `DELETE /{rut}`: Eliminar trabajador
- `GET /centro/{id}`: Trabajadores por centro

## Parámetros de Consulta Comunes

### Paginación

- `page`: Número de página (default: 1)
- `per_page`: Elementos por página (default: 10, max: 100)

### Filtros

- `nombre`: Filtro por nombre
- `rut`: Filtro por RUT
- `fecha_desde`: Filtro desde fecha (YYYY-MM-DD)
- `fecha_hasta`: Filtro hasta fecha (YYYY-MM-DD)

## Manejo de Errores

### Códigos de Error Estándar

- `VALIDATION_ERROR`: Error de validación de datos
- `BUSINESS_LOGIC_ERROR`: Error de lógica de negocio
- `AUTHENTICATION_ERROR`: Error de autenticación
- `AUTHORIZATION_ERROR`: Error de autorización
- `NOT_FOUND_ERROR`: Recurso no encontrado
- `INTERNAL_ERROR`: Error interno del servidor

### Ejemplo de Respuesta de Error

```json
{
  "success": false,
  "error": "RUT y contraseña son requeridos",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-09-22T16:30:00.000000"
}
```

## Logging y Monitoreo

### Configuración de Logs

Los logs se almacenan en `logs/backend.log` con la siguiente información:

- Timestamp
- Nivel de log (INFO, ERROR, WARNING)
- Módulo origen
- Mensaje descriptivo

### Monitoreo de Salud

- **Health Check**: `GET /` (verifica conectividad)
- **Status de Base de Datos**: Verificación automática en startup
- **Métricas de Rate Limiting**: Flask-Limiter integrado

## Testing

### Verificación del Sistema

Ejecutar el sistema completo de verificación:

```bash
python test_modular_system.py
```

Este script verifica:

- Conectividad del servidor
- Registro de blueprints
- Protección de endpoints
- Sistema de autenticación
- Funcionalidad de todos los endpoints

### Testing Manual

```bash
# Verificar usuarios en BD
python check_user.py

# Crear usuario de prueba
python create_test_user.py
```

## Despliegue

### Variables de Entorno Producción

```env
FLASK_ENV=production
DATABASE_URL=postgresql://prod_user:prod_pass@db_server/prod_db
SECRET_KEY=production-secret-key
JWT_SECRET_KEY=production-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
RATE_LIMIT_STORAGE_URL=redis://redis_server:6379
```

### Comandos de Despliegue

```bash
# Instalar dependencias de producción
pip install -r requirements.txt

# Aplicar migraciones
flask db upgrade

# Ejecutar con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## Seguridad

### Medidas Implementadas

- **JWT Tokens**: Autenticación basada en tokens con expiración configurable
- **Rate Limiting**: Límites de solicitudes por IP y por usuario
- **Security Headers**: Implementación completa de headers de seguridad
  - Content Security Policy (CSP)
  - X-Frame-Options (anti-clickjacking)
  - X-Content-Type-Options (anti-MIME sniffing)
  - Strict-Transport-Security (HSTS)
- **Validación de Entrada**: Sanitización y validación de todos los datos
- **Autorización por Roles**: Control granular de permisos por nivel de usuario
- **Hash de Contraseñas**: Werkzeug para almacenamiento seguro
- **CORS Configurado**: Restricción de orígenes permitidos

### Validación de Integridad

El sistema incluye verificación automática de:

- Configuración de variables de entorno
- Conectividad con base de datos
- Integridad de migraciones
- Funcionamiento de endpoints críticos
- Estado de autenticación y autorización

### Buenas Prácticas

- Usar HTTPS en producción
- Configurar CORS apropiadamente según entorno
- Rotar claves JWT regularmente
- Monitorear logs de seguridad
- Implementar backup automático de base de datos
- Validar entrada en todos los endpoints
- Mantener dependencias actualizadas

## Mantenimiento

### Tareas Regulares

1. **Backup de Base de Datos**: Diario automático
2. **Limpieza de Logs**: Rotación semanal
3. **Actualización de Dependencias**: Mensual
4. **Revisión de Seguridad**: Trimestral

### Comandos Útiles

```bash
# Verificar salud del sistema
python test_modular_system.py

# Limpiar logs antiguos
find logs/ -name "*.log" -mtime +30 -delete

# Verificar migraciones pendientes
flask db show

# Backup de base de datos
pg_dump dbname > backup_$(date +%Y%m%d).sql
```

## Contribución

### Estructura para Nuevos Módulos

1. Crear directorio en `app/api/nuevo_modulo/`
2. Implementar archivos: `__init__.py`, `routes.py`, `services.py`
3. Registrar blueprint en `app/routes/api.py`
4. Agregar tests en `test_modular_system.py`
5. Actualizar documentación

### Estándares de Código

- Seguir PEP 8 para Python
- Documentar funciones con docstrings
- Implementar manejo de errores consistente
- Usar type hints donde sea posible
- Mantener cobertura de tests > 80%

## Solución de Problemas Comunes

### Error de Conexión a Base de Datos

```bash
# Verificar conexión
pg_isready -h localhost -p 5432

# Verificar configuración
echo $DATABASE_URL
```

### Token JWT Expirado

Los tokens expiran en 1 hora. Renovar mediante:

```
POST /api/auth/login
```

### Error 500 en Endpoints

Revisar logs en `logs/backend.log` para detalles específicos.

### Performance Issues

```bash
# Verificar queries lentas en PostgreSQL
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

## Versioning

- **Versión Actual**: 2.0.0 (Modular)
- **Versión Anterior**: 1.0.0 (Monolítica - deprecada)

### Changelog

#### v2.0.0 (2025-09-22)

- Migración completa a arquitectura modular
- Implementación de 8 módulos independientes
- Sistema de autenticación JWT mejorado
- Endpoints completos para todas las entidades
- Testing automatizado implementado
- Limpieza de código legacy
- Verificación de integridad implementada
- Headers de seguridad completos
- Documentación técnica actualizada

---

**Contacto**: [Información del equipo de desarrollo]
**Repositorio**: [URL del repositorio]
**Documentación API**: [URL de documentación Swagger - pendiente]
