"""
Application Entry Point

"""

from app import create_app, db

# Crear instancia de la aplicación usando el Application Factory
app = create_app()

# Crear todas las tablas de la base de datos si no existen
# Se ejecuta dentro del contexto de la aplicación para acceder a la configuración
with app.app_context():
    db.create_all()
    print("Tablas de base de datos creadas/verificadas exitosamente")

# Punto de entrada principal - solo se ejecuta si el archivo se ejecuta directamente
if __name__ == '__main__':
    print("Iniciando servidor Flask para Sistema DPM...")
    print("Servidor disponible en: http://localhost:5000")
    print("API disponible en: http://localhost:5000/api/health")
    print("Modo debug: ACTIVADO")
    
    # Ejecutar servidor de desarrollo
    # debug=True: Recarga automática al detectar cambios en código
    # host='0.0.0.0': Acepta conexiones desde cualquier IP
    # port=5000: Puerto estándar para desarrollo Flask
    app.run(debug=True, host='0.0.0.0', port=5000)

