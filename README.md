# DPM Backend API - Sistema Interno

## Descripción General

API REST interna para la gestión del Departamento de Personas Mayores (DPM). Sistema desarrollado con Flask y arquitectura modular, diseñado específicamente para uso interno organizacional sin exposición pública.

**Propósito**: Aplicación web de uso interno exclusivo
**Audiencia**: Personal interno autorizado
**Acceso**: Red interna únicamente

## Estado del Sistema

**Estado Actual**: Operativo ✅
**Última Verificación**: 24 de Septiembre, 2025
**Integridad del Código**: Verificado - Sin errores
**Estado de Seguridad**: Configurado para uso interno
**Testing**: Smoke tests y pruebas de integración completadas

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

**Backend:**

- **Python**: 3.8+
- **Flask**: 2.3.3
- **SQLAlchemy**: 3.0.5
- **Flask-Migrate**: 4.0.5
- **Flask-Limiter**: 3.5.0
- **PyJWT**: 2.8.0
- **psycopg2-binary**: 2.9.7

**Infraestructura:**

- **PostgreSQL**: 12+ (Base de datos)
- **Redis**: 6.0+ (Rate limiting y cache)
- **Nginx**: 1.18+ (Reverse proxy)
- **Gunicorn**: 21.0+ (WSGI server)

**Desarrollo:**

- **python-dotenv**: 1.0.0
- **bcrypt**: 4.0+ (Hashing de contraseñas)

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

# Para producción, instalar también:
pip install gunicorn redis psutil
```

4. **Configurar variables de entorno**

Crear archivo `.env` en el directorio backend:

**Desarrollo:**

```env
# Base de datos
DB_HOST=100.126.196.33
DB_PORT=5432
DB_NAME=db_dpm
DB_USER=dbadmin
DB_PASSWORD=hola123

# Flask
FLASK_ENV=development
FLASK_APP=run.py

# Seguridad
SECRET_KEY=e73f6bc7d677d03655fee282b492f2038d761cd9ded0bf7077ea181e23b39ea5
JWT_SECRET_KEY=e73f6bc7d677d03655fee282b492f2038d761cd9ded0bf7077ea181e23b39ea5

# CORS - Solo IPs internas
CORS_ORIGINS=http://localhost:3000,http://192.168.1.100,http://192.168.1.101

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0
```

**Producción:**

```env
# Configurar según infraestructura interna
FLASK_ENV=production
DATABASE_URL=postgresql://prod_user:prod_pass@internal_db_server/appdpm_prod
SECRET_KEY=production-secret-key-change-this
JWT_SECRET_KEY=production-jwt-secret-change-this
REDIS_URL=redis://internal_redis_server:6379/0
CORS_ORIGINS=http://192.168.1.100,http://192.168.1.101
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

## Testing y Verificación

### Estado de Testing Actual

✅ **Completado - 24 de Septiembre, 2025:**

- **Escaneo completo de errores**: Sin errores de sintaxis encontrados
- **Smoke tests**: Aplicación se crea e inicializa correctamente
- **Pruebas de integración**: Endpoints responden apropiadamente
- **Health checks**: Base de datos y servicios conectados
- **Autenticación**: Sistema JWT funcionando
- **CORS**: Configurado correctamente
- **Rate limiting**: Implementado y funcional

### Verificación Rápida

**Health Check:**

```bash
curl http://localhost:5000/api/health
# Respuesta esperada: {"status": "healthy", "database": "connected"}
```

**Test de Autenticación:**

```bash
# Login (debe retornar 400 sin credenciales)
curl -X POST http://localhost:5000/api/auth/login

# Endpoint protegido (debe retornar 401 sin token)
curl http://localhost:5000/api/usuarios/
```

### Herramientas de Diagnóstico

```bash
# Verificar usuarios en BD
python check_user.py

# Crear usuario de prueba
python create_test_user.py

# Generar nueva clave secreta
python gen_secret_key.py
```

## Despliegue a Producción (Uso Interno)

### Requisitos de Infraestructura

- **Servidor**: Red interna únicamente
- **Web Server**: Nginx (reverse proxy)
- **WSGI Server**: Gunicorn
- **Base de Datos**: PostgreSQL 12+
- **Cache/Rate Limiting**: Redis (recomendado)
- **Sistema Operativo**: Ubuntu 20.04+ / CentOS 8+

### Configuración Gunicorn

Crear `gunicorn_config.py`:

```python
import multiprocessing

# Server socket - solo red interna
bind = "127.0.0.1:5000"
backlog = 2048

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30

# Logging
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"

# Process
proc_name = 'appdpm_backend'
preload_app = True
```

### Configuración Nginx

Crear `/etc/nginx/sites-available/appdpm`:

```nginx
upstream appdpm_backend {
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    server_name 192.168.1.100;  # IP interna del servidor

    # Logs
    access_log /var/log/nginx/appdpm_access.log;
    error_log /var/log/nginx/appdpm_error.log;

    # Rate limiting interno (permisivo)
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

    location /api/ {
        limit_req zone=api burst=20 nodelay;

        proxy_pass http://appdpm_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Timeouts para uso interno
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://appdpm_backend;
        access_log off;
    }
}
```

### Script de Despliegue

```bash
#!/bin/bash
set -e

echo "🚀 Desplegando APPDPM Backend..."

APP_DIR="/opt/appdpm/backend"
SERVICE_NAME="appdpm-backend"

# Detener servicio
sudo systemctl stop $SERVICE_NAME

# Actualizar código
cd $APP_DIR
git pull origin main

# Instalar dependencias
source venv/bin/activate
pip install -r requirements.txt

# Migraciones
export FLASK_APP=run.py
export FLASK_ENV=production
flask db upgrade

# Reiniciar servicios
sudo systemctl start $SERVICE_NAME
sudo systemctl reload nginx

# Verificar
curl -f http://127.0.0.1:5000/health && echo "✅ Despliegue exitoso"
```

## Seguridad (Configuración Interna)

### Medidas de Seguridad Implementadas

**Autenticación y Autorización:**

- **JWT Tokens**: Autenticación basada en tokens (8 horas por defecto para jornada laboral)
- **Niveles de Acceso**: Control granular por roles (Apoyo, Encargado, Admin)
- **Hash de Contraseñas**: Almacenamiento seguro con Werkzeug

**Protección de Red:**

- **CORS Restringido**: Solo IPs de red interna permitidas
- **Rate Limiting**: Configurado con Redis para uso interno (más permisivo)
- **Security Headers**: Implementados para navegadores internos
  - X-Frame-Options
  - X-Content-Type-Options
  - Content Security Policy (CSP)

**Validación de Datos:**

- **Sanitización**: Validación completa de entrada de datos
- **Esquemas de Validación**: Validación automática por endpoint
- **Control de Tipos**: Verificación de tipos de datos

### Configuración de Red Interna

**IPs Permitidas (Ejemplo):**

```
192.168.1.100-110  # Estaciones de trabajo
192.168.1.200      # Servidor de aplicaciones
192.168.1.201      # Servidor de base de datos
```

**Firewall Recomendado:**

```bash
# Permitir solo red interna
sudo ufw allow from 192.168.1.0/24 to any port 5000
sudo ufw deny 5000
```

### Validación de Integridad Automática

✅ **Verificaciones Implementadas:**

- Conectividad con base de datos PostgreSQL
- Disponibilidad de Redis (rate limiting)
- Integridad de migraciones
- Funcionamiento de endpoints críticos
- Validación de tokens JWT
- Estados de autenticación y autorización

### Buenas Prácticas para Uso Interno

1. **Monitoreo**: Logs centralizados en `/var/log/appdpm/`
2. **Backup**: Respaldo automático diario de base de datos
3. **Actualizaciones**: Mantener dependencias actualizadas mensualmente
4. **Acceso**: Restringir acceso a red interna únicamente
5. **Tokens**: Renovación automática durante jornada laboral
6. **Redis**: Usar Redis en producción para mejor performance

## Mantenimiento y Monitoreo

### Cronograma de Mantenimiento

| Tarea               | Frecuencia | Comando/Acción                  |
| ------------------- | ---------- | ------------------------------- |
| Health Check        | Diario     | `curl http://server/api/health` |
| Backup BD           | Diario     | Script automático PostgreSQL    |
| Rotación Logs       | Semanal    | Logrotate configurado           |
| Limpieza Cache      | Semanal    | Redis FLUSHDB si necesario      |
| Update Dependencias | Mensual    | `pip list --outdated`           |
| Revisión Seguridad  | Trimestral | Auditoria interna               |

### Comandos de Mantenimiento

**Monitoreo del Sistema:**

```bash
# Verificar salud completa
curl http://localhost:5000/api/health

# Estado de servicios
sudo systemctl status appdpm-backend
sudo systemctl status nginx
sudo systemctl status redis

# Verificar logs recientes
tail -f /var/log/appdpm/backend.log
```

**Backup y Limpieza:**

```bash
# Backup manual de base de datos
pg_dump -h DB_HOST -U DB_USER db_dpm > backup_$(date +%Y%m%d_%H%M).sql

# Limpiar logs antiguos (30+ días)
find /var/log/appdpm/ -name "*.log" -mtime +30 -delete

# Verificar espacio en disco
df -h /var/log/appdpm/
```

**Base de Datos:**

```bash
# Verificar migraciones pendientes
flask db show

# Aplicar nuevas migraciones
flask db upgrade

# Ver historial de migraciones
flask db history
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

## Solución de Problemas Comunes

### Problemas de Conexión

**Error: "Failed to create application: Missing required configuration"**

```bash
# Verificar variables de entorno
echo $SECRET_KEY
echo $DATABASE_URL

# Cargar archivo .env manualmente
source .env
python run.py
```

**Error: "Redis connection failed"**

```bash
# Verificar Redis
redis-cli ping
# Si no responde: sudo systemctl start redis

# Usar modo degradado (sin Redis)
export REDIS_URL="memory://"
```

**Error 500 en Endpoints**

```bash
# Revisar logs detallados
tail -f logs/backend.log

# Verificar permisos de base de datos
psql -h DB_HOST -U DB_USER -d DB_NAME -c "SELECT version();"
```

### Performance Issues

**Consultas lentas:**

```sql
-- En PostgreSQL, verificar consultas lentas
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 10;
```

**Memoria alta:**

```bash
# Verificar uso de memoria
ps aux | grep gunicorn
top -p $(pgrep -d, gunicorn)

# Reiniciar workers si necesario
sudo systemctl reload appdpm-backend
```

## Versioning y Changelog

**Versión Actual**: 2.1.0 (Configurado para Uso Interno)

### Changelog

#### v2.1.0 (2025-09-24)

- ✅ **Testing completo**: Smoke tests y pruebas de integración
- ✅ **Configuración Redis**: Rate limiting mejorado
- ✅ **Documentación actualizada**: Enfoque en uso interno
- ✅ **Configuración Nginx**: Reverse proxy para producción
- ✅ **Scripts de despliegue**: Automatización completa
- ✅ **Monitoreo mejorado**: Health checks detallados

#### v2.0.0 (2025-09-22)

- Arquitectura modular completa
- 8 módulos API independientes
- Autenticación JWT robusta
- Headers de seguridad implementados
- Sistema de testing automatizado

---

## Información del Proyecto

**Nombre**: Sistema DPM Backend API
**Tipo**: Aplicación Web Interna
**Repositorio**: `appdpm-backend`
**Mantenedor**: Equipo de Desarrollo Interno
**Soporte**: Red interna únicamente
**Documentación**: Este README (actualizado regularmente)

**📞 Contacto Técnico**: [Equipo de Desarrollo]
**🔧 Soporte**: [Mesa de Ayuda Interna]
**📄 Wiki**: [Enlace a documentación interna]
